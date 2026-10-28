"""Check sentinel-selected record reads with controlled source-owned pointers."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_script_only_records.lua'
INPUTS = (SCRIPT, 'tools/verify_script_only_records.py', 'config/source-us-v1.5.json',
          'include/nes.inc',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py', 'config/mesence-toolchain.json',
          'config/targets/us-v1.5.json')


def validate_addresses(addresses: list[int]) -> None:
    if (not addresses or addresses != sorted(set(addresses))
            or any(type(p) is not int or not 0 <= p <= BANK_SIZE - 10 for p in addresses)):
        raise ValueError('invalid bank-1 record pointers')


def symbol_bases(include: str) -> tuple[int, int]:
    result = []
    for name in ('SlotScriptPointerLow', 'SlotScriptPointerHigh'):
        matches = re.findall(r'^' + name + r' = \$([0-9A-F]{4})$', include, re.MULTILINE)
        if len(matches) != 1:
            raise ValueError('missing or ambiguous slot-script RAM symbol')
        result.append(int(matches[0], 16))
    return tuple(result)


def render_script(template: str, addresses: list[int], bases: tuple[int, int],
                  modes: tuple[int, ...] | None = None) -> str:
    validate_addresses(addresses)
    if (not isinstance(bases, tuple) or len(bases) != 2 or bases[0] == bases[1]
            or any(type(p) is not int or not 0 <= p <= 0x7fa for p in bases)):
        raise ValueError('invalid slot-script RAM bases')
    if modes is not None and (not isinstance(modes, tuple) or not modes
                              or modes != tuple(sorted(set(modes)))
                              or any(type(mode) is not int or mode not in (0, 1, 2) for mode in modes)):
        raise ValueError('invalid nonnegative record modes')
    cases = (','.join(f'0x{p:04X}' for p in addresses) if modes is None else
             ','.join(f'{{0x{p:04X},0x{mode:02X}}}' for p in addresses for mode in modes))
    replacements = {'{{RECORD_CASES}}': '{' + cases + '}',
                    '{{SCRIPT_LOW_BASE}}': f'0x{bases[0]:04X}',
                    '{{SCRIPT_HIGH_BASE}}': f'0x{bases[1]:04X}'}
    if any(template.count(key) != 1 for key in replacements):
        raise ValueError('invalid record probe template')
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def expected_events(bank1: bytes, addresses: list[int]) -> list[str]:
    validate_addresses(addresses)
    if len(bank1) != BANK_SIZE:
        raise ValueError('expected one complete bank')
    events = []
    for case, p in enumerate(addresses):
        raw = bank1[p:p + 10]
        if raw[1] != 0xff:
            raise ValueError('record lacks the resource sentinel')
        for i, value in enumerate(raw):
            events.append(f'FETCH {case} {0x8000 + p + i:04X} {BANK_SIZE + p + i:05X} {value:02X}')
            events.append(f'READ {case} {i} A5')  # Indexed store's destination dummy read.
        for offset in ([3, 1] if raw[3] == 0xff else [3, 2, 1]):
            events.append(f'READ {case} {offset} {raw[offset]:02X}')
        low, high = (0x34, 0x12) if raw[3] == 0xff else (raw[2], raw[3])
        values = [0x55] * 6 + [low, high, low, high]
        events.append(f'RESULT {case} ' + ' '.join(f'{v:02X}' for v in values) + ' 0')
    events.append(f'DONE {len(addresses)}')
    return events


def parse_output(output: str, expected: list[str], count: int) -> dict:
    events = []
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] in {'LOAD_FAILED', 'TIMEOUT', 'UNEXPECTED_FIELDS'}:
            raise ValueError('script-only record probe failed')
        if fields[0] in {'FETCH', 'READ', 'RESULT', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        position = next((i for i, pair in enumerate(zip(expected, events)) if pair[0] != pair[1]),
                        min(len(expected), len(events)))
        wanted = expected[position] if position < len(expected) else '<end>'
        actual = events[position] if position < len(events) else '<end>'
        raise ValueError(f'record sentinel mismatch at event {position}: expected {wanted}; observed {actual}')
    return {'records': count, 'bytes_fetched_per_record': 10, 'copy_dummy_reads_per_record': 10,
            'unselected_fields_preserved': True, 'interrupts': 0}


def main() -> int:
    try:
        target, _, bank1, _ = load_audited_banks()
        source_map = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())
        regions = [r for r in source_map['regions'] if r['id'].startswith('bank1-script-only-record-')]
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
        with tempfile.TemporaryDirectory(prefix='badp-script-only-') as directory:
            script = Path(directory) / 'probe.lua'
            script.write_text(render_script((ROOT / SCRIPT).read_text(), addresses, bases))
            for name, rom in (('reference', reference), ('build', build)):
                run = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                     env=env, capture_output=True, text=True, timeout=60, check=True)
                observations[name] = parse_output(run.stdout, expected, len(addresses))
                print(f'{name}: {len(addresses)} controlled script-only records', flush=True)
        if (observations['reference'] != observations['build']
                or digest_file(proof_path) != proof_hash or verify_primary(ROOT, target) != proof
                or digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('record verification inputs or observations changed')
        output = ROOT / 'analysis/us-v1.5/script-only-record-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                  'system_sdl2_sha256': sdl_hash, 'observations': observations,
                  'scope': 'injected record pointers; fetch, selected reads and skipped fields only; '
                  'not event reachability, script execution, rendering or physical hardware'}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/script-only-record-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'script-only record verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
