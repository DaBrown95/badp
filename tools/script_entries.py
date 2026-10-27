"""Inventory v1.5 slot-record script entries in ignored local analysis.

This follows only the statically identified descriptor -> ten-byte record ->
first command path. Bank selection follows the reconstructed helpers and is a
static assumption, not evidence of runtime mapper behavior. It does not follow
branches, discover all scripts, or classify data as reconstructed source.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, input_path, load_target

ROOT = Path(__file__).resolve().parents[1]
BANK_SIZE = 0x8000
DESCRIPTORS = 0x9F06 - 0x8000
DESCRIPTOR_COUNT = 114
LENGTH_TABLE = 0xFDA7 - 0x8000
LENGTH_COUNT = 197


def _locate(encoded: int) -> tuple[int, int]:
    """Map an encoded pointer according to the bank-0 fetch path."""
    if type(encoded) is not int or not 0 <= encoded <= 0xFFFF:
        raise ValueError('invalid encoded pointer')
    return (1, encoded) if encoded < 0x8000 else (0, encoded - 0x8000)


def _location(bank: int, offset: int) -> dict:
    return {'bank': bank, 'bank_offset': offset,
            'cpu_address': f'0x{0x8000 + offset:04x}',
            'physical_prg_offset': bank * BANK_SIZE + offset}


def inventory(bank0: bytes, bank1: bytes, descriptor_offset: int,
              descriptor_count: int, lengths: bytes) -> dict:
    """Inspect descriptor records and first commands, retaining uncertainty."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full 32 KiB banks')
    if (type(descriptor_count) is not int or descriptor_count <= 0
            or type(descriptor_offset) is not int or descriptor_offset < 0
            or descriptor_offset + descriptor_count * 6 > BANK_SIZE):
        raise ValueError('descriptor table outside bank 0')
    if not lengths or len(lengths) > 256:
        raise ValueError('invalid command length table')
    banks = (bank0, bank1)
    records: dict[tuple[int, int], dict] = {}
    entries: dict[tuple[int, int], dict] = {}
    descriptors = []
    for index in range(descriptor_count):
        start = descriptor_offset + index * 6
        encoded = int.from_bytes(bank0[start:start + 2], 'little')
        bank, offset = _locate(encoded)
        item = {'index': index, 'encoded_record_pointer': f'0x{encoded:04x}',
                'record': _location(bank, offset)}
        descriptors.append(item)
        key = (bank, offset)
        if key in records:
            records[key]['descriptor_indices'].append(index)
            continue
        record = {'location': _location(bank, offset), 'descriptor_indices': [index]}
        records[key] = record
        if offset + 10 > BANK_SIZE:
            record['status'] = 'crosses_bank_boundary'
            continue
        raw = banks[bank][offset:offset + 10]
        record['status'] = 'inspected'
        record['bytes'] = list(raw)
        script_pointer = int.from_bytes(raw[2:4], 'little')
        record['encoded_script_pointer'] = f'0x{script_pointer:04x}'
        # LoadSlotRecordAtFE suppresses script installation when byte 3 is FF.
        if raw[3] == 0xFF:
            record['script_status'] = 'not_installed_high_byte_ff'
            continue
        script_bank, script_offset = _locate(script_pointer)
        record['script_status'] = 'candidate'
        record['script'] = _location(script_bank, script_offset)
        script_key = (script_bank, script_offset)
        if script_key in entries:
            continue
        opcode = banks[script_bank][script_offset]
        entry = {'location': _location(script_bank, script_offset), 'opcode': opcode}
        entries[script_key] = entry
        if opcode >= len(lengths):
            entry['status'] = 'opcode_outside_length_table'
            continue
        length = lengths[opcode]
        entry['length'] = length
        if length == 0:
            entry['status'] = 'zero_length'
        elif script_offset + length > BANK_SIZE:
            entry['status'] = 'crosses_bank_boundary'
        else:
            entry['status'] = 'decoded_first_command'
            entry['operands'] = list(banks[script_bank][script_offset + 1:script_offset + length])
    return {'descriptors': descriptors, 'records': list(records.values()),
            'entries': list(entries.values())}


def main() -> int:
    try:
        if os.environ.get('BADP_TARGET') not in (None, '', 'us-v1.5'):
            raise ValueError('script-entry inventory currently supports us-v1.5 only')
        target = load_target(ROOT, 'us-v1.5')
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None).read_bytes()
        actual = inspect_rom(rom)
        mismatches = [part for part in IDENTITY_PARTS if actual[part] != target['reference'][part]]
        if mismatches:
            raise ValueError(f'reference audit failed: {mismatches}')
        prg = target['reference']['prg']
        payload = rom[prg['offset']:prg['offset'] + prg['size']]
        if len(payload) != 2 * BANK_SIZE:
            raise ValueError('unexpected PRG size')
        bank0, bank1 = payload[:BANK_SIZE], payload[BANK_SIZE:]
        lengths = bank0[LENGTH_TABLE:LENGTH_TABLE + LENGTH_COUNT]
        if lengths != bank1[LENGTH_TABLE:LENGTH_TABLE + LENGTH_COUNT]:
            raise ValueError('command length tables differ across banks')
        result = inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        result.update({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                       'interpretation': 'static candidate entry points only; no control-flow or runtime verification',
                       'bank_assumption': 'encoded addresses below 0x8000 use bank 1; others use the current bank 0'})
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5' / 'script-entries.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(ROOT.resolve() / 'analysis'):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': 'us-v1.5', 'descriptors': len(result['descriptors']),
                          'unique_records': len(result['records']),
                          'inspected_records': sum(r['status'] == 'inspected' for r in result['records']),
                          'unique_candidate_entries': len(result['entries']),
                          'decoded_first_commands': sum(e['status'] == 'decoded_first_command' for e in result['entries']),
                          'output': 'analysis/us-v1.5/script-entries.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'script-entry inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
