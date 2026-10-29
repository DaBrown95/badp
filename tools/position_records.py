"""Decode v1.5 position-record streams to ignored local analysis output.

The format is inferred from the bank-0 search code. This tool does not claim
that all record types or the runtime range of pointer indices are understood.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, input_path, load_target

ROOT = Path(__file__).resolve().parents[1]
CPU_BASE = 0x8000
BANK_SIZE = 0x8000
TABLE_A = 0xA3EC
TABLE_B = 0xA418
TABLE_ENTRIES = 22
STREAM_START = 0xA444
STREAM_LIMIT = 0xCBFF
TERMINATOR = b"\xff\xff\x00\x00"


def _word(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise ValueError("word outside bank")
    return int.from_bytes(data[offset:offset + 2], "little")


def decode_stream(data: bytes, *, require_order: bool = True) -> list[dict]:
    """Decode an exact stream span, rejecting malformed or unordered records."""
    if type(require_order) is not bool:
        raise ValueError('invalid position ordering policy')
    if len(data) < 4 or data[-4:] != TERMINATOR or (len(data) - 4) % 8:
        raise ValueError("invalid stream length or terminator")
    records = []
    previous = -1
    for offset in range(0, len(data) - 4, 8):
        entry = data[offset:offset + 8]
        raw_key = _word(entry, 0)
        if raw_key == 0xFFFF:
            raise ValueError("terminator key inside records")
        key = raw_key & 0x7FFF
        if require_order and key < previous:
            raise ValueError("position keys are not sorted")
        previous = key
        records.append({"key": key, "range_flag": bool(raw_key & 0x8000),
                        "type": entry[2], "parameters": list(entry[3:8])})
    return records


def encode_stream(records: list[dict], *, require_order: bool = True) -> bytes:
    """Re-encode a decoded stream, preserving the high key bit and all bytes."""
    if type(require_order) is not bool:
        raise ValueError('invalid position ordering policy')
    result = bytearray()
    previous = -1
    for record in records:
        key, flag, kind, params = (record["key"], record["range_flag"],
                                    record["type"], record["parameters"])
        if type(key) is not int or not 0 <= key <= 0x7FFF or (require_order and key < previous):
            raise ValueError("invalid or unordered position key")
        if type(flag) is not bool or type(kind) is not int or not 0 <= kind <= 255:
            raise ValueError("invalid flag or record type")
        if not isinstance(params, list) or len(params) != 5 or any(
                type(value) is not int or not 0 <= value <= 255 for value in params):
            raise ValueError("expected five byte parameters")
        raw_key = key | (0x8000 if flag else 0)
        if raw_key == 0xFFFF:
            raise ValueError("record key collides with terminator")
        result.extend(raw_key.to_bytes(2, "little"))
        result.append(kind)
        result.extend(params)
        previous = key
    result.extend(TERMINATOR)
    return bytes(result)


def decode_tables(bank: bytes, table_a: int, table_b: int, entries: int,
                  start: int, limit: int, address_base: int = 0, *,
                  unordered_streams: tuple[int, ...] = ()) -> dict:
    """Decode shared pointer targets once; addresses are relative to `bank`."""
    if not (0 <= start < limit <= len(bank)) or entries <= 0:
        raise ValueError("invalid stream bounds")
    tables = []
    for table in (table_a, table_b):
        if table < 0 or table + entries * 2 > len(bank):
            raise ValueError("pointer table outside bank")
        values = [_word(bank, table + i * 2) - address_base for i in range(entries)]
        if any(value < start or value >= limit for value in values):
            raise ValueError("stream pointer outside supported region")
        tables.append(values)
    starts = sorted(set(tables[0] + tables[1]))
    if not starts or starts[0] != start:
        raise ValueError("first stream does not start at the supported boundary")
    if (not isinstance(unordered_streams, tuple) or len(set(unordered_streams)) != len(unordered_streams)
            or any(type(offset) is not int or offset not in starts for offset in unordered_streams)):
        raise ValueError('unordered stream exception does not name a unique pointer target')
    streams = []
    for index, offset in enumerate(starts):
        if index + 1 < len(starts):
            end = starts[index + 1]
        else:
            # The last referenced stream has no following pointer to delimit it.
            # Look only at record boundaries, bounded by the supported region.
            end = offset
            while end + 4 <= limit and bank[end:end + 4] != TERMINATOR:
                end += 8
            if end + 4 > limit:
                raise ValueError("last stream terminator not found")
            end += 4
        raw = bank[offset:end]
        require_order = offset not in unordered_streams
        records = decode_stream(raw, require_order=require_order)
        if encode_stream(records, require_order=require_order) != raw:
            raise ValueError("stream does not round-trip")
        row = {"start": offset, "end": end, "records": records}
        if not require_order:
            row['order_exceptions'] = [
                {'index': i, 'previous_key': records[i - 1]['key'], 'key': record['key']}
                for i, record in enumerate(records) if i and record['key'] < records[i - 1]['key']]
            if not row['order_exceptions']:
                raise ValueError('unused unordered position stream exception')
        streams.append(row)
    return {"tables": tables, "streams": streams}


def main() -> int:
    try:
        if os.environ.get("BADP_TARGET") not in (None, "", "us-v1.5"):
            raise ValueError("position-record decoding currently supports us-v1.5 only")
        override = os.environ.get("BADP_ROM") or None
        target = load_target(ROOT, "us-v1.5")
        rom = input_path(ROOT, target, override).read_bytes()
        actual = inspect_rom(rom)
        mismatches = [part for part in IDENTITY_PARTS
                      if actual[part] != target["reference"][part]]
        if mismatches:
            raise ValueError(f"reference audit failed: {mismatches}")
        prg = target["reference"]["prg"]
        bank = rom[prg["offset"]:prg["offset"] + BANK_SIZE]
        if len(bank) != BANK_SIZE:
            raise ValueError("unexpected PRG bank length")
        decoded = decode_tables(bank, TABLE_A - CPU_BASE, TABLE_B - CPU_BASE,
                                TABLE_ENTRIES, STREAM_START - CPU_BASE,
                                STREAM_LIMIT - CPU_BASE, CPU_BASE)
        # Export physical bank-relative offsets and CPU addresses explicitly.
        for stream in decoded["streams"]:
            stream["cpu_start"] = f"0x{CPU_BASE + stream['start']:04x}"
            stream["cpu_end"] = f"0x{CPU_BASE + stream['end']:04x}"
        decoded.update({"target": "us-v1.5", "physical_prg_bank": 0,
                        "address_note": "table values and start/end are bank-relative offsets",
                        "reference_sha256": target["reference"]["file"]["sha256"]})
        analysis = ROOT / "analysis"
        output = analysis / "us-v1.5" / "position-records.json"
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError("refusing a symlinked analysis output")
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(ROOT.resolve() / "analysis"):
            raise ValueError("analysis output escapes its local directory")
        output.write_text(json.dumps(decoded, indent=2) + "\n")
        summary = {"target": "us-v1.5", "unique_streams": len(decoded["streams"]),
                   "records": sum(len(s["records"]) for s in decoded["streams"]),
                   "bytes": sum(s["end"] - s["start"] for s in decoded["streams"]),
                   "last_cpu_end": decoded["streams"][-1]["cpu_end"],
                   "output": "analysis/us-v1.5/position-records.json"}
        print(json.dumps(summary, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"position-record decoding failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
