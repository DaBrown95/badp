"""Round-trip v1.5's local map layout grids while retaining source headers.

State-table selections and field formats are static evidence. Grid bytes can
also have candidate script uses; this local representation does not claim
exclusive ownership or runtime reachability.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from . import map_data
from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
ASSET_PATH = Path('extracted/us-v1.5/map-layouts.json')


def _inventory(prg: bytes) -> list[dict]:
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    inventory = map_data.inventory(prg[:BANK_SIZE], prg[BANK_SIZE:])
    if (len(inventory['layouts']) != 14 or inventory['overlapping_layout_bytes']
            or inventory['layout_chunk_overlap_bytes']):
        raise ValueError('map layouts do not match the reviewed distinct non-overlapping inventory')
    return sorted(inventory['layouts'], key=lambda x: (x['location']['bank'], x['location']['bank_offset']))


def capture(prg: bytes, reference_sha256: str) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    layouts = []
    for layout in _inventory(prg):
        decoded, location = layout['decoded'], layout['location']
        layouts.append({'bank': location['bank'], 'cpu': location['cpu_address'],
                        'width_chunks': decoded['width_chunks'], 'height_chunks': decoded['height_chunks'],
                        'chunk_rows': decoded['chunk_rows']})
    return {'schema_version': 1, 'target': TARGET, 'reference_sha256': reference_sha256, 'layouts': layouts}


def encode(asset: dict, prg: bytes, reference_sha256: str) -> list[tuple[int, int, bytes]]:
    """Return physical-bank grid spans, without changing tracked headers."""
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'layouts'}
            or asset['schema_version'] != 1 or asset['target'] != TARGET
            or asset['reference_sha256'] != reference_sha256 or not isinstance(asset['layouts'], list)):
        raise ValueError('map layout asset identity differs from the reference')
    expected = _inventory(prg)
    if len(asset['layouts']) != len(expected):
        raise ValueError('map layout count differs from the reviewed inventory')
    result = []
    for row, original in zip(asset['layouts'], expected):
        if (not isinstance(row, dict) or set(row) != {'bank', 'cpu', 'width_chunks', 'height_chunks', 'chunk_rows'}
                or type(row['bank']) is not int or row['bank'] != original['location']['bank']
                or row['cpu'] != original['location']['cpu_address']
                or type(row['width_chunks']) is not int or type(row['height_chunks']) is not int
                or row['width_chunks'] != original['decoded']['width_chunks']
                or row['height_chunks'] != original['decoded']['height_chunks']):
            raise ValueError('map layout identity, ordering or dimensions differ')
        encoded = map_data.encode_layout(row)
        bank, offset = row['bank'], original['location']['bank_offset']
        if encoded[:2] != prg[bank * BANK_SIZE + offset:bank * BANK_SIZE + offset + 2]:
            raise ValueError('map layout header differs from the reference')
        result.append((bank, offset + 2, encoded[2:]))
    return result


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / ASSET_PATH
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked map layout input')
    if path.exists():
        raw = path.read_bytes()
        asset = json.loads(raw)
        source = 'local'
    else:
        asset = capture(prg, reference_sha256)
        raw = serialize(asset)
        source = 'reference'
    spans = encode(asset, prg, reference_sha256)
    return asset, spans, source, hashlib.sha256(raw).hexdigest()


def gap_payloads(prg: bytes, regions: list[dict], spans: list[tuple[int, int, bytes]]) -> dict[str, bytes]:
    """Assemble local gap inputs from reference pieces and supplied data spans."""
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    gaps = []
    for bank in range(2):
        cursor = 0
        owned = sorted((int(r['cpu'], 0) - 0x8000, r['size']) for r in regions if r['bank'] == bank)
        for start, size in [*owned, (BANK_SIZE, 0)]:
            if start < cursor or start + size > BANK_SIZE:
                raise ValueError('invalid or overlapping source region')
            if start > cursor:
                gaps.append((bank, cursor, start, f'bank{bank}_{cursor + 0x8000:04x}_{start + 0x8000:04x}.bin'))
            cursor = start + size
    grouped: dict[str, list[tuple[int, bytes]]] = {}
    locations = {name: (bank, start, end) for bank, start, end, name in gaps}
    for bank, start, grid in spans:
        if bank not in (0, 1) or type(start) is not int or not isinstance(grid, bytes) or not grid:
            raise ValueError('invalid local data span')
        matches = [name for gb, begin, end, name in gaps
                   if gb == bank and begin <= start and start + len(grid) <= end]
        if len(matches) != 1:
            raise ValueError('data span is not entirely within one local gap')
        grouped.setdefault(matches[0], []).append((start, grid))
    result = {}
    for name, pieces in grouped.items():
        bank, start, end = locations[name]
        cursor = start
        out = bytearray()
        for pos, grid in sorted(pieces):
            if pos < cursor:
                raise ValueError('overlapping local data spans')
            out.extend(prg[bank * BANK_SIZE + cursor:bank * BANK_SIZE + pos])
            out.extend(grid)
            cursor = pos + len(grid)
        out.extend(prg[bank * BANK_SIZE + cursor:bank * BANK_SIZE + end])
        if len(out) != end - start:
            raise ValueError('local input gap changed size')
        result[name] = bytes(out)
    return result


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if not changed['layouts']:
        raise ValueError('control has no layouts')
    for layout in changed['layouts']:
        if not layout['chunk_rows'] or not layout['chunk_rows'][0]:
            raise ValueError('control layout has no first grid cell')
        layout['chunk_rows'][0][0] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int, asset: dict) -> list[int]:
    if len(candidate) != len(reference):
        raise ValueError('map layout control changed ROM size')
    expected = sorted(prg_offset + layout['bank'] * BANK_SIZE + int(layout['cpu'], 0) - 0x8000 + 2
                      for layout in asset['layouts'])
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if (len(expected) != 14 or len(set(expected)) != len(expected) or changed != expected
            or any(candidate[offset] != (reference[offset] ^ 1) for offset in expected)):
        raise ValueError('map layout control did not change exactly one selected cell per layout')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(bank0 + bank1, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked map layout output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local map layouts already exist and differ; preserve or move them before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('map layout output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'layouts': len(asset['layouts']),
                          'grid_bytes': sum(len(row) for layout in asset['layouts'] for row in layout['chunk_rows']),
                          'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'map layout export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
