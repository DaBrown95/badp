"""Decode sprite metadata without assuming that resources are code.

The NES engine reads tiles through an eight-bit Y index; long frames wrap
that index. Payload bytes are game assets and must remain local.
"""
from __future__ import annotations


def decode_frame_header(data: bytes) -> dict:
    if len(data) < 2:
        raise ValueError('truncated sprite frame header')
    first, dimensions = data[:2]
    columns, rows = dimensions >> 4, dimensions & 0x0F
    # Both loops decrement an eight-bit counter before testing for zero.
    effective_columns, effective_rows = columns or 256, rows or 256
    cells = effective_columns * effective_rows
    # Y begins at 2 and wraps after every 256 indirect-indexed reads.
    offsets = sorted({(2 + 2 * i + part) & 0xFF
                      for i in range(min(cells, 128)) for part in (0, 1)})
    return {'oam_base_index': first & 0x7F, 'large_sprites': bool(first & 0x80),
            'columns': columns, 'rows': rows,
            'effective_columns': effective_columns, 'effective_rows': effective_rows,
            'tile_pairs': cells, 'tile_read_offsets': offsets,
            'index_wraps': cells >= 128}


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
