"""Conservatively trace selected v1.5 script opcodes into local analysis.

Only explicitly reviewed handlers have successor rules. Unknown or dynamic
handlers terminate a path, and both branches of a conditional are candidates.
This is static over-approximation, not runtime reachability or owned source.
"""
from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import sys

from .script_entries import (BANK_SIZE, DESCRIPTORS, DESCRIPTOR_COUNT, ROOT,
                             _locate, _location, inventory, load_audited_banks)

# These handlers have been reviewed in src/us-v1.5/rom.s. Codes not listed
# stop the path even when their record length is known.
FALLTHROUGH = frozenset({0x06, 0x09, 0x0B, 0x0C, 0x0D, 0x0E, 0x10, 0x1A,
                         0x1C, 0x1D, 0x21, 0x26, 0x29, 0x2C, 0x2F, 0x30,
                         0x31, 0x32, 0x36, 0x3E, 0x3F, 0x42, 0x43, 0x46,
                         0x47, 0x48, 0x49, 0x4A, 0x4C, 0x4F, 0x50, 0x55,
                         0x56, 0x5C, 0x5D, 0x5E, 0x6A, 0x72, 0xAE})
CONDITIONAL_POINTER = frozenset({0x01, 0x02, 0x03, 0x05, 0x15, 0x1B, 0x20,
                                 0x22, 0x23, 0x24, 0x25, 0x27, 0x28, 0x2A, 0x2B,
                                 0x35, 0x41, 0x4B, 0x51, 0x52, 0x53, 0x5F, 0x60,
                                 0x6B, 0x82, 0x8B, 0xA3, 0xBB, 0xC2})
UNCONDITIONAL_POINTER = frozenset({0x04})
YIELD_RESUME = frozenset({0x07, 0x0F, 0x2E})
POSSIBLE_YIELD = frozenset({0x08, 0x2D, 0x81, 0x96})


def walk(bank0: bytes, bank1: bytes, lengths: bytes, seeds: list[int],
         limit: int = 10000) -> dict:
    """Explore proven local successor rules, stopping on every unknown opcode."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full 32 KiB banks')
    if not lengths or len(lengths) > 256 or type(limit) is not int or limit <= 0:
        raise ValueError('invalid command lengths or node limit')
    banks = (bank0, bank1)
    pending: deque[int] = deque()
    queued: set[int] = set()
    for seed in seeds:
        _locate(seed)
        if seed not in queued:
            queued.add(seed)
            pending.append(seed)
    nodes: dict[int, dict] = {}
    # Track physical ownership for detecting possible overlapping decodes.
    coverage: dict[tuple[int, int], set[int]] = {}
    while pending and len(nodes) < limit:
        encoded = pending.popleft()
        bank, offset = _locate(encoded)
        opcode = banks[bank][offset]
        node = {'encoded_pointer': f'0x{encoded:04x}', 'location': _location(bank, offset),
                'opcode': opcode, 'successors': []}
        nodes[encoded] = node
        if opcode >= len(lengths):
            node['status'] = 'opcode_outside_length_table'
            continue
        length = lengths[opcode]
        node['length'] = length
        if length == 0:
            node['status'] = 'zero_length'
            continue
        if offset + length > BANK_SIZE:
            node['status'] = 'crosses_bank_boundary'
            continue
        data = banks[bank][offset:offset + length]
        node['operands'] = list(data[1:])
        for pos in range(offset, offset + length):
            coverage.setdefault((bank, pos), set()).add(encoded)
        following = (encoded + length) & 0xFFFF
        edges: list[tuple[str, int]] = []
        if opcode in FALLTHROUGH:
            node['status'] = 'reviewed_fallthrough'
            edges.append(('next', following))
        elif opcode in YIELD_RESUME:
            node['status'] = 'reviewed_yield'
            edges.append(('possible_resume', following))
        elif opcode in POSSIBLE_YIELD:
            node['status'] = 'reviewed_possible_yield'
            edges.append(('next_or_possible_resume', following))
        elif opcode in CONDITIONAL_POINTER or opcode in UNCONDITIONAL_POINTER:
            if length < 3:
                node['status'] = 'missing_pointer_operands'
                continue
            target = int.from_bytes(data[1:3], 'little')
            node['status'] = ('reviewed_conditional' if opcode in CONDITIONAL_POINTER
                              else 'reviewed_jump')
            edges.append(('target', target))
            if opcode in CONDITIONAL_POINTER:
                edges.append(('fallthrough', following))
        else:
            node['status'] = 'unreviewed_or_dynamic_handler'
        for kind, target in edges:
            node['successors'].append({'kind': kind, 'encoded_pointer': f'0x{target:04x}'})
            if target not in queued:
                queued.add(target)
                pending.append(target)
    overlaps: dict[int, set[int]] = {}
    for owners in coverage.values():
        if len(owners) > 1:
            for owner in owners:
                overlaps.setdefault(owner, set()).update(owners - {owner})
    for encoded, others in overlaps.items():
        nodes[encoded]['overlaps'] = [f'0x{x:04x}' for x in sorted(others)]
    return {'nodes': list(nodes.values()), 'unprocessed': [f'0x{x:04x}' for x in pending],
            'node_limit': limit, 'overlapping_physical_bytes': sum(len(v) > 1 for v in coverage.values())}


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        initial = inventory(bank0, bank1, DESCRIPTORS, DESCRIPTOR_COUNT, lengths)
        seeds = [int(record['encoded_script_pointer'], 16) for record in initial['records']
                 if record.get('script_status') == 'candidate']
        result = walk(bank0, bank1, lengths, seeds)
        result.update({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                       'interpretation': 'candidate paths only; unknown handlers stop and conditional edges are not proven reachable',
                       'bank_assumption': 'encoded addresses below 0x8000 use bank 1; others use current bank 0'})
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5' / 'script-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(ROOT.resolve() / 'analysis'):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': 'us-v1.5', 'candidate_nodes': len(result['nodes']),
                          'unreviewed_or_dynamic': sum(n['status'] == 'unreviewed_or_dynamic_handler' for n in result['nodes']),
                          'overlapping_physical_bytes': result['overlapping_physical_bytes'],
                          'unprocessed': len(result['unprocessed']),
                          'output': 'analysis/us-v1.5/script-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'script-flow inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
