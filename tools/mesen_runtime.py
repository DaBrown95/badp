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
          2400, 2600, 2800, 3000, 3100, 3200, 3250, 3300, 3350, 3400, 3450, 3650, 3700, 3750,
          3800, 3825, 3850, 3900, 4050, 4150, 4300, 4400, 4500, 4600, 4650, 4750, 4900, 5000, 5100, 5200, 5250, 5300, 5375, 5450, 5500, 5550, 5575, 5625, 5650, 5700, 5880, 5950, 6000, 6040, 6100, 6160, 6200, 6260, 6300, 6340, 6500, 6690, 6740, 6780, 6800, 6840, 6900, 7000, 7020, 7100)
SLOT_FRAMES = (1400, 1496, 1511, 1550, 1700, 1800, 2100, 2150, 2300,
               2400, 2600, 2800, 3000, 3100, 3200, 3250, 3300, 3350, 3400, 3450, 3650, 3700, 3750,
               3800, 3825, 3850, 3900, 4050, 4150, 4300, 4400, 4500, 4600, 4650, 4750, 4900, 5000, 5100, 5200, 5250, 5300, 5375, 5450, 5500, 5550, 5575, 5625, 5650, 5700, 5880, 5950, 6000, 6040, 6100, 6160, 6200, 6260, 6300, 6340, 6500, 6690, 6740, 6780, 6800, 6840, 6900, 7000, 7020, 7100)
# Pinned emulator screenshot of the first-level success screen for the audited v1.5 input.
MOSES_SUCCESS_SCREEN_SHA256 = 'c3d483860076f9e782d92de0913c671d4ed1aef84f8ce81688423cad40c19346'
# Pinned second-level success screen for the same audited input.
MOSES_LEVEL_TWO_SUCCESS_SHA256 = '74a782b79533afa78724df4550879634814f4c4e15cdeb4291380df2c7b225ca'
SCENARIOS = (('noah', 1), ('moses', 5), ('david', 11), ('inventory', 1), ('moses-roof', 5))
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
    ppu: list[str] = []
    ppu_summary = None
    ppu_visible_control = ppu_visible_data = 0
    mismatches = unmapped = 0
    banks: set[int] = set()
    reported = None
    probes = None
    inventory = None
    stage2_record = None
    position_event = None
    controller_events = None
    controlled09 = None
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
        elif line.startswith('BADP_PPU '):
            parts = line.split()
            if len(parts) != 8:
                raise ValueError('malformed PPU timing event')
            frame, cpu_cycle, scanline, dot = map(int, parts[1:5])
            address, value, rendering = int(parts[5], 16), int(parts[6], 16), int(parts[7])
            if (not 0 <= frame <= FRAMES[-1] or cpu_cycle < 0
                    or not -1 <= scanline <= 260 or not 0 <= dot <= 340
                    or not 0x2000 <= address <= 0x2007 or address == 0x2004
                    or not 0 <= value <= 255 or rendering not in (0, 1)):
                raise ValueError('out-of-range PPU timing event')
            if 0 <= scanline < 240 and rendering:
                ppu_visible_control += address == 0x2000
                ppu_visible_data += address == 0x2007
            ppu.append(line)
        elif line.startswith('BADP_PPU_SUMMARY '):
            parts = line.split()
            if ppu_summary is not None or len(parts) != 2:
                raise ValueError('malformed or duplicate PPU timing summary')
            ppu_summary = int(parts[1])
            if ppu_summary < 0:
                raise ValueError('invalid PPU timing count')
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
            if len(parts) != 13:
                raise ValueError('malformed slot evidence')
            frame, *values = map(int, parts[1:])
            if frame not in SLOT_FRAMES or frame in slots or any(not 0 <= value <= 255 for value in values):
                raise ValueError('unexpected, duplicated or out-of-range slot evidence')
            slots[frame] = dict(zip(('player_descriptor', 'object_descriptor', 'object_link',
                                     'object_x', 'object_y', 'player_x', 'player_y', 'third_descriptor',
                                     'third_link', 'third_x', 'third_y'), values))
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
        elif line.startswith('BADP_STAGE2_RECORD '):
            parts = line.split()
            if stage2_record is not None or len(parts) != 2:
                raise ValueError('malformed or duplicate stage-two record evidence')
            stage2_record = int(parts[1])
            if stage2_record < 0:
                raise ValueError('invalid stage-two record count')
        elif line.startswith('BADP_POSITION_EVENT '):
            parts = line.split()
            if position_event is not None or len(parts) != 3:
                raise ValueError('malformed or duplicate position-event evidence')
            position_event = tuple(map(int, parts[1:]))
            if any(value < 0 for value in position_event):
                raise ValueError('invalid position-event count')
        elif line.startswith('BADP_CONTROLLER_EVENTS '):
            parts = line.split()
            if controller_events is not None or len(parts) != 5:
                raise ValueError('malformed or duplicate controller-event evidence')
            controller_events = tuple(map(int, parts[1:]))
            if any(value < 0 for value in controller_events):
                raise ValueError('invalid controller-event count')
        elif line.startswith('BADP_CONTROLLED_09 '):
            parts = line.split()
            if controlled09 is not None or len(parts) != 3:
                raise ValueError('malformed or duplicate controlled-descriptor evidence')
            controlled09 = tuple(map(int, parts[1:]))
            if any(value < 0 for value in controlled09):
                raise ValueError('invalid controlled-descriptor count')
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
            or ppu_summary != len(ppu) or not ppu
            or probes is None or inventory is None or stage2_record is None or position_event is None
            or controller_events is None or controlled09 is None
            or set(targets) != expected_targets):
        raise ValueError('runtime evidence is incomplete or inconsistent')
    write_data = ('\n'.join(writes) + '\n').encode('ascii')
    audio_data = ('\n'.join(audio) + '\n').encode('ascii')
    dma_data = ('\n'.join(dma) + '\n').encode('ascii')
    ppu_data = ('\n'.join(ppu) + '\n').encode('ascii')
    return ({'frames': {str(k): frames[k] for k in FRAMES},
             'slots': {str(k): slots[k] for k in SLOT_FRAMES},
             'mapper_writes': len(writes), 'mapper_write_sha256': digest(write_data),
             'mapper_value_mismatches': mismatches, 'unmapped_mapper_writes': unmapped,
             'physical_prg_banks_seen': sorted(banks),
             'nmi_count': expected[5], 'apu_writes': len(audio),
             'apu_write_sha256': digest(audio_data), 'ppu_writes': len(ppu),
             'ppu_write_sha256': digest(ppu_data),
             'ppu_visible_rendering_control_writes': ppu_visible_control,
             'ppu_visible_rendering_data_writes': ppu_visible_data, 'oam_dma_writes': len(dma),
             'oam_dma_write_sha256': digest(dma_data),
             'script_fetch_probes': probes[0], 'record_load_probes': probes[1],
             'inventory_list_index_zero': inventory[0], 'inventory_template_index_zero': inventory[1],
             'inventory_other_index_reads': inventory[2],
             'stage2_record_mode2': stage2_record,
             'position_event_matches': position_event[0], 'position_event_mismatches': position_event[1],
             'controller_event_24_matches': controller_events[0], 'controller_event_2d_matches': controller_events[1],
             'controller_event_36_matches': controller_events[2], 'controller_event_mismatches': controller_events[3],
             'controlled09_disabled_samples': controlled09[0], 'controlled09_other_samples': controlled09[1],
             'contested_target_hits': dict(sorted(targets.items())),
             'uninitialized_read_warnings': warnings}, images,
            {'mapper': write_data, 'apu': audio_data, 'ppu': ppu_data, 'oam_dma': dma_data})


def validate_scenario(evidence: dict, expected_state: int, *, inventory: bool = False, roof: bool = False) -> None:
    frames = evidence['frames']
    expected_frames = ((1200, 1), (1400, 1), (1800, 16), (2100, 16), (2300, 16), (2800, 1)) if inventory else tuple(
        (frame, expected_state) for frame in (1200, 1400, 1800, 2100, 2300))
    if (frames['240']['state'] != 0 or frames['650']['state'] != 16
            or any(frames[str(frame)]['state'] != state for frame, state in expected_frames)):
        raise ValueError('input sequence did not reach the expected adventure state')
    if evidence['position_event_mismatches'] or (expected_state == 11 and not evidence['position_event_matches']):
        raise ValueError('David position event did not resolve to the expected record')
    if (evidence['controller_event_mismatches']
            or (expected_state == 5 and (not evidence['controller_event_24_matches']
                                         or not evidence['controller_event_2d_matches']))
            or (inventory and not evidence['controller_event_36_matches'])):
        raise ValueError('controller event did not resolve to the expected record')
    if (evidence['controlled09_other_samples']
            or ((expected_state == 5 or inventory) and not evidence['controlled09_disabled_samples'])):
        raise ValueError('controlled descriptor 09 did not retain its observed disabled state')
    if inventory:
        if (not evidence['inventory_list_index_zero'] or not evidence['inventory_template_index_zero']
                or frames['1800']['screenshot_sha256'] == frames['1400']['screenshot_sha256']):
            raise ValueError('inventory opening or index-zero table reads were not observed')
    elif (frames['1800']['scroll_x'] <= frames['1400']['scroll_x']
          or frames['1800']['screenshot_sha256'] == frames['1400']['screenshot_sha256']):
        raise ValueError('rightward input did not produce the expected opening-area change')
    if expected_state == 5:
        slots = evidence['slots']
        carried_frames = (5950, 6000, 6040, 6100, 6160, 6200, 6260, 6300, 6340,
                          6500, 6690, 6740, 6780, 6800, 6840, 6900, 7000, 7020)
        if roof:
            carried_frames += (7100,)
        if (not evidence['stage2_record_mode2']
                or any(slots[str(frame)]['player_descriptor'] != 1 or
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
                or any(frames[str(frame)]['state'] != 6 for frame in (3700, 3750, 3800, 3825, 3850, 3900, 4050, 4150, 4300, 4400, 4500, 4600, 4650, 4750, 4900, 5000, 5100, 5200, 5250, 5300, 5375, 5450, 5500, 5550))
                or frames['3750']['screenshot_sha256'] == frames['3450']['screenshot_sha256']
                or slots['3750']['third_descriptor'] != 0x6a or slots['3750']['third_link'] != 0xff
                or slots['3900']['third_descriptor'] != 0x6a or slots['3900']['third_link'] != 1
                or slots['3900']['third_x'] != slots['3900']['player_x']
                or slots['3900']['third_y'] >= slots['3900']['player_y']
                or frames['4050']['scroll_x'] < 128 or frames['4300']['scroll_x'] < 450
                or slots['4300']['third_descriptor'] != 0x6a or slots['4300']['third_link'] != 1
                or slots['4300']['third_x'] != slots['4300']['player_x']
                or slots['4300']['third_y'] >= slots['4300']['player_y']
                or frames['4600']['scroll_x'] < 850
                or slots['4600']['third_descriptor'] != 0x6a or slots['4600']['third_link'] != 1
                or slots['4600']['third_x'] != slots['4600']['player_x']
                or slots['4600']['third_y'] >= slots['4600']['player_y']
                or frames['4900']['scroll_x'] < 1190
                or slots['4900']['third_descriptor'] != 0x6a or slots['4900']['third_link'] != 1
                or slots['4900']['third_x'] != slots['4900']['player_x']
                or slots['4900']['third_y'] >= slots['4900']['player_y']
                or frames['5200']['scroll_x'] < 1550
                or slots['5200']['third_descriptor'] != 0x6a or slots['5200']['third_link'] != 1
                or slots['5200']['third_x'] != slots['5200']['player_x']
                or slots['5200']['third_y'] >= slots['5200']['player_y']
                or frames['5550']['scroll_x'] < 1984
                or slots['5550']['third_descriptor'] != 0x6a or slots['5550']['third_link'] != 1
                or slots['5550']['third_x'] != slots['5550']['player_x']
                or slots['5550']['third_y'] >= slots['5550']['player_y']
                or any(frames[str(frame)]['state'] != 16 for frame in (5575, 5625, 5650))
                or frames['5625']['screenshot_sha256'] != MOSES_LEVEL_TWO_SUCCESS_SHA256
                or frames['5700']['state'] != 7 or slots['5700']['third_descriptor'] != 0x6a
                or slots['5700']['third_link'] != 0xff
                or frames['5700']['screenshot_sha256'] == frames['5625']['screenshot_sha256']
                or any(frames[str(frame)]['state'] != 7 for frame in (5880, *carried_frames))
                or slots['5880']['third_descriptor'] != 0x6a or slots['5880']['third_link'] != 0xff
                or any(slots[str(frame)]['third_descriptor'] != 0x6a
                       or slots[str(frame)]['third_link'] != 1
                       # The carried slot can trail by four pixels at the two jump samples.
                       or abs(slots[str(frame)]['third_x'] - slots[str(frame)]['player_x']) > (4 if frame in (6690, 6780) else 0)
                       or slots[str(frame)]['third_y'] >= slots[str(frame)]['player_y']
                       for frame in carried_frames)
                or any(slots[str(frame)]['player_descriptor'] != 1 for frame in carried_frames if frame >= 6500)
                or frames['6100']['scroll_x'] != frames['6000']['scroll_x']
                or slots['6100']['player_x'] + 32 >= slots['6000']['player_x']
                or frames['6340']['scroll_x'] + slots['6340']['player_x']
                   < frames['6100']['scroll_x'] + slots['6100']['player_x'] + 60
                or frames['6340']['scroll_y'] + slots['6340']['player_y']
                   >= frames['6100']['scroll_y'] + slots['6100']['player_y']
                or frames['6740']['scroll_y'] + slots['6740']['player_y'] + 32
                   > frames['6340']['scroll_y'] + slots['6340']['player_y']
                or frames['7020']['scroll_x'] + slots['7020']['player_x']
                   < frames['6740']['scroll_x'] + slots['6740']['player_x'] + 100):
            raise ValueError('Moses pickup, carry and recovery observations did not match')
        if roof and (frames['6900']['scroll_y'] + slots['6900']['player_y'] > 120
                     or frames['7100']['scroll_x'] + slots['7100']['player_x'] < 600):
            raise ValueError('Moses roof route did not reach the stairs while carrying')
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


def evidence_difference_paths(left: object, right: object, *, limit: int = 32) -> list[str]:
    """Summarize differing parsed values without discarding the full evidence."""
    if type(limit) is not int or limit <= 0:
        raise ValueError('invalid difference limit')
    differences: list[str] = []

    def visit(a: object, b: object, path: str) -> None:
        if len(differences) >= limit:
            return
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(a.keys() | b.keys()):
                child = f'{path}/{key}'
                if key not in a or key not in b:
                    differences.append(child)
                else:
                    visit(a[key], b[key], child)
                if len(differences) >= limit:
                    return
        elif a != b:
            differences.append(path or '/')

    visit(left, right, '')
    return differences


def retain_runtime_failure(output: Path, scenario: str, reason: str, metadata: dict,
                           reference: dict, candidate: dict, reference_images: dict[int, bytes],
                           candidate_images: dict[int, bytes], reference_events: dict[str, bytes],
                           candidate_events: dict[str, bytes]) -> Path:
    """Keep one bounded local comparison when a parsed runtime check fails."""
    if scenario not in {name for name, _ in SCENARIOS}:
        raise ValueError('invalid runtime failure scenario')
    root = output / 'failures'
    if root.is_symlink():
        raise ValueError('refusing symlinked runtime failure directory')
    root.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix=f'{scenario}-', dir=root))
    report = {'scenario': scenario, 'reason': reason, 'metadata': metadata,
              'different_evidence_paths': evidence_difference_paths(reference, candidate),
              'different_event_streams': sorted(k for k in reference_events.keys() | candidate_events.keys()
                                                if reference_events.get(k) != candidate_events.get(k)),
              'different_screenshots': sorted(k for k in reference_images.keys() | candidate_images.keys()
                                               if reference_images.get(k) != candidate_images.get(k)),
              'reference': reference, 'build': candidate}
    (destination / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    for label, images, events in (('reference', reference_images, reference_events),
                                   ('build', candidate_images, candidate_events)):
        for frame, png in images.items():
            if frame not in FRAMES or not png.startswith(PNG_SIGNATURE):
                raise ValueError('invalid runtime failure screenshot')
            (destination / f'{label}-{frame}.png').write_bytes(png)
        for kind, data in events.items():
            if kind not in ('mapper', 'apu', 'ppu', 'oam_dma'):
                raise ValueError('invalid runtime failure event stream')
            (destination / f'{label}-{kind}.txt.zlib').write_bytes(zlib.compress(data, 9))
    return destination


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
            ref, ref_images, ref_events = run_case(exe, script, reference, root)
            # A first run extracts embedded dependencies into the portable folder.
            verify_emulator(root, require_core=True)
            candidate, images, candidate_events = run_case(exe, script, built, root)
            verify_emulator(root, require_core=True)
            if digest_file(SDL2) != sdl_digest:
                raise ValueError('SDL2 changed during runtime verification')
            try:
                validate_scenario(ref, expected_state, inventory=name == 'inventory', roof=name == 'moses-roof')
                validate_scenario(candidate, expected_state, inventory=name == 'inventory', roof=name == 'moses-roof')
                if ref != candidate or ref_events != candidate_events:
                    raise ValueError('reference and build runtime evidence differ')
            except ValueError as exc:
                failure = retain_runtime_failure(
                    output, name, str(exc),
                    {'reference_sha256': target['reference']['file']['sha256'],
                     'source_sha256': verified['source_sha256'],
                     'source_map_sha256': verified['source_map_sha256'],
                     'build_proof_sha256': digest_file(root / 'build/us-v1.5/proof.json'),
                     'runtime_input_sha256': runtime_inputs, 'emulator_flags': list(GAMEPLAY_FLAGS),
                     'emulator_release': pin['release'], 'emulator_executable_sha256': pin['executable_sha256'],
                     'emulator_core_sha256': pin['core_sha256'], 'emulator_database_sha256': pin['database_sha256'],
                     'system_sdl2_sha256': sdl_digest, 'macos_version': platform.mac_ver()[0]},
                    ref, candidate, ref_images, images, ref_events, candidate_events)
                raise ValueError(f'{name}: {exc}; comparison retained at {failure.relative_to(root)}') from exc
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
