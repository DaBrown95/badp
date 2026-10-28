"""Bounded candidate inventory for native slot contact and position events.

A slot's script can clear a bit that gates a native event. That event may load
another record and install a later script, which may in turn clear more bits.
This fixed-point inventory preserves those candidate contexts. It does not
prove flag clears, slot survival, contact, position matches, or reachability.
Controller events are limited to an observed controlled descriptor; other
controlled descriptors, configured action values and flag writes remain open.
"""
from __future__ import annotations

import json
import sys

from .script_entries import DESCRIPTORS, DESCRIPTOR_COUNT, ROOT, inventory, load_audited_banks
from .script_flow import PRIMARY_INDEXED_JUMPS, walk
from .slot_record_flow import record_script_overlaps, resolve_access, trace

# Controller actions are restricted to descriptor $01, observed in the
# opening-gameplay and inventory traces. The $36 entry models the observed
# configured action (gate $20), not every possible value of $15/$16.
CONTROLLED_DESCRIPTORS = frozenset({1})
EVENTS = (('contact', 9, 1, False), ('position', 27, 4, False),
          ('controller24', 36, 8, True), ('controller2d', 45, 16, True),
          ('configured36', 54, 32, True))


def inventory_events(bank0: bytes, bank1: bytes, lengths: bytes, records: list[dict],
                     *, indexed_jumps: dict | None = None, limit: int = 10000,
                     max_rounds: int = 32) -> dict:
    """Expand possible event records from descriptor-associated script contexts."""
    if type(limit) is not int or limit <= 0 or type(max_rounds) is not int or max_rounds <= 0:
        raise ValueError('invalid native event inventory limit')
    seeds: set[tuple[int, int]] = set()
    controlled_bases: set[int] = set()
    for record in records:
        if record.get('status') != 'inspected' or record.get('script_status') != 'candidate':
            continue
        loc = record['location']
        if loc['bank'] not in (0, 1) or not 0 <= loc['bank_offset'] < 0x8000:
            raise ValueError('invalid descriptor record location')
        base = loc['bank_offset'] + (0x8000 if loc['bank'] == 0 else 0)
        seeds.add((base, int(record['encoded_script_pointer'], 16)))
        if CONTROLLED_DESCRIPTORS.intersection(record['descriptor_indices']):
            controlled_bases.add(base)
    cache: dict[int, dict] = {}
    events: dict[tuple[str, int], dict] = {}
    for round_number in range(1, max_rounds + 1):
        flow = trace(bank0, bank1, lengths, sorted(seeds), indexed_jumps=indexed_jumps, limit=limit)
        if flow['unprocessed_contexts'] or flow['merged_script_flow']['unprocessed']:
            raise ValueError('native event context inventory reached its node limit')
        previous = len(seeds)
        for context in flow['contexts']:
            base, entry = int(context['base'], 16), int(context['entry'], 16)
            if entry not in cache:
                cache[entry] = walk(bank0, bank1, lengths, [entry], indexed_jumps=indexed_jumps)
            graph = cache[entry]
            if graph['unprocessed']:
                raise ValueError('native event eligibility graph reached its node limit')
            for name, offset, mask, controlled in EVENTS:
                if controlled and base not in controlled_bases:
                    continue
                clears = sorted(node['encoded_pointer'] for node in graph['nodes']
                                if node['opcode'] == 0x30 and node.get('length') == 2
                                and node.get('operands') and node['operands'][0] & mask)
                if not clears:
                    continue
                key = (name, base)
                if key not in events:
                    ref = resolve_access(bank0, bank1, base, offset, 0)
                    ref.update({'base': f'0x{base:04x}', 'command': f'native_{name}', 'support': []})
                    events[key] = ref
                ref = events[key]
                support = {'entry': f'0x{entry:04x}', 'candidate_clear_sites': clears,
                           'eligibility_graph_overlap_bytes': graph['overlapping_physical_bytes']}
                if support not in ref['support']:
                    ref['support'].append(support)
                if ref['status'] == 'candidate' and ref['fields']['script_installable_in_zero_mode']:
                    seeds.add((base, ref['fields']['encoded_script_pointer']))
        if len(seeds) == previous:
            references = [events[key] for key in sorted(events)]
            overlaps = record_script_overlaps(references + flow['references'], flow['merged_script_flow'])
            return {'event_records': references, 'flow': flow, 'rounds': round_number,
                    'record_script_overlaps': overlaps}
    raise ValueError('native event inventory did not reach a fixed point')


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        descriptors = inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        result = inventory_events(bank0, bank1, lengths, descriptors['records'],
                                  indexed_jumps=PRIMARY_INDEXED_JUMPS)
        result.update({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                       'interpretation': 'candidate native-event paths; controller scope is observed descriptor 1 only, and other flag writes remain open'})
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/native-event-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        graph = result['flow']['merged_script_flow']
        print(json.dumps({'candidate_contact_records': sum(r['command'] == 'native_contact' for r in result['event_records']),
                          'candidate_position_records': sum(r['command'] == 'native_position' for r in result['event_records']),
                          'candidate_controller_records': sum(r['command'] in ('native_controller24', 'native_controller2d', 'native_configured36') for r in result['event_records']),
                          'contexts': len(result['flow']['contexts']), 'candidate_nodes': len(graph['nodes']),
                          'script_overlap_bytes': graph['overlapping_physical_bytes'],
                          'record_script_overlap_bytes': result['record_script_overlaps']['physical_bytes'],
                          'rounds': result['rounds'], 'output': 'analysis/us-v1.5/native-event-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'native event inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
