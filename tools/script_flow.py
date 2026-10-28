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
FALLTHROUGH = frozenset({0x06, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x10,
                         0x13, 0x14, 0x18, 0x1A, 0x1F,
                         0x1C, 0x1D, 0x21, 0x26, 0x29, 0x2C, 0x2F, 0x30,
                         0x31, 0x32, 0x36, 0x3B, 0x3E, 0x3F, 0x40, 0x42, 0x43, 0x46,
                         0x47, 0x48, 0x49, 0x4A, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x54, 0x55,
                         0x56, 0x5A, 0x5B, 0x5C, 0x5D, 0x5E, 0x61, 0x64, 0x65, 0x68, 0x69, 0x6A,
                         0x72, 0x76, 0x78, 0x79, 0x7A, 0x80, 0x84, 0x85, 0x86, 0x87, 0x8C, 0x8D, 0x8E, 0x8F, 0x90,
                         0x9C, 0x9D, 0xA1, 0xA2, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAC, 0xAE, 0xAF, 0xB2, 0xB3, 0xB7, 0xB8, 0xB9, 0xBA, 0xBC, 0xBD, 0xBE, 0xC0, 0xC3})
CONDITIONAL_POINTER = frozenset({0x01, 0x02, 0x03, 0x05, 0x15, 0x1B, 0x20,
                                 0x22, 0x23, 0x24, 0x25, 0x27, 0x28, 0x2A, 0x2B,
                                 0x35, 0x3D, 0x41, 0x4B, 0x51, 0x52, 0x53, 0x5F, 0x60,
                                 0x62, 0x66, 0x6B, 0x77, 0x7B, 0x82, 0x8B, 0x92, 0x93, 0x94, 0x9A,
                                 0x9E, 0x9F, 0xA0, 0xA3, 0xBB, 0xC2})
UNCONDITIONAL_POINTER = frozenset({0x04})
YIELD_RESUME = frozenset({0x07, 0x2E, 0x67, 0x6C, 0xB6})
POSSIBLE_YIELD = frozenset({0x08, 0x11, 0x12, 0x2D, 0x7D, 0x81, 0x96})
# Candidate bounds from the specific immediately preceding clamp/divide or
# mask sequences. They do not prove that no other entry reaches these opcodes.
PRIMARY_INDEXED_JUMPS = {0x362C: 11, 0x548F: 4, 0x671C: 8}


def scan_lookup_table(banks: tuple[bytes, bytes], start: int, limit: int = 256) -> dict:
    """Read $95 cases until the zero pointer, without assuming a match occurs."""
    if type(limit) is not int or limit <= 0:
        raise ValueError('invalid lookup-table limit')
    position = start
    records = []
    seen = set()
    for _ in range(limit):
        if position in seen:
            return {'records': records, 'status': 'cycle'}
        seen.add(position)
        bank, offset = _locate(position)
        # The handler fetches four bytes even when the first two are zero.
        if offset + 4 > BANK_SIZE:
            return {'records': records, 'status': 'crosses_bank_boundary'}
        data = banks[bank][offset:offset + 4]
        target = int.from_bytes(data[:2], 'little')
        if target == 0:
            records.append({'encoded_pointer': f'0x{position:04x}',
                            'location': _location(bank, offset), 'size': 2,
                            'terminator': True})
            return {'records': records, 'status': 'terminated',
                    'continuation': (position + 2) & 0xFFFF}
        records.append({'encoded_pointer': f'0x{position:04x}',
                        'location': _location(bank, offset), 'size': 4,
                        'target': target, 'slot_value': list(data[2:4])})
        position = (position + 4) & 0xFFFF
    return {'records': records, 'status': 'limit'}


def walk(bank0: bytes, bank1: bytes, lengths: bytes, seeds: list[int],
         limit: int = 10000, indexed_jumps: dict[int, int] | None = None) -> dict:
    """Explore proven local successor rules, stopping on every unknown opcode."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full 32 KiB banks')
    if not lengths or len(lengths) > 256 or type(limit) is not int or limit <= 0:
        raise ValueError('invalid command lengths or node limit')
    banks = (bank0, bank1)
    indexed_jumps = indexed_jumps if indexed_jumps is not None else {}
    if not isinstance(indexed_jumps, dict):
        raise ValueError('invalid indexed-jump bounds')
    for site, count in indexed_jumps.items():
        _locate(site)
        if type(count) is not int or not 1 <= count <= 128:
            raise ValueError('invalid indexed-jump entry count')
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
        elif opcode == 0x89 and length == 3:
            # The relative-position path preserves the main state and yields.
            # The setup path can change $00, so its later scheduling is unknown.
            node['status'] = 'reviewed_possible_relative_resume'
            edges.append(('possible_relative_resume', following))
        elif opcode == 0x17 and length == 1:
            # A saved high byte of $FF leaves the current pointer intact.
            # Other values restore a dynamic pointer that is not modeled.
            node['status'] = 'reviewed_saved_pointer_or_next'
            edges.append(('possible_next_without_saved_pointer', following))
        elif opcode == 0xAD and length == 1:
            # $0140,Y can reach the active stack page and overwrite a return.
            # Only the ordinary return is represented by this candidate edge.
            node['status'] = 'reviewed_possible_indexed_stack_write_return'
            edges.append(('possible_normal_return', following))
        elif opcode == 0x8A and length == 2:
            # A normal return preserves the script pointer. The $FF form
            # clears $0100-$011F, potentially including stack frames; a
            # corrupted return is not represented by this candidate edge.
            node['status'] = 'reviewed_possible_stack_buffer_return'
            edges.append(('possible_normal_return', following))
        elif opcode == 0x98 and length == 2:
            # It marks slots disabled and yields while switching state. If a
            # later restore re-enables this retained slot, its saved pointer can
            # resume here; that restoration and slot survival are not proven.
            node['status'] = 'reviewed_possible_state_restore_resume'
            edges.append(('possible_resume_after_restore', following))
        elif opcode in (0x0F, 0x99):
            # Later scheduling after these state changes is not established.
            node['status'] = 'reviewed_main_state_change'
        elif opcode in (0x19, 0x6D, 0x6E, 0x6F, 0xAB, 0xBF):
            # The wait path restores the prior slot pointer and yields, retrying
            # the command; the other path continues to the next command.
            node['status'] = 'reviewed_busy_retry'
            edges.extend((('possible_retry', encoded), ('possible_next', following)))
        elif opcode == 0xC4 and length == 2:
            # $C4 enters the reviewed record loader with nonzero mode $01.
            node['status'] = 'reviewed_nonzero_mode_record_load'
            edges.append(('possible_next', following))
        elif opcode == 0x91 and length == 3 and data[1:3] in (b'\x55\x00', b'\x56\x00'):
            # These exact destinations are text pointer bytes, not $53/$54.
            node['status'] = 'reviewed_text_pointer_write'
            edges.append(('possible_next', following))
        elif opcode == 0x9B and length == 3 and data[1:3] == b'\xe9\x3e':
            # $3EE9 is an RTS-encoded call to the reviewed bank-1 $BEEA
            # decoder. Other native targets remain unreviewed.
            node['status'] = 'reviewed_packed_text_native_call'
            edges.append(('possible_next', following))
        elif opcode == 0x9B and length == 3 and data[1:3] == b'\x1b\xb5':
            # Under the current bank-0 mapping, $B51B enters the reviewed
            # palette fade at $B51C. PPU polling may prevent its return.
            node['status'] = 'reviewed_palette_fade_native_call'
            edges.append(('possible_next', following))
        elif opcode == 0x58 and length == 4:
            # $58's selector precedes its little-endian branch target. $57
            # has only three bytes and relies on stale $63, so it still stops.
            node['status'] = 'reviewed_selector_conditional'
            edges.append(('target', int.from_bytes(data[2:4], 'little')))
            edges.append(('fallthrough', following))
        elif opcode == 0x44 and length == 1 and encoded in indexed_jumps:
            # Opcode $44 indexes the following little-endian pointer array.
            # The supplied count covers only the reviewed predecessor context.
            node['status'] = 'reviewed_bounded_indexed_jump'
            node['jump_records'] = []
            for index in range(indexed_jumps[encoded]):
                entry = (following + index * 2) & 0xFFFF
                entry_bank, entry_offset = _locate(entry)
                if entry_offset + 2 > BANK_SIZE:
                    node['status'] = 'indexed_jump_crosses_bank_boundary'
                    break
                target = int.from_bytes(banks[entry_bank][entry_offset:entry_offset + 2], 'little')
                node['jump_records'].append({'index': index, 'encoded_pointer': f'0x{entry:04x}',
                                             'location': _location(entry_bank, entry_offset),
                                             'target': target})
                for pos in range(entry_offset, entry_offset + 2):
                    coverage.setdefault((entry_bank, pos), set()).add(encoded)
                edges.append(('bounded_index_target', target))
        elif opcode == 0x63 and length >= 3 and data[2] != 0:
            # The record loader restores $53/$54 after its fetch and only
            # installs a record's script pointer when mode $57 is zero.
            node['status'] = 'reviewed_nonzero_mode_record_load'
            edges.append(('possible_next', following))
        elif opcode == 0x1E and length >= 2:
            # Mode 2 marks the slot and yields without releasing it. Other
            # modes yield and release it; later reuse has an unknown entry.
            if data[1] == 2:
                node['status'] = 'reviewed_yield_retained_slot'
                edges.append(('possible_resume', following))
            else:
                node['status'] = 'reviewed_yield_release_slot'
        elif opcode in (0x95, 0xB1) and length == 1:
            table = scan_lookup_table(banks, following)
            node['status'] = ('reviewed_inline_lookup_' if opcode == 0x95
                              else 'reviewed_inline_remap_') + table['status']
            node['lookup_records'] = []
            for record in table['records']:
                location = record['location']
                for pos in range(location['bank_offset'], location['bank_offset'] + record['size']):
                    coverage.setdefault((location['bank'], pos), set()).add(encoded)
                if opcode == 0xB1 and not record.get('terminator'):
                    record = {k: v for k, v in record.items() if k not in ('target', 'slot_value')} | {
                        'value': record['target'], 'replacement': record['slot_value']}
                node['lookup_records'].append(record)
                if opcode == 0x95 and not record.get('terminator'):
                    edges.append(('possible_table_match', record['target']))
            if table['status'] == 'terminated':
                edges.append(('possible_no_match' if opcode == 0x95 else 'next', table['continuation']))
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
        result = walk(bank0, bank1, lengths, seeds, indexed_jumps=PRIMARY_INDEXED_JUMPS)
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
