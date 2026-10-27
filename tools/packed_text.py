"""Decode the pinned v1.5 packed-text records into ignored local analysis."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TABLE_OFFSET = 0x3E82
RECORD_COUNT = 52
DATA_END = 0x4FC7
PRIMARY_OFFSET = 0x3FFE
SECONDARY_OFFSET = 0x401E


def decode_record(bank: bytes, start: int, end: int, primary: bytes, secondary: bytes) -> dict:
    """Decode one bounded record; the first two bytes are retained as a header."""
    if len(primary) != 32 or len(secondary) != 32:
        raise ValueError('character tables must each contain 32 bytes')
    if not 0 <= start < end <= len(bank) or end - start < 3:
        raise ValueError('invalid packed-text record bounds')
    payload = bank[start + 2:end]
    bit_count = len(payload) * 8
    packed = int.from_bytes(payload, 'big')
    position = 0
    text = []
    tokens = []
    line_breaks = 0

    def symbol() -> int:
        nonlocal position
        if position + 5 > bit_count:
            raise ValueError('truncated or unterminated packed-text record')
        value = (packed >> (bit_count - position - 5)) & 31
        position += 5
        return value

    while True:
        value = symbol()
        if value == 0:
            index = symbol()
            text.append(chr(secondary[index]))
            tokens.append({'kind': 'secondary', 'index': index})
        elif value == 11:
            text.append('\n')
            tokens.append({'kind': 'line_break'})
            line_breaks += 1
        elif value == 26:
            break
        else:
            text.append(chr(primary[value]))
            tokens.append({'kind': 'primary', 'index': value})
    if (position + 7) // 8 != len(payload):
        raise ValueError('unaccounted bytes after packed-text terminator')
    padding_bits = bit_count - position
    return {'header': list(bank[start:start + 2]), 'text': ''.join(text), 'tokens': tokens,
            'symbols_consumed': position // 5, 'padding_bits': padding_bits,
            'padding_value': packed & ((1 << padding_bits) - 1),
            'line_breaks': line_breaks}


def encode_record(record: dict) -> bytes:
    """Re-encode parsed tokens, retaining table selection and final padding."""
    header, tokens = record['header'], record['tokens']
    if (not isinstance(header, list) or len(header) != 2
            or any(type(x) is not int or not 0 <= x <= 255 for x in header)
            or not isinstance(tokens, list)):
        raise ValueError('invalid packed-text header or tokens')
    symbols = []
    for token in tokens:
        if not isinstance(token, dict):
            raise ValueError('invalid packed-text token')
        kind = token.get('kind')
        index = token.get('index')
        if kind == 'line_break' and set(token) == {'kind'}:
            symbols.append(11)
        elif (kind in ('primary', 'secondary') and set(token) == {'kind', 'index'}
              and type(index) is int and 0 <= index < 32):
            if kind == 'primary':
                if index in (0, 11, 26):
                    raise ValueError('primary token uses a control symbol')
                symbols.append(index)
            else:
                symbols.extend((0, index))
        else:
            raise ValueError('invalid packed-text token')
    symbols.append(26)
    padding_bits, padding_value = record['padding_bits'], record['padding_value']
    if (type(padding_bits) is not int or padding_bits != (-5 * len(symbols)) % 8
            or type(padding_value) is not int or not 0 <= padding_value < 1 << padding_bits):
        raise ValueError('invalid packed-text padding')
    packed = 0
    for value in symbols:
        packed = (packed << 5) | value
    packed = (packed << padding_bits) | padding_value
    return bytes(header) + packed.to_bytes((len(symbols) * 5 + padding_bits) // 8, 'big')


def decode_records(bank: bytes, table_offset: int, count: int, data_end: int,
                   primary: bytes, secondary: bytes) -> list[dict]:
    if len(bank) != BANK_SIZE or type(count) is not int or count <= 0:
        raise ValueError('expected one full bank and a positive record count')
    if (type(table_offset) is not int or table_offset < 0
            or table_offset + count * 2 > BANK_SIZE
            or type(data_end) is not int or not 0 < data_end <= BANK_SIZE):
        raise ValueError('invalid pointer table or data end')
    pointers = [int.from_bytes(bank[p:p + 2], 'little') - 0x8000
                for p in range(table_offset, table_offset + count * 2, 2)]
    if (any(p < table_offset + count * 2 or p >= data_end for p in pointers)
            or any(a >= b for a, b in zip(pointers, pointers[1:]))):
        raise ValueError('record pointers must be ordered and within the data extent')
    records = []
    for index, (start, end) in enumerate(zip(pointers, pointers[1:] + [data_end])):
        record = decode_record(bank, start, end, primary, secondary)
        if encode_record(record) != bank[start:end]:
            raise ValueError('packed-text record did not round-trip')
        record.update({'index': index, 'cpu_address': f'0x{start + 0x8000:04x}',
                       'bank_offset': start, 'size': end - start})
        records.append(record)
    return records


def main() -> int:
    try:
        target, _, bank, _ = load_audited_banks()
        records = decode_records(bank, TABLE_OFFSET, RECORD_COUNT, DATA_END,
                                 bank[PRIMARY_OFFSET:PRIMARY_OFFSET + 32],
                                 bank[SECONDARY_OFFSET:SECONDARY_OFFSET + 32])
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'interpretation': 'static decoded records; message roles and rendering unverified',
                  'records': records}
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5' / 'packed-text.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(ROOT.resolve() / 'analysis'):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': 'us-v1.5', 'records': len(records),
                          'round_trip_records': len(records),
                          'line_breaks': sum(r['line_breaks'] for r in records),
                          'output': 'analysis/us-v1.5/packed-text.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'packed-text decoding failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
