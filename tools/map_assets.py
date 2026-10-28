"""Round-trip v1.5's locally extracted map chunks without publishing assets.

The table identifies 145 referenced 68-byte slots. One aligned slot has no
known table reference but exactly duplicates referenced slot 134. Its local
rows are editable independently; the duplicate relation describes the reference. The decoded
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
DUPLICATE_SLOT = 22
DUPLICATE_OF = 134
CONTROL_TILES = ((0, 0, 0), (DUPLICATE_SLOT, 0, 1), (DUPLICATE_OF, 0, 2))


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


def duplicate_slot(prg: bytes) -> int:
    """Validate the reviewed physical relation without claiming table use."""
    slots_for_reference(prg)
    start = BANK_SIZE + DUPLICATE_SLOT * CHUNK_SIZE
    other = BANK_SIZE + DUPLICATE_OF * CHUNK_SIZE
    if prg[start:start + CHUNK_SIZE] != prg[other:other + CHUNK_SIZE]:
        raise ValueError('unreferenced map slot no longer duplicates the reviewed referenced slot')
    return DUPLICATE_SLOT


def capture(prg: bytes, reference_sha256: str) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    referenced = slots_for_reference(prg)
    duplicate_slot(prg)
    blob = prg[BANK_SIZE:BANK_SIZE + REGION_SIZE]
    slots = []
    for index in range(SLOT_COUNT):
        raw = blob[index * CHUNK_SIZE:(index + 1) * CHUNK_SIZE]
        if index in referenced:
            decoded = decode_chunk(raw)
            slots.append({'index': index, 'kind': 'chunk', **decoded})
        else:
            slots.append({'index': index, 'kind': 'unreferenced_duplicate_chunk',
                          'reference_duplicate_of': DUPLICATE_OF, **decode_chunk(raw)})
    return {'schema_version': 2, 'target': TARGET, 'reference_sha256': reference_sha256,
            'chunk_size': CHUNK_SIZE, 'slots': slots}


def encode(asset: dict, prg: bytes, reference_sha256: str) -> bytes:
    """Encode an editable local view, enforcing geometry and the reviewed duplicate identity."""
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'chunk_size', 'slots'}
            or asset['schema_version'] != 2 or asset['target'] != TARGET
            or asset['reference_sha256'] != reference_sha256 or asset['chunk_size'] != CHUNK_SIZE
            or not isinstance(asset['slots'], list) or len(asset['slots']) != SLOT_COUNT):
        raise ValueError('map asset identity or geometry differs from the reference')
    referenced = slots_for_reference(prg)
    duplicate_slot(prg)
    output = bytearray()
    for index, slot in enumerate(asset['slots']):
        if not isinstance(slot, dict) or type(slot.get('index')) is not int or slot['index'] != index:
            raise ValueError('map asset slot order or index is invalid')
        if index in referenced:
            if set(slot) != {'index', 'kind', 'tile_rows', 'attribute_rows'} or slot['kind'] != 'chunk':
                raise ValueError('referenced map slot must be a structured chunk')
            raw = encode_chunk(slot)
        else:
            if (set(slot) != {'index', 'kind', 'reference_duplicate_of', 'tile_rows', 'attribute_rows'}
                    or slot['kind'] != 'unreferenced_duplicate_chunk'
                    or type(slot['reference_duplicate_of']) is not int
                    or slot['reference_duplicate_of'] != DUPLICATE_OF):
                raise ValueError('unreferenced map slot must retain the reviewed duplicate metadata')
            raw = encode_chunk(slot)
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
    """Change distinct tiles in ordinary, duplicate and referenced-original slots."""
    changed = json.loads(json.dumps(asset))
    for index, row, column in CONTROL_TILES:
        expected = 'unreferenced_duplicate_chunk' if index == DUPLICATE_SLOT else 'chunk'
        if changed['slots'][index]['kind'] != expected:
            raise ValueError('control slot is not its reviewed chunk kind')
        changed['slots'][index]['tile_rows'][row][column] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int) -> list[int]:
    if len(candidate) != len(reference):
        raise ValueError('map asset control changed ROM size')
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    expected = sorted(prg_offset + BANK_SIZE + index * CHUNK_SIZE + row * 8 + column
                      for index, row, column in CONTROL_TILES)
    if changed != expected or any(candidate[p] != (reference[p] ^ 1) for p in expected):
        raise ValueError('map asset control did not change exactly its three selected tiles')
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
        print(json.dumps({'target': TARGET, 'referenced_chunks': 145, 'unreferenced_duplicate_chunks': 1,
                          'bytes': REGION_SIZE, 'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'map asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
