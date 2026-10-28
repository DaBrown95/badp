"""Inventory direct script-record targets and possible script overlaps.

All outputs are candidate interpretations. A reachable opcode can inherit any
untracked $57 mode; the four represented modes are field-selection classes,
not claims that those values occur at a particular command.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from .progress import verify_primary
from .project import load_target
from .script_entries import ROOT, load_audited_banks
from .script_flow import PRIMARY_INDEXED_JUMPS, walk
from .slot_record_flow import DIRECT_MODE_CLASSES, record_script_overlaps, resolve_access

LABEL = re.compile(r'^(?:[A-Za-z]*Script|Script|Candidate)([0-9A-F]{4}):', re.MULTILINE)


def source_script_seeds(source: str, regions: list[dict]) -> list[int]:
    """Find explicitly named bank-1 script entries within owned data regions."""
    if source.count('.scope Bank1') != 1:
        raise ValueError('expected one bank-1 scope')
    bank_scope = source.split('.scope Bank1', 1)[1]
    if '.endscope' not in bank_scope:
        raise ValueError('unterminated bank-1 scope')
    bank_source = bank_scope.split('.endscope', 1)[0]
    seeds = []
    for match in LABEL.finditer(bank_source):
        cpu = int(match.group(1), 16)
        if not 0x8000 <= cpu <= 0xffff:
            raise ValueError('invalid bank-1 script label')
        if not any(r['bank'] == 1 and r['kind'] == 'data'
                   and int(r['cpu'], 0) <= cpu < int(r['cpu'], 0) + r['size']
                   for r in regions):
            raise ValueError('script label outside an owned data region')
        seeds.append(cpu - 0x8000)
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError('missing or duplicate script labels')
    return sorted(seeds)


def direct_inventory(bank0: bytes, bank1: bytes, graph: dict) -> dict:
    """Resolve direct opcode-$16 targets for each representative mode."""
    references = []
    dynamic = []
    for node in graph['nodes']:
        if node['opcode'] != 0x16 or len(node.get('operands', [])) != 2:
            continue
        pointer = node['operands'][0] | (node['operands'][1] << 8)
        if pointer == 0:
            dynamic.append(node['encoded_pointer'])
            continue
        for mode, mode_class in DIRECT_MODE_CLASSES:
            access = resolve_access(bank0, bank1, pointer, 0, mode)
            access.update({'command': node['encoded_pointer'], 'base': None,
                           'addressing': 'direct', 'mode_class': mode_class})
            references.append(access)
    return {'references': references, 'dynamic_slot_pointer_commands': sorted(dynamic),
            'record_script_overlaps': record_script_overlaps(references, graph)}


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        proof = verify_primary(ROOT, target)
        source_path = ROOT / 'src/us-v1.5/rom.s'
        source = source_path.read_text()
        regions = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())['regions']
        seeds = source_script_seeds(source, regions)
        graph = walk(bank0, bank1, lengths, seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS,
                     limit=25000)
        if graph['unprocessed']:
            raise ValueError('script graph reached its node limit')
        result = direct_inventory(bank0, bank1, graph)
        result.update(target='us-v1.5', reference_sha256=target['reference']['file']['sha256'],
                      source_sha256=proof['source_sha256'], seed_count=len(seeds),
                      candidate_nodes=len(graph['nodes']),
                      incomplete_observed_indexed_jumps=sum(
                          n['status'] == 'observed_indexed_jump_incomplete' for n in graph['nodes']),
                      script_graph=graph,
                      interpretation='candidate direct targets and mode classes, not proven reachability')
        if verify_primary(ROOT, target) != proof:
            raise ValueError('verified build changed during inventory')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/direct-record-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'seeds': len(seeds), 'candidate_nodes': len(graph['nodes']),
                          'script_overlap_bytes': graph['overlapping_physical_bytes'],
                          'direct_commands': len(result['references']) // 4,
                          'distinct_records': len({r['encoded_pointer'] for r in result['references']}),
                          'dynamic_slot_pointers': len(result['dynamic_slot_pointer_commands']),
                          'incomplete_observed_indexed_jumps': result['incomplete_observed_indexed_jumps'],
                          'record_script_overlap_bytes': result['record_script_overlaps']['physical_bytes'],
                          'output': 'analysis/us-v1.5/direct-record-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'direct record inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
