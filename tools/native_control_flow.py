"""Inventory direct native control transfers from the verified assembler debug map.

This is a static source inventory, not a reachability or mapper proof. The
retained debug file is authenticated by the matching-build proof. Output
contains addresses and ownership classifications, never ROM payloads.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys

from .build_rom import digest, source_regions
from .progress import verify_primary
from .project import load_target
from .nes6502 import MNEMONICS, OPCODES as NATIVE_OPCODES, source_mode_matches
from .verify_native_opcodes import verify as verify_opcode_table
from .script_entries import BANK_SIZE, ROOT

BRANCHES = {'bpl': 0x10, 'bmi': 0x30, 'bvc': 0x50, 'bvs': 0x70,
            'bcc': 0x90, 'bcs': 0xb0, 'bne': 0xd0, 'beq': 0xf0}
OPCODES = {**BRANCHES, 'jsr': 0x20, 'jmp': 0x4c, 'rts': 0x60, 'rti': 0x40}
NATIVE_INSTRUCTION = re.compile(r'^\s*(' + '|'.join(sorted(MNEMONICS)) + r')\b', re.I)
INSTRUCTION = re.compile(r'^\s*(jsr|jmp|rts|rti|b(?:pl|mi|vc|vs|cc|cs|ne|eq))\b', re.I)


NOMINAL_SCRIPT_OPCODES = 197
BYTE_INDICES = 256
DISPATCH_LOW, DISPATCH_HIGH, LENGTH_TABLE = 0x5585, 0x564a, 0x7da7


def dispatch_lookup_spans() -> list[tuple[int, int]]:
    """All byte-indexed reads, including aliases beyond nominal table bounds."""
    return [(DISPATCH_LOW, BYTE_INDICES), (DISPATCH_HIGH, BYTE_INDICES),
            (LENGTH_TABLE, BYTE_INDICES), (BANK_SIZE + LENGTH_TABLE, BYTE_INDICES)]


def _fields(line: str) -> dict[str, str]:
    values = {}
    for field in line.split(','):
        key, sep, value = field.partition('=')
        if not sep or key in values:
            raise ValueError('malformed or duplicate debug field')
        values[key] = value.strip('"')
    return values


def inventory(debug: str, source: str, prg: bytes, regions: list[dict], *,
              include_script_dispatch: bool = False,
              extra_targets: tuple[tuple[int, int], ...] = ()) -> dict:
    """Inspect source-associated spans, preserving physical-bank alternatives."""
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two 32 KiB PRG banks')
    ownership = bytearray(2 * BANK_SIZE)
    for region in regions:
        bank, cpu, size, kind = region['bank'], int(region['cpu'], 0), region['size'], region['kind']
        if bank not in (0, 1) or kind not in ('code', 'data', 'fill') or not 0x8000 <= cpu <= 0xffff:
            raise ValueError('invalid source region')
        start = bank * BANK_SIZE + cpu - 0x8000
        if type(size) is not int or size <= 0 or cpu - 0x8000 + size > BANK_SIZE or any(ownership[start:start + size]):
            raise ValueError('overlapping or invalid source region')
        ownership[start:start + size] = bytes([{'code': 1, 'data': 2, 'fill': 3}[kind]]) * size

    files, segments, spans, lines = {}, {}, {}, defaultdict(list)
    for line in debug.splitlines():
        tag, sep, rest = line.partition('\t')
        if not sep or tag not in ('file', 'seg', 'span', 'line'):
            continue
        fields = _fields(rest)
        if tag == 'file':
            ident = int(fields['id'])
            if ident in files:
                raise ValueError('duplicate debug file id')
            files[ident] = fields['name']
        elif tag == 'seg':
            ident = int(fields['id'])
            if ident in segments:
                raise ValueError('duplicate debug segment id')
            segments[ident] = fields
        elif tag == 'span':
            ident = int(fields['id'])
            if ident in spans:
                raise ValueError('duplicate debug span id')
            spans[ident] = (int(fields['seg']), int(fields['start'], 0), int(fields['size'], 0))
        elif 'span' in fields:
            file_id, number = int(fields['file']), int(fields['line'])
            for ident in fields['span'].split('+'):
                lines[int(ident)].append((file_id, number))
    source_ids = [key for key, name in files.items() if name == 'source/rom.s']
    if len(source_ids) != 1:
        raise ValueError('missing or ambiguous debug source')
    segment_banks = {}
    for bank in (0, 1):
        matches = [(ident, item) for ident, item in segments.items() if item.get('name') == f'PRG{bank}']
        if len(matches) != 1:
            raise ValueError('missing or ambiguous debug PRG segment')
        ident, item = matches[0]
        if (int(item['start'], 0) != 0x8000 or int(item['size'], 0) != BANK_SIZE
                or int(item['ooffs'], 0) != 16 + bank * BANK_SIZE):
            raise ValueError('unexpected debug PRG geometry')
        segment_banks[ident] = bank

    source_lines = source.splitlines()
    covered = bytearray(len(prg))
    span_starts = set()
    transfers = {}
    instructions = {}
    for ident, (segment, offset, size) in spans.items():
        if segment not in segment_banks:
            continue
        bank = segment_banks[segment]
        if size <= 0 or offset < 0 or offset + size > BANK_SIZE:
            raise ValueError('invalid debug PRG span')
        start = bank * BANK_SIZE + offset
        # Macro and segment parent spans may include both source and local
        # bytes. Only fully code-owned spans can describe a source instruction.
        if any(value != 1 for value in ownership[start:start + size]):
            continue
        covered[start:start + size] = bytes([1]) * size
        span_starts.add((bank, offset))
        for file_id, number in lines.get(ident, []):
            if file_id != source_ids[0]:
                continue
            if not 1 <= number <= len(source_lines):
                raise ValueError('debug source line outside source')
            native = NATIVE_INSTRUCTION.match(source_lines[number - 1])
            decoded = NATIVE_OPCODES.get(prg[start])
            if (native and decoded and native.group(1).lower() == decoded[0]
                    and size == decoded[2]
                    and source_mode_matches(decoded[0], source_lines[number - 1].split(';', 1)[0][native.end():], decoded[1])):
                key = (bank, offset)
                form = (decoded[0], decoded[1], size)
                if key in instructions and instructions[key]['form'] != form:
                    raise ValueError('conflicting native instruction extents')
                instructions.setdefault(key, {'form': form, 'lines': set()})['lines'].add(number)
            match = INSTRUCTION.match(source_lines[number - 1])
            if not match:
                continue
            op = match.group(1).lower()
            expected_size = 2 if op in BRANCHES else (1 if op in ('rts', 'rti') else 3)
            raw = prg[start:start + size]
            if (size != expected_size or (raw[0] != OPCODES[op]
                    and not (op == 'jmp' and raw[0] == 0x6c))):
                raise ValueError('debug instruction does not match its source or opcode')
            key = (bank, offset)
            entry = (op, number, raw)
            if key in transfers and transfers[key] != entry:
                raise ValueError('conflicting source instructions at one physical address')
            transfers[key] = entry
    if any(value == 1 and not covered[i] for i, value in enumerate(ownership)):
        raise ValueError('debug spans do not cover source-owned code')

    # Unlike parent debug spans, each accepted unit is a source-associated
    # official instruction with the exact mnemonic, opcode mode and byte size.
    instruction_owner = {}
    for (bank, offset), entry in instructions.items():
        for position in range(bank * BANK_SIZE + offset, bank * BANK_SIZE + offset + entry['form'][2]):
            if position in instruction_owner and instruction_owner[position] != (bank, offset):
                raise ValueError('overlapping native instruction boundaries')
            instruction_owner[position] = (bank, offset)
    missing = [position for position, value in enumerate(ownership)
               if value == 1 and position not in instruction_owner]
    if missing:
        first = missing[0]
        raise ValueError(f'native instruction spans omit source code at bank {first // BANK_SIZE} '
                         f'CPU {0x8000 + first % BANK_SIZE:04X} ({len(missing)} bytes)')

    def instruction_start(bank: int, cpu: int) -> bool:
        return (bank, cpu - 0x8000) in instructions

    def classify(bank: int, target: int) -> dict:
        if not 0x8000 <= target <= 0xffff:
            return {'ownership': 'outside_prg', 'span_start': False}
        offset = target - 0x8000
        value = ownership[bank * BANK_SIZE + offset]
        return {'ownership': ('local', 'code', 'data', 'fill')[value],
                'span_start': (bank, offset) in span_starts}

    rows = []
    for (bank, offset), (op, line_number, raw) in sorted(transfers.items()):
        row = {'bank': bank, 'cpu': f'0x{0x8000 + offset:04x}', 'source_line': line_number, 'operation': op}
        if op in ('rts', 'rti'):
            row['target_kind'] = 'stack_or_interrupt'
        elif op == 'jmp' and raw[0] == 0x6c:
            row.update({'target_kind': 'indirect', 'pointer': f'0x{int.from_bytes(raw[1:], "little"):04x}'})
        else:
            target = ((0x8000 + offset + 2 + int.from_bytes(raw[1:2], 'little', signed=True)) & 0xffff
                      if op in BRANCHES else int.from_bytes(raw[1:], 'little'))
            row.update({'target_kind': 'relative' if op in BRANCHES else 'absolute',
                        'target_cpu': f'0x{target:04x}', 'same_physical_bank': classify(bank, target),
                        'same_bank_instruction_start': instruction_start(bank, target)})
            if op not in BRANCHES:
                row['other_physical_bank'] = classify(1 - bank, target)
                row['other_bank_instruction_start'] = instruction_start(1 - bank, target)
        rows.append(row)
    direct = [row for row in rows if row['target_kind'] in ('relative', 'absolute')]
    gaps = [row for row in direct if row['same_physical_bank']['ownership'] != 'code']
    interior = [row for row in direct if row['same_physical_bank']['ownership'] == 'code'
                and not row['same_physical_bank']['span_start']]
    non_instruction = [row for row in direct if row['same_physical_bank']['ownership'] == 'code'
                       and not row['same_bank_instruction_start']]
    instruction_rows = [{'bank': bank, 'cpu': f'0x{0x8000 + offset:04x}',
                         'operation': entry['form'][0], 'addressing_mode': entry['form'][1],
                         'size': entry['form'][2], 'source_lines': sorted(entry['lines'])}
                        for (bank, offset), entry in sorted(instructions.items())]
    result = {'instruction_count': len(instructions), 'instruction_code_bytes': len(instruction_owner),
              'instruction_mode_counts': dict(sorted(Counter(row['addressing_mode'] for row in instruction_rows).items())),
              'instructions': instruction_rows, 'same_bank_non_instruction_start_targets': non_instruction,
              'source_code_bytes': sum(value == 1 for value in ownership),
              'covered_code_bytes': sum(covered), 'operation_counts': dict(sorted(Counter(r['operation'] for r in rows).items())),
              'direct_transfer_count': len(direct), 'same_bank_non_code_targets': gaps,
              'same_bank_non_span_start_targets': interior, 'transfers': rows,
              'interpretation': 'Static source-associated spans; absolute targets have two physical bank alternatives. '
                                'Official instruction boundaries require exact source-associated opcode/size matches for all code bytes; '
                                'legacy span_start fields also include parent spans. No boundary proves runtime execution. '
                                'Returns and indirect or dynamically constructed transfers remain unresolved.'}
    if extra_targets:
        if (len(set(extra_targets)) != len(extra_targets)
                or any(bank not in (0, 1) or type(target) is not int or not 0 <= target <= 0xffff
                       for bank, target in extra_targets)):
            raise ValueError('invalid or duplicate extra target')
        result['extra_targets'] = [{'bank': bank, 'cpu': f'0x{target:04x}', **classify(bank, target),
                                    'instruction_start': instruction_start(bank, target)}
                                   for bank, target in extra_targets]
    if include_script_dispatch:
        # DispatchScriptCommand indexes two bank-0 tables and pushes an
        # address one byte before the handler; RTS then increments it. The
        # 197 nominal entries do not establish the runtime index bound.
        count, low, high, lengths = NOMINAL_SCRIPT_OPCODES, DISPATCH_LOW, DISPATCH_HIGH, LENGTH_TABLE
        if prg[lengths:lengths + BYTE_INDICES] != prg[BANK_SIZE + lengths:BANK_SIZE + lengths + BYTE_INDICES]:
            raise ValueError('script length tables differ between physical banks')
        dispatch = []
        for index in range(BYTE_INDICES):
            encoded = prg[low + index] | (prg[high + index] << 8)
            target = (encoded + 1) & 0xffff
            dispatch.append({'opcode': index, 'record_length': prg[lengths + index],
                             'effective_fetch_bytes': prg[lengths + index] or 256,
                             'target_cpu': f'0x{target:04x}', 'bank0': classify(0, target),
                             'bank1': classify(1, target), 'bank0_instruction_start': instruction_start(0, target),
                             'bank1_instruction_start': instruction_start(1, target)})
        additional, dispatch = dispatch[count:], dispatch[:count]
        result['script_dispatch'] = {'byte_indices': BYTE_INDICES, 'nominal_entries': count,
                                     'additional_entries': additional,
                                     'lookup_spans': [{'physical_prg_offset': start, 'size': size}
                                                      for start, size in dispatch_lookup_spans()],
                                     'unique_targets': len({item['target_cpu'] for item in dispatch}),
                                     'bank0_non_code_targets': [item for item in dispatch if item['bank0']['ownership'] != 'code'],
                                     'bank0_non_span_start_targets': [item for item in dispatch if item['bank0']['ownership'] == 'code' and not item['bank0']['span_start']],
                                     'bank0_non_instruction_start_targets': [item for item in dispatch
                                         if item['bank0']['ownership'] == 'code' and not item['bank0_instruction_start']],
                                     'entries': dispatch}
    result['vectors'] = [{'bank': bank, 'kind': kind, 'target_cpu': f'0x{target:04x}',
                           'target': classify(bank, target),
                           'instruction_start': instruction_start(bank, target)}
                          for bank in (0, 1) for kind, offset in (('nmi', 0x7ffa), ('reset', 0x7ffc), ('irq', 0x7ffe))
                          for target in (int.from_bytes(prg[bank * BANK_SIZE + offset:bank * BANK_SIZE + offset + 2], 'little'),)]
    return result


def main() -> int:
    try:
        target = load_target(ROOT, 'us-v1.5')
        verified = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest(proof_path.read_bytes())
        debug_path = ROOT / 'build/us-v1.5/bible-adventures.dbg'
        debug = debug_path.read_bytes()
        config = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())
        source_bytes = (ROOT / config['source']).read_bytes()
        source = source_bytes.decode('utf-8')
        reference = (ROOT / target['input_path']).read_bytes()
        if (digest(source_bytes) != verified['source_sha256']
                or digest(reference) != target['reference']['file']['sha256']):
            raise ValueError('source or reference changed during inventory')
        offset = target['reference']['prg']['offset']
        opcode_assembly = verify_opcode_table(ROOT)
        result = inventory(debug.decode(), source, reference[offset:offset + 2 * BANK_SIZE],
                           source_regions(config, offset), include_script_dispatch=True)
        result.update({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                       'source_sha256': verified['source_sha256'], 'build_proof_sha256': proof_hash,
                       'debug_sha256': digest(debug), 'tool_sha256': digest(Path(__file__).read_bytes()),
                       'opcode_spec_sha256': digest((ROOT / 'tools/nes6502.py').read_bytes()),
                       'opcode_verifier_sha256': digest((ROOT / 'tools/verify_native_opcodes.py').read_bytes()),
                       'opcode_assembly': opcode_assembly})
        if (digest(proof_path.read_bytes()) != proof_hash or digest(debug_path.read_bytes()) != result['debug_sha256']
                or digest((ROOT / 'tools/nes6502.py').read_bytes()) != result['opcode_spec_sha256']
                or digest((ROOT / 'tools/verify_native_opcodes.py').read_bytes()) != result['opcode_verifier_sha256']
                or digest((ROOT / config['source']).read_bytes()) != verified['source_sha256']
                or digest((ROOT / target['input_path']).read_bytes()) != target['reference']['file']['sha256']):
            raise ValueError('build evidence changed during inventory')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/native-control-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({key: result[key] for key in ('source_code_bytes', 'covered_code_bytes', 'instruction_code_bytes', 'instruction_count',
              'operation_counts', 'direct_transfer_count', 'same_bank_non_code_targets',
              'same_bank_non_span_start_targets', 'same_bank_non_instruction_start_targets')}, indent=2))
        dispatch = result['script_dispatch']
        print(json.dumps({key: dispatch[key] for key in ('nominal_entries', 'unique_targets',
              'bank0_non_code_targets', 'bank0_non_span_start_targets', 'bank0_non_instruction_start_targets')}, indent=2))
        print('Saved static inventory to analysis/us-v1.5/native-control-flow.json')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as exc:
        print(f'native control-flow inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
