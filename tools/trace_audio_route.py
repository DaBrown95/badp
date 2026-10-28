"""Compare aggregated audio-command fetches along the maintained Moses route.

The output contains reference bytes and remains in ignored local analysis.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .audio_commands import inventory_observed
from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator
from .trace_audio import parse_output

FRAMES = 4300
EXPECTED_STARTS = (tuple(range(0xAC58, 0xAC6F)) + tuple(range(0xAC70, 0xAC7F))
                   + (0xAC86, 0xB7A3, 0xB7A4, 0xB7A9, 0xB7AB,
                      0xB7AC, 0xB7AD, 0xB7B2, 0xB7B4))


def probe_script(gameplay: str, audio: str) -> str:
    """Combine the maintained input callback with the existing audio probe."""
    input_start = 'emu.addEventCallback(function()\n local move=frames>=180'
    input_end = 'end,emu.eventType.inputPolled)'
    audio_start = 'local pending=false'
    audio_end = 'emu.addEventCallback(function()\n local move=frames>=180'
    if (gameplay.count(input_start) != 1 or audio.count(audio_start) != 1
            or audio.count(audio_end) != 1):
        raise ValueError('audio-route probe markers changed')
    start = gameplay.index(input_start)
    end = gameplay.find(input_end, start)
    if end < 0:
        raise ValueError('maintained input callback is incomplete')
    controls = gameplay[start:end + len(input_end)]
    hooks = audio[audio.index(audio_start):audio.index(audio_end)]
    return ('local SCENARIO=4;local frames=0\n' + hooks + controls + '''
emu.addEventCallback(function()
 frames=frames+1
 if frames==4300 then
  print(string.format('AUDIO_DONE %d %d %d %d %d %d',frames,crossings,started,completed,overwritten,pending and 1 or 0))
  for k,n in pairs(audio) do print(string.format('AUDIO_READ %s %d',k,n)) end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
''')


def validate_entries(result: dict) -> None:
    starts = {entry['physical_prg_offset'] for entry in result['commands']}
    if not set(EXPECTED_STARTS) <= starts:
        raise ValueError('extended Moses route did not reach the expected audio commands')
    if result['conflicts']:
        raise ValueError('observed audio commands have conflicting decodes')


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        verified = verify_primary(ROOT, target)
        proof = ROOT / 'build/us-v1.5/proof.json'
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        inputs = tuple(ROOT / name for name in (
            'tools/mesen_gameplay.lua', 'tools/mesen_audio.lua', 'tools/trace_audio_route.py',
            'tools/trace_audio.py', 'tools/audio_commands.py', 'tools/mesen_runtime.py',
            'tools/setup_mesen.py', 'tools/script_entries.py', 'tools/progress.py', 'tools/project.py',
            'config/targets/us-v1.5.json'))
        hashes = {str(path.relative_to(ROOT)): digest_file(path) for path in inputs}
        proof_hash = digest_file(proof)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        sdl_hash = digest_file(SDL2)
        output = ROOT / 'analysis/us-v1.5/audio-route.json'
        if output.parent.is_symlink() or output.is_symlink() or (ROOT / 'analysis').is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.parent.mkdir(parents=True, exist_ok=True)
        flags = [('--timeout=120' if flag == '--timeout=30' else flag) for flag in FLAGS]
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        with tempfile.TemporaryDirectory(prefix='audio-route-', dir=output.parent) as directory:
            script = Path(directory) / 'route.lua'
            script.write_text(probe_script(inputs[0].read_text(), inputs[1].read_text()))
            for name, rom in (('reference', reference), ('build', build)):
                completed = subprocess.run([str(exe), *flags, str(script), str(rom)],
                                           cwd=ROOT, env=env, capture_output=True,
                                           text=True, timeout=150, check=True)
                results[name] = parse_output(completed.stdout, frames=FRAMES)
                decoded = inventory_observed({'results': {name: results[name]}}, bank0, bank1)
                validate_entries(decoded)
                print(f'{name}: {results[name]["count"]} validated audio fetches', flush=True)
        if results['reference'] != results['build']:
            raise ValueError('reference and build audio fetches differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe
                or {str(path.relative_to(ROOT)): digest_file(path) for path in inputs} != hashes
                or verify_primary(ROOT, target)['source_sha256'] != verified['source_sha256']):
            raise ValueError('audio-route inputs changed during capture')
        result = {'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': verified['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'sdl_sha256': sdl_hash,
                  'emulator_core_sha256': emulator['core_sha256'],
                  'scope': 'reference and build, maintained Moses input through 4300 frames',
                  'results': results}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Local audio route evidence saved to analysis/us-v1.5/audio-route.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'audio route trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
