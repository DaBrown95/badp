"""Check conditional overlapping record reads on the reference and build.

The probe injects descriptor/command inputs and stops before resource reads.
It does not establish gameplay reachability or physical cartridge behavior.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, DESCRIPTORS, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_record_overlaps.lua'
INPUTS = (SCRIPT, 'tools/verify_record_overlaps.py', 'tools/script_entries.py',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py', 'config/mesence-toolchain.json',
          'config/targets/us-v1.5.json')


def expected_events(bank0: bytes, bank1: bytes, *, descriptor_index: int = 0x21,
                    expected_descriptor: int = 0x6f5a, command_a: int = 0x3673,
                    command_b: int = 0x3d20, offsets: tuple[int, int, int] = (0x18, 0x1c, 0x1d)) -> list[str]:
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    if (type(descriptor_index) is not int or not 0 <= descriptor_index < 128
            or type(expected_descriptor) is not int or not 0 <= expected_descriptor < 0x8000
            or type(command_a) is not int or not 0 <= command_a <= 0x7ffd
            or type(command_b) is not int or not 0 <= command_b <= 0x7ffe
            or not isinstance(offsets, tuple) or len(offsets) != 3
            or any(type(x) is not int or not 0 <= x <= 255 for x in offsets)):
        raise ValueError('invalid controlled record inputs')
    descriptor_pos = DESCRIPTORS + 6 * descriptor_index
    descriptor = int.from_bytes(bank0[descriptor_pos:descriptor_pos + 2], 'little')
    if (descriptor != expected_descriptor or bank1[command_a:command_a + 3] != bytes((0x63, offsets[0], 0xff))
            or bank1[command_b:command_b + 2] != bytes((0x00, offsets[1]))):
        raise ValueError('audited descriptor or source command premise changed')
    events = []
    for case, (offset, mode) in enumerate(((offsets[0], 0xff), (offsets[1], 0), (offsets[2], 0))):
        encoded = (descriptor - offset if mode & 0x80 else descriptor + offset) & 0xffff
        if encoded >= 0x8000 or encoded + 10 > 0x8000:
            raise ValueError('candidate record does not fit in bank 1')
        raw = bank1[encoded:encoded + 10]
        for i, value in enumerate(raw):
            cpu = 0x8000 + encoded + i
            events.append(f'FETCH {case} {cpu:04X} {cpu:05X} {value:02X}')
        y = 2 if mode & 0x80 else 4
        events.append(f'MODE {case} {mode:02X} {y:02X} {raw[y]:02X}')
        if raw[1] == 0xff:
            raise ValueError('resource sentinel would skip the controlled field reads')
        fields = [0x55] * 4 if mode & 0x80 else list(raw[5:9])
        pointer = (raw[2], raw[3]) if mode == 0 and raw[3] != 0xff else (0x34, 0x12)
        values = [raw[y], *fields, *pointer]
        events.append(f'RESULT {case} ' + ' '.join(f'{v:02X}' for v in values) + ' 0')
    events.append('DONE')
    return events


def parse_output(output: str, expected: list[str]) -> dict:
    events = []
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] in {'LOAD_FAILED', 'TIMEOUT'}:
            raise ValueError('controlled record probe failed')
        if fields[0] in {'FETCH', 'MODE', 'RESULT', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        raise ValueError('record observations differ from the controlled model')
    return {'cases': 3, 'record_bytes_fetched_per_case': 10, 'interrupts': 0}


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
            print(f'{name}: {observations[name]["cases"]} controlled overlapping-record cases', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build record observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('record verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/record-overlap-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('record verification output escapes its local directory')
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                  'system_sdl2_sha256': sdl_hash, 'observations': observations,
                  'scope': 'injected descriptor and command inputs; no gameplay reachability or physical hardware claim'}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/record-overlap-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'record overlap verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
