"""Check an injected ambiguous record/script path in the pinned emulator.

The descriptor and busy flag are controlled, and the CPU is redirected into
an existing command. This does not prove the association is reached by play.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import DESCRIPTORS, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_script_overlap.lua'
INPUTS = (SCRIPT, 'tools/verify_script_overlap.py', 'tools/script_entries.py',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py',
          'config/mesence-toolchain.json', 'config/targets/us-v1.5.json')


def expected_events(bank0: bytes, bank1: bytes) -> list[list[str]]:
    """Derive the controlled trace from the audited banks, checking the premise."""
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two full PRG banks')
    bases = [int.from_bytes(bank0[DESCRIPTORS + i * 6:DESCRIPTORS + i * 6 + 2], 'little')
             for i in (0x1a, 0x1b)]
    op0, operand = bank1[0x6dfc:0x6dfe]
    record = (bases[0] + operand) & 0xffff
    if bases != [0x5b4e, 0x5b4e] or (op0, operand, record) != (0, 0x1b, 0x5b69):
        raise ValueError('audited bytes do not support the controlled record premise')
    script = int.from_bytes(bank1[record + 2:record + 4], 'little')
    flags = bank1[record + 4]
    if (script, flags) != (0xff, 0):
        raise ValueError('audited bytes do not support the controlled script premise')
    op1 = bank1[script]
    len0, len1 = bank1[0x7da7 + op0], bank1[0x7da7 + op1]
    next_ptr = (script + len1) & 0xffff
    if (op1, len0, len1, next_ptr) != (0x6f, 2, 6, 0x105):
        raise ValueError('audited bytes do not support the controlled command premise')
    op2 = bank1[next_ptr]
    len2 = bank1[0x7da7 + op2]
    dest = ((bank0[0x564a + op2] << 8 | bank0[0x5585 + op2]) + 1) & 0xffff
    if (op2, len2, dest) != (0xca, 14, 0xa9d8):
        raise ValueError('audited bytes do not support the controlled dispatch premise')
    result = []
    for case, busy in enumerate((0, 0, 1)):
        events = [f'FETCH {case} 6DFC 00 7E6C',
                  f'COPY {case} EDFC EDFC {len0:02X}',
                  f'DISPATCH {case} {op0:02X} {len0:02X} {0x6dfc + len0:04X} 557A {busy:02X}',
                  f'FETCH {case} {record:04X} 0A 7E6C',
                  f'COPY {case} {record | 0x8000:04X} {record | 0x8000:04X} 0A',
                  f'FETCH {case} {script:04X} 00 7E6C',
                  f'COPY {case} {script | 0x8000:04X} {script | 0x8000:04X} {len1:02X}',
                  f'DISPATCH {case} {op1:02X} {len1:02X} {next_ptr:04X} 557A {busy:02X}']
        if busy:
            events.append(f'WAIT {case} 61DD')
        else:
            events += [f'FETCH {case} {next_ptr:04X} 00 7E6C',
                       f'COPY {case} {next_ptr | 0x8000:04X} {next_ptr | 0x8000:04X} {len2:02X}',
                       f'DISPATCH {case} {op2:02X} {len2:02X} {next_ptr + len2:04X} 557A {bank1[script + 5]:02X}',
                       f'TARGET {case} {dest - 0x8000:04X}']
        result.append(events)
    return result


def parse_output(output: str, expected: list[list[str]]) -> dict:
    """Reject missing, reordered, duplicated or unexpected controlled events."""
    observed = [[] for _ in expected]
    interrupts = []
    case = 0
    done = False
    for line in output.splitlines():
        fields = line.split()
        if not fields or fields[0] not in {'FETCH', 'COPY', 'DISPATCH', 'TARGET', 'WAIT', 'RESULT', 'DONE', 'TIMEOUT', 'LOAD_FAILED'}:
            continue
        if done or fields[0] in {'TIMEOUT', 'LOAD_FAILED'}:
            raise ValueError('unexpected or failed overlap trace')
        if fields[0] == 'DONE':
            if fields != ['DONE', str(len(expected))] or case != len(expected):
                raise ValueError('invalid overlap trace summary')
            done = True
        elif fields[0] == 'RESULT':
            if case >= len(expected) or len(fields) != 4 or fields[1] != str(case):
                raise ValueError('invalid overlap result')
            expected_kind = 'wait' if expected[case][-1].startswith('WAIT ') else 'target'
            if fields[2] != expected_kind or observed[case] != expected[case]:
                raise ValueError('incomplete overlap observations')
            try:
                count = int(fields[3])
            except ValueError as exc:
                raise ValueError('invalid interrupt count') from exc
            if not 0 <= count <= 3:
                raise ValueError('unexpected interrupt count')
            interrupts.append(count)
            case += 1
        else:
            if case >= len(expected) or len(fields) < 2 or fields[1] != str(case):
                raise ValueError('overlap event out of order')
            observed[case].append(line.strip())
    if not done:
        raise ValueError('missing overlap summary')
    return {'cases': len(expected), 'interrupts': interrupts,
            'outcomes': ['wait' if e[-1].startswith('WAIT ') else 'target' for e in expected]}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        expected = expected_events(bank0, bank1)
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        sdl_hash = digest_file(SDL2)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        observations = {}
        for name, rom in (('reference', reference), ('build', build)):
            run = subprocess.run([str(exe), *FLAGS, str(ROOT / SCRIPT), str(rom)], cwd=ROOT,
                                 env=env, capture_output=True, text=True, timeout=60, check=True)
            observations[name] = parse_output(run.stdout, expected)
            print(f'{name}: {observations[name]["cases"]} controlled cases, '
                  f'outcomes {observations[name]["outcomes"]}', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build overlap observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('overlap verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/script-overlap-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                                     'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                                     'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                                     'system_sdl2_sha256': sdl_hash, 'observations': observations,
                                     'scope': 'CPU entry, descriptor, bank variables and busy flag injected; '
                                              'not evidence of normal reachability or physical cartridge behavior'}, indent=2) + '\n')
        print('Local overlap evidence saved to analysis/us-v1.5/script-overlap-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'script-overlap verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
