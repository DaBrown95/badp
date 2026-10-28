"""Editable local text for the v1.5 packed-message records.

The encoding slots and padding are kept from the audited ROM. Each edited
character must retain its original one- or two-symbol width so record extents
and source-owned destination headers remain fixed. The data may overlap
candidate script or audio uses and is never credited as code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from .asset_paths import asset_path
import sys

from . import packed_text
from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
ASSET_PATH = Path('extracted/us-v1.5/packed-text.json')
RESERVED = frozenset((0, 11, 26))


def _records(prg: bytes) -> tuple[list[dict], bytes, bytes]:
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    bank = prg[BANK_SIZE:]
    primary = bank[packed_text.PRIMARY_OFFSET:packed_text.PRIMARY_OFFSET + 32]
    secondary = bank[packed_text.SECONDARY_OFFSET:packed_text.SECONDARY_OFFSET + 32]
    records = packed_text.decode_records(bank, packed_text.TABLE_OFFSET, packed_text.RECORD_COUNT,
                                         packed_text.DATA_END, primary, secondary)
    return records, primary, secondary


def capture(prg: bytes, reference_sha256: str, *, target: str = TARGET) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    records, _, _ = _records(prg)
    return {'schema_version': 1, 'target': target, 'reference_sha256': reference_sha256,
            'records': [{'index': r['index'], 'cpu': r['cpu_address'], 'text': r['text'],
                         'encoding_slots': r['tokens'], 'padding_bits': r['padding_bits'],
                         'padding_value': r['padding_value']} for r in records]}


def _edited_tokens(text: str, slots: list[dict], primary: bytes, secondary: bytes) -> list[dict]:
    if not isinstance(text, str) or len(text) != len(slots):
        raise ValueError('edited text must preserve the record character count')
    result = []
    for char, slot in zip(text, slots):
        kind = slot['kind']
        if kind == 'line_break':
            old_char = '\n'
        elif kind == 'primary':
            old_char = chr(primary[slot['index']])
        elif kind == 'secondary':
            old_char = chr(secondary[slot['index']])
        else:
            raise ValueError('invalid original encoding slot')
        if char == old_char:
            result.append(slot)
            continue
        if kind == 'secondary':
            choices = [i for i, value in enumerate(secondary) if chr(value) == char]
            if not choices:
                raise ValueError('edited character is not available in its two-symbol table')
            result.append({'kind': 'secondary', 'index': choices[0]})
        elif char == '\n':
            result.append({'kind': 'line_break'})
        else:
            choices = [i for i, value in enumerate(primary) if i not in RESERVED and chr(value) == char]
            if not choices:
                raise ValueError('edited character is not available in its one-symbol table')
            result.append({'kind': 'primary', 'index': choices[0]})
    return result


def encode(asset: dict, prg: bytes, reference_sha256: str, *, target: str = TARGET) -> list[tuple[int, int, bytes]]:
    """Return 52 physical payload spans, leaving source-owned headers alone."""
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'records'}
            or asset['schema_version'] != 1 or asset['target'] != target
            or asset['reference_sha256'] != reference_sha256 or not isinstance(asset['records'], list)):
        raise ValueError('packed-text asset identity differs from the reference')
    originals, primary, secondary = _records(prg)
    if len(asset['records']) != len(originals):
        raise ValueError('packed-text record count differs from the reference')
    result = []
    for record, original in zip(asset['records'], originals):
        if (not isinstance(record, dict)
                or set(record) != {'index', 'cpu', 'text', 'encoding_slots', 'padding_bits', 'padding_value'}
                or type(record['index']) is not int or record['index'] != original['index']
                or record['cpu'] != original['cpu_address'] or record['encoding_slots'] != original['tokens']
                or type(record['padding_bits']) is not int or record['padding_bits'] != original['padding_bits']
                or type(record['padding_value']) is not int or record['padding_value'] != original['padding_value']):
            raise ValueError('packed-text record identity or encoding metadata differs')
        tokens = _edited_tokens(record['text'], original['tokens'], primary, secondary)
        encoded = packed_text.encode_record({'header': original['header'], 'tokens': tokens,
                                             'padding_bits': original['padding_bits'],
                                             'padding_value': original['padding_value']})
        if len(encoded) != original['size'] or encoded[:2] != bytes(original['header']):
            raise ValueError('packed-text record extent or destination header changed')
        result.append((1, original['bank_offset'] + 2, encoded[2:]))
    return result


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, ensure_ascii=True, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / asset_path(target, ASSET_PATH.name)
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked packed-text input')
    if path.exists():
        raw = path.read_bytes()
        asset = json.loads(raw)
        source = 'local'
    else:
        asset = capture(prg, reference_sha256, target=target)
        raw = serialize(asset)
        source = 'reference'
    spans = encode(asset, prg, reference_sha256, target=target)
    return asset, spans, source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict, prg: bytes) -> dict:
    """Change the first and last encodable primary character in every record."""
    changed = json.loads(json.dumps(asset))
    _, primary, _ = _records(prg)
    for record in changed['records']:
        chars = list(record['text'])
        positions = [index for index, slot in enumerate(record['encoding_slots']) if slot['kind'] == 'primary']
        if not positions:
            raise ValueError('record has no mutable primary character')
        for index in dict.fromkeys((positions[0], positions[-1])):
            alternatives = [chr(value) for i, value in enumerate(primary)
                            if i not in RESERVED and chr(value) != chars[index] and chr(value) != '\n']
            if not alternatives:
                raise ValueError('record has no mutable primary character')
            chars[index] = alternatives[0]
        record['text'] = ''.join(chars)
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int,
                   original_spans: list[tuple[int, int, bytes]],
                   changed_spans: list[tuple[int, int, bytes]]) -> list[int]:
    if len(candidate) != len(reference) or len(original_spans) != 52 or len(changed_spans) != 52:
        raise ValueError('packed-text control has incorrect ROM or record count')
    expected: dict[int, int] = {}
    for original, altered in zip(original_spans, changed_spans):
        bank, start, before = original
        other_bank, other_start, after = altered
        if (bank, start, len(before)) != (other_bank, other_start, len(after)) or bank != 1:
            raise ValueError('packed-text control changed a record extent')
        changes = [(i, b) for i, (a, b) in enumerate(zip(before, after)) if a != b]
        if not changes:
            raise ValueError('packed-text control missed a record')
        for offset, value in changes:
            position = prg_offset + bank * BANK_SIZE + start + offset
            if position in expected or reference[position] != before[offset]:
                raise ValueError('packed-text control has conflicting record spans')
            expected[position] = value
    observed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if observed != sorted(expected) or any(candidate[i] != value for i, value in expected.items()):
        raise ValueError('packed-text control changed bytes outside its selected characters')
    return observed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(bank0 + bank1, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked packed-text output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local packed text already exists and differs; preserve or move it before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('packed-text output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'records': len(asset['records']),
                          'characters': sum(len(r['text']) for r in asset['records']),
                          'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'packed-text export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
