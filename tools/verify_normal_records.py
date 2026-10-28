"""Check all nonnegative loader modes for complete source-owned record views."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .mesen_runtime import FLAGS, SDL2
from .verify_script_only_records import parse_output as parse_events, render_script, symbol_bases, validate_addresses
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_normal_records.lua'
INPUTS = (SCRIPT, 'tools/verify_normal_records.py', 'tools/verify_script_only_records.py', 'config/source-us-v1.5.json',
          'include/nes.inc',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py', 'config/mesence-toolchain.json',
          'config/targets/us-v1.5.json')


def expected_events(bank1: bytes, addresses: list[int]) -> list[str]:
    validate_addresses(addresses)
    if len(bank1) != BANK_SIZE:
        raise ValueError('expected one complete bank')
    events = []
    for record, p in enumerate(addresses):
        raw = bank1[p:p + 10]
        for mode in (0, 1, 2):
            case = record * 3 + mode
            for i, value in enumerate(raw):
                events.append(f'FETCH {case} {0x8000 + p + i:04X} {BANK_SIZE + p + i:05X} {value:02X}')
                events.append(f'READ {case} {i} A5')
            if mode == 0:
                events.append(f'READ {case} 3 {raw[3]:02X}')
                if raw[3] != 0xff:
                    events.append(f'READ {case} 2 {raw[2]:02X}')
            events.append(f'READ {case} 1 {raw[1]:02X}')
            values = [0x55] * 6
            finish = 0xf296
            if raw[1] != 0xff:
                finish = 0xf184
                events.append(f'READ {case} 4 {raw[4]:02X}')
                values[0] = raw[4]
                if mode != 1:
                    for i in range(5, 9):
                        events.append(f'READ {case} {i} {raw[i]:02X}')
                    values[1:5] = raw[5:9]
                    values[5] = (0x55 | 0x28) ^ 0x08
            low, high = (raw[2], raw[3]) if mode == 0 and raw[3] != 0xff else (0x34, 0x12)
            values += [low, high, low, high]
            events.append(f'RESULT {case} {finish:04X} ' + ' '.join(f'{v:02X}' for v in values) + ' 0')
    events.append(f'DONE {len(addresses) * 3}')
    return events


def parse_output(output: str, expected: list[str], records: int) -> dict:
    parse_events(output, expected, records * 3)
    return {'records': records, 'cases': records * 3, 'modes': [0, 1, 2],
            'bytes_fetched_per_case': 10, 'copy_dummy_reads_per_case': 10,
            'selected_fields_checked': True, 'interrupts': 0}


def main() -> int:
    try:
        target, _, bank1, _ = load_audited_banks()
        source_map = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())
        regions = [r for r in source_map['regions'] if r['id'].startswith('bank1-complete-record-')]
        if not regions or any(r['bank'] != 1 or r['kind'] != 'data' or r['size'] != 9 for r in regions):
            raise ValueError('source-owned record inventory is invalid')
        addresses = sorted(int(r['cpu'], 0) - 0x8000 for r in regions)
        expected = expected_events(bank1, addresses)
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
        bases = symbol_bases((ROOT / 'include/nes.inc').read_text())
        with tempfile.TemporaryDirectory(prefix='badp-normal-records-') as directory:
            script = Path(directory) / 'probe.lua'
            script.write_text(render_script((ROOT / SCRIPT).read_text(), addresses, bases, (0, 1, 2)))
            for name, rom in (('reference', reference), ('build', build)):
                run = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                     env=env, capture_output=True, text=True, timeout=60, check=True)
                observations[name] = parse_output(run.stdout, expected, len(addresses))
                print(f'{name}: {len(addresses)} complete records in modes 0, 1 and 2', flush=True)
        if (observations['reference'] != observations['build']
                or digest_file(proof_path) != proof_hash or verify_primary(ROOT, target) != proof
                or digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('record verification inputs or observations changed')
        output = ROOT / 'analysis/us-v1.5/normal-record-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                  'system_sdl2_sha256': sdl_hash, 'observations': observations,
                  'scope': 'injected pointers in modes 0, 1 and 2; fetch and selected fields only; stop before resource reads; '
                  'not event reachability, script execution, rendering or physical hardware'}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/normal-record-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'normal record verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
