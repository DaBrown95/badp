"""Verify the shared ten-byte record fetch across $FFFF in pinned MesenCE.

The probe replays a real helper call with synthetic CPU RAM and observes the
copied bytes and effective mappings. It does not measure every CPU bus cycle,
prove descriptor reachability, or establish real cartridge mapping.
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
from .script_entries import BANK_SIZE, DESCRIPTORS, ROOT, load_audited_banks, record_fetch_plan
from .setup_mesen import digest_file, spec, verify_emulator

BASES = (0xffff, 0xffff, 0x7fff, 0xfffb)
DESCRIPTOR_INDICES = (0x40, 0x41, 0x46, 0x47, 0x4c, 0x42)
SCRIPTS = ('tools/mesen_record_boundary.lua', 'tools/mesen_record_descriptor.lua')
INPUTS = (*SCRIPTS, 'tools/verify_record_boundary.py',
          'tools/script_entries.py', 'tools/mesen_runtime.py', 'tools/setup_mesen.py',
          'config/mesence-toolchain.json', 'config/targets/us-v1.5.json')


def parse_output(output: str, bank0: bytes, bank1: bytes) -> dict:
    """Validate copied bytes and their effective CPU and physical mappings."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE:
        raise ValueError('expected two full PRG banks')
    reads: list[list[int]] = [[] for _ in BASES]
    completed = 0
    done = None
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'COPY':
            if len(fields) != 7 or done is not None:
                raise ValueError('malformed boundary read')
            try:
                case, index = int(fields[1]), int(fields[2])
                address, physical, value = int(fields[3], 16), int(fields[5], 16), int(fields[6], 16)
            except ValueError as exc:
                raise ValueError('invalid boundary read') from exc
            if case != completed or case >= len(BASES) or index != len(reads[case]) or index >= 10:
                raise ValueError('boundary reads are incomplete or out of order')
            expected_address = ((BASES[case] | 0x8000) + index) & 0xffff
            if address != expected_address:
                raise ValueError('boundary read has the wrong CPU address')
            if address >= 0x8000:
                bank = 1 if case == 2 else 0
                expected_kind, expected_physical = 'prg', bank * BANK_SIZE + address - 0x8000
                expected_value = (bank0, bank1)[bank][address - 0x8000]
            else:
                expected_kind, expected_physical = 'ram', address
                expected_value = 0x30 + address + (0x40 if case == 1 and address == 4 else 0)
            if (fields[4], physical, value) != (expected_kind, expected_physical, expected_value):
                raise ValueError('boundary read disagrees with controlled memory or mapping')
            reads[case].append(value)
        elif fields[0] == 'CASE':
            if len(fields) != 8 or completed >= len(BASES) or done is not None:
                raise ValueError('malformed boundary case')
            try:
                case, count, interrupts = map(int, fields[1:4])
                x, y, pointer_high = (int(item, 16) for item in fields[4:7])
                physical_bank = int(fields[7])
            except ValueError as exc:
                raise ValueError('invalid boundary case') from exc
            if (case != completed or len(reads[case]) != 10 or count != 10 or interrupts != 0
                    or x != 0 or y != (0 if case == 2 else 10)
                    or pointer_high != BASES[case] >> 8 or physical_bank != 0):
                raise ValueError('boundary case did not finish with the expected state')
            completed += 1
        elif fields[0] == 'DONE':
            if done is not None or len(fields) != 3:
                raise ValueError('malformed boundary summary')
            done = tuple(map(int, fields[1:]))
    changed = [index for index, (a, b) in enumerate(zip(reads[0], reads[1])) if a != b]
    if completed != len(BASES) or done != (len(BASES), 0) or changed != [5]:
        raise ValueError('boundary observations or RAM change control are incomplete')
    return {'cases': len(BASES), 'copied_bytes': sum(map(len, reads)), 'ram_control_changed_indices': changed,
            'fetch_plans': [record_fetch_plan(base) for base in BASES]}


def parse_descriptor_output(output: str, bank0: bytes) -> dict:
    """Check the controlled descriptor path against the audited table."""
    if len(bank0) != BANK_SIZE:
        raise ValueError('expected a full PRG bank')
    observed = []
    done = None
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'DESC':
            if len(fields) != 6 or len(observed) >= len(DESCRIPTOR_INDICES) or done is not None:
                raise ValueError('malformed descriptor observation')
            try:
                index, pointer, mode, count = (int(value, 16) for value in fields[1:5])
                interrupts = int(fields[5])
            except ValueError as exc:
                raise ValueError('invalid descriptor observation') from exc
            expected_index = DESCRIPTOR_INDICES[len(observed)]
            offset = DESCRIPTORS + expected_index * 6
            expected_pointer = int.from_bytes(bank0[offset:offset + 2], 'little')
            if (index != expected_index or pointer != expected_pointer or mode != 0
                    or count != 10 or interrupts != 0):
                raise ValueError('descriptor observation disagrees with the audited table or fetch')
            observed.append(pointer)
        elif fields[0] == 'DONE':
            if done is not None or len(fields) != 2:
                raise ValueError('malformed descriptor summary')
            done = int(fields[1])
    if (len(observed) != len(DESCRIPTOR_INDICES) or done != len(DESCRIPTOR_INDICES)
            or observed[:5] != [0xffff] * 5 or observed[5] == 0xffff):
        raise ValueError('descriptor observations or comparison case are incomplete')
    return {'cases': len(observed), 'wrap_cases': 5,
            'indices': [f'0x{index:02x}' for index in DESCRIPTOR_INDICES]}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
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
            fetch = subprocess.run([str(exe), *FLAGS, str(ROOT / SCRIPTS[0]), str(rom)], cwd=ROOT,
                                   env=env, capture_output=True, text=True, timeout=60, check=True)
            descriptors = subprocess.run([str(exe), *FLAGS, str(ROOT / SCRIPTS[1]), str(rom)], cwd=ROOT,
                                         env=env, capture_output=True, text=True, timeout=60, check=True)
            observations[name] = {'fetch': parse_output(fetch.stdout, bank0, bank1),
                                  'descriptor': parse_descriptor_output(descriptors.stdout, bank0)}
            print(f'{name}: {observations[name]["fetch"]["copied_bytes"]} copied bytes, '
                  f'{observations[name]["descriptor"]["cases"]} descriptor cases', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build boundary observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('boundary verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/record-boundary-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                                     'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                                     'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                                     'system_sdl2_sha256': sdl_hash, 'observations': observations,
                                     'scope': 'controlled CPU, RAM and descriptor inputs in the pinned emulator; '
                                              'copied bytes and effective mappings only, not every bus cycle; '
                                              'the injected path bypasses its caller and is not gameplay reachability or hardware proof'}, indent=2) + '\n')
        print('Local record-boundary evidence saved to analysis/us-v1.5/record-boundary-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'record-boundary verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
