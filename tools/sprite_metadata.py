"""Decode sprite metadata without assuming that resources are code.

The NES engine reads tiles through an eight-bit Y index; long frames wrap
that index. Payload bytes are game assets and must remain local.
"""
from __future__ import annotations


def frame_header_size(header_format: str = 'packed-nibbles') -> int:
    if header_format not in ('packed-nibbles', 'separate-bytes'):
        raise ValueError('unknown sprite frame header format')
    return 2 if header_format == 'packed-nibbles' else 3


def decode_frame_header(data: bytes, *, header_format: str = 'packed-nibbles') -> dict:
    size = frame_header_size(header_format)
    if len(data) < size:
        raise ValueError('truncated sprite frame header')
    first = data[0]
    if header_format == 'packed-nibbles':
        columns, rows = data[1] >> 4, data[1] & 0x0F
    else:
        columns, rows = data[1:3]
    # Both loops decrement an eight-bit counter before testing for zero.
    effective_columns, effective_rows = columns or 256, rows or 256
    cells = effective_columns * effective_rows
    # Y begins immediately after the header and remains an eight-bit index.
    offsets = sorted({(size + 2 * i + part) & 0xFF
                      for i in range(min(cells, 128)) for part in (0, 1)})
    return {'oam_base_index': first & 0x7F, 'large_sprites': bool(first & 0x80),
            'columns': columns, 'rows': rows,
            'effective_columns': effective_columns, 'effective_rows': effective_rows,
            'tile_pairs': cells, 'tile_read_offsets': offsets,
            'index_wraps': size + 2 * cells > 256}


def decode_resource_header(data: bytes) -> dict:
    if not data:
        raise ValueError('missing sprite resource header')
    if data[0] == 0x4F:
        return {'kind': 'empty'}
    if data[0] == 0x53:
        if len(data) < 5:
            raise ValueError('truncated animated sprite header')
        return {'kind': 'animated', 'frame_count': data[1], 'delay': data[2],
                'first_frame_pointer': int.from_bytes(data[3:5], 'little')}
    if len(data) < 2:
        raise ValueError('truncated direct sprite header')
    return {'kind': 'direct', 'frame': decode_frame_header(data)}


def resource_pointer_candidates(descriptor_records: list[dict], references: list[dict]) -> dict:
    """Collect possible resource pointers without treating CPU RAM as ROM."""
    values = []
    for entry in descriptor_records:
        if entry.get('status') == 'inspected':
            fields = entry['decoded_fields']
            if fields['sprite_fields_present']:
                values.append(fields['sprite_pointer'])
    for entry in references:
        if entry.get('status') == 'candidate':
            fields = entry['fields']
            if fields['sprite_fields_present']:
                values.append(fields['sprite_pointer'])
    if any(type(value) is not int or not 0 <= value <= 0xffff for value in values):
        raise ValueError('invalid candidate sprite pointer')
    return {'rom_pointers': sorted({value for value in values if 0x8000 <= value < 0xff00}),
            'non_rom_pointers': sorted({value for value in values if value < 0x8000}),
            'sentinel_pointers': sorted({value for value in values if value >= 0xff00})}


def inventory_candidates(bank0: bytes, pointers: list[int]) -> dict:
    """Follow candidate resource and bounded animation-frame pointers in bank 0.

    The candidate descriptor association and bank mapping are not runtime
    evidence. Other frame indices can be computed dynamically. Returned spans
    are physical PRG offsets and include only bytes within this bank.
    """
    if len(bank0) != 0x8000 or any(type(p) is not int or not 0x8000 <= p < 0xff00 for p in pointers):
        raise ValueError('expected a full bank and bank-0 candidate pointers')
    spans: list[tuple[int, int]] = []
    headers = []
    frames: dict[int, dict] = {}
    crossings = []
    non_rom_frames: set[int] = set()

    def record_frame(pointer: int) -> None:
        if pointer < 0x8000:
            non_rom_frames.add(pointer)
            return
        offset = pointer - 0x8000
        if offset in frames:
            return
        if offset + 2 > len(bank0):
            crossings.append({'kind': 'frame_header', 'cpu_address': pointer})
            return
        decoded = decode_frame_header(bank0[offset:offset + 2])
        frames[offset] = {'cpu_address': pointer, 'physical_prg_offset': offset, 'decoded': decoded}
        spans.append((offset, 2))
        for relative in decoded['tile_read_offsets']:
            if offset + relative < len(bank0):
                spans.append((offset + relative, 1))
            else:
                crossings.append({'kind': 'frame_tile', 'cpu_address': pointer, 'index': relative})

    for pointer in sorted(set(pointers)):
        offset = pointer - 0x8000
        if bank0[offset] == 0x4f:
            headers.append({'cpu_address': pointer, 'kind': 'empty'})
            # The slot loader also reads the following dimension byte, even
            # though the sprite allocator stops at the empty marker.
            spans.append((offset, 2))
        elif bank0[offset] == 0x53:
            if offset + 3 > len(bank0):
                crossings.append({'kind': 'resource_header', 'cpu_address': pointer})
                continue
            count = bank0[offset + 1] or 256
            available = min(count, (len(bank0) - offset - 3) // 2)
            headers.append({'cpu_address': pointer, 'kind': 'animated', 'candidate_frames': count,
                            'frame_pointers_within_bank': available})
            spans.append((offset, 3 + 2 * available))
            if available != count:
                crossings.append({'kind': 'frame_pointer_table', 'cpu_address': pointer})
            for index in range(available):
                position = offset + 3 + 2 * index
                record_frame(int.from_bytes(bank0[position:position + 2], 'little'))
        else:
            headers.append({'cpu_address': pointer, 'kind': 'direct'})
            record_frame(pointer)
    return {'resources': headers, 'frames': [frames[offset] for offset in sorted(frames)],
            'spans': spans, 'crossings': crossings, 'non_rom_frames': sorted(non_rom_frames)}


def inventory_observed(trace: dict, bank0: bytes, bank1: bytes) -> dict:
    """Validate observed mapped header samples and describe their formats.

    The two-byte sample can include bytes the code has not actually read yet.
    Frame payloads, pointers and decoded metadata remain local game data.
    """
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two full PRG banks')
    entries: dict[str, dict[int, dict]] = {'header': {}, 'frame': {}}
    for scenario, result in trace['results'].items():
        for kind in entries:
            totals = result['totals'][kind]
            if (not isinstance(totals, list) or len(totals) != 2
                    or any(type(value) is not int or value < 0 for value in totals)):
                raise ValueError('invalid sprite trace totals')
            observed = 0
            for key, count in result['reads'][kind].items():
                parts = key.split(':')
                if (len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 4
                        or type(count) is not int or count <= 0):
                    raise ValueError('invalid sprite header observation')
                try:
                    physical = int(parts[0], 16)
                    sample = bytes.fromhex(parts[1])
                except ValueError as exc:
                    raise ValueError('invalid sprite header observation') from exc
                if len(sample) != 2 or not 0 <= physical < 0x10000:
                    raise ValueError('invalid sprite header observation')
                bank, offset = divmod(physical, 0x8000)
                if offset + 2 > 0x8000:
                    raise ValueError('sprite sample crosses a bank')
                rom = (bank0, bank1)[bank]
                if sample != rom[offset:offset + 2]:
                    raise ValueError('sprite sample differs from reference')
                if physical not in entries[kind]:
                    record = {'physical_prg_offset': physical, 'bank': bank,
                              'cpu_address': 0x8000 + offset, 'scenarios': {}}
                    if kind == 'frame':
                        decoded = decode_frame_header(sample)
                        record['decoded'] = decoded
                        record['tile_reads_within_bank'] = all(
                            offset + index < 0x8000 for index in decoded['tile_read_offsets'])
                    else:
                        record['decoded'] = decode_resource_header(rom[offset:offset + 5])
                    entries[kind][physical] = record
                scenarios = entries[kind][physical]['scenarios']
                scenarios[scenario] = scenarios.get(scenario, 0) + count
                observed += count
            if observed + totals[1] != totals[0]:
                raise ValueError('sprite trace totals do not match observations')
    return {kind: [values[offset] for offset in sorted(values)]
            for kind, values in entries.items()}


def main() -> int:
    import json
    import sys
    from .script_entries import ROOT, load_audited_banks

    try:
        target, bank0, bank1, _ = load_audited_banks()
        trace = json.loads((ROOT / 'analysis/us-v1.5/sprite-exploration.json').read_text())
        reference = target['reference']['file']['sha256']
        if trace['reference_sha256'] != reference:
            raise ValueError('sprite trace reference does not match audited ROM')
        result = inventory_observed(trace, bank0, bank1)
        result.update(target='us-v1.5', reference_sha256=reference,
                      interpretation='observed headers only; frame use and other paths are incomplete')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/sprite-inventory.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'headers': len(result['header']), 'frames': len(result['frame']),
                          'wrapped_index_frames': sum(x['decoded']['index_wraps'] for x in result['frame']),
                          'frames_crossing_bank': sum(not x['tile_reads_within_bank'] for x in result['frame']),
                          'output': 'analysis/us-v1.5/sprite-inventory.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'sprite inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
