"""Round-trip v1.5's locally extracted map chunks without publishing assets.

The table identifies 145 referenced 68-byte slots. One aligned slot has no
known table reference and remains an opaque local byte sequence. The decoded
view is a candidate data use, not proof that overlapping bytes cannot be code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from .map_data import CHUNK_INDEX_COUNT, CHUNK_SIZE, CHUNK_TABLE_OFFSET, decode_chunk, encode_chunk
from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
ASSET_PATH = Path('extracted/us-v1.5/map-chunks.json')
GAP_NAME = 'bank1_8000_a6c8.bin'
SLOT_COUNT = 146
REGION_SIZE = SLOT_COUNT * CHUNK_SIZE


def slots_for_reference(prg: bytes) -> set[int]:
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    table = prg[CHUNK_TABLE_OFFSET:CHUNK_TABLE_OFFSET + 2 * CHUNK_INDEX_COUNT]
    offsets = [int.from_bytes(table[i:i + 2], 'little') for i in range(0, len(table), 2)]
    if len(offsets) != CHUNK_INDEX_COUNT or any(x % CHUNK_SIZE or x >= REGION_SIZE for x in offsets):
        raise ValueError('map chunk table has an invalid or unaligned offset')
    slots = {x // CHUNK_SIZE for x in offsets}
    if len(slots) != 145 or set(range(SLOT_COUNT)) - slots != {22}:
        raise ValueError('map chunk table does not match the reviewed slot inventory')
    return slots


def capture(prg: bytes, reference_sha256: str) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    referenced = slots_for_reference(prg)
    blob = prg[BANK_SIZE:BANK_SIZE + REGION_SIZE]
    slots = []
    for index in range(SLOT_COUNT):
        raw = blob[index * CHUNK_SIZE:(index + 1) * CHUNK_SIZE]
        if index in referenced:
            decoded = decode_chunk(raw)
            slots.append({'index': index, 'kind': 'chunk', **decoded})
        else:
            slots.append({'index': index, 'kind': 'unclassified', 'bytes_hex': raw.hex()})
    return {'schema_version': 1, 'target': TARGET, 'reference_sha256': reference_sha256,
            'chunk_size': CHUNK_SIZE, 'slots': slots}


def encode(asset: dict, prg: bytes, reference_sha256: str) -> bytes:
    """Encode an editable local view, enforcing geometry and opaque slots."""
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'chunk_size', 'slots'}
            or asset['schema_version'] != 1 or asset['target'] != TARGET
            or asset['reference_sha256'] != reference_sha256 or asset['chunk_size'] != CHUNK_SIZE
            or not isinstance(asset['slots'], list) or len(asset['slots']) != SLOT_COUNT):
        raise ValueError('map asset identity or geometry differs from the reference')
    referenced = slots_for_reference(prg)
    output = bytearray()
    for index, slot in enumerate(asset['slots']):
        if not isinstance(slot, dict) or type(slot.get('index')) is not int or slot['index'] != index:
            raise ValueError('map asset slot order or index is invalid')
        if index in referenced:
            if set(slot) != {'index', 'kind', 'tile_rows', 'attribute_rows'} or slot['kind'] != 'chunk':
                raise ValueError('referenced map slot must be a structured chunk')
            raw = encode_chunk(slot)
        else:
            if set(slot) != {'index', 'kind', 'bytes_hex'} or slot['kind'] != 'unclassified':
                raise ValueError('unreferenced map slot must remain unclassified')
            try:
                raw = bytes.fromhex(slot['bytes_hex'])
            except (ValueError, TypeError) as exc:
                raise ValueError('invalid unclassified slot bytes') from exc
            if len(raw) != CHUNK_SIZE or raw != prg[BANK_SIZE + index * CHUNK_SIZE:BANK_SIZE + (index + 1) * CHUNK_SIZE]:
                raise ValueError('unclassified slot differs from the reference')
        output.extend(raw)
    return bytes(output)


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str) -> tuple[dict, bytes, str, str]:
    """Use an optional edited local file, or decode the fixed reference."""
    path = root / ASSET_PATH
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked map asset input')
    if path.exists():
        raw = path.read_bytes()
        asset = json.loads(raw)
        source = 'local'
    else:
        asset = capture(prg, reference_sha256)
        raw = serialize(asset)
        source = 'reference'
    payload = encode(asset, prg, reference_sha256)
    return asset, payload, source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    """Change one actual tile in an isolated local control, not an output ROM."""
    changed = json.loads(json.dumps(asset))
    if changed['slots'][0]['kind'] != 'chunk':
        raise ValueError('control slot is not a referenced chunk')
    changed['slots'][0]['tile_rows'][0][0] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int) -> list[int]:
    if len(candidate) != len(reference):
        raise ValueError('map asset control changed ROM size')
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    expected = prg_offset + BANK_SIZE
    if changed != [expected] or candidate[expected] != (reference[expected] ^ 1):
        raise ValueError('map asset control did not change exactly its selected tile')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(bank0 + bank1, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked map asset output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local map asset already exists and differs; preserve or move it before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('map asset output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'referenced_chunks': 145, 'unclassified_slots': 1,
                          'bytes': REGION_SIZE, 'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'map asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
