"""Round-trip v1.5 CHR as local, physical-order NES 2bpp tiles.

Each pixel is a palette index 0-3. Tile numbers are physical CHR offsets,
not a claim about PPU mapping, palettes, animation or tile usage.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, input_path, load_target

ROOT = Path(__file__).resolve().parents[1]

TARGET = 'us-v1.5'
ASSET_PATH = Path('extracted/us-v1.5/chr-tiles.json')
CHR_SIZE = 0x10000
TILE_SIZE = 16
TILE_COUNT = CHR_SIZE // TILE_SIZE
CONTROL_TILE_STEP = 0x200  # One physical tile per 8 KiB interval.


def decode_tile(raw: bytes) -> list[str]:
    if len(raw) != TILE_SIZE:
        raise ValueError('NES tile must contain sixteen bytes')
    rows = []
    for y in range(8):
        low, high = raw[y], raw[y + 8]
        rows.append(''.join(str(((low >> bit) & 1) | (((high >> bit) & 1) << 1))
                            for bit in range(7, -1, -1)))
    return rows


def encode_tile(rows: list[str]) -> bytes:
    if (not isinstance(rows, list) or len(rows) != 8
            or any(not isinstance(row, str) or len(row) != 8 or set(row) - set('0123') for row in rows)):
        raise ValueError('NES tile must contain eight rows of eight palette indices')
    low, high = [], []
    for row in rows:
        lo = hi = 0
        for char in row:
            pixel = int(char)
            lo = (lo << 1) | (pixel & 1)
            hi = (hi << 1) | (pixel >> 1)
        low.append(lo)
        high.append(hi)
    return bytes(low + high)


def capture(chr_data: bytes, reference_sha256: str) -> dict:
    if len(chr_data) != CHR_SIZE or not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid CHR input or reference identity')
    return {'schema_version': 1, 'target': TARGET, 'reference_sha256': reference_sha256,
            'format': 'nes-2bpp-physical-order',
            'tiles': [decode_tile(chr_data[i:i + TILE_SIZE]) for i in range(0, CHR_SIZE, TILE_SIZE)]}


def encode(asset: dict, reference_sha256: str) -> bytes:
    if (not isinstance(asset, dict)
            or set(asset) != {'schema_version', 'target', 'reference_sha256', 'format', 'tiles'}
            or type(asset['schema_version']) is not int or asset['schema_version'] != 1
            or asset['target'] != TARGET or asset['reference_sha256'] != reference_sha256
            or asset['format'] != 'nes-2bpp-physical-order' or not isinstance(asset['tiles'], list)
            or len(asset['tiles']) != TILE_COUNT):
        raise ValueError('CHR asset identity or physical tile count differs')
    return b''.join(encode_tile(tile) for tile in asset['tiles'])


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, separators=(',', ':')) + '\n').encode('utf-8')


def select(root: Path, chr_data: bytes, reference_sha256: str) -> tuple[dict, bytes, str, str]:
    path = root / ASSET_PATH
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked CHR asset input')
    if path.exists():
        raw = path.read_bytes()
        asset, source = json.loads(raw), 'local'
    else:
        asset, source = capture(chr_data, reference_sha256), 'reference'
        raw = serialize(asset)
    return asset, encode(asset, reference_sha256), source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if len(changed['tiles']) != TILE_COUNT:
        raise ValueError('invalid CHR tile control input')
    for tile in range(0, TILE_COUNT, CONTROL_TILE_STEP):
        row = changed['tiles'][tile][0]
        changed['tiles'][tile][0] = str(int(row[0]) ^ 1) + row[1:]
    return changed


def verify_control(reference: bytes, candidate: bytes, chr_offset: int) -> list[int]:
    if (len(reference) != len(candidate) or type(chr_offset) is not int or chr_offset < 0
            or chr_offset + CHR_SIZE > len(reference)):
        raise ValueError('invalid CHR control ROM geometry')
    expected = [chr_offset + i * TILE_SIZE for i in range(0, TILE_COUNT, CONTROL_TILE_STEP)]
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if changed != expected or any(candidate[i] != (reference[i] ^ 0x80) for i in expected):
        raise ValueError('CHR control did not change the selected pixels')
    return changed


def main() -> int:
    try:
        if os.environ.get('BADP_TARGET') not in (None, '', TARGET):
            raise ValueError('CHR export currently supports us-v1.5 only')
        target = load_target(ROOT, TARGET)
        ref = input_path(ROOT, target, os.environ.get('BADP_ROM') or None).read_bytes()
        actual = inspect_rom(ref)
        if any(actual[part] != target['reference'][part] for part in IDENTITY_PARTS):
            raise ValueError('CHR export input differs from the pinned target')
        info = actual['chr']
        raw = ref[info['offset']:info['offset'] + info['size']]
        asset = capture(raw, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked CHR asset output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local CHR data differs; preserve or move it before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('CHR output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'tiles': TILE_COUNT, 'chr_bytes': CHR_SIZE,
                          'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'CHR asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
