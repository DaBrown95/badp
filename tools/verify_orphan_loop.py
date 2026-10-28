"""Check an inferred script loop's conditional fields, sound and branch behavior."""
from __future__ import annotations

import json
import os
import subprocess
import sys

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_orphan_loop.lua'
INPUTS = (SCRIPT, 'tools/verify_orphan_loop.py', 'tools/mesen_runtime.py', 'tools/setup_mesen.py',
          'config/mesence-toolchain.json', 'config/targets/us-v1.5.json')


def expected_events(bank: bytes) -> list[str]:
    if len(bank) != BANK_SIZE:
        raise ValueError('expected one complete bank')
    loop = bank[0x7c88:0x7c9f]
    starts, sizes = (0, 3, 5, 8, 10, 13, 17, 20), (3, 2, 3, 2, 3, 4, 3, 3)
    opcodes = (0x2d, 7, 0x2d, 7, 0x49, 0x1b, 4, 4)
    if (tuple(loop[p] for p in starts) != opcodes or loop[1] != 0 or loop[6] != 0
            or loop[4] != 1 or loop[9] != 1 or loop[16] != 0
            or any(bank[0x7da7 + op] != size for op, size in zip(opcodes, sizes))
            or int.from_bytes(loop[14:16], 'little') != 0x7c9c
            or int.from_bytes(loop[18:20], 'little') != 0x7c88
            or int.from_bytes(loop[21:23], 'little') != 0x7c9c):
        raise ValueError('inferred loop differs from the controlled command structure')
    voice = int.from_bytes(loop[11:13], 'little')
    if not 0 < voice >> 8 < 0x80:
        raise ValueError('controlled voice pointer is not a bank-1 start')
    result = []
    for case in (0, 1):
        offsets = (0, 3, 5, 8, 10, 13, 20, 20) if case == 0 else (0, 3, 5, 8, 10, 13, 17, 0)
        first, second, wait, flags, audio_flags, audio_pointer = 0x55, 0x55, 0, 0, 0, 0
        for step, offset in enumerate(offsets, 1):
            size = bank[0x7da7 + loop[offset]]
            cpu = 0xfc88 + offset
            # Length selection reads the opcode once, followed by the copy.
            for i in (0, *range(size)):
                result.append(f'READ {case} {step} {cpu + i:04X} {cpu + i:05X} {loop[offset + i]:02X}')
            op = loop[offset]
            next_pointer = 0x7c88 + offset + size
            budget = 0x10
            if op == 0x2d:
                first, second, flags, budget = 0, loop[offset + 2], 0x20, 0
            elif op == 7:
                wait, budget = 1, 0
            elif op == 0x49:
                audio_flags, audio_pointer = 0xc0, voice
            elif op == 0x1b:
                if case == 0:
                    next_pointer = 0x7c9c
            elif op == 4:
                next_pointer = int.from_bytes(loop[offset + 1:offset + 3], 'little')
            result.append(f'STEP {case} {step} 05568 {next_pointer:04X} {next_pointer:04X} '
                          f'{first:02X} {second:02X} {wait:02X} {flags:02X} {audio_flags:02X} {audio_pointer:04X} {budget:02X}')
        result.append(f'RESULT {case} 0')
    result.append('DONE 2')
    return result


def parse_output(output: str, expected: list[str]) -> dict:
    events = []
    for line in output.splitlines():
        word = line.split(maxsplit=1)[0] if line.split() else ''
        if word in {'TIMEOUT', 'LOAD_FAILED'}:
            raise ValueError('controlled loop probe failed')
        if word in {'READ', 'STEP', 'RESULT', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        index = next((i for i, pair in enumerate(zip(expected, events)) if pair[0] != pair[1]),
                     min(len(expected), len(events)))
        raise ValueError(f'controlled loop observations differ at event {index}')
    return {'cases': 2, 'dispatches_per_case': 8, 'script_reads_per_case': 31,
            'branch_outcomes': ['terminal_loop', 'repeat_loop'], 'interrupts': 0}


def main() -> int:
    try:
        target, _, bank, _ = load_audited_banks()
        expected = expected_events(bank)
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        sdl_hash = digest_file(SDL2)
        exe, emulator = verify_emulator(ROOT), spec(ROOT)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        env = {k: v for k, v in os.environ.items() if not k.startswith('DYLD_')}
        observations = {}
        for name, rom in (('reference', reference), ('build', build)):
            run = subprocess.run([str(exe), *FLAGS, str(ROOT / SCRIPT), str(rom)], cwd=ROOT,
                                 env=env, capture_output=True, text=True, timeout=60, check=True)
            observations[name] = parse_output(run.stdout, expected)
            print(f'{name}: two controlled orphan-loop cases', flush=True)
        if (observations['reference'] != observations['build'] or digest_file(proof_path) != proof_hash
                or verify_primary(ROOT, target) != proof or digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('loop verification inputs or observations changed')
        output = ROOT / 'analysis/us-v1.5/orphan-loop-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
            'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
            'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
            'system_sdl2_sha256': sdl_hash, 'observations': observations,
            'scope': 'injected FC88 entry and slot state; wait and normal counter updates skipped between dispatches; '
                     'not ordinary entry, timing, audio playback or physical-cartridge behavior'}, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/orphan-loop-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'orphan-loop verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
