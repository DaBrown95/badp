"""Check conditional banked native-call destinations and the wrapper return.

The computed helper is replaced at entry with a RAM mapper write and RTS. Its body,
side effects and actual script/mapping reachability are outside this probe.
"""
from __future__ import annotations

from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .mesen_runtime import FLAGS, SDL2
from .native_script_calls import call_contract
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_native_calls.lua'
INPUTS = (SCRIPT, 'tools/verify_native_calls.py', 'tools/native_script_calls.py',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py',
          'config/mesence-toolchain.json', 'config/targets/us-v1.5.json')


def cases() -> tuple[tuple[int, ...], ...]:
    # Both encoded forms of both declared helper destinations, and both
    # forms of the OR-before-increment wrap to CPU $0000. Two stack depths
    # and both mappings when the helper returns to the shared continuation.
    return tuple(product((0, 1), (0, 1), (0, 1),
                         (0xb51b, 0x351b, 0xbee9, 0x3ee9, 0xffff, 0x7fff), (0xe0, 0xf0), (0, 1)))


def expected_events(bank0: bytes, bank1: bytes) -> list[str]:
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    banks = (bank0, bank1)
    for bank in banks:
        if bank[0x7fb7:0x7fb9] != bytes((0x0c, 0x0d)):
            raise ValueError('controlled conflict-free bank values differ')
    result = []
    for index, (entry, default, secondary, operand, stack, returned) in enumerate(cases()):
        contract = call_contract(operand)
        selected = secondary if operand < 0x8000 else entry
        target = int(contract['target_cpu'], 0)
        result.append(f'ENTRY {index} {entry * BANK_SIZE + 0x7d88:05X} {stack:02X}')
        if operand < 0x8000:
            address = 0xffb7 + secondary
            result.append(f'WRITE {index} 1 {address:04X} {0x0c + secondary:02X} '
                          f'{banks[entry][address - 0x8000]:02X} {entry * BANK_SIZE + address - 0x8000:05X}')
        physical = selected * BANK_SIZE + target - 0x8000 if target >= 0x8000 else -1
        result.append(f'TARGET {index} {target:04X} {physical} {stack - 2:02X} 98 FD FF 02 1234')
        address = 0xffb7 + returned
        result.append(f'WRITE {index} 2 {address:04X} {0x0c + returned:02X} '
                      f'{banks[selected][address - 0x8000]:02X} {selected * BANK_SIZE + address - 0x8000:05X}')
        result.append(f'CONTINUE {index} {returned * BANK_SIZE + 0x7d99:05X} {stack:02X}')
        address = 0xffb7 + default
        result.append(f'WRITE {index} 3 {address:04X} {0x0c + default:02X} '
                      f'{banks[returned][address - 0x8000]:02X} {returned * BANK_SIZE + address - 0x8000:05X}')
        result.append(f'RETURN {index} {default * BANK_SIZE + 0x7d88:05X} {stack + 2:02X} {operand:04X} 1234 0')
    result.append(f'DONE {len(cases())}')
    return result


def parse_output(output: str, expected: list[str]) -> dict:
    events = []
    for line in output.splitlines():
        words = line.split()
        if words and words[0] in {'TIMEOUT', 'LOAD_FAILED'}:
            raise ValueError('controlled native-call probe failed')
        if words and words[0] in {'ENTRY', 'WRITE', 'TARGET', 'CONTINUE', 'RETURN', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        index = next((i for i, pair in enumerate(zip(expected, events)) if pair[0] != pair[1]),
                     min(len(expected), len(events)))
        raise ValueError(f'native-call observations differ at event {index}: '
                         f'expected {expected[index:index + 1]}, observed {events[index:index + 1]}')
    return {'cases': len(cases()), 'computed_target_wrap_cases': 64,
            'secondary_bank_writes': 96, 'synthetic_helper_bank_writes': 192,
            'default_bank_restorations': 192,
            'stack_depths': [0xe0, 0xf0], 'interrupts': 0}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        expected = expected_events(bank0, bank1)
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        exe, emulator = verify_emulator(ROOT), spec(ROOT)
        sdl_hash = digest_file(SDL2)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        observations = {}
        template = (ROOT / SCRIPT).read_text()
        if template.count('{{CALL_CASES}}') != 1:
            raise ValueError('invalid native-call Lua template')
        source = template.replace('{{CALL_CASES}}', '{' + ','.join(
            '{' + ','.join(str(v) for v in row) + '}' for row in cases()) + '}')
        env = {k: v for k, v in os.environ.items() if not k.startswith('DYLD_')}
        with tempfile.TemporaryDirectory(prefix='native-calls-', dir=ROOT / 'build') as temporary:
            script = Path(temporary) / 'probe.lua'
            script.write_text(source)
            for name, rom in (('reference', reference), ('build', ROOT / 'build/us-v1.5/bible-adventures.nes')):
                run = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                     env=env, capture_output=True, text=True, timeout=60, check=True)
                observations[name] = parse_output(run.stdout, expected)
                print(f'{name}: {len(cases())} controlled native-call cases', flush=True)
        if (observations['reference'] != observations['build'] or digest_file(proof_path) != proof_hash
                or verify_primary(ROOT, target) != proof or digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('native-call verification inputs or observations changed')
        output = ROOT / 'analysis/us-v1.5/native-call-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
            'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
            'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
            'system_sdl2_sha256': sdl_hash, 'observations': observations,
            'scope': 'injected wrapper operands, mapping registers, entry/return banks and stack; computed helper replaced '
                     'by RAM mapper write and RTS; helper bodies, ordinary reachability, interrupt behavior and cartridge hardware '
                     'are not established'}, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/native-call-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'native-call verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
