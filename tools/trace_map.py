"""Capture bounded map-layout and chunk-span mapping in pinned MesenCE."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from .map_data import CHUNK_SIZE, inventory
from .mesen_runtime import FLAGS, SDL2
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

KINDS = ('layout', 'row', 'column')
KEY = re.compile(r'^(layout|row|column):([0-9A-F]{4}):([01]):([0-9A-F]{2})$')


def parse_output(output: str) -> dict:
    totals = {}
    paired = {}
    done = False
    errors = None
    for line in output.splitlines():
        if line.startswith('MAP_DATA '):
            parts = line.split()
            if len(parts) != 3 or not KEY.fullmatch(parts[1]) or parts[1] in paired:
                raise ValueError('malformed or duplicate map observation')
            count = int(parts[2])
            if count <= 0:
                raise ValueError('invalid map observation count')
            paired[parts[1]] = count
        elif line.startswith('MAP_TOTAL '):
            parts = line.split()
            if len(parts) != 5 or parts[1] not in KINDS or parts[1] in totals:
                raise ValueError('malformed or duplicate map totals')
            started, checked, pending = map(int, parts[2:])
            if started <= 0 or started != checked or pending != 0:
                raise ValueError('incomplete map probe')
            totals[parts[1]] = [started, checked, pending]
        elif line.startswith('MAP_ERRORS '):
            if errors is not None or line != 'MAP_ERRORS 0':
                raise ValueError('map mapping check failed')
            errors = 0
        elif line.startswith('MAP_DONE '):
            if done or line != 'MAP_DONE 16000':
                raise ValueError('incomplete map trace')
            done = True
    if not done or errors is None or set(totals) != set(KINDS):
        raise ValueError('incomplete map trace')
    for kind in KINDS:
        if sum(n for key, n in paired.items() if key.startswith(kind + ':')) != totals[kind][1]:
            raise ValueError('map observations do not match totals')
    return {'totals': totals, 'paired': paired}


def classify_observations(paired: dict, static: dict) -> dict:
    """Compare mapped spans with static candidates without discarding outliers."""
    layouts = {(int(item['encoded_pointer'], 16), item['location']['bank'])
               for item in static['layouts']}
    offsets = set(static['chunk_table_offsets'])
    result = {'unrecognized_layouts': 0, 'unrecognized_spans': 0,
              'chunk_offsets_seen': set()}
    for key, count in paired.items():
        match = KEY.fullmatch(key)
        if not match or type(count) is not int or count <= 0:
            raise ValueError('invalid map observation')
        kind, encoded, bank, _ = match.groups()
        pointer, bank = int(encoded, 16), int(bank)
        if kind == 'layout':
            if (pointer, bank) not in layouts:
                result['unrecognized_layouts'] += count
        else:
            offset = pointer & 0x7fff
            found = [base for base in offsets if base <= offset < base + CHUNK_SIZE]
            if bank != 1 or len(found) != 1:
                result['unrecognized_spans'] += count
            else:
                result['chunk_offsets_seen'].add(found[0])
    result['chunk_offsets_seen'] = sorted(result['chunk_offsets_seen'])
    return result


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        static = inventory(bank0, bank1)
        reference = target['reference']['file']['sha256']
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        script = ROOT / 'tools/mesen_map.lua'
        script_hash, sdl_hash = digest_file(script), digest_file(SDL2)
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/map-trace.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        flags = [('--timeout=180' if flag == '--timeout=30' else flag) for flag in FLAGS]
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        with tempfile.TemporaryDirectory(prefix='map-trace-', dir=output.parent) as temporary:
            for index, name in enumerate(('noah', 'moses', 'david')):
                lua = Path(temporary) / f'{name}.lua'
                lua.write_text(f'local SCENARIO = {index}\n' + script.read_text())
                completed = subprocess.run([str(exe), *flags, str(lua), str(rom)],
                                           cwd=ROOT, env=env, capture_output=True,
                                           text=True, timeout=240, check=True)
                result = parse_output(completed.stdout)
                result['classification'] = classify_observations(result['paired'], static)
                results[name] = result
                print(f"{name}: {result['totals']['layout'][1]} layouts, "
                      f"{result['totals']['row'][1]} row and "
                      f"{result['totals']['column'][1]} column spans", flush=True)
        if (digest_file(rom) != reference or digest_file(script) != script_hash
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe):
            raise ValueError('map trace inputs changed during capture')
        report = {'reference_sha256': reference,
                  'scope': '16000-frame directed inputs; selected first map fetches only',
                  'script_sha256': script_hash, 'sdl_sha256': sdl_hash,
                  'emulator_core_sha256': emulator['core_sha256'], 'results': results}
        output.write_text(json.dumps(report, indent=2) + '\n')
        print('Local map trace saved to analysis/us-v1.5/map-trace.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'map trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
