"""Compare controller serialization and simultaneous transitions in MesenCE."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path, load_target
from .setup_mesen import ROOT, digest_file, spec, verify_emulator

BUTTONS = (0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01)
# A->B and B->A execute both action entry points on the transition frame.
TRANSITIONS = ((1600, 0xFBD8, 0x80), (1620, 0xFC03, 0x40),
               (1620, 0xFBD8, 0x40), (1660, 0xFC03, 0x40),
               (1680, 0xFC03, 0x80), (1680, 0xFBD8, 0x80))


def parse_output(output: str) -> dict:
    buttons: dict[int, int] = {}
    handlers = []
    done = False
    for line in output.splitlines():
        if line.startswith('BUTTON '):
            parts = line.split()
            if len(parts) != 3:
                raise ValueError('malformed controller sample')
            index, value = int(parts[1]), int(parts[2], 16)
            if index not in range(8) or index in buttons or not 0 <= value <= 255:
                raise ValueError('duplicate or invalid controller sample')
            buttons[index] = value
        elif line.startswith('HANDLER '):
            parts = line.split()
            if len(parts) != 4:
                raise ValueError('malformed controller handler event')
            frame, address, value = int(parts[1]), int(parts[2], 16), int(parts[3], 16)
            if not 1590 <= frame < 1720 or address not in (0xFBD8, 0xFC03) or not 0 <= value <= 255:
                raise ValueError('invalid controller handler event')
            handlers.append((frame, address, value))
        elif line.startswith('CONTROLLER_DONE '):
            if done or line != 'CONTROLLER_DONE 2200':
                raise ValueError('duplicate or incomplete controller run')
            done = True
    if not done or set(buttons) != set(range(8)):
        raise ValueError('controller samples are incomplete')
    if tuple(buttons[i] for i in range(8)) != BUTTONS or tuple(handlers) != TRANSITIONS:
        raise ValueError('controller bit order or transition behavior changed')
    return {'button_masks': [buttons[i] for i in range(8)],
            'handler_events': [list(event) for event in handlers]}


def controller_script(template: str) -> str:
    start_marker = 'emu.addEventCallback(function()\n local move='
    end_marker = 'end,emu.eventType.inputPolled)'
    if template.count(start_marker) != 1 or template.count(end_marker) != 1:
        raise ValueError('gameplay input callback is ambiguous')
    begin = template.index(start_marker)
    end = template.index(end_marker, begin) + len(end_marker)
    callback = template[begin:end]
    original = (' emu.setInput({up=route_up or (move and (SCENARIO==0 or SCENARIO==3)),down=move and SCENARIO==2,'
                'left=left,right=right,start=start,select=select,a=jump,b=pickup},0)')
    if callback.count(original) != 1:
        raise ValueError('gameplay input assignment is ambiguous')
    override = ''' if frames>=1600 and frames<1800 then
  local a=(frames<1620) or (frames>=1680 and frames<1700)
  local b=(frames>=1620 and frames<1640) or (frames>=1660 and frames<1680)
  emu.setInput({a=a,b=b},0)
 elseif frames>=1800 then
  local which=math.floor((frames-1800)/50);local held=(frames-1800)%50<20
  emu.setInput({a=held and which==0,b=held and which==1,select=held and which==2,start=held and which==3,
   up=held and which==4,down=held and which==5,left=held and which==6,right=held and which==7},0)
 else
''' + original + '\n end'
    callback = callback.replace(original, override)
    prelude = '''local SCENARIO=1;local frames=0
local function event(addr)
 if frames>=1590 and frames<1720 then
  local p=emu.convertAddress(addr,emu.memType.nesMemory)
  if p and p.memType==emu.memType.nesPrgRom and p.address==addr-0x8000 then
   print(string.format('HANDLER %d %04X %02X',frames,addr,emu.read(0x038d,emu.memType.nesDebug)))
  end
 end
end
emu.addMemoryCallback(event,emu.callbackType.exec,0xFBD8,0xFBD8)
emu.addMemoryCallback(event,emu.callbackType.exec,0xFC03,0xFC03)
'''
    ending = '''
emu.addEventCallback(function() frames=frames+1
 if frames>=1800 and (frames-1800)%50==15 then
  print(string.format('BUTTON %d %02X',math.floor((frames-1800)/50),emu.read(0x038d,emu.memType.nesDebug)))
 end
 if frames==2200 then print('CONTROLLER_DONE 2200');emu.stop(0) end
end,emu.eventType.endFrame)
'''
    return prelude + callback + ending


def run() -> dict:
    if os.environ.get('BADP_TARGET') not in (None, '', 'us-v1.5'):
        raise ValueError('controller verification supports us-v1.5 only')
    target = load_target(ROOT, 'us-v1.5')
    verified = verify_primary(ROOT, target)
    reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
    built = ROOT / 'build/us-v1.5/bible-adventures.nes'
    proof = ROOT / 'build/us-v1.5/proof.json'
    template = ROOT / 'tools/mesen_gameplay.lua'
    identity = {'reference': digest_file(reference), 'built': digest_file(built),
                'proof': digest_file(proof), 'template': digest_file(template),
                'collector': digest_file(Path(__file__)), 'sdl': digest_file(SDL2)}
    if identity['reference'] != target['reference']['file']['sha256'] or identity['built'] != identity['reference']:
        raise ValueError('reference or matching build identity changed')
    exe = verify_emulator(ROOT)
    emulator = spec(ROOT)
    script = controller_script(template.read_text())
    analysis = ROOT / 'analysis'
    directory = analysis / 'us-v1.5'
    output = directory / 'controller-verification.json'
    if analysis.is_symlink() or directory.is_symlink() or output.is_symlink():
        raise ValueError('refusing a symlinked controller output')
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.resolve().is_relative_to(analysis.resolve()):
        raise ValueError('controller output escapes analysis directory')
    env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
    with tempfile.TemporaryDirectory(prefix='controller-', dir=directory) as temporary:
        lua = Path(temporary) / 'controller.lua'
        lua.write_text(script)
        def one(rom: Path) -> dict:
            proc = subprocess.run([str(exe), *FLAGS, str(lua), str(rom)], cwd=ROOT,
                                  env=env, capture_output=True, text=True, timeout=60, check=True)
            return parse_output(proc.stdout)
        with ThreadPoolExecutor(max_workers=2) as pool:
            ref_future = pool.submit(one, reference)
            built_future = pool.submit(one, built)
            ref, candidate = ref_future.result(), built_future.result()
    if ref != candidate:
        raise ValueError('reference and build controller observations differ')
    current = {'reference': digest_file(reference), 'built': digest_file(built),
               'proof': digest_file(proof), 'template': digest_file(template),
               'collector': digest_file(Path(__file__)), 'sdl': digest_file(SDL2)}
    if current != identity or verify_emulator(ROOT) != exe:
        raise ValueError('controller verification inputs changed during capture')
    result = {'target': 'us-v1.5', 'scope': '2200-frame controller input and transition probe',
              'reference_sha256': identity['reference'], 'source_sha256': verified['source_sha256'],
              'source_map_sha256': verified['source_map_sha256'], 'build_proof_sha256': identity['proof'],
              'template_sha256': identity['template'], 'collector_sha256': identity['collector'],
              'emulator_core_sha256': emulator['core_sha256'], 'system_sdl2_sha256': identity['sdl'],
              'emulator_flags': list(FLAGS), 'observations': ref,
              'limitations': 'pinned emulator and selected inputs only; not a physical-controller test'}
    with tempfile.TemporaryDirectory(prefix='controller-result-', dir=directory) as temporary:
        path = Path(temporary) / 'result.json'
        path.write_text(json.dumps(result, indent=2) + '\n')
        path.replace(output)
    return {'target': 'us-v1.5', 'button_masks': ref['button_masks'],
            'handler_events': len(ref['handler_events']),
            'output': 'analysis/us-v1.5/controller-verification.json'}


def main() -> int:
    try:
        print(json.dumps(run(), indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'controller verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
