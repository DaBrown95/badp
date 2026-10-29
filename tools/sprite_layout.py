"""Review a contiguous candidate animation directory and sprite frame region.

Sequential layout and pointer closure are static evidence. They do not prove
exclusive sprite use, runtime reachability, or the absence of interior entries.
All decoded values and asset payloads stay in ignored local analysis.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from .build_rom import digest
from .identify_rom import inspect_rom
from .prg_inventory import _optional_trace
from .project import IDENTITY_PARTS, load_project, load_target
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import spec
from .sprite_assets import frame_addresses
from .sprite_metadata import decode_frame_header, frame_header_size, inventory_observed

# The reconstructed native fade routine ends at $B5D3. The reviewed palette
# header begins at $C7DF. The animation records fill the prefix through $BA23.
ANIMATIONS, FRAMES, END = 0x35D3, 0x3A23, 0x47DF


def decode_layout(bank: bytes, animation_start: int, frame_start: int, end: int, *,
                  header_format: str = 'packed-nibbles', animation_end: int | None = None) -> dict:
    directory_end = frame_start if animation_end is None else animation_end
    if (len(bank) != BANK_SIZE
            or any(type(x) is not int for x in (animation_start, directory_end, frame_start, end))
            or not 0 <= animation_start < directory_end <= frame_start < end <= BANK_SIZE):
        raise ValueError('invalid sprite layout range')
    header_size = frame_header_size(header_format)
    frames = []
    cursor = frame_start
    while cursor < end:
        if cursor + header_size > end:
            raise ValueError('truncated sequential sprite frame')
        header = decode_frame_header(bank[cursor:cursor + header_size], header_format=header_format)
        size = header_size + 2 * header['tile_pairs']
        if header['index_wraps'] or cursor + size > end:
            raise ValueError('sequential sprite frame wraps its index or exceeds the region')
        frames.append({'bank_offset': cursor, 'cpu_address': 0x8000 + cursor,
                       'size': size, 'header': header})
        cursor += size
    frame_starts = {row['cpu_address'] for row in frames}
    animations, targeted = [], set()
    cursor = animation_start
    while cursor < directory_end:
        if cursor + 3 > directory_end or bank[cursor] != 0x53:
            raise ValueError('invalid sequential animation header')
        count = bank[cursor + 1] or 256
        size = 3 + 2 * count
        if cursor + size > directory_end:
            raise ValueError('sequential animation table exceeds the region')
        pointers = [int.from_bytes(bank[p:p + 2], 'little')
                    for p in range(cursor + 3, cursor + size, 2)]
        if any(pointer not in frame_starts for pointer in pointers):
            raise ValueError('animation pointer is not a sequential frame boundary')
        targeted.update(pointers)
        animations.append({'bank_offset': cursor, 'cpu_address': 0x8000 + cursor,
                           'size': size, 'frame_count': count, 'delay': bank[cursor + 2],
                           'frame_pointers': pointers})
        cursor += size
    result = {'animations': animations, 'frames': frames,
            'frames_without_animation_pointer': sorted(frame_starts - targeted),
            'region_bytes': end - animation_start,
            'animation_bytes': directory_end - animation_start,
            'frame_bytes': end - frame_start}
    if animation_end is not None:
        result['intervening_bytes'] = frame_start - directory_end
    return result


def compare_layout(bank: bytes, layout: dict, other_prg: bytes) -> dict:
    """Relocate frame bytes and animation pointers independently of directory placement."""
    start = layout['frames'][0]['bank_offset']
    size = layout['frame_bytes']
    payload = bank[start:start + size]
    first = other_prg.find(payload)
    if first < 0:
        return {'frame_region_exact_occurrences': 0}
    if other_prg.find(payload, first + 1) >= 0:
        return {'frame_region_exact_occurrences': 'multiple'}
    delta = first - start
    normalized = bytearray()
    for animation in layout['animations']:
        normalized.extend((0x53, animation['frame_count'] & 0xff, animation['delay']))
        for pointer in animation['frame_pointers']:
            relocated = pointer + delta
            if not 0x8000 <= relocated <= 0xffff:
                return {'frame_region_exact_occurrences': 1,
                        'frame_physical_prg_offset': first,
                        'animation_comparison': 'frame relocation changes bank; CPU pointers unresolved'}
            normalized.extend(relocated.to_bytes(2, 'little'))
    directory = other_prg.find(normalized)
    result = {'frame_region_exact_occurrences': 1, 'frame_physical_prg_offset': first,
              'frame_delta': delta, 'normalized_animation_directory_offset': directory,
              'interpretation': 'Exact frames and pointer-normalized directory search only; '
              'no claim about callers, runtime mapping or target-version builds.'}
    if directory >= 0:
        result['animation_directory_delta'] = directory - layout['animations'][0]['bank_offset']
        result['normalized_animation_directory_unique'] = other_prg.find(normalized, directory + 1) < 0
    return result


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        reference = target['reference']['file']['sha256']
        script = ROOT / 'tools/mesen_sprites.lua'
        path = ROOT / 'analysis/us-v1.5/sprite-exploration.json'
        trace = _optional_trace(path, script, reference, spec(ROOT)['core_sha256'])
        if trace is None:
            raise ValueError('observed sprite trace is missing')
        trace_hash, tool_hash = digest(path.read_bytes()), digest(Path(__file__).read_bytes())
        observed = inventory_observed(trace, bank0, bank1)
        result = decode_layout(bank0, ANIMATIONS, FRAMES, END)
        comparisons = {}
        for target_id in load_project(ROOT)['target_order'][1:]:
            manifest = load_target(ROOT, target_id)
            rom = (ROOT / manifest['input_path']).read_bytes()
            actual = inspect_rom(rom)
            if any(actual[part] != manifest['reference'][part] for part in IDENTITY_PARTS):
                raise ValueError('comparative ROM differs from reviewed identity')
            start, size = actual['prg']['offset'], actual['prg']['size']
            comparisons[target_id] = compare_layout(bank0, result, rom[start:start + size])
            comparisons[target_id]['reference_sha256'] = actual['file']['sha256']
        result['revision_comparisons'] = comparisons
        frames = {x['cpu_address'] for x in result['frames']}
        resources = {x['cpu_address'] for x in result['animations']} | frames
        if (any(x['bank'] != 0 or x['cpu_address'] not in frames for x in observed['frame'])
                or any(x['bank'] != 0 or x['cpu_address'] not in resources for x in observed['header'])
                or not set(frame_addresses(ROOT)) <= frames):
            raise ValueError('sequential layout omits an observed sprite entry')
        result.update(target='us-v1.5', reference_sha256=reference, bank=0,
                      script_sha256=digest(script.read_bytes()), trace_sha256=trace_hash,
                      tool_sha256=tool_hash, observed_resources=len(observed['header']),
                      observed_frames=len(observed['frame']),
                      interpretation='Static contiguous records and closed frame-pointer tables; '
                      'all observed entries are included, but interior entries, overlapping '
                      'script interpretations and unobserved runtime use remain possible.')
        output = ROOT / 'analysis/us-v1.5/sprite-layout.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        if digest(path.read_bytes()) != trace_hash:
            raise ValueError('sprite trace changed during layout review')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'animations': len(result['animations']), 'frames': len(result['frames']),
                          'animation_pointers': sum(x['frame_count'] for x in result['animations']),
                          'frames_without_animation_pointer': len(result['frames_without_animation_pointer']),
                          'observed_frames': len(observed['frame']),
                          'output': 'analysis/us-v1.5/sprite-layout.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'sprite layout review failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
