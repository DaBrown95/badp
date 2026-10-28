"""Inventory evidence about physical v1.5 PRG bytes without exporting game data.

The categories can overlap. A candidate data use does not prove that a byte
cannot also be code, and an uncatalogued byte is not necessarily executable.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
import re
from pathlib import Path
import sys

from . import (audio_commands, audio_flow, direct_record_flow, map_data, native_event_flow, packed_text, ppu_streams,
               slot_record_flow, sprite_metadata)
from .build_rom import source_regions
from .progress import verify_primary
from .project import input_path
from .script_entries import (BANK_SIZE, DESCRIPTORS, DESCRIPTOR_COUNT, ROOT,
                             inventory as descriptor_inventory, load_audited_banks)
from .script_flow import ConditionalIndexedJump, PRIMARY_INDEXED_JUMPS, walk
from .setup_mesen import spec

CATEGORIES = ('source_code', 'source_data', 'candidate_map_chunks', 'candidate_map_layouts',
              'candidate_map_header_bytes', 'candidate_map_grid_bytes', 'candidate_unreferenced_map_slots',
              'packed_text_records', 'packed_text_header_bytes', 'packed_text_payload_bytes',
              'observed_audio_commands', 'candidate_sprite_bytes',
              'candidate_script_bytes', 'candidate_record_bytes', 'candidate_palette_setup_bytes',
              'candidate_audio_commands', 'candidate_ppu_stream_bytes', 'candidate_ppu_control_bytes',
              'candidate_ppu_payload_bytes', 'candidate_sprite_static_bytes', 'source_fill')
INVENTORY_INPUTS = ('tools/prg_inventory.py', 'tools/map_data.py', 'tools/packed_text.py',
                    'tools/script_entries.py', 'tools/script_flow.py', 'tools/slot_record_flow.py',
                    'tools/direct_record_flow.py', 'tools/native_event_flow.py',
                    'tools/audio_commands.py', 'tools/audio_flow.py', 'tools/ppu_streams.py',
                    'tools/sprite_metadata.py', 'tools/setup_mesen.py',
                    'config/mesence-toolchain.json')


def summarize(spans: dict[str, list[tuple[int, int]]], *, bank_size: int = BANK_SIZE,
              bank_count: int = 2) -> dict:
    """Count each physical byte once, retaining every competing use label."""
    if (type(bank_size) is not int or bank_size <= 0 or type(bank_count) is not int
            or bank_count <= 0 or set(spans) - set(CATEGORIES)):
        raise ValueError('invalid inventory geometry or category')
    size = bank_size * bank_count
    masks = [0] * size
    for bit, name in enumerate(CATEGORIES):
        for span in spans.get(name, []):
            if not isinstance(span, (list, tuple)) or len(span) != 2:
                raise ValueError('invalid evidence span')
            start, length = span
            if (type(start) is not int or type(length) is not int or start < 0 or length <= 0
                    or start + length > size or start // bank_size != (start + length - 1) // bank_size):
                raise ValueError('evidence span crosses a physical bank or lies outside PRG')
            flag = 1 << bit
            for offset in range(start, start + length):
                masks[offset] |= flag
    counts = {name: sum(bool(mask & (1 << bit)) for mask in masks)
              for bit, name in enumerate(CATEGORIES)}
    combinations = Counter(masks)
    groups = [{'uses': [name for bit, name in enumerate(CATEGORIES) if mask & (1 << bit)],
               'bytes': count}
              for mask, count in sorted(combinations.items())]
    # Preserve locations, overlaps and holes for an audit of every region.
    evidence_spans = []
    for bank in range(bank_count):
        position, end = bank * bank_size, (bank + 1) * bank_size
        while position < end:
            start, mask = position, masks[position]
            while position < end and masks[position] == mask:
                position += 1
            evidence_spans.append({
                'bank': bank, 'cpu_start': f'0x{0x8000 + start % bank_size:04x}',
                'physical_prg_offset': start, 'size': position - start,
                'uses': [name for bit, name in enumerate(CATEGORIES) if mask & (1 << bit)]})
    unknown = []
    for bank in range(bank_count):
        begin = bank * bank_size
        offset = 0
        while offset < bank_size:
            if masks[begin + offset]:
                offset += 1
                continue
            start = offset
            while offset < bank_size and not masks[begin + offset]:
                offset += 1
            unknown.append({'bank': bank, 'cpu_start': f'0x{0x8000 + start:04x}',
                            'physical_prg_offset': begin + start, 'size': offset - start})
    source_mask = 3
    script_mask = 1 << CATEGORIES.index('candidate_script_bytes')
    data_mask = ((1 << len(CATEGORIES)) - 1) ^ source_mask ^ script_mask
    map_mask = ((1 << CATEGORIES.index('candidate_map_chunks'))
                | (1 << CATEGORIES.index('candidate_map_layouts')))
    unreferenced_map_mask = 1 << CATEGORIES.index('candidate_unreferenced_map_slots')
    record_mask = 1 << CATEGORIES.index('candidate_record_bytes')
    observed_audio_mask = 1 << CATEGORIES.index('observed_audio_commands')
    candidate_audio_mask = 1 << CATEGORIES.index('candidate_audio_commands')
    map_header_mask = 1 << CATEGORIES.index('candidate_map_header_bytes')
    map_grid_mask = 1 << CATEGORIES.index('candidate_map_grid_bytes')
    text_header_mask = 1 << CATEGORIES.index('packed_text_header_bytes')
    text_payload_mask = 1 << CATEGORIES.index('packed_text_payload_bytes')
    ppu_control_mask = 1 << CATEGORIES.index('candidate_ppu_control_bytes')
    ppu_payload_mask = 1 << CATEGORIES.index('candidate_ppu_payload_bytes')
    observed_sprite_mask = 1 << CATEGORIES.index('candidate_sprite_bytes')
    static_sprite_mask = 1 << CATEGORIES.index('candidate_sprite_static_bytes')
    return {'prg_bytes': size, 'category_bytes': counts, 'use_combinations': groups,
            'evidence_spans': evidence_spans,
            'uncatalogued_bytes': combinations.get(0, 0),
            'source_and_candidate_data_bytes': sum(bool(mask & source_mask) and bool(mask & data_mask)
                                                   for mask in masks),
            'source_and_candidate_script_bytes': sum(bool(mask & source_mask) and bool(mask & script_mask)
                                                     for mask in masks),
            'map_and_candidate_script_bytes': sum(bool(mask & map_mask) and bool(mask & script_mask)
                                                  for mask in masks),
            'unreferenced_map_slot_and_candidate_script_bytes': sum(
                bool(mask & unreferenced_map_mask) and bool(mask & script_mask) for mask in masks),
            'record_and_candidate_script_bytes': sum(bool(mask & record_mask) and bool(mask & script_mask)
                                                     for mask in masks),
            'source_and_candidate_map_header_bytes': sum(
                bool(mask & source_mask) and bool(mask & map_header_mask) for mask in masks),
            'source_and_candidate_map_grid_bytes': sum(
                bool(mask & source_mask) and bool(mask & map_grid_mask) for mask in masks),
            'source_and_packed_text_header_bytes': sum(
                bool(mask & source_mask) and bool(mask & text_header_mask) for mask in masks),
            'source_and_packed_text_payload_bytes': sum(
                bool(mask & source_mask) and bool(mask & text_payload_mask) for mask in masks),
            'source_and_candidate_ppu_control_bytes': sum(
                bool(mask & source_mask) and bool(mask & ppu_control_mask) for mask in masks),
            'source_and_candidate_ppu_payload_bytes': sum(
                bool(mask & source_mask) and bool(mask & ppu_payload_mask) for mask in masks),
            'observed_and_candidate_audio_bytes': sum(bool(mask & observed_audio_mask)
                                                      and bool(mask & candidate_audio_mask) for mask in masks),
            'observed_and_static_sprite_bytes': sum(bool(mask & observed_sprite_mask)
                                                     and bool(mask & static_sprite_mask) for mask in masks),
            'uncatalogued_spans': unknown}


def script_graph_spans(graphs: list[dict]) -> list[tuple[int, int]]:
    """Collect script and inline-table extents from all candidate graphs."""
    spans = []
    for graph in graphs:
        if graph['unprocessed']:
            raise ValueError('candidate script graph is incomplete')
        for node in graph['nodes']:
            location, length = node['location'], node.get('length', 0)
            if length and location['bank_offset'] + length <= BANK_SIZE:
                spans.append((location['physical_prg_offset'], length))
            for key in ('lookup_records', 'jump_records'):
                for record in node.get(key, []):
                    location, length = record['location'], record.get('size', 2)
                    if length and location['bank_offset'] + length <= BANK_SIZE:
                        spans.append((location['physical_prg_offset'], length))
    return spans


def record_spans(references: list[dict]) -> list[tuple[int, int]]:
    """Collect only the physical fields used by candidate records."""
    spans = []
    for reference in references:
        if reference['status'] == 'candidate':
            start = reference['location']['physical_prg_offset']
            spans.extend((start + offset, 1) for offset in slot_record_flow.record_used_offsets(reference))
    return spans


def expansion_counts(baseline: list[tuple[int, int]], expanded: list[tuple[int, int]]) -> dict:
    """Compare physical-byte sets; neither set establishes execution."""
    def offsets(spans: list[tuple[int, int]]) -> set[int]:
        result = set()
        for start, length in spans:
            if (type(start) is not int or type(length) is not int or start < 0 or length <= 0
                    or start + length > 2 * BANK_SIZE
                    or start // BANK_SIZE != (start + length - 1) // BANK_SIZE):
                raise ValueError('invalid conditional expansion span')
            result.update(range(start, start + length))
        return result

    before, after = offsets(baseline), offsets(expanded)
    if not before <= after:
        raise ValueError('conditional graph expansion lost baseline bytes')
    return {'baseline_bytes': len(before), 'expanded_bytes': len(after),
            'added_bytes': len(after - before)}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def palette_setup_spans(pointers: bytes, *, sprite: bool, bank_size: int = BANK_SIZE) -> list[tuple[int, int]]:
    """Candidate bank-0 bytes read when the selected palette stream is installed."""
    if not pointers or len(pointers) % 2 or type(bank_size) is not int or bank_size <= 0:
        raise ValueError('invalid palette pointer table')
    spans = []
    for index in range(0, len(pointers), 2):
        start = int.from_bytes(pointers[index:index + 2], 'little') - 0x8000
        if start < 0 or start + 19 > bank_size:
            raise ValueError('palette setup crosses a physical bank or is not a ROM pointer')
        # Both paths read the three-byte header. The sprite path skips the
        # shared background colour at offset 3 and copies the next 15 bytes.
        spans.append((start, 3))
        spans.append((start + (4 if sprite else 3), 15 if sprite else 16))
    return spans


def palette_script_spans(source: str, regions: list[dict]) -> list[tuple[int, int]]:
    """Find named literal palette starts in BOGUS source, retaining mapping uncertainty.

    $FFFF selects the state table and $0000 resolves a dynamic per-slot pair;
    neither is a literal ROM pointer. Each named start must correspond to a
    source-owned bank-0 header. This does not prove the script path executes.
    """
    line_pattern = re.compile(r'^\s*BogusSet(Background|Sprite)PalettePointer\s+(\S+)')
    label_pattern = re.compile(r'^Bank0::PaletteHeader([0-9A-F]{4})$')
    spans = []
    for line in source.splitlines():
        match = line_pattern.match(line.split(';', 1)[0])
        if not match:
            continue
        kind, operand = match.groups()
        if operand in ('$FFFF', '$0000'):
            continue
        label = label_pattern.fullmatch(operand)
        if not label:
            raise ValueError('palette script pointer is neither a known dynamic form nor a named header')
        address = int(label.group(1), 16)
        matching = [region for region in regions if region['bank'] == 0 and region['kind'] == 'data'
                    and int(region['cpu'], 0) == address and region['size'] == 3
                    and region['id'] == f'bank0-palette-header-{address:04x}']
        if len(matching) != 1:
            raise ValueError('palette script pointer does not identify a source-owned header')
        spans.extend(palette_setup_spans(address.to_bytes(2, 'little'), sprite=(kind == 'Sprite')))
    return spans


def _optional_trace(path: Path, script: Path, reference: str, core: str) -> dict | None:
    if path.is_symlink():
        raise ValueError('refusing a symlinked trace')
    if not path.exists():
        return None
    trace = json.loads(path.read_text())
    if (trace.get('reference_sha256') != reference or trace.get('script_sha256') != _digest(script)
            or trace.get('emulator_core_sha256') != core
            or set(trace.get('results', {})) != {'noah', 'moses', 'david'}):
        raise ValueError(f'trace identity or scenarios do not match: {path.name}')
    return trace


def inventory(root: Path = ROOT) -> dict:
    """Combine the matching source map with independently validated data uses."""
    if root.resolve() != ROOT.resolve():
        raise ValueError('inventory currently requires the project workspace')
    inventory_inputs = {name: _digest(root / name) for name in INVENTORY_INPUTS}
    target, bank0, bank1, lengths = load_audited_banks()
    build_proof = root / 'build/us-v1.5/proof.json'
    build_proof_sha256 = _digest(build_proof)
    verified = verify_primary(root, target)
    reference = target['reference']['file']['sha256']
    config = json.loads((root / 'config/source-us-v1.5.json').read_text())
    regions = source_regions(config, target['reference']['prg']['offset'])
    spans: dict[str, list[tuple[int, int]]] = {key: [] for key in CATEGORIES}
    for region in regions:
        start = region['bank'] * BANK_SIZE + int(region['cpu'], 0) - 0x8000
        spans['source_' + region['kind']].append((start, region['size']))

    maps = map_data.inventory(bank0, bank1)
    spans['candidate_map_chunks'] = [(x['location']['physical_prg_offset'], map_data.CHUNK_SIZE)
                                     for x in maps['chunks']]
    spans['candidate_map_layouts'] = [(x['location']['physical_prg_offset'], x['decoded']['size'])
                                      for x in maps['layouts']]
    spans['candidate_map_header_bytes'] = [(x['location']['physical_prg_offset'], 2)
                                           for x in maps['layouts']]
    spans['candidate_map_grid_bytes'] = [(x['location']['physical_prg_offset'] + 2, x['decoded']['size'] - 2)
                                         for x in maps['layouts'] if x['decoded']['size'] > 2]
    spans['candidate_unreferenced_map_slots'] = [
        (x['location']['physical_prg_offset'], x['size'])
        for x in maps['unreferenced_aligned_chunk_slots']]
    records = packed_text.decode_records(bank1, packed_text.TABLE_OFFSET, packed_text.RECORD_COUNT,
                                         packed_text.DATA_END,
                                         bank1[packed_text.PRIMARY_OFFSET:packed_text.PRIMARY_OFFSET + 32],
                                         bank1[packed_text.SECONDARY_OFFSET:packed_text.SECONDARY_OFFSET + 32])
    spans['packed_text_records'] = [(BANK_SIZE + x['bank_offset'], x['size']) for x in records]
    spans['packed_text_header_bytes'] = [(BANK_SIZE + x['bank_offset'], 2) for x in records]
    spans['packed_text_payload_bytes'] = [(BANK_SIZE + x['bank_offset'] + 2, x['size'] - 2) for x in records]
    # State-selected streams and the candidate $FD05 sprite-palette table.
    # The reader executes in bank 0; other mapping or callers remain possible.
    spans['candidate_palette_setup_bytes'] = (
        palette_setup_spans(bank0[0x2394:0x23c0], sprite=False)
        + palette_setup_spans(bank0[0x23c0:0x23ec], sprite=True)
        + palette_setup_spans(bank1[0x7ced:0x7cf7], sprite=True))

    descriptors = descriptor_inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
    events = native_event_flow.inventory_events(bank0, bank1, lengths, descriptors['records'],
                                                 indexed_jumps=PRIMARY_INDEXED_JUMPS)
    flow = events['flow']
    graph = flow['merged_script_flow']
    source = (root / config['source']).read_text()
    spans['candidate_palette_setup_bytes'] += palette_script_spans(source, regions)
    direct_seeds = direct_record_flow.source_script_seeds(source, config['regions'])
    direct_graph = walk(bank0, bank1, lengths, direct_seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS,
                        limit=65536)
    if flow['unprocessed_contexts'] or graph['unprocessed'] or direct_graph['unprocessed']:
        raise ValueError('candidate script context inventory is incomplete')
    direct = direct_record_flow.direct_inventory(bank0, bank1, direct_graph)
    spans['candidate_script_bytes'] = script_graph_spans([graph, direct_graph])
    candidate_references = events['event_records'] + flow['references'] + direct['references']
    spans['candidate_record_bytes'] = record_spans(candidate_references)

    # Compare the widened graph with the same candidate roots and the three
    # observed indices only. Roots and baseline edges are still candidates;
    # membership in either graph does not establish actual execution.
    indexed_jump = PRIMARY_INDEXED_JUMPS[0x7434]
    if not isinstance(indexed_jump, ConditionalIndexedJump):
        raise ValueError('expected conditional indexed jump configuration')
    baseline_indexed = dict(PRIMARY_INDEXED_JUMPS)
    baseline_indexed[0x7434] = indexed_jump.observed
    baseline_events = native_event_flow.inventory_events(bank0, bank1, lengths, descriptors['records'],
                                                          indexed_jumps=baseline_indexed)
    baseline_flow = baseline_events['flow']
    baseline_graph = baseline_flow['merged_script_flow']
    baseline_direct_graph = walk(bank0, bank1, lengths, direct_seeds, indexed_jumps=baseline_indexed,
                                 limit=65536)
    if baseline_flow['unprocessed_contexts'] or baseline_graph['unprocessed'] or baseline_direct_graph['unprocessed']:
        raise ValueError('baseline candidate script context inventory is incomplete')
    baseline_direct = direct_record_flow.direct_inventory(bank0, bank1, baseline_direct_graph)
    baseline_records = (baseline_events['event_records'] + baseline_flow['references']
                        + baseline_direct['references'])
    conditional_expansion = {
        'script_bytes': expansion_counts(script_graph_spans([baseline_graph, baseline_direct_graph]),
                                         spans['candidate_script_bytes']),
        'record_field_bytes': expansion_counts(record_spans(baseline_records), spans['candidate_record_bytes']),
        'interpretation': 'Added bytes are relative to the observed-index candidate baseline; '
                          'neither baseline nor expansion proves execution. Shared candidate roots '
                          'can hide paths that also depend on the predecessor condition.'}

    sprite_pointers = sprite_metadata.resource_pointer_candidates(descriptors['records'], candidate_references)
    sprite_candidates = sprite_metadata.inventory_candidates(bank0, sprite_pointers['rom_pointers'])
    spans['candidate_sprite_static_bytes'] = sprite_candidates['spans']

    audio_graph = audio_flow.walk(bank0, bank1, audio_flow.literal_seeds(source))
    if audio_graph['unprocessed']:
        raise ValueError('candidate audio flow reached its node limit')
    spans['candidate_audio_commands'] = [(node['location']['physical_prg_offset'], node['length'])
                                          for node in audio_graph['nodes'] if 'length' in node]
    ppu_graph = ppu_streams.inventory(bank0, bank1, ppu_streams.literal_seeds(source, bank1))
    spans['candidate_ppu_stream_bytes'] = [(stream['location']['physical_prg_offset'], stream['size'])
                                           for stream in ppu_graph['streams']]
    for stream in ppu_graph['streams']:
        start = stream['location']['physical_prg_offset']
        for segment in stream['segments']:
            category = ('candidate_ppu_payload_bytes' if segment['kind'] == 'payload'
                        else 'candidate_ppu_control_bytes')
            spans[category].append((start + segment['offset'], segment['size']))

    analysis_root = root / 'analysis'
    analysis = analysis_root / 'us-v1.5'
    if (analysis_root.is_symlink() or analysis.is_symlink()
            or not analysis.resolve().is_relative_to(analysis_root.resolve())):
        raise ValueError('refusing a symlinked analysis directory')
    core = spec(root)['core_sha256']
    trace_specs = (('audio', analysis / 'audio-sweep.json', root / 'tools/mesen_audio.lua'),
                   ('sprite', analysis / 'sprite-exploration.json', root / 'tools/mesen_sprites.lua'))
    traces = {}
    trace_hashes = {}
    for name, path, script in trace_specs:
        trace = _optional_trace(path, script, reference, core)
        if trace is not None:
            traces[name] = trace
            trace_hashes[name] = _digest(path)
    if 'audio' in traces:
        for result in traces['audio']['results'].values():
            if (type(result.get('count')) is not int or result['count'] <= 0
                    or result.get('crossings') != 0 or result['count'] != sum(result['reads'].values())):
                raise ValueError('audio trace totals are incomplete')
        audio = audio_commands.inventory_observed(traces['audio'], bank0, bank1)
        spans['observed_audio_commands'] = [(x['physical_prg_offset'], x['command']['size'])
                                             for x in audio['commands']]
    crossing_sprite_offsets = 0
    if 'sprite' in traces:
        sprites = sprite_metadata.inventory_observed(traces['sprite'], bank0, bank1)
        spans['candidate_sprite_bytes'].extend((x['physical_prg_offset'], 2)
                                                for x in sprites['header'] + sprites['frame'])
        for frame in sprites['frame']:
            start = frame['physical_prg_offset']
            for offset in frame['decoded']['tile_read_offsets']:
                if start % BANK_SIZE + offset >= BANK_SIZE:
                    crossing_sprite_offsets += 1
                else:
                    spans['candidate_sprite_bytes'].append((start + offset, 1))

    summary = summarize(spans)
    rom_path = input_path(root, target, os.environ.get('BADP_ROM') or None)
    if (_digest(rom_path) != reference or _digest(root / config['source']) != verified['source_sha256']
            or _digest(root / 'config/source-us-v1.5.json') != verified['source_map_sha256']
            or _digest(build_proof) != build_proof_sha256
            or {name: _digest(root / name) for name in INVENTORY_INPUTS} != inventory_inputs):
        raise ValueError('reference or source inputs changed during inventory')
    for name, path, script in trace_specs:
        if name in trace_hashes and (_digest(path) != trace_hashes[name]
                                     or _digest(script) != traces[name]['script_sha256']):
            raise ValueError('trace changed during inventory')
    summary.update({'schema_version': 1, 'target': 'us-v1.5', 'reference_sha256': reference,
                    'source_sha256': verified['source_sha256'],
                    'source_map_sha256': verified['source_map_sha256'],
                    'build_proof_sha256': build_proof_sha256, 'inventory_input_sha256': inventory_inputs,
                    'optional_traces': {name: trace_hashes.get(name) for name, _, _ in trace_specs},
                    'sprite_offsets_crossing_bank': crossing_sprite_offsets,
                    'direct_script_overlap_bytes': direct_graph['overlapping_physical_bytes'],
                    'direct_record_script_overlap_bytes': direct['record_script_overlaps']['physical_bytes'],
                    'conditional_index_expansion': conditional_expansion,
                    'direct_dynamic_slot_pointers': len(direct['dynamic_slot_pointer_commands']),
                    'candidate_contact_records': sum(r['command'] == 'native_contact' for r in events['event_records']),
                    'candidate_position_event_records': sum(r['command'] == 'native_position' for r in events['event_records']),
                    'candidate_controller_event_records': sum(
                        r['command'] in ('native_controller24', 'native_controller2d', 'native_configured36', 'native_direction36')
                        for r in events['event_records']),
                    'native_event_rounds': events['rounds'],
                    'direct_incomplete_observed_indexed_jumps': sum(
                        n['status'] == 'observed_indexed_jump_incomplete' for n in direct_graph['nodes']),
                    'direct_incomplete_predecessor_indexed_jumps': sum(
                        n['status'] == 'predecessor_indexed_jump_incomplete' for n in direct_graph['nodes']),
                    'static_sprite_resource_count': len(sprite_candidates['resources']),
                    'static_sprite_frame_count': len(sprite_candidates['frames']),
                    'static_sprite_crossings': len(sprite_candidates['crossings']),
                    'static_sprite_non_rom_resources': len(sprite_pointers['non_rom_pointers']),
                    'static_sprite_non_rom_frames': len(sprite_candidates['non_rom_frames']),
                    'audio_fetches_crossing_bank': audio_graph['crossing_fetches'],
                    'audio_overlapping_decode_bytes': audio_graph['overlapping_decode_bytes'],
                    'ppu_lookahead_crossing_streams': ppu_graph['lookahead_crossing_streams'],
                    'ppu_overlapping_stream_bytes': ppu_graph['overlapping_stream_bytes'],
                    'interpretation': 'Overlapping evidence is retained; uncatalogued does not mean code. '
                                      'Candidate scripts and records include descriptor, native-event and direct-target paths; '
                                      'fixed controller events cover observed descriptors 1 and 9; configured 36 covers descriptor 1; audio paths use literal starts. '
                                      'Audio and PPU streams may be unreachable or incomplete; '
                                      'Candidate map, sprite and palette ranges do not prove exclusive data use; '
                                      'static sprite frame indices and resource contexts may be unreachable.'})
    return summary


def main() -> int:
    try:
        result = inventory()
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/prg-inventory.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': result['target'], 'category_bytes': result['category_bytes'],
                          'uncatalogued_bytes': result['uncatalogued_bytes'],
                          'source_and_candidate_data_bytes': result['source_and_candidate_data_bytes'],
                          'map_and_candidate_script_bytes': result['map_and_candidate_script_bytes'],
                          'unreferenced_map_slot_and_candidate_script_bytes': result['unreferenced_map_slot_and_candidate_script_bytes'],
                          'record_and_candidate_script_bytes': result['record_and_candidate_script_bytes'],
                          'source_and_candidate_map_header_bytes': result['source_and_candidate_map_header_bytes'],
                          'source_and_candidate_map_grid_bytes': result['source_and_candidate_map_grid_bytes'],
                          'source_and_packed_text_header_bytes': result['source_and_packed_text_header_bytes'],
                          'source_and_packed_text_payload_bytes': result['source_and_packed_text_payload_bytes'],
                          'source_and_candidate_ppu_control_bytes': result['source_and_candidate_ppu_control_bytes'],
                          'source_and_candidate_ppu_payload_bytes': result['source_and_candidate_ppu_payload_bytes'],
                          'observed_and_candidate_audio_bytes': result['observed_and_candidate_audio_bytes'],
                          'observed_and_static_sprite_bytes': result['observed_and_static_sprite_bytes'],
                          'direct_script_overlap_bytes': result['direct_script_overlap_bytes'],
                          'direct_record_script_overlap_bytes': result['direct_record_script_overlap_bytes'],
                          'conditional_index_expansion': result['conditional_index_expansion'],
                          'direct_dynamic_slot_pointers': result['direct_dynamic_slot_pointers'],
                          'candidate_contact_records': result['candidate_contact_records'],
                          'candidate_position_event_records': result['candidate_position_event_records'],
                          'candidate_controller_event_records': result['candidate_controller_event_records'],
                          'native_event_rounds': result['native_event_rounds'],
                          'direct_incomplete_observed_indexed_jumps': result['direct_incomplete_observed_indexed_jumps'],
                          'direct_incomplete_predecessor_indexed_jumps': result['direct_incomplete_predecessor_indexed_jumps'],
                          'static_sprite_resource_count': result['static_sprite_resource_count'],
                          'static_sprite_frame_count': result['static_sprite_frame_count'],
                          'static_sprite_crossings': result['static_sprite_crossings'],
                          'static_sprite_non_rom_resources': result['static_sprite_non_rom_resources'],
                          'static_sprite_non_rom_frames': result['static_sprite_non_rom_frames'],
                          'optional_traces_present': [k for k, v in result['optional_traces'].items() if v],
                          'output': 'analysis/us-v1.5/prg-inventory.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'PRG inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
