"""Round-trip locally supplied, inventoried sprite-frame metadata and tile pairs.

The address list combines a reviewed contiguous layout with a subset of
emulator observations. Other entries and overlapping interpretations may exist. Tile indices and attribute
bytes are game assets and remain in ignored local files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from .asset_paths import asset_path
import sys

from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .sprite_metadata import decode_frame_header, frame_header_size

TARGET = 'us-v1.5'
MANIFEST = Path('config/sprite-frames-us-v1.5.json')
ASSET_PATH = Path('extracted/us-v1.5/sprite-frames.json')


def frame_addresses(root: Path, *, target: str = TARGET, manifest: dict | None = None) -> list[int]:
    data = json.loads((root / MANIFEST).read_text()) if manifest is None else manifest
    required = {'schema_version', 'target', 'source', 'bank', 'cpu_addresses'}
    if (not isinstance(data, dict) or set(data) not in (required, required | {'header_format'})
            or type(data['schema_version']) is not int or data['schema_version'] != 1 or data['target'] != target
            or type(data['bank']) is not int or data['bank'] != 0
            or not isinstance(data['source'], str) or not isinstance(data['cpu_addresses'], list)):
        raise ValueError('invalid inventoried sprite frame inventory')
    frame_header_size(data.get('header_format', 'packed-nibbles'))
    addresses = []
    for item in data['cpu_addresses']:
        if not isinstance(item, str) or len(item) != 6 or not item.startswith('0x'):
            raise ValueError('invalid inventoried sprite frame address')
        try:
            address = int(item, 16)
        except ValueError as exc:
            raise ValueError('invalid inventoried sprite frame address') from exc
        if not 0x8000 <= address <= 0xfffd:
            raise ValueError('inventoried sprite frame lies outside the PRG window')
        addresses.append(address)
    if not addresses or addresses != sorted(set(addresses)):
        raise ValueError('inventoried sprite frames must be unique and ordered')
    return addresses


def inventory(root: Path, prg: bytes, *, target: str = TARGET, manifest: dict | None = None) -> list[dict]:
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    manifest = json.loads((root / MANIFEST).read_text()) if manifest is None else manifest
    addresses = frame_addresses(root, target=target, manifest=manifest)
    header_format = manifest.get('header_format', 'packed-nibbles')
    header_size = frame_header_size(header_format)
    frames = []
    end = 0
    for address in addresses:
        offset = address - 0x8000
        header = decode_frame_header(prg[offset:offset + header_size], header_format=header_format)
        if header['index_wraps'] or offset + header_size + 2 * header['tile_pairs'] > BANK_SIZE:
            raise ValueError('inventoried frame index wraps or crosses its PRG bank')
        size = header_size + 2 * header['tile_pairs']
        if offset < end:
            raise ValueError('inventoried sprite frames overlap')
        end = offset + size
        frames.append({'offset': offset, 'size': size, 'header': header, 'header_size': header_size})
    return frames


def capture(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET,
            manifest: dict | None = None) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    manifest = json.loads((root / MANIFEST).read_text()) if manifest is None else manifest
    frames = []
    for frame in inventory(root, prg, target=target, manifest=manifest):
        start, h = frame['offset'], frame['header']
        rows = []
        for row in range(h['rows']):
            pairs = []
            for col in range(h['columns']):
                pos = start + frame['header_size'] + 2 * (row * h['columns'] + col)
                pairs.append([prg[pos], prg[pos + 1]])
            rows.append(pairs)
        frames.append({'cpu': f'0x{start + 0x8000:04x}', 'oam_base_index': h['oam_base_index'],
                       'large_sprites': h['large_sprites'], 'columns': h['columns'], 'rows': h['rows'],
                       'tile_rows': rows})
    result = {'schema_version': 1, 'target': target, 'reference_sha256': reference_sha256, 'bank': 0,
              'frames': frames}
    if manifest and manifest.get('header_format', 'packed-nibbles') != 'packed-nibbles':
        result['header_format'] = manifest['header_format']
    return result


def encode(root: Path, asset: dict, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           manifest: dict | None = None) -> list[tuple[int, int, bytes]]:
    """Return frame spans with stable headers and locally editable tile pairs."""
    required = {'schema_version', 'target', 'reference_sha256', 'bank', 'frames'}
    if (not isinstance(asset, dict) or set(asset) not in (required, required | {'header_format'})
            or asset['schema_version'] != 1 or asset['target'] != target or asset['reference_sha256'] != reference_sha256
            or type(asset['bank']) is not int or asset['bank'] != 0 or not isinstance(asset['frames'], list)):
        raise ValueError('sprite asset identity differs from the reference')
    originals = inventory(root, prg, target=target, manifest=manifest)
    if any(frame_header_size(asset.get('header_format', 'packed-nibbles')) != row['header_size']
           for row in originals):
        raise ValueError('sprite asset header format differs from the declared inventory')
    if len(asset['frames']) != len(originals):
        raise ValueError('sprite frame count differs from the declared inventory')
    spans = []
    for item, original in zip(asset['frames'], originals):
        header, start = original['header'], original['offset']
        if (not isinstance(item, dict) or set(item) != {'cpu', 'oam_base_index', 'large_sprites', 'columns', 'rows', 'tile_rows'}
                or item['cpu'] != f'0x{start + 0x8000:04x}'
                or type(item['oam_base_index']) is not int or item['oam_base_index'] != header['oam_base_index']
                or type(item['large_sprites']) is not bool or item['large_sprites'] != header['large_sprites']
                or type(item['columns']) is not int or item['columns'] != header['columns']
                or type(item['rows']) is not int or item['rows'] != header['rows']
                or not isinstance(item['tile_rows'], list) or len(item['tile_rows']) != header['rows']):
            raise ValueError('sprite frame identity, order or header differs')
        payload = bytearray(prg[start:start + original['header_size']])
        for row in item['tile_rows']:
            if not isinstance(row, list) or len(row) != header['columns']:
                raise ValueError('sprite tile row has wrong width')
            for pair in row:
                if (not isinstance(pair, list) or len(pair) != 2
                        or any(type(value) is not int or not 0 <= value <= 255 for value in pair)):
                    raise ValueError('sprite tile pair must contain two bytes')
                payload.extend(pair)
        if len(payload) != original['size']:
            raise ValueError('sprite frame changed size')
        spans.append((0, start, bytes(payload)))
    return spans


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           manifest: dict | None = None) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / asset_path(target, ASSET_PATH.name)
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked sprite asset input')
    if path.exists():
        raw = path.read_bytes()
        asset, source = json.loads(raw), 'local'
    else:
        asset = capture(root, prg, reference_sha256, target=target, manifest=manifest)
        raw, source = serialize(asset), 'reference'
    return asset, encode(root, asset, prg, reference_sha256, target=target, manifest=manifest), source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if not changed['frames']:
        raise ValueError('sprite control has no frames')
    for frame in changed['frames']:
        if not frame['tile_rows'] or not frame['tile_rows'][0]:
            raise ValueError('sprite control frame has no first tile')
        frame['tile_rows'][0][0][0] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int, asset: dict) -> list[int]:
    if len(reference) != len(candidate):
        raise ValueError('sprite control changed ROM size')
    header_size = frame_header_size(asset.get('header_format', 'packed-nibbles'))
    expected = sorted(prg_offset + int(frame['cpu'], 16) - 0x8000 + header_size for frame in asset['frames'])
    changed = [index for index, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if (len(expected) != len(set(expected)) or changed != expected
            or any(candidate[index] != (reference[index] ^ 1) for index in expected)):
        raise ValueError('sprite control did not change exactly one tile per inventoried frame')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(ROOT, bank0 + bank1, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked sprite asset output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local sprite frames already exist and differ; preserve or move them before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('sprite asset output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'frames': len(asset['frames']),
                          'tile_pairs': sum(f['columns'] * f['rows'] for f in asset['frames']),
                          'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'sprite asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
