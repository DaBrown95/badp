"""Inventory possible descriptor contact records and their script paths.

Slot initialization sets $0790 to $FF; the native contact marker requests
record offset $09 only when bit 0 is clear.  This model selects descriptor
scripts with a candidate literal opcode-$30 clear of that bit. It does not
establish that the slot is active, the clear executes, or contact occurs, and
it does not cover other ways that the flag may change.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from .script_entries import (DESCRIPTORS, DESCRIPTOR_COUNT, ROOT, inventory,
                             load_audited_banks)
from .script_flow import PRIMARY_INDEXED_JUMPS, walk
from .slot_record_flow import record_script_overlaps, resolve_access, trace


def contact_candidates(bank0: bytes, bank1: bytes, lengths: bytes, records: list[dict],
                       *, indexed_jumps: dict | None = None) -> dict:
    """Find possible mode-zero contact records after a candidate flag clear."""
    cached: dict[int, dict] = {}
    references = []
    seeds = []
    for record in records:
        if record.get('status') != 'inspected' or record.get('script_status') != 'candidate':
            continue
        location = record['location']
        if location['bank'] not in (0, 1) or not 0 <= location['bank_offset'] < 0x8000:
            raise ValueError('invalid descriptor record location')
        base = location['bank_offset'] + (0x8000 if location['bank'] == 0 else 0)
        entry = int(record['encoded_script_pointer'], 16)
        if entry not in cached:
            cached[entry] = walk(bank0, bank1, lengths, [entry], indexed_jumps=indexed_jumps)
        graph = cached[entry]
        if graph['unprocessed']:
            raise ValueError('contact eligibility graph reached its node limit')
        clears = [node['encoded_pointer'] for node in graph['nodes']
                  if node['opcode'] == 0x30 and node.get('length') == 2
                  and node.get('operands') and node['operands'][0] & 1]
        if not clears:
            continue
        access = resolve_access(bank0, bank1, base, 9, 0)
        access.update({'base': f'0x{base:04x}', 'command': 'native_contact',
                       'initial_script': f'0x{entry:04x}',
                       'descriptor_indices': record['descriptor_indices'],
                       'candidate_clear_sites': clears,
                       'eligibility_graph_overlap_bytes': graph['overlapping_physical_bytes']})
        references.append(access)
        if access['status'] == 'candidate' and access['fields']['script_installable_in_zero_mode']:
            seeds.append((base, access['fields']['encoded_script_pointer']))
    return {'references': references, 'seeds': seeds}


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        descriptors = inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        candidates = contact_candidates(bank0, bank1, lengths, descriptors['records'],
                                        indexed_jumps=PRIMARY_INDEXED_JUMPS)
        flow = trace(bank0, bank1, lengths, candidates['seeds'], indexed_jumps=PRIMARY_INDEXED_JUMPS)
        if flow['unprocessed_contexts'] or flow['merged_script_flow']['unprocessed']:
            raise ValueError('contact context inventory reached its node limit')
        overlaps = record_script_overlaps(candidates['references'] + flow['references'],
                                          flow['merged_script_flow'])
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'contact_records': candidates['references'], 'flow': flow,
                  'record_script_overlaps': overlaps,
                  'interpretation': 'candidate flag-clear and contact paths; not runtime reachability or a complete event inventory'}
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/contact-record-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'candidate_contact_records': len(candidates['references']),
                          'candidate_script_seeds': len(candidates['seeds']),
                          'contexts': len(flow['contexts']),
                          'candidate_nodes': len(flow['merged_script_flow']['nodes']),
                          'script_overlap_bytes': flow['merged_script_flow']['overlapping_physical_bytes'],
                          'record_script_overlap_bytes': overlaps['physical_bytes'],
                          'output': 'analysis/us-v1.5/contact-record-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'contact record inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
