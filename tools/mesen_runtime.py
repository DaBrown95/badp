"""Run bounded v1.5 opening-gameplay comparisons in pinned MesenCE."""
from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import zlib

from .build_rom import digest
from .progress import verify_primary
from .project import load_target
from .setup_mesen import ROOT, digest_file, spec, verify_emulator

FRAMES = (240, 650, 1200, 1400, 1496, 1511, 1550, 1700, 1800, 2100, 2150, 2300,
          2400, 2600, 2800, 3000, 3100, 3200, 3250, 3300, 3350, 3400, 3450, 3650, 3700, 3750)
SLOT_FRAMES = (1400, 1496, 1511, 1550, 1700, 1800, 2100, 2150, 2300,
               2400, 2600, 2800, 3000, 3100, 3200, 3250, 3300, 3350, 3400, 3450, 3650, 3700, 3750)
# Pinned emulator screenshot of the first-level success screen for the audited v1.5 input.
MOSES_SUCCESS_SCREEN_SHA256 = 'c3d483860076f9e782d92de0913c671d4ed1aef84f8ce81688423cad40c19346'
SCENARIOS = (('noah', 1), ('moses', 5), ('david', 11), ('inventory', 1))
SCRIPT_TARGETS = (0x3D21, 0x3D22, 0x5CFE, 0x5D00, 0x5D01, 0x5D04, 0x5D06, 0x5D08, 0x5D0A)
RECORD_TARGETS = (0x5A40, 0x6D71, 0x6E65, 0x6E7F, 0x6ECD, 0x6EE5, 0x6EFD)
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
SDL2 = Path('/opt/homebrew/opt/sdl2/lib/libSDL2-2.0.0.dylib')
FLAGS = ('--testRunner', '--doNotSaveSettings', '--timeout=30', '--nes.region=Ntsc',
         '--nes.ramPowerOnState=AllZeros', '--nes.randomizeMapperPowerOnState=false',
         '--nes.randomizeCpuPpuAlignment=false')
GAMEPLAY_FLAGS = tuple('--timeout=120' if flag == '--timeout=30' else flag for flag in FLAGS)
RUNTIME_INPUTS = ('config/mesence-toolchain.json', 'tools/setup_mesen.py',
                  'tools/mesen_gameplay.lua', 'tools/mesen_runtime.py')


def parse_output(output: str) -> tuple[dict, dict[int, bytes], dict[str, bytes]]:
    """Parse emulator evidence strictly; unrelated emulator messages are ignored."""
    frames: dict[int, dict] = {}
    slots: dict[int, dict] = {}
    images: dict[int, bytes] = {}
    writes: list[str] = []
    audio: list[str] = []
    dma: list[str] = []
    mismatches = unmapped = 0
    banks: set[int] = set()
    reported = None
    probes = None
    inventory = None
    targets: dict[str, int] = {}
    warnings = 0
    for line in output.splitlines():
        if line.startswith('[CPU] Uninitialized memory read:'):
            warnings += 1
        if line.startswith('BADP_WRITE '):
            parts = line.split()
            if len(parts) != 6:
                raise ValueError('malformed mapper write')
            frame, address, value, physical, rom = (int(parts[1]), int(parts[2], 16),
                                                     int(parts[3], 16), int(parts[4]), int(parts[5]))
            if (not 0 <= frame <= FRAMES[-1] or not 0x8000 <= address <= 0xffff
                    or not 0 <= value <= 255 or not -1 <= physical < 0x10000
                    or not -1 <= rom <= 255):
                raise ValueError('out-of-range mapper write')
            if physical < 0:
                unmapped += 1
            else:
                banks.add(physical // 0x8000)
                if value != rom:
                    mismatches += 1
            writes.append(line)
        elif line.startswith(('BADP_APU ', 'BADP_DMA ')):
            parts = line.split()
            if len(parts) != 4:
                raise ValueError('malformed hardware write')
            frame, address, value = int(parts[1]), int(parts[2], 16), int(parts[3], 16)
            if not 0 <= frame <= FRAMES[-1] or not 0 <= value <= 255:
                raise ValueError('out-of-range hardware write')
            if parts[0] == 'BADP_APU' and (0x4000 <= address <= 0x4013 or address == 0x4015):
                audio.append(line)
            elif parts[0] == 'BADP_DMA' and address == 0x4014:
                dma.append(line)
            else:
                raise ValueError('unexpected hardware write address')
        elif line.startswith('BADP_FRAME '):
            parts = line.split()
            if len(parts) != 10:
                raise ValueError('malformed frame evidence')
            frame, main, state, scroll_x, scroll_y, physical, cycles, nmis = map(int, parts[1:9])
            if (frame not in FRAMES or frame in frames or not 0 <= physical < 0x10000
                    or cycles <= 0 or nmis < 0):
                raise ValueError('unexpected or duplicated frame evidence')
            if (any(not 0 <= value <= 255 for value in (main, state))
                    or any(not 0 <= value <= 65535 for value in (scroll_x, scroll_y))):
                raise ValueError('out-of-range frame state')
            image = bytes.fromhex(parts[9])
            if not image.startswith(PNG_SIGNATURE) or len(image) > 8_000_000:
                raise ValueError('invalid frame screenshot')
            frames[frame] = {'main_state': main, 'state': state, 'scroll_x': scroll_x,
                             'scroll_y': scroll_y, 'mapped_prg_offset': physical,
                             'cpu_cycles': cycles, 'nmi_count': nmis,
                             'screenshot_sha256': digest(image)}
            images[frame] = image
        elif line.startswith('BADP_SLOT '):
            parts = line.split()
            if len(parts) != 9:
                raise ValueError('malformed slot evidence')
            frame, *values = map(int, parts[1:])
            if frame not in SLOT_FRAMES or frame in slots or any(not 0 <= value <= 255 for value in values):
                raise ValueError('unexpected, duplicated or out-of-range slot evidence')
            slots[frame] = dict(zip(('player_descriptor', 'object_descriptor', 'object_link',
                                     'object_x', 'object_y', 'player_x', 'player_y'), values))
        elif line.startswith('BADP_SUMMARY '):
            if reported is not None:
                raise ValueError('duplicate mapper summary')
            parts = line.split()
            if len(parts) != 9:
                raise ValueError('malformed mapper summary')
            reported = tuple(map(int, parts[1:]))
        elif line.startswith('BADP_PROBE '):
            parts = line.split()
            if probes is not None or len(parts) != 3:
                raise ValueError('malformed or duplicate probe summary')
            probes = tuple(map(int, parts[1:]))
            if any(value < 0 for value in probes):
                raise ValueError('invalid probe count')
        elif line.startswith('BADP_INVENTORY '):
            parts = line.split()
            if inventory is not None or len(parts) != 4:
                raise ValueError('malformed or duplicate inventory evidence')
            inventory = tuple(map(int, parts[1:]))
            if any(value < 0 for value in inventory):
                raise ValueError('invalid inventory count')
        elif line.startswith('BADP_TARGET '):
            parts = line.split()
            if len(parts) != 4 or parts[1] not in ('script', 'record'):
                raise ValueError('malformed target evidence')
            address, count = int(parts[2], 16), int(parts[3])
            allowed = SCRIPT_TARGETS if parts[1] == 'script' else RECORD_TARGETS
            key = f'{parts[1]}:{address:04X}'
            if address not in allowed or count < 0 or key in targets:
                raise ValueError('unexpected or duplicate target evidence')
            targets[key] = count
        elif line.startswith('BADP_'):
            raise ValueError('unexpected runtime evidence line')
    expected = (len(writes), mismatches, unmapped, int(0 in banks), int(1 in banks),
                frames.get(FRAMES[-1], {}).get('nmi_count'), len(audio), len(dma))
    expected_targets = ({f'script:{address:04X}' for address in SCRIPT_TARGETS}
                        | {f'record:{address:04X}' for address in RECORD_TARGETS})
    if (set(frames) != set(FRAMES) or set(slots) != set(SLOT_FRAMES) or reported != expected or not writes
            or probes is None or inventory is None or set(targets) != expected_targets):
        raise ValueError('runtime evidence is incomplete or inconsistent')
    write_data = ('\n'.join(writes) + '\n').encode('ascii')
    audio_data = ('\n'.join(audio) + '\n').encode('ascii')
    dma_data = ('\n'.join(dma) + '\n').encode('ascii')
    return ({'frames': {str(k): frames[k] for k in FRAMES},
             'slots': {str(k): slots[k] for k in SLOT_FRAMES},
             'mapper_writes': len(writes), 'mapper_write_sha256': digest(write_data),
             'mapper_value_mismatches': mismatches, 'unmapped_mapper_writes': unmapped,
             'physical_prg_banks_seen': sorted(banks),
             'nmi_count': expected[5], 'apu_writes': len(audio),
             'apu_write_sha256': digest(audio_data), 'oam_dma_writes': len(dma),
             'oam_dma_write_sha256': digest(dma_data),
             'script_fetch_probes': probes[0], 'record_load_probes': probes[1],
             'inventory_list_index_zero': inventory[0], 'inventory_template_index_zero': inventory[1],
             'inventory_other_index_reads': inventory[2],
             'contested_target_hits': dict(sorted(targets.items())),
             'uninitialized_read_warnings': warnings}, images,
            {'mapper': write_data, 'apu': audio_data, 'oam_dma': dma_data})


def validate_scenario(evidence: dict, expected_state: int, *, inventory: bool = False) -> None:
    frames = evidence['frames']
    expected_frames = ((1200, 1), (1400, 1), (1800, 16), (2100, 16), (2300, 16), (2800, 1)) if inventory else tuple(
        (frame, expected_state) for frame in (1200, 1400, 1800, 2100, 2300))
    if (frames['240']['state'] != 0 or frames['650']['state'] != 16
            or any(frames[str(frame)]['state'] != state for frame, state in expected_frames)):
        raise ValueError('input sequence did not reach the expected adventure state')
    if inventory:
        if (not evidence['inventory_list_index_zero'] or not evidence['inventory_template_index_zero']
                or frames['1800']['screenshot_sha256'] == frames['1400']['screenshot_sha256']):
            raise ValueError('inventory opening or index-zero table reads were not observed')
    elif (frames['1800']['scroll_x'] <= frames['1400']['scroll_x']
          or frames['1800']['screenshot_sha256'] == frames['1400']['screenshot_sha256']):
        raise ValueError('rightward input did not produce the expected opening-area change')
    if expected_state == 5:
        slots = evidence['slots']
        if (any(slots[str(frame)]['player_descriptor'] != 1 or
                slots[str(frame)]['object_descriptor'] != 0x6a for frame in SLOT_FRAMES if frame <= 3350)
                or slots['1400']['object_link'] != 0xff
                or any(slots[str(frame)]['object_link'] != 1
                       for frame in SLOT_FRAMES[1:] if frame <= 3350 and frame != 3250)
                or slots['3250']['object_link'] != 0xff
                or slots['1511']['object_y'] >= slots['1400']['object_y']
                or slots['1700']['object_x'] != slots['1700']['player_x']
                or frames['2150']['scroll_x'] <= frames['2100']['scroll_x']
                or frames['3200']['scroll_x'] - frames['1700']['scroll_x'] < 1700
                or frames['3350']['scroll_x'] < frames['3200']['scroll_x']
                or any(frames[str(frame)]['state'] != 16 for frame in (3400, 3450, 3650))
                or frames['3450']['screenshot_sha256'] != MOSES_SUCCESS_SCREEN_SHA256
                or any(frames[str(frame)]['state'] != 6 for frame in (3700, 3750))
                or frames['3750']['screenshot_sha256'] == frames['3450']['screenshot_sha256']):
            raise ValueError('Moses pickup, carry and recovery observations did not match')
    if (evidence['mapper_value_mismatches'] or evidence['unmapped_mapper_writes']
            or evidence['physical_prg_banks_seen'] != [0, 1]):
        raise ValueError('mapper write evidence did not meet the observed-bank checks')
    if not evidence['nmi_count'] or not evidence['apu_writes'] or not evidence['oam_dma_writes']:
        raise ValueError('NMI, audio or OAM DMA activity was not observed')
    if not evidence['script_fetch_probes'] or not evidence['record_load_probes']:
        raise ValueError('the interpreter or record-loader probes were not observed')


def run_case(exe: Path, lua: Path, rom: Path, root: Path) -> tuple[dict, dict[int, bytes], dict[str, bytes]]:
    command = [str(exe), *GAMEPLAY_FLAGS, str(lua), str(rom)]
    env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=150)
    if result.returncode != 0:
        raise ValueError(f'MesenCE exited with status {result.returncode}: {result.stderr[-500:]}')
    if len(result.stdout) > 30_000_000:
        raise ValueError('MesenCE output exceeded the expected bound')
    return parse_output(result.stdout)


def run(root: Path = ROOT) -> dict:
    if sys.platform != 'darwin' or platform.machine() != 'arm64':
        raise ValueError('the pinned MesenCE runtime currently supports macOS Apple silicon only')
    target = load_target(root, 'us-v1.5')
    verified = verify_primary(root, target)
    pin = spec(root)
    exe = verify_emulator(root, require_core=False)
    sdl_digest = digest_file(SDL2)
    runtime_inputs = {name: digest_file(root / name) for name in RUNTIME_INPUTS}
    template = (root / 'tools/mesen_gameplay.lua').read_text()
    reference = root / target['input_path']
    built = root / 'build/us-v1.5/bible-adventures.nes'
    output = root / 'reports/us-v1.5/runtime'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix='mesen-run-', dir=output) as temporary:
        work = Path(temporary) / 'evidence'
        work.mkdir()
        for index, (name, expected_state) in enumerate(SCENARIOS):
            script = work / f'{name}.lua'
            script.write_text(f'local SCENARIO = {index}\n' + template)
            ref, _, ref_events = run_case(exe, script, reference, root)
            # A first run extracts embedded dependencies into the portable folder.
            verify_emulator(root, require_core=True)
            candidate, images, candidate_events = run_case(exe, script, built, root)
            verify_emulator(root, require_core=True)
            if digest_file(SDL2) != sdl_digest:
                raise ValueError('SDL2 changed during runtime verification')
            validate_scenario(ref, expected_state, inventory=name == 'inventory')
            validate_scenario(candidate, expected_state, inventory=name == 'inventory')
            if ref != candidate or ref_events != candidate_events:
                raise ValueError(f'{name}: reference and build runtime evidence differ')
            for frame, image in images.items():
                (work / f'{name}-{frame}.png').write_bytes(image)
            for kind, data in ref_events.items():
                (work / f'{name}-{kind}-writes.txt.zlib').write_bytes(zlib.compress(data, 9))
            results.append({'adventure': name, 'expected_state': expected_state, **candidate})
        if verify_primary(root, target) != verified:
            raise ValueError('matching build evidence changed during runtime verification')
        if {name: digest_file(root / name) for name in RUNTIME_INPUTS} != runtime_inputs:
            raise ValueError('runtime verification inputs changed during the run')
        # The directory name is local evidence, not a substitute for a ROM hash.
        run_name = f"run-{int(time.time())}-{verified['source_sha256'][:12]}"
        destination = output / run_name
        if destination.exists():
            raise ValueError('runtime evidence directory already exists')
        report = {'schema_version': 1, 'target': 'us-v1.5', 'scope': 'opening gameplay and Noah inventory',
                  'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': verified['source_sha256'],
                  'source_map_sha256': verified['source_map_sha256'],
                  'build_proof_sha256': digest_file(root / 'build/us-v1.5/proof.json'),
                  'emulator_release': pin['release'], 'emulator_archive_sha256': pin['archive_sha256'],
                  'emulator_executable_sha256': pin['executable_sha256'],
                  'emulator_core_sha256': pin['core_sha256'], 'emulator_database_sha256': pin['database_sha256'],
                  'system_sdl2_sha256': sdl_digest, 'macos_version': platform.mac_ver()[0],
                  'runtime_input_sha256': runtime_inputs,
                  'emulator_flags': list(GAMEPLAY_FLAGS), 'results': results,
                  'evidence_directory': f'reports/us-v1.5/runtime/{run_name}',
                  'limitations': 'Emulator evidence only; not full gameplay completion or cartridge hardware verification.'}
        (work / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
        # Move the completed directory only after every scenario has passed.
        os.rename(work, destination)
    return report


def main() -> int:
    try:
        report = run()
        print(json.dumps({'target': report['target'], 'scope': report['scope'],
                          'adventures': [r['adventure'] for r in report['results']],
                          'evidence_directory': report['evidence_directory']}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f'Runtime verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
