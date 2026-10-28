"""Capture bounded v1.5 audio-command fetches in the pinned emulator."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .audio_commands import inventory_observed
from .mesen_runtime import FLAGS, SDL2
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator


def parse_output(output: str, *, frames: int = 16000) -> dict:
    if type(frames) is not int or frames <= 0:
        raise ValueError('invalid expected frame count')
    reads = {}
    done = None
    for line in output.splitlines():
        if line.startswith('AUDIO_READ '):
            parts = line.split()
            if len(parts) != 3 or parts[1] in reads:
                raise ValueError('malformed or duplicate audio read')
            try:
                count = int(parts[2])
            except ValueError as exc:
                raise ValueError('invalid audio read count') from exc
            if count <= 0:
                raise ValueError('invalid audio read count')
            reads[parts[1]] = count
        elif line.startswith('AUDIO_DONE '):
            parts = line.split()
            if done is not None or len(parts) != 7:
                raise ValueError('malformed audio trace summary')
            try:
                done = tuple(map(int, parts[1:]))
            except ValueError as exc:
                raise ValueError('malformed audio trace summary') from exc
    if (done is None or not reads or done[0] != frames or done[1] != 0
            or done[2] != done[3] or done[3] != sum(reads.values())
            or done[4] != 0 or done[5] != 0):
        raise ValueError('incomplete audio trace or bank crossing')
    return {'reads': reads, 'count': sum(reads.values()), 'crossings': 0}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        reference = target['reference']['file']['sha256']
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        script = ROOT / 'tools/mesen_audio.lua'
        script_hash = digest_file(script)
        sdl_hash = digest_file(SDL2)
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/audio-sweep.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        flags = [('--timeout=180' if flag == '--timeout=30' else flag) for flag in FLAGS]
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        with tempfile.TemporaryDirectory(prefix='audio-trace-', dir=output.parent) as temporary:
            for index, name in enumerate(('noah', 'moses', 'david')):
                lua = Path(temporary) / f'{name}.lua'
                lua.write_text(f'local SCENARIO = {index}\n' + script.read_text())
                completed = subprocess.run([str(exe), *flags, str(lua), str(rom)],
                                           cwd=ROOT, env=env, capture_output=True,
                                           text=True, timeout=240, check=True)
                results[name] = parse_output(completed.stdout)
                # Reject mismatched bytes before reporting an observation as valid.
                inventory_observed({'results': {name: results[name]}}, bank0, bank1)
                print(f'{name}: {results[name]["count"]} validated reads', flush=True)
        if (digest_file(rom) != reference or digest_file(script) != script_hash
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe):
            raise ValueError('audio trace inputs changed during capture')
        result = {'reference_sha256': reference,
                  'scope': 'exploratory reference ROM only; 16000 frames with repeated actions and direction changes',
                  'script_sha256': script_hash, 'sdl_sha256': sdl_hash,
                  'emulator_core_sha256': emulator['core_sha256'], 'results': results}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Local audio trace saved to analysis/us-v1.5/audio-sweep.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'audio trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
