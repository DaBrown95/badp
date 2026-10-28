"""Capture sampled interpreter and record accesses on the v1.5 Moses route."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .mesen_runtime import FLAGS, RUNTIME_INPUTS, parse_output, validate_scenario
from .progress import verify_primary
from .project import input_path, load_target
from .runtime_extents import TRACE, coverage
from .script_entries import load_audited_banks
from .setup_mesen import ROOT, digest_file, spec, verify_emulator


def capture_script(template: str, prelude: str, ending: str) -> str:
    """Attach the collector to the maintained roof-route scenario."""
    if template.count('  emu.stop(0)') != 1:
        raise ValueError('gameplay stop marker is ambiguous')
    return 'local SCENARIO=4\n' + prelude + template.replace('  emu.stop(0)', ending + '  emu.stop(0)')


def capture() -> dict:
    if os.environ.get('BADP_TARGET') not in (None, '', 'us-v1.5'):
        raise ValueError('runtime trace supports us-v1.5 only')
    target = load_target(ROOT, 'us-v1.5')
    verified = verify_primary(ROOT, target)
    proof_path = ROOT / 'build/us-v1.5/proof.json'
    proof_sha = digest_file(proof_path)
    proof = json.loads(proof_path.read_text())
    rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
    reference = target['reference']['file']['sha256']
    if digest_file(rom) != reference:
        raise ValueError('reference ROM identity changed')
    inputs = {name: digest_file(ROOT / name) for name in RUNTIME_INPUTS}
    collector_sha = digest_file(Path(__file__))
    template = (ROOT / 'tools/mesen_gameplay.lua').read_text()
    ranges = [(g['bank'] * 0x8000 + int(g['cpu_start'], 16) - 0x8000, g['size'])
              for g in proof['local_prg_gaps']]
    prelude = 'local gaps={}\n' + ''.join(f'for p={start},{start + size - 1} do gaps[p]=true end\n'
                                          for start, size in ranges) + '''local code={};local scripts={};local records={}
emu.addMemoryCallback(function(addr)
 local p=emu.convertAddress(addr,emu.memType.nesMemory)
 if p and p.memType==emu.memType.nesPrgRom and gaps[p.address] then code[p.address]=(code[p.address] or 0)+1 end
end,emu.callbackType.exec,0x8000,0xffff)
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xD54E,emu.memType.nesMemory)
 if m and m.memType==emu.memType.nesPrgRom and m.address==0x554E then
  local ptr=emu.read(0x53,emu.memType.nesDebug)+256*emu.read(0x54,emu.memType.nesDebug)
  local bank=emu.read(0x03C2,emu.memType.nesDebug)
  local key=string.format('%04X:%02X',ptr,bank);scripts[key]=(scripts[key] or 0)+1
 end
end,emu.callbackType.exec,0xD54E,0xD54E)
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xF10C,emu.memType.nesMemory)
 if m and m.memType==emu.memType.nesPrgRom and m.address==0x710C then
  local ptr=emu.read(0xFE,emu.memType.nesDebug)+256*emu.read(0xFF,emu.memType.nesDebug)
  local bank=emu.read(0x03C2,emu.memType.nesDebug);local mode=emu.read(0x57,emu.memType.nesDebug)
  local key=string.format('%04X:%02X:%02X',ptr,bank,mode);records[key]=(records[key] or 0)+1
 end
end,emu.callbackType.exec,0xF10C,0xF10C)
local inline=nil;local inline_counts={};local inline_done=0;local inline_bad=0;local inline_nonrom=0
local function begin_inline(kind, expected)
 local state=emu.getState();local m=emu.convertAddress(state['cpu.pc'],emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=expected then return end
 if inline then inline_bad=inline_bad+1 end
 -- The JSR and the fetch helper's PHA leave three bytes on the stack.
 inline={kind=kind,sp=(state['cpu.sp']-3)%256,reads=0}
end
emu.addMemoryCallback(function() begin_inline(0x95,0x662E) end,emu.callbackType.exec,0xE62E,0xE62E)
emu.addMemoryCallback(function() begin_inline(0xB1,0x691E) end,emu.callbackType.exec,0xE91E,0xE91E)
emu.addMemoryCallback(function()
 if not inline then return end
 local state=emu.getState();if state['cpu.sp']~=inline.sp then return end
 local y=state['cpu.y'];if y>=4 then inline_bad=inline_bad+1;return end
 local ptr=emu.read(0x53,emu.memType.nesDebug)+256*emu.read(0x54,emu.memType.nesDebug)
 local m=emu.convertAddress((ptr+y)%65536,emu.memType.nesMemory)
 if m and m.memType==emu.memType.nesPrgRom then
  local key=string.format('%02X:%05X',inline.kind,m.address);inline_counts[key]=(inline_counts[key] or 0)+1
 else inline_nonrom=inline_nonrom+1 end
 inline.reads=inline.reads+1
end,emu.callbackType.exec,0xFE90,0xFE90)
local function end_inline(kind, expected)
 local state=emu.getState();local m=emu.convertAddress(state['cpu.pc'],emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=expected then return end
 if not inline or inline.kind~=kind or inline.reads~=4 then inline_bad=inline_bad+1 else inline_done=inline_done+1 end
 inline=nil
end
emu.addMemoryCallback(function() end_inline(0x95,0x6631) end,emu.callbackType.exec,0xE631,0xE631)
emu.addMemoryCallback(function() end_inline(0xB1,0x6921) end,emu.callbackType.exec,0xE921,0xE921)
'''
    ending = '''for p,n in pairs(code) do print(string.format('CODE_GAP %05X %d',p,n)) end
for k,n in pairs(scripts) do print(string.format('SCRIPT_EXEC %s %d',k,n)) end
for k,n in pairs(records) do print(string.format('RECORD_EXEC %s %d',k,n)) end
for k,n in pairs(inline_counts) do print(string.format('INLINE_READ %s %d',k,n)) end
print(string.format('INLINE_SUMMARY %d %d %d %d',inline_done,inline_bad,inline_nonrom,inline and 1 or 0))
'''
    source = capture_script(template, prelude, ending)
    analysis = ROOT / 'analysis'
    directory = analysis / 'us-v1.5'
    if analysis.is_symlink() or directory.is_symlink():
        raise ValueError('refusing a symlinked analysis directory')
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.resolve().is_relative_to(analysis.resolve()):
        raise ValueError('analysis output escapes its local directory')
    with tempfile.TemporaryDirectory(prefix='runtime-trace-', dir=directory) as temporary:
        lua = Path(temporary) / 'trace.lua'
        lua.write_text(source)
        flags = tuple('--timeout=180' if flag == '--timeout=30' else flag for flag in FLAGS)
        proc = subprocess.run([str(verify_emulator(ROOT)), *flags, str(lua), str(rom)],
                              cwd=ROOT, capture_output=True, text=True, timeout=240, check=True)
    evidence, _, _ = parse_output(proc.stdout)
    validate_scenario(evidence, 5, roof=True)
    results: dict[str, dict[str, int]] = {'code': {}, 'scripts': {}, 'records': {}, 'inline': {}}
    names = {'CODE_GAP': 'code', 'SCRIPT_EXEC': 'scripts', 'RECORD_EXEC': 'records', 'INLINE_READ': 'inline'}
    inline_summary = None
    for line in proc.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] in names:
            if len(parts) != 3 or parts[1] in results[names[parts[0]]]:
                raise ValueError('malformed or duplicate trace output')
            results[names[parts[0]]][parts[1]] = int(parts[2])
        elif parts and parts[0] == 'INLINE_SUMMARY':
            if inline_summary is not None or len(parts) != 5:
                raise ValueError('malformed or duplicate inline summary')
            inline_summary = [int(value) for value in parts[1:]]
    if not results['scripts'] or not results['records']:
        raise ValueError('missing sampled script or record events')
    if (inline_summary is None or any(value < 0 for value in inline_summary)
            or not inline_summary[0] or inline_summary[1] or inline_summary[3]
            or not any(key.startswith('95:') for key in results['inline'])
            or sum(results['inline'].values()) + inline_summary[2] != 4 * inline_summary[0]):
        raise ValueError('inline lookup trace is incomplete or inconsistent')
    _, bank0, bank1, lengths = load_audited_banks()
    gap_offsets = {position for start, size in ranges for position in range(start, start + size)}
    coverage(bank0, bank1, lengths, gap_offsets, {'inline_summary': inline_summary, 'results': results})
    if (digest_file(rom) != reference or digest_file(proof_path) != proof_sha
            or digest_file(ROOT / 'src/us-v1.5/rom.s') != verified['source_sha256']
            or digest_file(ROOT / 'config/source-us-v1.5.json') != verified['source_map_sha256']
            or digest_file(Path(__file__)) != collector_sha
            or {name: digest_file(ROOT / name) for name in RUNTIME_INPUTS} != inputs):
        raise ValueError('trace inputs changed during capture')
    report = {'reference_sha256': reference, 'source_sha256': verified['source_sha256'],
              'source_map_sha256': verified['source_map_sha256'], 'build_proof_sha256': proof_sha,
              'collector_sha256': collector_sha, 'runtime_input_sha256': inputs,
              'emulator_core_sha256': spec(ROOT)['core_sha256'],
              'scope': 'reference-only Moses roof and fifth-level carry through 11900 frames',
              'inline_summary': inline_summary, 'results': results}
    output = ROOT / TRACE
    if output.is_symlink():
        raise ValueError('refusing a symlinked trace output')
    with tempfile.TemporaryDirectory(prefix='runtime-trace-result-', dir=directory) as temporary:
        candidate = Path(temporary) / 'trace.json'
        candidate.write_text(json.dumps(report, indent=2) + '\n')
        candidate.replace(output)
    return {'script_pointer_bank_pairs': len(results['scripts']),
            'record_pointer_bank_modes': len(results['records']),
            'inline_fetches': inline_summary[0],
            'native_gap_instruction_starts': len(results['code']), 'output': TRACE}


def main() -> int:
    try:
        print(json.dumps(capture(), indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'runtime trace failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
