"""Check the reconstructed audio selector and mapper using controlled inputs.

These probes change emulator RAM or CPU state temporarily. They do not establish
which selector values are reachable in ordinary gameplay or prove board behavior.
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
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator


def parse_selector(output: str, bank0: bytes, bank1: bytes) -> dict:
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two PRG banks')
    selected = []
    conflicts = []
    done = None
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'SELECT':
            if len(parts) != 7:
                raise ValueError('malformed selector observation')
            try:
                a, carry = int(parts[1], 16), int(parts[2])
                value, index, expected, expected_index = (int(item, 16) for item in parts[3:])
            except ValueError as exc:
                raise ValueError('invalid selector observation') from exc
            case = len(selected)
            wanted_a, wanted_carry = case % 128, case // 128
            high = ((wanted_a % 32) // 2)
            wanted_value, wanted_index = 0x0D + high * 0x10, 1 + high * 2
            if (case >= 256 or (a, carry) != (wanted_a, wanted_carry)
                    or (value, index, expected, expected_index)
                    != (wanted_value, wanted_index, wanted_value, wanted_index)):
                raise ValueError('selector value or order differs from the reconstructed routine')
            selected.append((a, carry, value, index))
        elif parts[0] == 'CONFLICT':
            if len(parts) != 6:
                raise ValueError('malformed selector conflict')
            try:
                a, carry = int(parts[1], 16), int(parts[2])
                value, index, rom = (int(item, 16) for item in parts[3:])
            except ValueError as exc:
                raise ValueError('invalid selector conflict') from exc
            if (not 0 <= a < 128 or carry not in (0, 1) or not 0 <= index < 32
                    or bank0[0x7FB7 + index] != rom or bank1[0x7FB7 + index] != rom
                    or value == rom or (a, carry, value, index) in conflicts):
                raise ValueError('selector conflict is inconsistent with the audited banks')
            conflicts.append((a, carry, value, index))
        elif parts[0] == 'DONE':
            if done is not None or len(parts) != 4:
                raise ValueError('malformed selector summary')
            done = tuple(map(int, parts[1:]))
    expected_conflicts = {entry for entry in selected if bank0[0x7FB7 + entry[3]] != entry[2]}
    if (len(selected) != 256 or len(conflicts) != len(expected_conflicts)
            or set(conflicts) != expected_conflicts or done != (256, 0, len(expected_conflicts))):
        raise ValueError('selector observations are incomplete')
    return {'cases': len(selected), 'table_mismatches': len(conflicts)}


def parse_mapping(output: str, bank0: bytes, bank1: bytes) -> dict:
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two PRG banks')
    entries = []
    done = None
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'BANK':
            if len(parts) != 10:
                raise ValueError('malformed mapper observation')
            try:
                n = int(parts[1]);value, index, rom, pointer, physical, assumed, ram_value, ram_index = (int(x, 16) for x in parts[2:])
            except ValueError as exc:
                raise ValueError('invalid mapper observation') from exc
            if (n != len(entries) or n >= 16 or value != 0x0D + n * 0x10 or index != 1 + n * 2
                    or bank0[0x7FB7 + index] != rom or bank1[0x7FB7 + index] != rom
                    or not 0x8000 <= pointer <= 0xFFFF or assumed != pointer
                    or (ram_value, ram_index) != (value, index)):
                raise ValueError('mapper observation does not match its selector or ROM byte')
            mapped = (pointer - 0x8000) + ((value & rom) & 1) * 0x8000
            if physical != mapped:
                raise ValueError('mapper observation disagrees with the measured bus-conflict mapping')
            entries.append({'selector': value, 'index': index, 'rom_byte': rom,
                            'physical_bank': physical // 0x8000})
        elif parts[0] == 'DONE':
            if done is not None or len(parts) != 5:
                raise ValueError('malformed mapper summary')
            done = tuple(map(int, parts[1:]))
    changed = sum(entry['physical_bank'] != 1 for entry in entries)
    if (len(entries) != 16 or done is None or done[0] <= 0
            or done[1:] != (16, changed, 0) or any(entry['physical_bank'] != 1 for entry in entries[:8])):
        raise ValueError('mapper observations are incomplete')
    return {'cases': len(entries), 'bank0_cases': changed, 'entries': entries}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        verified = verify_primary(ROOT, target)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        proof = ROOT / 'build/us-v1.5/proof.json'
        scripts = (ROOT / 'tools/mesen_audio_bank_selector.lua', ROOT / 'tools/mesen_audio_bank_mapping.lua')
        inputs = (*scripts, ROOT / 'tools/verify_audio_bank.py', ROOT / 'tools/mesen_runtime.py',
                  ROOT / 'tools/setup_mesen.py', ROOT / 'config/targets/us-v1.5.json')
        hashes = {str(path.relative_to(ROOT)): digest_file(path) for path in inputs}
        proof_hash = digest_file(proof);sdl_hash = digest_file(SDL2)
        exe = verify_emulator(ROOT);emulator = spec(ROOT)
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        for kind, rom in (('reference', reference), ('build', build)):
            observations = []
            for script, parser in zip(scripts, (parse_selector, parse_mapping)):
                completed = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                           env=env, capture_output=True, text=True, timeout=60, check=True)
                observations.append(parser(completed.stdout, bank0, bank1))
            results[kind] = {'selector': observations[0], 'mapping': observations[1]}
            print(f'{kind}: {observations[0]["cases"]} selector cases, {observations[1]["cases"]} mappings', flush=True)
        if results['reference'] != results['build']:
            raise ValueError('reference and build bank observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe
                or {str(path.relative_to(ROOT)): digest_file(path) for path in inputs} != hashes
                or verify_primary(ROOT, target)['source_sha256'] != verified['source_sha256']):
            raise ValueError('bank-verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/audio-bank-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                                     'source_sha256': verified['source_sha256'], 'build_proof_sha256': proof_hash,
                                     'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                                     'system_sdl2_sha256': sdl_hash, 'observations': results,
                                     'scope': 'controlled CPU and RAM inputs in the pinned emulator; not gameplay reachability or hardware proof'}, indent=2) + '\n')
        print('Local audio bank evidence saved to analysis/us-v1.5/audio-bank-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'audio bank verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
