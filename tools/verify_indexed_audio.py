"""Verify unbounded $B3 lookups and isolated candidate audio fragments.

Inputs are injected; this does not establish ordinary-play reachability or
physical cartridge behavior. The timer is forced to one between commands.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from .audio_commands import decode_command
from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SCRIPT = 'tools/mesen_indexed_audio.lua'
INPUTS = (SCRIPT, 'tools/verify_indexed_audio.py', 'tools/audio_commands.py', 'tools/script_entries.py',
          'tools/mesen_runtime.py', 'tools/setup_mesen.py', 'config/mesence-toolchain.json',
          'config/targets/us-v1.5.json')


def expected_events(bank0: bytes, bank1: bytes) -> list[str]:
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two complete PRG banks')
    indices = (0x451b, 0xc51b, 0x451a, 0x16a6, 0x96a6, 0x16a5, 0x1365, 0x5176, 0x5178)
    expected = []
    for case, index in enumerate(indices):
        pointer = (0x26d0 + 2 * index) & 0xffff
        bank = 1 if pointer < 0x8000 else 0
        cpu = pointer | 0x8000
        if cpu == 0xffff:
            raise ValueError('lookup crosses the controlled PRG window')
        pair = (bank0, bank1)[bank][cpu - 0x8000:cpu - 0x8000 + 2]
        result = int.from_bytes(pair, 'little')
        target = 0x2814 if case < 3 else 0x2c54 if case < 6 else 0x2817 if case == 6 else 0x2818
        negative = case in (2, 5)
        if (not negative and result != target) or (negative and (result == target or result >> 8 in (0, 0xff))):
            raise ValueError('audited pointer pair does not support the controlled cases')
        for i, value in enumerate(pair):
            addr = cpu + i
            physical = bank * 0x8000 + addr - 0x8000
            expected.append(f'PAIR {case} {addr:04X} {physical:05X} {value:02X}')
        expected.append(f'VOICE {case} C0 01 {result & 255:02X} {result >> 8:02X}')
        if not negative:
            starts = ((0xa814, 0xa815, 0xa81a, 0xa81c) if case < 3 else
                      (0xac54, 0xac55, 0xac56, 0xac57) if case < 6 else
                      (0xa817, 0xa818, 0xa81a, 0xa81c) if case == 6 else
                      (0xa818, 0xa81a, 0xa81c))
            commands = [decode_command(bank1[p - 0x8000:p - 0x8000 + 5]) for p in starts]
            if case < 3:
                if ([c['kind'] for c in commands] != ['select_channel', 'write_five', 'delay', 'stop_voice']
                        or commands[0]['channel'] != 1 or commands[2]['duration'] != 8):
                    raise ValueError('candidate A814 stream has unexpected command structure')
                outcomes = ((0x84, 1, 0x2815), (0x84, 1, 0x281a), (0x84, 8, 0x281c), (0, 1, 0x281d))
            elif case < 6:
                if ([c['kind'] for c in commands] != ['instrument', 'select_channel', 'instrument', 'stop_voice']
                        or commands[0]['instrument'] != 1 or commands[1]['channel'] != 2
                        or commands[2]['instrument'] != 1):
                    raise ValueError('candidate AC54 stream has unexpected command structure')
                outcomes = ((0xc0, 1, 0x2c55), (0x88, 1, 0x2c56), (0x88, 1, 0x2c57), (0, 1, 0x2c58))
            else:
                kinds = ['note', 'write_register', 'delay', 'stop_voice'] if case == 6 else ['write_register', 'delay', 'stop_voice']
                if ([c['kind'] for c in commands] != kinds or commands[-2]['duration'] != 8
                        or commands[-3]['register'] != 2):
                    raise ValueError('overlapping candidate audio entry has unexpected structure')
                common = ((0xc0, 1, 0x281a), (0xc0, 8, 0x281c), (0, 1, 0x281d))
                if case == 6:
                    timing = bank0[0x1267 + 2 * commands[0]['duration_index']]
                    outcomes = ((0xc0, timing, 0x2818),) + common
                else:
                    outcomes = common
            for command, (start, (flags, timer, cursor)) in enumerate(zip(starts, outcomes), 1):
                for i in range(5):
                    addr = start + i
                    expected.append(f'AUDIO {case} {addr:04X} {addr:05X} {bank1[addr - 0x8000]:02X}')
                expected.append(f'AFTER {case} {command * 5} {flags:02X} {timer:02X} {cursor & 255:02X} {cursor >> 8:02X}')
        expected.append(f'RESULT {case} 0')
    expected.extend(fragment_events(bank1))
    expected.append('DONE 13')
    return expected


def fragment_events(bank1: bytes) -> list[str]:
    """Model four isolated fragments; starts are conditional, not discovered play."""
    if len(bank1) != 0x8000:
        raise ValueError('expected one complete audio bank')
    cases = (
        (0xa6f6, (0, 2), ('delay', 'stop_voice'), (0xc0, 0)),
        (0xa757, (0, 1, 6, 8), ('select_channel', 'write_five', 'delay', 'stop_voice'), (0x80, 0x80, 0x80, 0)),
        (0xa8a4, (0, 1, 6, 8), ('select_channel', 'write_five', 'delay', 'stop_voice'), (0x8c, 0x8c, 0x8c, 0)),
        (0xac53, (0, 1, 2, 3, 4), ('select_channel', 'instrument', 'select_channel', 'instrument', 'stop_voice'), (0x84, 0x84, 0x88, 0x88, 0)),
    )
    result = []
    for case, (base, offsets, kinds, flags) in enumerate(cases, 9):
        for step, (offset, kind, flag) in enumerate(zip(offsets, kinds, flags), 1):
            start = base + offset
            raw = bank1[start - 0x8000:start - 0x8000 + 5]
            decoded = decode_command(raw)
            if decoded['kind'] != kind:
                raise ValueError('isolated audio fragment has unexpected command structure')
            if kind == 'select_channel' and decoded['channel'] * 4 != flag & 0x1f:
                raise ValueError('isolated audio fragment selects an unexpected channel')
            if kind == 'instrument' and decoded['instrument'] != 1:
                raise ValueError('isolated audio fragment selects an unexpected instrument')
            for i, value in enumerate(raw):
                result.append(f'AUDIO {case} {start + i:04X} {start + i:05X} {value:02X}')
            timer = decoded['duration'] if kind == 'delay' else 1
            cursor = start - 0x8000 + decoded['size']
            result.append(f'AFTER {case} {step * 5} {flag:02X} {timer:02X} {cursor & 255:02X} {cursor >> 8:02X}')
        result.append(f'RESULT {case} 0')
    return result


def parse_output(output: str, expected: list[str]) -> dict:
    events = []
    for line in output.splitlines():
        word = line.split(maxsplit=1)[0] if line.split() else ''
        if word in {'TIMEOUT', 'LOAD_FAILED'}:
            raise ValueError('controlled indexed-audio probe failed')
        if word in {'PAIR', 'VOICE', 'AUDIO', 'AFTER', 'RESULT', 'DONE'}:
            events.append(line.strip())
    if events != expected:
        raise ValueError('indexed-audio observations differ from the controlled model')
    return {'cases': 13, 'fragment_cases': 4, 'alias_cases': 4, 'changed_index_controls': 2, 'overlap_cases': 3, 'interrupts': 0}


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        expected = expected_events(bank0, bank1)
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        build = ROOT / 'build/us-v1.5/bible-adventures.nes'
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        sdl_hash = digest_file(SDL2)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        observations = {}
        for name, rom in (('reference', reference), ('build', build)):
            run = subprocess.run([str(exe), *FLAGS, str(ROOT / SCRIPT), str(rom)], cwd=ROOT,
                                 env=env, capture_output=True, text=True, timeout=60, check=True)
            observations[name] = parse_output(run.stdout, expected)
            print(f'{name}: {observations[name]["cases"]} controlled indexed-audio cases', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build indexed-audio observations differ')
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('indexed-audio verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/indexed-audio-verification.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        result = {'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                  'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                  'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                  'system_sdl2_sha256': sdl_hash, 'observations': observations,
                  'scope': 'injected slot values and four isolated fragment starts; timer forced between commands; no gameplay reachability or hardware claim'}
        output.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved controlled evidence to analysis/us-v1.5/indexed-audio-verification.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'indexed-audio verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
