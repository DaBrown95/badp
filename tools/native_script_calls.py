"""Inventory possible BOGUS native calls without assuming active mapper state.

The script graph is a conservative collection of candidate decodes, not proof
of execution. ROM data and generated results remain local.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys

from .build_rom import digest
from .direct_record_flow import source_script_seeds
from .native_control_flow import _fields, inventory as native_inventory
from .progress import verify_primary
from .project import load_target
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .script_flow import PRIMARY_INDEXED_JUMPS, walk

INVENTORY_INPUTS = ('tools/native_script_calls.py', 'tools/native_control_flow.py',
                    'tools/direct_record_flow.py', 'tools/script_flow.py',
                    'tools/script_entries.py', 'tools/slot_record_flow.py', 'tools/nes6502.py',
                    'tools/verify_native_opcodes.py')


def call_contract(operand: int) -> dict:
    """Conditional wrapper contract; neither mapper inputs nor helper return is proven.

    The pushed high byte is ORed before RTS increments the complete address.
    The low encoded form selects the secondary mapping, including $7FFF.
    A helper returning normally reaches RestoreDefaultBank before its caller.
    """
    if type(operand) is not int or not 0 <= operand <= 0xffff:
        raise ValueError('invalid encoded native-call operand')
    return {'target_cpu': f'0x{((operand | 0x8000) + 1) & 0xffff:04x}',
            'target_bank_rule': ('secondary_mapper_write' if operand < 0x8000 else 'current_mapping'),
            'normal_return_bank_rule': 'default_mapper_write',
            'requires_normal_helper_return': True}


def origin_statements(debug: str, source: str, addresses: set[tuple[int, int]]) -> dict:
    """Find the smallest source-associated span containing each candidate opcode.

    A candidate may start in an operand or asset. Only an exact three-byte
    span attached to a declared BOGUS call establishes that source form.
    Parent macro spans and incidental opcode bytes do not establish a call.
    The caller authenticates the debug geometry with native_inventory first.
    """
    files, segments, spans, lines = {}, {}, {}, defaultdict(list)
    for row in debug.splitlines():
        tag, sep, rest = row.partition('\t')
        if not sep or tag not in ('file', 'seg', 'span', 'line'):
            continue
        fields = _fields(rest)
        if tag == 'file':
            files[int(fields['id'])] = fields['name']
        elif tag == 'seg':
            segments[int(fields['id'])] = fields['name']
        elif tag == 'span':
            spans[int(fields['id'])] = (int(fields['seg']), int(fields['start'], 0), int(fields['size'], 0))
        elif 'span' in fields:
            for ident in fields['span'].split('+'):
                lines[int(ident)].append((int(fields['file']), int(fields['line'])))
    source_ids = {key for key, value in files.items() if value == 'source/rom.s'}
    source_lines = source.splitlines()
    candidates = defaultdict(list)
    for ident, (segment, offset, size) in spans.items():
        segment_name = segments.get(segment)
        if segment_name not in ('PRG0', 'PRG1'):
            continue
        bank = int(segment_name[-1])
        for origin_bank, cpu in addresses:
            if bank != origin_bank or not offset <= cpu - 0x8000 < offset + size:
                continue
            for file_id, number in lines.get(ident, []):
                if file_id not in source_ids:
                    continue
                if not 1 <= number <= len(source_lines):
                    raise ValueError('origin debug source line outside source')
                text = source_lines[number - 1].split(';', 1)[0].strip()
                if text and not text.startswith('.assert') and not text.endswith(':'):
                    candidates[(bank, cpu)].append({'line': number, 'statement': text,
                        'span_cpu': f'0x{offset + 0x8000:04x}', 'span_size': size,
                        'opcode_offset': cpu - 0x8000 - offset,
                        'declared_call': (cpu == offset + 0x8000 and size == 3
                                          and text.split(maxsplit=1)[0] in ('BogusCallNativeEncoded', 'BogusCallNativeBank1'))})
    result = {}
    for address in addresses:
        statements = candidates[address]
        calls = [row for row in statements if row['declared_call']]
        selected = calls or [row for row in statements
                             if row['span_size'] == min((s['span_size'] for s in statements), default=0)]
        unique = {json.dumps(row, sort_keys=True): row for row in selected}
        result[address] = {'classification': ('declared_bogus_call' if calls else
                          'inside_other_source_statement' if statements else 'no_named_source_statement'),
                          'statements': sorted(unique.values(), key=lambda row: (row['line'], row['span_size']))}
    return result


def inventory(graph: dict, bank0: bytes, bank1: bytes, debug: str, source: str,
              regions: list[dict]) -> dict:
    """Classify source and both physical targets for each candidate $9B call."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    if (not isinstance(graph.get('unprocessed'), list) or graph['unprocessed']
            or not isinstance(graph.get('nodes'), list)):
        raise ValueError('incomplete candidate script graph')
    parents: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for node in graph['nodes']:
        for edge in node.get('successors', []):
            target = edge.get('target') or edge.get('encoded_pointer') or edge.get('pointer')
            if target:
                parents[target].add((node['encoded_pointer'], edge['kind']))
    calls = []
    seen = set()
    for node in graph['nodes']:
        if node.get('opcode') != 0x9b:
            continue
        encoded = int(node['encoded_pointer'], 0)
        location = node['location']
        bank = 0 if encoded >= 0x8000 else 1
        cpu = encoded if bank == 0 else encoded + 0x8000
        offset = cpu - 0x8000
        if (encoded in seen or not 0 <= encoded <= 0xffff or location['bank'] != bank
                or int(location['cpu_address'], 0) != cpu or location['bank_offset'] != offset
                or location['physical_prg_offset'] != bank * BANK_SIZE + offset or offset + 3 > BANK_SIZE
                or node.get('length') != 3 or len(node.get('operands', [])) != 2):
            raise ValueError('invalid or incomplete native-call candidate')
        seen.add(encoded)
        raw = (bank0, bank1)[bank][offset:offset + 3]
        if raw != bytes([0x9b, *node['operands']]):
            raise ValueError('native-call candidate disagrees with the audited PRG')
        operand = raw[1] | raw[2] << 8
        # The wrapper sets bit 7 of the high byte, pushes the address and
        # executes RTS. Increment after the OR, including the $FFFF wrap.
        contract = call_contract(operand)
        target = int(contract['target_cpu'], 0)
        calls.append({'script_pointer': f'0x{encoded:04x}', 'origin_bank': bank,
                      'origin_cpu': f'0x{cpu:04x}', 'encoded_operand': f'0x{operand:04x}',
                      'target_cpu': f'0x{target:04x}',
                      'selection': 'secondary_write' if operand < 0x8000 else 'current_mapping',
                      'conditional_wrapper_contract': contract,
                      'graph_status': node['status'],
                      'parents': [{'script_pointer': p, 'edge': k}
                                  for p, k in sorted(parents[node['encoded_pointer']])]})
    targets = {(row['origin_bank'], int(row['origin_cpu'], 0)) for row in calls}
    targets.update((bank, int(row['target_cpu'], 0)) for row in calls for bank in (0, 1))
    classified = native_inventory(debug, source, bank0 + bank1, regions,
                                  extra_targets=tuple(sorted(targets)))
    lookup = {(item['bank'], int(item['cpu'], 0)):
              {'ownership': item['ownership'], 'span_start': item['span_start']}
              for item in classified.get('extra_targets', [])}
    origins = origin_statements(debug, source, {(r['origin_bank'], int(r['origin_cpu'], 0)) for r in calls})
    boundaries = {(item['bank'], int(item['cpu'], 0)): item['instruction_start']
                  for item in classified.get('extra_targets', [])}
    for row in calls:
        row['source_origin'] = origins[(row['origin_bank'], int(row['origin_cpu'], 0))]
        cpu = int(row['target_cpu'], 0)
        row['origin'] = lookup[(row['origin_bank'], int(row['origin_cpu'], 0))]
        row['bank0_target'] = lookup[(0, cpu)]
        row['bank1_target'] = lookup[(1, cpu)]
        row['target_instruction_starts'] = {'bank0': boundaries[(0, cpu)], 'bank1': boundaries[(1, cpu)]}
    origin_counts = defaultdict(int)
    for row in calls:
        origin_counts[row['source_origin']['classification']] += 1
    return {'candidate_calls': calls, 'count': len(calls), 'source_origin_counts': dict(sorted(origin_counts.items())),
            'interpretation': 'Candidate graph decodes and physical-bank alternatives only. Span starts '
                              'are legacy debug-span classifications; target_instruction_starts uses the complete checked instruction map. '
                              'Source-origin classification distinguishes declared calls from incidental decodes, without excluding '
                              'conditional execution. Each wrapper contract states the selection and normal-return rules, '
                              'conditional on mapper inputs and an ordinary helper RTS. Actual mapper state, helper return '
                              'and runtime reachability for a candidate are not established.'}


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest(proof_path.read_bytes())
        hashes = {name: digest((ROOT / name).read_bytes()) for name in INVENTORY_INPUTS}
        source_path = ROOT / 'src/us-v1.5/rom.s'
        source = source_path.read_text()
        regions = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())['regions']
        debug_path = ROOT / 'build/us-v1.5/bible-adventures.dbg'
        debug_bytes = debug_path.read_bytes()
        debug = debug_bytes.decode('utf-8')
        seeds = source_script_seeds(source, regions)
        graph = walk(bank0, bank1, lengths, seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS, limit=65536)
        result = inventory(graph, bank0, bank1, debug, source, regions)
        if (verify_primary(ROOT, target) != proof
                or digest(proof_path.read_bytes()) != proof_hash
                or digest(debug_path.read_bytes()) != digest(debug_bytes)
                or hashes != {name: digest((ROOT / name).read_bytes()) for name in INVENTORY_INPUTS}):
            raise ValueError('verified build changed during native-call inventory')
        result.update(target='us-v1.5', reference_sha256=target['reference']['file']['sha256'],
                      source_sha256=proof['source_sha256'], debug_sha256=digest(debug_bytes),
                      source_map_sha256=proof['source_map_sha256'], build_proof_sha256=proof_hash,
                      inventory_input_sha256=hashes,
                      seed_count=len(seeds), candidate_nodes=len(graph['nodes']))
        output = ROOT / 'analysis/us-v1.5/native-script-calls.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'candidate_calls': result['count'], 'seed_count': len(seeds),
                          'output': 'analysis/us-v1.5/native-script-calls.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'native script call inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
