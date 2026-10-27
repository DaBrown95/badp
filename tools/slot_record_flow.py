"""Trace candidate slot-record accesses in a descriptor/script context.

This is a conservative inventory of possible static paths, not proof of slot
identity or runtime reachability. Records and any game bytes stay local.
"""
from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import sys

from .script_entries import (BANK_SIZE, DESCRIPTORS, DESCRIPTOR_COUNT, ROOT,
                             _locate, _location, decode_slot_record, inventory,
                             load_audited_banks)
from .script_flow import PRIMARY_INDEXED_JUMPS, walk


def resolve_access(bank0: bytes, bank1: bytes, base: int, offset: int, mode: int) -> dict:
    """Resolve the loader's unsigned add or subtract and bounded ten-byte fetch."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full 32 KiB banks')
    _locate(base)
    if type(offset) is not int or not 0 <= offset <= 255:
        raise ValueError('invalid record offset')
    if type(mode) is not int or not 0 <= mode <= 255:
        raise ValueError('invalid record mode')
    encoded = (base - offset if mode & 0x80 else base + offset) & 0xffff
    bank, position = _locate(encoded)
    result = {'encoded_pointer': f'0x{encoded:04x}', 'location': _location(bank, position),
              'offset': offset, 'mode': mode}
    if position + 10 > BANK_SIZE:
        result['status'] = 'fetch_crosses_bank_boundary'
        return result
    raw = (bank0, bank1)[bank][position:position + 10]
    fields = decode_slot_record(raw)
    # A negative mode uses byte 2 for flags; positive modes use byte 4.
    # Some checks skip fields entirely when a pointer's high byte is $FF.
    result['status'] = 'candidate'
    result['fields'] = fields
    result['negative_mode_flags'] = raw[2] if mode & 0x80 else None
    return result


def trace(bank0: bytes, bank1: bytes, lengths: bytes, seeds: list[tuple[int, int]],
          indexed_jumps: dict[int, int] | None = None, limit: int = 10000) -> dict:
    """Explore candidate (descriptor base, script entry) contexts with a hard limit."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full 32 KiB banks')
    if not lengths or len(lengths) > 256:
        raise ValueError('invalid command lengths')
    if type(limit) is not int or limit <= 0:
        raise ValueError('invalid context limit')
    pending: deque[tuple[int, int]] = deque()
    queued: set[tuple[int, int]] = set()
    for base, entry in seeds:
        _locate(base)
        _locate(entry)
        if (base, entry) not in queued:
            queued.add((base, entry))
            pending.append((base, entry))
    references: list[dict] = []
    contexts = []
    cached_flows: dict[int, dict] = {}
    while pending and len(contexts) < limit:
        base, entry = pending.popleft()
        flow = cached_flows.get(entry)
        if flow is None:
            flow = walk(bank0, bank1, lengths, [entry], indexed_jumps=indexed_jumps)
            cached_flows[entry] = flow
        contexts.append({'base': f'0x{base:04x}', 'entry': f'0x{entry:04x}',
                         'unprocessed_script_nodes': len(flow['unprocessed']),
                         'overlapping_script_bytes': flow['overlapping_physical_bytes']})
        for node in flow['nodes']:
            opcode, operands = node['opcode'], node.get('operands', [])
            if opcode == 0x00 and len(operands) == 1:
                offset, mode = operands[0], 0
            elif opcode == 0x63 and len(operands) == 2:
                offset, mode = operands
            else:
                continue
            access = resolve_access(bank0, bank1, base, offset, mode)
            access.update({'base': f'0x{base:04x}', 'entry': f'0x{entry:04x}',
                           'command': node['encoded_pointer'], 'opcode': opcode})
            references.append(access)
            if (access['status'] == 'candidate' and mode == 0
                    and access['fields']['script_installable_in_zero_mode']):
                successor = (base, access['fields']['encoded_script_pointer'])
                if successor not in queued:
                    queued.add(successor)
                    pending.append(successor)
    return {'contexts': contexts, 'references': references,
            'unprocessed_contexts': [{'base': f'0x{base:04x}', 'entry': f'0x{entry:04x}'}
                                     for base, entry in pending], 'context_limit': limit}


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        initial = inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        seeds = []
        for rec in initial['records']:
            if rec['status'] != 'inspected' or rec.get('script_status') != 'candidate':
                continue
            loc = rec['location']
            base = loc['bank_offset'] + (0x8000 if loc['bank'] == 0 else 0)
            seeds.append((base, int(rec['encoded_script_pointer'], 16)))
        result = trace(bank0, bank1, lengths, seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS)
        result.update({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                       'interpretation': 'possible paths and slot contexts, not proven runtime use or source ownership'})
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5' / 'slot-record-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(ROOT.resolve() / 'analysis'):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': 'us-v1.5', 'contexts': len(result['contexts']),
                          'references': len(result['references']),
                          'distinct_records': len({r['encoded_pointer'] for r in result['references']}),
                          'contexts_with_unprocessed_nodes': sum(bool(c['unprocessed_script_nodes']) for c in result['contexts']),
                          'contexts_with_overlaps': sum(bool(c['overlapping_script_bytes']) for c in result['contexts']),
                          'unprocessed_contexts': len(result['unprocessed_contexts']),
                          'output': 'analysis/us-v1.5/slot-record-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'slot-record trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
