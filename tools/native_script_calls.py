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
from .native_control_flow import inventory as native_inventory
from .progress import verify_primary
from .project import load_target
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .script_flow import PRIMARY_INDEXED_JUMPS, walk

INVENTORY_INPUTS = ('tools/native_script_calls.py', 'tools/native_control_flow.py',
                    'tools/direct_record_flow.py', 'tools/script_flow.py',
                    'tools/script_entries.py', 'tools/slot_record_flow.py')


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
        target = ((operand | 0x8000) + 1) & 0xffff
        calls.append({'script_pointer': f'0x{encoded:04x}', 'origin_bank': bank,
                      'origin_cpu': f'0x{cpu:04x}', 'encoded_operand': f'0x{operand:04x}',
                      'target_cpu': f'0x{target:04x}',
                      'selection': 'secondary_write' if operand < 0x8000 else 'current_mapping',
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
    for row in calls:
        cpu = int(row['target_cpu'], 0)
        row['origin'] = lookup[(row['origin_bank'], int(row['origin_cpu'], 0))]
        row['bank0_target'] = lookup[(0, cpu)]
        row['bank1_target'] = lookup[(1, cpu)]
    return {'candidate_calls': calls, 'count': len(calls),
            'interpretation': 'Candidate graph decodes and physical-bank alternatives only. Span starts '
                              'refer to code-owned debug spans, not proven instruction boundaries. '
                              'Mapper state, call return and runtime reachability are not established.'}


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
