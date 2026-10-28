"""Round-trip local palette colours using reviewed native stream geometry.

Headers remain structured source. Initial colours and trailing animation groups
are local artwork; this encoding does not establish exclusive use or reachability.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
MANIFEST = Path('config/palettes-us-v1.5.json')
ASSET_PATH = Path('extracted/us-v1.5/palettes.json')


def inventory(root: Path, prg: bytes) -> list[dict]:
    manifest = json.loads((root / MANIFEST).read_text())
    if (len(prg) != 2 * BANK_SIZE or not isinstance(manifest, dict)
            or set(manifest) != {'schema_version', 'target', 'source', 'bank', 'cpu_addresses', 'end_cpu'}
            or type(manifest['schema_version']) is not int or manifest['schema_version'] != 1
            or manifest['target'] != TARGET or type(manifest['bank']) is not int or manifest['bank'] != 0
            or not isinstance(manifest['source'], str) or not isinstance(manifest['cpu_addresses'], list)):
        raise ValueError('invalid palette layout manifest')
    addresses = []
    for item in manifest['cpu_addresses'] + [manifest['end_cpu']]:
        if not isinstance(item, str) or len(item) != 6 or not item.startswith('0x'):
            raise ValueError('invalid palette address')
        address = int(item, 16)
        if not 0x8000 <= address <= 0xffff:
            raise ValueError('palette address is outside PRG')
        addresses.append(address)
    if len(addresses) < 2 or addresses != sorted(set(addresses)):
        raise ValueError('palette layout must have ordered unique boundaries')
    streams = []
    for start, end in zip(addresses, addresses[1:]):
        offset = start - 0x8000
        if end - start < 19:
            raise ValueError('truncated palette stream')
        groups, frames, ticks = prg[offset:offset + 3]
        width = groups * 4
        if groups > 4 or (groups and (not frames or width * (frames - 1) + 16 - width > 255)):
            raise ValueError('palette layout exceeds reviewed background-index behavior')
        size = 19 + (width * (frames - 1) if groups else 0)
        if start + size != end:
            raise ValueError('palette stream does not end at the next boundary')
        streams.append({'cpu': f'0x{start:04x}', 'offset': offset, 'size': size,
                        'group_count': groups, 'frame_count': frames, 'ticks': ticks})
    return streams


def capture(root: Path, prg: bytes, reference_sha256: str) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid palette reference identity')
    streams = []
    for stream in inventory(root, prg):
        start = stream['offset'] + 3
        width = stream['group_count'] * 4
        streams.append({key: stream[key] for key in ('cpu', 'group_count', 'frame_count', 'ticks')} |
                       {'initial': list(prg[start:start + 16]),
                        'updates': [list(prg[p:p + width])
                                    for p in range(start + 16, start + stream['size'] - 3, width or 1)]})
    return {'schema_version': 1, 'target': TARGET, 'reference_sha256': reference_sha256,
            'bank': 0, 'streams': streams}


def encode(root: Path, asset: dict, prg: bytes, reference_sha256: str) -> list[tuple[int, int, bytes]]:
    if (not isinstance(asset, dict)
            or set(asset) != {'schema_version', 'target', 'reference_sha256', 'bank', 'streams'}
            or type(asset['schema_version']) is not int or asset['schema_version'] != 1
            or asset['target'] != TARGET or asset['reference_sha256'] != reference_sha256
            or type(asset['bank']) is not int or asset['bank'] != 0
            or not isinstance(asset['streams'], list)):
        raise ValueError('palette asset identity differs from reference')
    originals = inventory(root, prg)
    if len(asset['streams']) != len(originals):
        raise ValueError('palette asset stream count differs')
    spans = []
    for stream, original in zip(asset['streams'], originals):
        if (not isinstance(stream, dict)
                or set(stream) != {'cpu', 'group_count', 'frame_count', 'ticks', 'initial', 'updates'}
                or stream['cpu'] != original['cpu']
                or any(type(stream[key]) is not int or stream[key] != original[key]
                       for key in ('group_count', 'frame_count', 'ticks'))
                or not isinstance(stream['initial'], list) or len(stream['initial']) != 16
                or not isinstance(stream['updates'], list)
                or len(stream['updates']) != (original['frame_count'] - 1 if original['group_count'] else 0)):
            raise ValueError('palette asset layout or header differs')
        rows = [stream['initial']] + stream['updates']
        for index, row in enumerate(rows):
            if (not isinstance(row, list) or len(row) != (16 if index == 0 else original['group_count'] * 4)
                    or any(type(value) is not int or not 0 <= value <= 255 for value in row)):
                raise ValueError('invalid palette colour row')
        payload = bytes(value for row in rows for value in row)
        spans.append((0, original['offset'] + 3, payload))
    return spans


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / ASSET_PATH
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked palette input')
    if path.exists():
        raw = path.read_bytes()
        asset, source = json.loads(raw), 'local'
    else:
        asset = capture(root, prg, reference_sha256)
        raw, source = serialize(asset), 'reference'
    return asset, encode(root, asset, prg, reference_sha256), source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if not changed['streams']:
        raise ValueError('palette control has no streams')
    for stream in changed['streams']:
        # Colour 1 is consumed by both background and sprite setup. Exercise
        # every trailing animation group as well as each initial palette.
        for row in [stream['initial']] + stream['updates']:
            row[1] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int, asset: dict) -> list[int]:
    if len(reference) != len(candidate):
        raise ValueError('palette control changed ROM size')
    expected = []
    for stream in asset['streams']:
        start = prg_offset + int(stream['cpu'], 16) - 0x8000 + 3
        expected.append(start + 1)
        expected.extend(start + 16 + i * stream['group_count'] * 4 + 1
                        for i in range(len(stream['updates'])))
    expected.sort()
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if (not expected or len(expected) != len(set(expected)) or changed != expected
            or any(candidate[i] != (reference[i] ^ 1) for i in expected)):
        raise ValueError('palette control did not change exactly one colour per initial palette and update group')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(ROOT, bank0 + bank1, target['reference']['file']['sha256'])
        data, path = serialize(asset), ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked palette output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local palettes differ; preserve or move them before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('palette output escapes extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'streams': len(asset['streams']), 'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'palette export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
