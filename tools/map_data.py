"""Decode candidate v1.5 map layouts and chunk metadata locally.

The map's payload is game data: callers must keep decoded records and exports
under the ignored analysis directory. This static inventory does not establish
runtime index bounds or physical cartridge behavior.
"""
from __future__ import annotations

import json
import sys

from .script_entries import BANK_SIZE, ROOT, _locate, _location, load_audited_banks

STATE_TABLE_OFFSET = 0x21B2
STATE_COUNT = 22
CHUNK_TABLE_OFFSET = 0x21DE
CHUNK_INDEX_COUNT = 146
CHUNK_SIZE = 68


def decode_chunk(data: bytes) -> dict:
    """Separate 64 tile bytes and four attribute bytes in a map chunk."""
    if len(data) != CHUNK_SIZE:
        raise ValueError('expected exactly 68 chunk bytes')
    return {'tile_rows': [list(data[i:i + 8]) for i in range(0, 64, 8)],
            'attribute_rows': [list(data[64:66]), list(data[66:68])]}


def encode_chunk(record: dict) -> bytes:
    """Reassemble a decoded chunk without changing tile or attribute values."""
    tiles, attrs = record['tile_rows'], record['attribute_rows']
    if (len(tiles) != 8 or any(len(row) != 8 for row in tiles)
            or len(attrs) != 2 or any(len(row) != 2 for row in attrs)):
        raise ValueError('invalid chunk dimensions')
    values = [v for row in tiles + attrs for v in row]
    if any(type(v) is not int or not 0 <= v <= 255 for v in values):
        raise ValueError('invalid chunk value')
    return bytes(values)


def decode_layout(bank: bytes, offset: int, table_count: int) -> dict:
    """Decode the nominal grid, preserving the engine's dimension arithmetic."""
    if len(bank) != BANK_SIZE or type(offset) is not int or not 0 <= offset < BANK_SIZE:
        raise ValueError('invalid layout bank or offset')
    if type(table_count) is not int or not 1 <= table_count <= 256:
        raise ValueError('invalid chunk table size')
    if offset + 2 > BANK_SIZE:
        raise ValueError('layout header crosses a physical bank')
    width, height = bank[offset:offset + 2]
    cells = width * height
    end = offset + 2 + cells
    if end > BANK_SIZE:
        raise ValueError('layout grid crosses a physical bank')
    grid = bank[offset + 2:end]
    width_tiles = width * 8
    height_tiles = (height * 8) & 0xff
    first_columns = min(width_tiles, 33) if width_tiles else 256
    return {'width_chunks': width, 'height_chunks': height,
            'chunk_rows': [list(grid[i:i + width]) for i in range(0, cells, width)] if width else [],
            'size': 2 + cells, 'width_tiles': width_tiles, 'height_tiles_low': height_tiles,
            'horizontal_bound_pixels': ((width_tiles - 32) * 8) & 0xffff,
            'vertical_bound_pixels': max(height_tiles - 30, 0) * 8,
            'initial_draw_columns': first_columns,
            'out_of_table_indices': sorted(set(v for v in grid if v >= table_count)),
            'last_lookup_crosses_bank': bool(cells and end == BANK_SIZE)}


def encode_layout(layout: dict) -> bytes:
    width, height, rows = layout['width_chunks'], layout['height_chunks'], layout['chunk_rows']
    if (type(width) is not int or type(height) is not int or not 0 <= width <= 255
            or not 0 <= height <= 255 or len(rows) != (height if width else 0)
            or any(len(row) != width for row in rows)):
        raise ValueError('invalid layout dimensions')
    values = [value for row in rows for value in row]
    if any(type(v) is not int or not 0 <= v <= 255 for v in values):
        raise ValueError('invalid layout index')
    return bytes([width, height, *values])


def inventory(bank0: bytes, bank1: bytes) -> dict:
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full PRG banks')
    offsets = [int.from_bytes(bank0[CHUNK_TABLE_OFFSET + 2*i:CHUNK_TABLE_OFFSET + 2*i + 2], 'little')
               for i in range(CHUNK_INDEX_COUNT)]
    chunks = {}
    for index, offset in enumerate(offsets):
        if offset >= 0x8000 or offset + CHUNK_SIZE > BANK_SIZE:
            raise ValueError('chunk offset outside candidate alternate bank')
        if offset not in chunks:
            raw = bank1[offset:offset + CHUNK_SIZE]
            decoded = decode_chunk(raw)
            if encode_chunk(decoded) != raw:
                raise ValueError('chunk did not round-trip')
            chunks[offset] = {'encoded_pointer': f'0x{offset:04x}',
                              'location': _location(1, offset), 'decoded': decoded,
                              'table_indices': []}
        chunks[offset]['table_indices'].append(index)
    layouts = {}
    states = []
    for index in range(STATE_COUNT):
        pos = STATE_TABLE_OFFSET + 2 * index
        pointer = int.from_bytes(bank0[pos:pos + 2], 'little')
        bank, offset = _locate(pointer)
        key = (bank, offset)
        if key not in layouts:
            data = (bank0, bank1)[bank]
            decoded = decode_layout(data, offset, CHUNK_INDEX_COUNT)
            raw = data[offset:offset + decoded['size']]
            if encode_layout(decoded) != raw:
                raise ValueError('layout did not round-trip')
            layouts[key] = {'encoded_pointer': f'0x{pointer:04x}',
                            'location': _location(bank, offset), 'decoded': decoded,
                            'state_indices': []}
        layouts[key]['state_indices'].append(index)
        states.append({'index': index, 'encoded_pointer': f'0x{pointer:04x}',
                       'location': _location(bank, offset)})
    chunk_coverage: dict[int, int] = {}
    for offset in chunks:
        for position in range(offset, offset + CHUNK_SIZE):
            chunk_coverage[position] = chunk_coverage.get(position, 0) + 1
    layout_coverage: dict[tuple[int, int], int] = {}
    for (bank, offset), layout in layouts.items():
        for position in range(offset, offset + layout['decoded']['size']):
            key = (bank, position)
            layout_coverage[key] = layout_coverage.get(key, 0) + 1
    return {'states': states, 'layouts': list(layouts.values()),
            'chunk_table_offsets': offsets, 'chunks': [chunks[p] for p in sorted(chunks)],
            'overlapping_chunk_bytes': sum(n > 1 for n in chunk_coverage.values()),
            'overlapping_layout_bytes': sum(n > 1 for n in layout_coverage.values()),
            'layout_chunk_overlap_bytes': sum((1, p) in layout_coverage for p in chunk_coverage)}


def map_script_overlaps(map_inventory: dict, graph: dict) -> dict:
    """Report physical bytes interpreted as both map data and candidate script."""
    map_bytes: set[int] = set()
    for chunk in map_inventory['chunks']:
        start = chunk['location']['physical_prg_offset']
        map_bytes.update(range(start, start + CHUNK_SIZE))
    for layout in map_inventory['layouts']:
        start = layout['location']['physical_prg_offset']
        map_bytes.update(range(start, start + layout['decoded']['size']))
    conflicts = []
    overlap_bytes: set[int] = set()
    for node in graph['nodes']:
        loc = node['location']
        offset, length = loc['bank_offset'], node.get('length', 0)
        positions: set[int] = set()
        if offset + length <= BANK_SIZE:
            start = loc['bank'] * BANK_SIZE + offset
            positions.update(range(start, start + length))
        for key in ('lookup_records', 'jump_records'):
            for record in node.get(key, []):
                place, size = record['location'], record.get('size', 2)
                if place['bank_offset'] + size <= BANK_SIZE:
                    start = place['bank'] * BANK_SIZE + place['bank_offset']
                    positions.update(range(start, start + size))
        overlap = sorted(positions & map_bytes)
        if overlap:
            overlap_bytes.update(overlap)
            conflicts.append({'encoded_pointer': node['encoded_pointer'],
                              'physical_prg_offsets': overlap})
    return {'physical_bytes': len(overlap_bytes), 'nodes': conflicts}


def main() -> int:
    try:
        from .script_entries import DESCRIPTORS, DESCRIPTOR_COUNT, inventory as descriptor_inventory
        from .script_flow import PRIMARY_INDEXED_JUMPS
        from .slot_record_flow import trace

        target, bank0, bank1, lengths = load_audited_banks()
        result = inventory(bank0, bank1)
        descriptors = descriptor_inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        seeds = []
        for record in descriptors['records']:
            if record['status'] != 'inspected' or record.get('script_status') != 'candidate':
                continue
            loc = record['location']
            base = loc['bank_offset'] + (0x8000 if loc['bank'] == 0 else 0)
            seeds.append((base, int(record['encoded_script_pointer'], 16)))
        flow = trace(bank0, bank1, lengths, seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS)
        if flow['unprocessed_contexts'] or flow['merged_script_flow']['unprocessed']:
            raise ValueError('candidate script context inventory is incomplete')
        result['candidate_script_overlaps'] = map_script_overlaps(result, flow['merged_script_flow'])
        result.update(target='us-v1.5', reference_sha256=target['reference']['file']['sha256'],
                      interpretation='static candidate layouts; alternate-bank mapping and bounds require runtime evidence')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/map-data.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'states': len(result['states']), 'distinct_layouts': len(result['layouts']),
                          'chunk_table_entries': len(result['chunk_table_offsets']),
                          'distinct_chunks': len(result['chunks']),
                          'overlapping_chunk_bytes': result['overlapping_chunk_bytes'],
                          'overlapping_layout_bytes': result['overlapping_layout_bytes'],
                          'layout_chunk_overlap_bytes': result['layout_chunk_overlap_bytes'],
                          'candidate_script_overlap_bytes': result['candidate_script_overlaps']['physical_bytes'],
                          'candidate_script_overlap_nodes': len(result['candidate_script_overlaps']['nodes']),
                          'out_of_table_indices': sum(len(x['decoded']['out_of_table_indices']) for x in result['layouts']),
                          'output': 'analysis/us-v1.5/map-data.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'map inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
