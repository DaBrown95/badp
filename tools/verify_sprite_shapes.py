"""Check observed sprite dimensions with controlled frame pointers in MesenCE.

This executes only the dimension read; it does not prove every frame is used
in all contexts, rendered correctly, or mapped the same on a physical board.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator
from .sprite_assets import MANIFEST, frame_addresses

SCRIPT = 'tools/mesen_sprite_shapes.lua'
INPUTS = (SCRIPT, 'tools/verify_sprite_shapes.py', 'tools/sprite_assets.py', 'tools/sprite_metadata.py',
          'tools/script_entries.py', 'tools/mesen_runtime.py', 'tools/setup_mesen.py', str(MANIFEST),
          'config/mesence-toolchain.json', 'config/targets/us-v1.5.json')


def render_script(template: str, addresses: list[int]) -> str:
    if (template.count('{{FRAME_CASES}}') != 1 or not addresses
            or any(type(x) is not int or not 0x8000 <= x < 0xffff for x in addresses)
            or addresses != sorted(set(addresses))):
        raise ValueError('invalid sprite probe template or frame list')
    return template.replace('{{FRAME_CASES}}', '{' + ','.join(f'0x{x:04X}' for x in addresses) + '}')


def parse_output(output: str, bank0: bytes, addresses: list[int]) -> dict:
    if (len(bank0) != BANK_SIZE or not addresses
            or any(type(p) is not int or not 0x8000 <= p < 0xffff for p in addresses)
            or addresses != sorted(set(addresses))):
        raise ValueError('invalid controlled sprite input')
    expected = []
    for case, p in enumerate(addresses):
        if type(p) is not int or not 0x8000 <= p < 0xffff:
            raise ValueError('frame lies outside the controlled bank')
        shape = bank0[p + 1 - 0x8000]
        expected.append(f'SHAPE {case} {p:04X} {p + 1 - 0x8000:05X} {shape:02X} '
                        f'{shape >> 4:02X} {shape & 15:02X} 2 0 0')
    expected.append(f'DONE {len(addresses)}')
    events = []
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] in {'LOAD_FAILED', 'TIMEOUT'}:
            raise ValueError('controlled sprite probe failed')
        if fields[0] in {'SHAPE', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        raise ValueError('sprite dimension observations differ from the controlled model')
    return {'frames': len(addresses), 'reads_per_frame': 2, 'interrupts': 0}


def main() -> int:
    try:
        target, bank0, _, _ = load_audited_banks()
        addresses = frame_addresses(ROOT)
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        sdl_hash = digest_file(SDL2)
        exe, emulator = verify_emulator(ROOT), spec(ROOT)
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        observations = {}
        with tempfile.TemporaryDirectory(prefix='badp-sprite-shapes-') as directory:
            script = Path(directory) / 'probe.lua'
            script.write_text(render_script((ROOT / SCRIPT).read_text(), addresses))
            for name, rom in (('reference', reference), ('build', build)):
                run = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                     env=env, capture_output=True, text=True, timeout=60, check=True)
                observations[name] = parse_output(run.stdout, bank0, addresses)
                print(f'{name}: {observations[name]["frames"]} controlled frame dimensions', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build sprite observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('sprite shape verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/sprite-shape-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('sprite verification output escapes its local directory')
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                  'system_sdl2_sha256': sdl_hash, 'observations': observations,
                  'scope': 'injected observed frame pointers; no rendering or physical-hardware claim'}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/sprite-shape-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'sprite shape verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
