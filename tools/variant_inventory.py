"""Review a release's actual entries and representations using shared rules."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from .build_variant_source import digest
from .direct_record_flow import source_script_seeds, direct_inventory
from .inventory_review import apply_review
from .native_control_flow import _fields
from .native_script_calls import inventory as call_inventory
from .prg_inventory import summarize, script_graph_spans
from .record_views import inventory as record_inventory
from .script_entries import DESCRIPTORS, DESCRIPTOR_COUNT, inventory as descriptor_inventory
from .script_flow import PRIMARY_INDEXED_JUMPS, walk
from .source_audit import partition
from .source_variants import load_profile
from . import audio_flow, variant_assets

INPUTS = ('tools/variant_inventory.py', 'tools/inventory_review.py', 'tools/source_audit.py',
          'tools/prg_inventory.py', 'tools/direct_record_flow.py', 'tools/native_script_calls.py',
          'tools/native_control_flow.py', 'tools/nes6502.py', 'tools/record_views.py',
          'tools/script_entries.py', 'tools/script_flow.py', 'tools/slot_record_flow.py',
          'tools/audio_flow.py', 'tools/audio_commands.py')


def audio_source_literals(source: str, debug: str) -> str:
    """Read the renderer's restricted constant expressions, not arbitrary code.

    The audio parser retains its literal-only contract. Relocated literals
    keep their original operand plus a signed layout delta in generated source.
    The one moved native audio label is resolved from the actual PRG0 debug map.
    """
    pattern = r'\(\(\$([0-9a-fA-F]{4}) \+ \((-?\d+)\)\)\)'
    def fold(match):
        value = int(match[1], 16) + int(match[2])
        if not 0 <= value <= 65535:raise ValueError('audio literal leaves its word namespace')
        return f'${value:04X}'
    source = re.sub(pattern, fold, source)
    if '#<LegacyOpcode18Audio' not in source and '#>LegacyOpcode18Audio' not in source:
        return source
    segments, scopes, symbols = {}, {}, []
    for line in debug.splitlines():
        tag, sep, rest = line.partition('\t')
        if not sep or tag not in ('seg', 'scope', 'sym'):continue
        fields = _fields(rest)
        if tag == 'seg':segments[fields['id']] = fields
        elif tag == 'scope':scopes[fields['id']] = fields
        elif fields.get('name') == 'LegacyOpcode18Audio':symbols.append(fields)
    if len(symbols) != 1:raise ValueError('missing or ambiguous moved native audio label')
    symbol = symbols[0];segment = segments.get(symbol.get('seg'), {})
    if (symbol.get('type') != 'lab' or scopes.get(symbol.get('scope'), {}).get('name') != 'Bank0'
            or segment.get('name') != 'PRG0' or int(segment.get('ooffs', '-1'), 0) != 16):
        raise ValueError('moved native audio label lacks a physical bank-0 identity')
    value = int(symbol['val'], 0)
    if not 0x8000 <= value <= 0xffff:raise ValueError('native audio label outside PRG')
    for operator, byte in (('<', value & 255), ('>', value >> 8)):
        original = '#' + operator + 'LegacyOpcode18Audio'
        if source.count(original) != 1:raise ValueError('ambiguous native audio operand')
        source = source.replace(original, f'#${byte:02X}', 1)
        source = source.replace('#' + operator + 'Bank0::LegacyOpcode18Audio', f'#${byte:02X}')
    return source


def analyze(root: Path, target: dict, proof: dict, reference: bytes) -> dict:
    profile = load_profile(root, target['id']);layout = profile['geometry']
    canonical_config = json.loads((root / profile['canonical_map']).read_text())
    source = (root / 'build' / target['id'] / 'source/rom.s').read_text()
    debug = (root / 'build' / target['id'] / 'bible-adventures.dbg').read_text()
    canonical = (root / profile['canonical_source']).read_text()
    prg = reference[16:65552];bank0, bank1 = prg[:32768], prg[32768:]
    regions = proof['regions']
    length_offset = layout.offset(0, 0x7da7)
    lengths = bank0[length_offset:length_offset + profile.get('nominal_script_entries', 197)]
    roots = [layout.offset(1, seed) for seed in source_script_seeds(canonical, canonical_config['regions'])]
    roots += [int(cpu, 0) - 32768 for cpu in profile.get('additional_script_roots', [])]
    indices = {layout.offset(1, site): value for site, value in PRIMARY_INDEXED_JUMPS.items()}
    graph = walk(bank0, bank1, lengths, roots, indexed_jumps=indices, limit=65536)
    if graph['unprocessed']:
        raise ValueError('variant script inventory has unprocessed source roots')
    calls = call_inventory(graph, bank0, bank1, debug, source, regions)
    declared_calls = [row for row in calls['candidate_calls'] if row['source_origin']['classification'] == 'declared_bogus_call']
    for row in declared_calls:
        bank = 'bank1' if row['selection'] == 'secondary_write' else 'bank0'
        if not row['target_instruction_starts'][bank]:
            raise ValueError('declared variant native call lacks its supported target boundary')
    descriptors = descriptor_inventory(bank0, bank1, layout.offset(0, DESCRIPTORS), profile.get("descriptor_count", DESCRIPTOR_COUNT), lengths)
    direct = direct_inventory(bank0, bank1, graph)
    target_map = {**canonical_config, 'target': target['id'], 'regions': regions}
    if 'loader_views' in target_map:
        target_map['loader_views'] = [{**row, 'cpu': f'0x{layout.address(row["bank"], int(row["cpu"], 0)):04x}'}
                                      for row in target_map['loader_views']]
    records = record_inventory(source, debug, target_map)
    # The primary voice overlays at E01A/E023 are record interpretations whose
    # opcode no longer agrees after resource relocation. Keep the actual record
    # view, but do not promote its old literal voice fields to target entries.
    audio_source = '\n'.join(line for line in source.splitlines()
                             if not line.strip().startswith('SlotRecordVoiceOverlay '))
    audio_source = audio_source_literals(audio_source, debug)
    audio = audio_flow.walk(bank0, bank1, audio_flow.literal_seeds(audio_source))
    if audio['unprocessed']:
        raise ValueError('variant audio inventory has unprocessed source roots')
    selected = variant_assets.select(root, prg, reference[65552:], target['reference']['file']['sha256'], profile)
    assets = variant_assets.spans(selected)
    spans = {f'source_{kind}': [(row['bank'] * 32768 + int(row['cpu'], 0) - 32768, row['size'])
                               for row in regions if row['kind'] == kind] for kind in ('code', 'data', 'fill')}
    spans['candidate_script_bytes'] = script_graph_spans([graph])
    spans['candidate_audio_commands'] = [(node['location']['physical_prg_offset'], node['length'])
                                        for node in audio['nodes'] if 'length' in node]
    spans['candidate_record_bytes'] = [(32768 + int(row['cpu'], 0) - 32768, row['size']) for row in records]
    low, high, length = (layout.offset(0, value) for value in (0x5585, 0x564a, 0x7da7))
    spans['native_dispatch_lookup_bytes'] = [(low, 256), (high, 256), (length, 256), (32768 + length, 256)]
    summary = summarize(spans)
    asset_spans = {name: [(bank * 32768 + offset, len(data)) for bank, offset, data in rows]
                   for name, rows in assets.items()}
    result = partition(summary['evidence_spans'], asset_spans)
    if result['representation_bytes'].get('unresolved_local', 0):
        raise ValueError('variant inventory contains opaque physical PRG bytes')
    result.update(target=target['id'], reference_sha256=target['reference']['file']['sha256'],
                  source_sha256=proof['source_sha256'],
                  source_map_sha256=digest(json.dumps({'target': target['id'], 'regions': regions}, sort_keys=True).encode()),
                  build_proof_sha256=digest((root / 'build' / target['id'] / 'proof.json').read_bytes()),
                  inventory_input_sha256={name: digest((root / name).read_bytes()) for name in INPUTS},
                  audit_input_sha256={},
                  script_review={'declared_roots': len(roots), 'candidate_nodes': len(graph['nodes']),
                                 'unprocessed_nodes': len(graph['unprocessed']),
                                 'statuses': dict(sorted(Counter(row['status'] for row in graph['nodes']).items())),
                                 'primary_only_aliases_not_carried_forward': profile['primary_only_candidate_aliases'],
                                 'scope': 'Actual target candidate decodes from relocated logical source roots; no ordinary reachability claim.'},
                  native_calls={'count': calls['count'], 'declared': len(declared_calls),
                                'origins': calls['source_origin_counts'],
                                'scope': 'Target operands and physical instruction starts; wrapper rules inherited from identical shared code, without transferring primary gameplay evidence.'},
                  descriptors={'count': len(descriptors['descriptors']), 'records': len(descriptors['records'])},
                  record_views={'count': len(records), 'modes': dict(Counter(row['kind'] for row in records))},
                  audio_review={'seeds': len(audio['seeds']), 'candidate_nodes': len(audio['nodes']),
                                'crossing_fetches': audio['crossing_fetches'],
                                'scope': 'Actual target bytes from supported literal starts; no primary runtime observation is imported.'},
                  conditional_contexts={'dynamic_direct_record_pointers': len(direct['dynamic_slot_pointer_commands'])},
                  interpretation='Physical representation and supported mechanisms are reviewed without requiring exclusive use. '
                                 'Counterfactual script decodes and arbitrary-state indices are not automatically new missing routines.')
    directory = root / 'analysis' / target['id']
    for name, payload in {'native-script-calls': calls, 'script-flow': graph, 'record-views': records,
                          'audio-flow': audio, 'script-entries': descriptors, 'direct-record-flow': direct}.items():
        (directory / (name + '.json')).write_text(json.dumps(payload, indent=2) + '\n')
    return result


def review(root: Path, target: dict, proof: dict, reference: bytes) -> dict:
    result = analyze(root, target, proof, reference)
    path = root / f'config/inventory-review-{target["id"]}.json'
    ledger = json.loads(path.read_text())
    result['audit_input_sha256'][path.relative_to(root).as_posix()] = digest(path.read_bytes())
    result = apply_review(result, ledger, root)
    output = root / 'analysis' / target['id'] / 'source-audit.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result
