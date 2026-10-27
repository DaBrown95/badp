"""Capture bounded v1.5 sprite resource and frame observations in the pinned emulator."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .sprite_metadata import inventory_observed
from .mesen_runtime import FLAGS, SDL2
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator


def parse_output(output: str) -> dict:
    reads = {'frame': {}, 'header': {}}
    totals = {}
    done = False
    for line in output.splitlines():
        if line.startswith('SPRITE_READ '):
            parts = line.split()
            if len(parts) != 4 or parts[1] not in reads or parts[2] in reads[parts[1]]:
                raise ValueError('malformed or duplicate sprite observation')
            count = int(parts[3])
            if count <= 0:
                raise ValueError('invalid sprite observation count')
            reads[parts[1]][parts[2]] = count
        elif line.startswith('SPRITE_TOTAL '):
            parts = line.split()
            if len(parts) != 4 or parts[1] not in reads or parts[1] in totals:
                raise ValueError('malformed or duplicate sprite totals')
            calls, missing = int(parts[2]), int(parts[3])
            if calls < 0 or missing < 0 or missing > calls:
                raise ValueError('invalid sprite totals')
            totals[parts[1]] = [calls, missing]
        elif line.startswith('SPRITE_DONE '):
            if done or line != 'SPRITE_DONE 16000':
                raise ValueError('incomplete sprite trace')
            done = True
    if not done or set(totals) != set(reads):
        raise ValueError('incomplete sprite trace')
    for kind in reads:
        if not reads[kind] or sum(reads[kind].values()) + totals[kind][1] != totals[kind][0]:
            raise ValueError('sprite trace totals do not match observations')
    return {'reads': reads, 'totals': totals}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        reference = target['reference']['file']['sha256']
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        script = ROOT / 'tools/mesen_sprites.lua'
        script_hash = digest_file(script)
        sdl_hash = digest_file(SDL2)
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/sprite-exploration.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        flags = [('--timeout=180' if flag == '--timeout=30' else flag) for flag in FLAGS]
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        with tempfile.TemporaryDirectory(prefix='sprite-trace-', dir=output.parent) as temporary:
            for index, name in enumerate(('noah', 'moses', 'david')):
                lua = Path(temporary) / f'{name}.lua'
                lua.write_text(f'local SCENARIO = {index}\n' + script.read_text())
                completed = subprocess.run([str(exe), *flags, str(lua), str(rom)],
                                           cwd=ROOT, env=env, capture_output=True,
                                           text=True, timeout=240, check=True)
                results[name] = parse_output(completed.stdout)
                # Reject mismatched bytes before reporting an observation as valid.
                inventory_observed({'results': {name: results[name]}}, bank0, bank1)
                print(f"{name}: {results[name]['totals']['frame'][0]} frame calls", flush=True)
        if (digest_file(rom) != reference or digest_file(script) != script_hash
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe):
            raise ValueError('sprite trace inputs changed during capture')
        result = {'reference_sha256': reference,
                  'scope': 'exploratory reference ROM only; 16000 frames with repeated actions and direction changes',
                  'script_sha256': script_hash, 'sdl_sha256': sdl_hash,
                  'emulator_core_sha256': emulator['core_sha256'], 'results': results}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Local sprite trace saved to analysis/us-v1.5/sprite-exploration.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'sprite trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
