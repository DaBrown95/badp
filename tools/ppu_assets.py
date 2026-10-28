"""Local tile payloads for the reviewed logical PPU command-stream inventory.

Address commands and terminators stay in source. Payload edits preserve their
fixed extents and cannot introduce control bytes. Candidate stream selection,
overlapping script interpretations and native lookahead retain their scope.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from .asset_paths import asset_path
import sys

from . import ppu_streams
from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
MANIFEST = Path('config/ppu-streams-us-v1.5.json')
ASSET_PATH = Path('extracted/us-v1.5/ppu-tiles.json')


def inventory(root: Path, prg: bytes, *, target: str = TARGET, manifest: dict | None = None) -> list[dict]:
    manifest = json.loads((root / MANIFEST).read_text()) if manifest is None else manifest
    if (len(prg) != 2 * BANK_SIZE or not isinstance(manifest, dict)
            or set(manifest) != {'schema_version', 'target', 'source', 'encoded_pointers'}
            or type(manifest['schema_version']) is not int or manifest['schema_version'] != 1
            or manifest['target'] != target or not isinstance(manifest['source'], str)
            or not isinstance(manifest['encoded_pointers'], list)):
        raise ValueError('invalid PPU asset inventory')
    pointers = []
    for item in manifest['encoded_pointers']:
        if not isinstance(item, str) or len(item) != 6 or not item.startswith('0x'):
            raise ValueError('invalid PPU encoded pointer')
        value = int(item, 16)
        if not 0 < value <= 0xffff:
            raise ValueError('PPU pointer must identify a fixed stream')
        pointers.append(value)
    if not pointers or pointers != sorted(set(pointers)):
        raise ValueError('PPU pointers must be unique and ordered')
    result = ppu_streams.inventory(prg[:BANK_SIZE], prg[BANK_SIZE:], pointers)
    if result['overlapping_stream_bytes'] or result['control_payload_overlap_bytes']:
        raise ValueError('PPU asset inventory has overlapping stream interpretations')
    return result['streams']


def capture(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET,
            manifest: dict | None = None) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid PPU asset reference identity')
    streams = []
    for stream in inventory(root, prg, target=target, manifest=manifest):
        start = stream['location']['physical_prg_offset']
        payloads = [{'offset': row['offset'],
                     'tiles': list(prg[start + row['offset']:start + row['offset'] + row['size']])}
                    for row in stream['segments'] if row['kind'] == 'payload']
        streams.append({'encoded_pointer': stream['encoded_pointer'], 'payloads': payloads})
    return {'schema_version': 1, 'target': target, 'reference_sha256': reference_sha256, 'streams': streams}


def encode(root: Path, asset: dict, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           manifest: dict | None = None) -> list[tuple[int, int, bytes]]:
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'streams'}
            or type(asset['schema_version']) is not int or asset['schema_version'] != 1
            or asset['target'] != target or asset['reference_sha256'] != reference_sha256
            or not isinstance(asset['streams'], list)):
        raise ValueError('PPU asset identity differs')
    originals = inventory(root, prg, target=target, manifest=manifest)
    if len(asset['streams']) != len(originals):
        raise ValueError('PPU asset stream count differs')
    spans = []
    for stream, original in zip(asset['streams'], originals):
        rows = [row for row in original['segments'] if row['kind'] == 'payload']
        if (not isinstance(stream, dict) or set(stream) != {'encoded_pointer', 'payloads'}
                or stream['encoded_pointer'] != original['encoded_pointer']
                or not isinstance(stream['payloads'], list) or len(stream['payloads']) != len(rows)):
            raise ValueError('PPU stream identity or payload count differs')
        for row, original_row in zip(stream['payloads'], rows):
            if (not isinstance(row, dict) or set(row) != {'offset', 'tiles'}
                    or type(row['offset']) is not int or row['offset'] != original_row['offset']
                    or not isinstance(row['tiles'], list) or len(row['tiles']) != original_row['size']
                    or any(type(value) is not int or not 1 <= value <= 0xfd for value in row['tiles'])):
                raise ValueError('PPU payload extent differs or tiles contain a control byte')
            location = original['location']
            spans.append((location['bank'], location['bank_offset'] + row['offset'], bytes(row['tiles'])))
    return spans


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           manifest: dict | None = None) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / asset_path(target, ASSET_PATH.name)
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked PPU asset input')
    if path.exists():
        raw = path.read_bytes()
        asset, source = json.loads(raw), 'local'
    else:
        asset = capture(root, prg, reference_sha256, target=target, manifest=manifest)
        raw, source = serialize(asset), 'reference'
    return asset, encode(root, asset, prg, reference_sha256, target=target, manifest=manifest), source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if not any(stream['payloads'] for stream in changed['streams']):
        raise ValueError('PPU control has no payloads')
    for stream in changed['streams']:
        for row in stream['payloads']:
            row['tiles'][0] = row['tiles'][0] % 253 + 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int, asset: dict) -> list[int]:
    if len(reference) != len(candidate):
        raise ValueError('PPU control changed ROM size')
    expected = {}
    for stream in asset['streams']:
        encoded = int(stream['encoded_pointer'], 16)
        bank, start = (0, encoded - 0x8000) if encoded >= 0x8000 else (1, encoded)
        for row in stream['payloads']:
            offset = prg_offset + bank * BANK_SIZE + start + row['offset']
            if offset in expected:
                raise ValueError('overlapping PPU control payloads')
            expected[offset] = row['tiles'][0] % 253 + 1
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if not expected or changed != sorted(expected) or any(candidate[i] != expected[i] for i in expected):
        raise ValueError('PPU control did not change exactly one tile in every payload')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(ROOT, bank0 + bank1, target['reference']['file']['sha256'])
        data, path = serialize(asset), ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked PPU asset output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local PPU tiles differ; preserve or move them before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('PPU output escapes extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'streams': len(asset['streams']), 'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'PPU asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
