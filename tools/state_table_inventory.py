"""Check BOGUS $AF state-table reads and conditional palette fetch addresses.

The CPU is injected into the handler with controlled state/selector inputs.
The static fetch plans assume bank 0 is mapped while palette data is read;
they do not establish reachability, interrupt timing or physical wiring.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys

from .build_rom import source_regions
from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

SELECTORS = tuple(range(256))
BYTE_TABLE = 0xa37e
BG_TABLE = 0xa394
SPRITE_TABLE = 0xa3c0
NOMINAL_STATES = 22
SCRIPT = 'tools/mesen_state_tables.lua'
INPUTS = (SCRIPT, 'tools/state_table_inventory.py', 'tools/mesen_runtime.py', 'tools/setup_mesen.py',
          'tools/script_entries.py', 'config/mesence-toolchain.json', 'config/targets/us-v1.5.json',
          'config/source-us-v1.5.json')


def af_result(bank0: bytes, state: int, selector: int) -> int:
    """Return the handler's low/high slot pair under bank-0 mapping."""
    if (len(bank0) != BANK_SIZE or type(state) is not int or not 0 <= state <= 255
            or type(selector) is not int or selector not in SELECTORS):
        raise ValueError('invalid state-table model input')
    if selector == 0x0f:
        return state
    if selector == 0xaa:
        return bank0[BYTE_TABLE - 0x8000 + state]
    index = (state << 1) & 0xff
    base = BG_TABLE if selector == 0x4d else SPRITE_TABLE
    start = base - 0x8000 + index
    return int.from_bytes(bank0[start:start + 2], 'little')


def parse_probe(output: str, bank0: bytes) -> dict:
    """Require every controlled input, both result bytes, mapping and no NMI."""
    count = 0
    done = False
    for line in output.splitlines():
        fields = line.split()
        if not fields or fields[0] not in {'STATE', 'DONE', 'TIMEOUT', 'LOAD_FAILED'}:
            continue
        if done or fields[0] in {'TIMEOUT', 'LOAD_FAILED'}:
            raise ValueError('unexpected or failed state-table trace')
        if fields[0] == 'DONE':
            if fields != ['DONE', str(len(SELECTORS) * 256)] or count != len(SELECTORS) * 256:
                raise ValueError('invalid state-table summary')
            done = True
            continue
        if len(fields) != 10 or count >= len(SELECTORS) * 256:
            raise ValueError('malformed state-table observation')
        try:
            case = int(fields[1])
            state, selector, low, high, physical = (int(x, 16) for x in fields[2:7])
            interrupts, read_trace, bad_reads = (int(x) for x in fields[7:10])
        except ValueError as exc:
            raise ValueError('invalid state-table observation') from exc
        if case != count or state != count % 256 or selector != SELECTORS[count // 256]:
            raise ValueError('state-table observations are out of order')
        expected_reads = 0 if selector == 0x0f else 1 if selector == 0xaa else 123 if selector == 0x4d else 12345
        if ((low | high << 8) != af_result(bank0, state, selector) or physical != 0x6915 or interrupts != 0
                or read_trace != expected_reads or bad_reads != 0):
            raise ValueError('state-table observation differs from the controlled model')
        count += 1
    if not done:
        raise ValueError('missing state-table summary')
    return {'cases': count, 'states': 256, 'selectors': 256, 'interrupts': 0}


def cpu_region(address: int) -> str:
    if type(address) is not int or not 0 <= address <= 0xffff:
        raise ValueError('invalid CPU address')
    if address < 0x2000:
        return 'internal_ram'
    if address < 0x4000:
        return 'ppu_register'
    if address < 0x4018:
        return 'apu_or_controller'
    if address < 0x4020:
        return 'test_io'
    if address < 0x6000:
        return 'expansion'
    if address < 0x8000:
        return 'cartridge_low'
    return 'program_rom'


def read_plan(pointer: int, *, sprite: bool) -> dict:
    """Describe effective CPU addresses read by setup, including wrap.

    This is not a bus-cycle model. In particular, it excludes dummy reads,
    asynchronous mapper changes and the values or side effects of I/O reads.
    """
    if type(pointer) is not int or not 0 <= pointer <= 0xffff or type(sprite) is not bool:
        raise ValueError('invalid palette pointer')
    header = [(pointer + i) & 0xffff for i in range(3)]
    payload = [(pointer + (4 if sprite else 3) + i) & 0xffff for i in range(15 if sprite else 16)]
    def item(address: int) -> dict:
        region = cpu_region(address)
        return {'cpu': f'0x{address:04x}', 'region': region,
                'bank0_prg_offset': address - 0x8000 if region == 'program_rom' else None}
    return {'header': [item(x) for x in header], 'initial_payload': [item(x) for x in payload],
            'crosses_ffff': pointer + 18 > 0xffff}


def inventory(bank0: bytes, regions: list[dict]) -> dict:
    if len(bank0) != BANK_SIZE:
        raise ValueError('expected one full PRG bank')
    owner = ['local'] * BANK_SIZE
    for region in regions:
        if region['bank'] != 0:
            continue
        start = int(region['cpu'], 0) - 0x8000
        size = region['size']
        if (type(size) is not int or size <= 0 or start < 0 or start + size > BANK_SIZE
                or region['kind'] not in ('code', 'data', 'fill')):
            raise ValueError('invalid source region')
        for pos in range(start, start + size):
            if owner[pos] != 'local':
                raise ValueError('overlapping source regions')
            owner[pos] = region['kind']
    rows = []
    summaries = {'background': Counter(), 'sprite': Counter()}
    for state in range(256):
        index = (state << 1) & 0xff
        row = {'state': f'0x{state:02x}', 'doubled_index': index,
               'byte_index_in_nominal_table': state < NOMINAL_STATES,
               'pointer_index_in_nominal_table': index < 2 * NOMINAL_STATES,
               'byte_table_cpu': f'0x{BYTE_TABLE + state:04x}',
               'byte_table_ownership': owner[BYTE_TABLE + state - 0x8000],
               'selector_value': af_result(bank0, state, 0xaa)}
        for name, selector, base, sprite in (('background', 0x4d, BG_TABLE, False),
                                             ('sprite', 0x4e, SPRITE_TABLE, True)):
            pointer = af_result(bank0, state, selector)
            plan = read_plan(pointer, sprite=sprite)
            header = plan['header']
            header_ownership = sorted({owner[x['bank0_prg_offset']] if x['region'] == 'program_rom'
                                       else x['region'] for x in header})
            item = {'table_cpu': f'0x{base + index:04x}',
                    'table_ownership': sorted(set(owner[base - 0x8000 + index:base - 0x8000 + index + 2])),
                    'pointer': f'0x{pointer:04x}', 'header_ownership': header_ownership, 'fetch_plan': plan}
            row[name] = item
            if not row['pointer_index_in_nominal_table']:
                if plan['crosses_ffff'] and any(x['region'] != 'program_rom' for x in header):
                    category = 'header_wraps_out_of_prg'
                elif all(x['region'] == 'program_rom' for x in header):
                    category = 'prg_' + '_and_'.join(header_ownership)
                else:
                    category = 'non_prg_or_mixed_header'
                summaries[name][category] += 1
        rows.append(row)
    return {'states': rows, 'summary': {name: dict(sorted(counts.items())) for name, counts in summaries.items()},
            'scope': 'all injected state values; palette plans are conditional on applying the result and bank-0 '
                     'mapping, not proof of gameplay reachability, bus cycles or physical cartridge behavior'}


def main() -> int:
    try:
        target, bank0, _, _ = load_audited_banks()
        proof = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_hash = digest_file(proof_path)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        built = ROOT / 'build/us-v1.5/bible-adventures.nes'
        hashes = {name: digest_file(ROOT / name) for name in INPUTS}
        sdl_hash = digest_file(SDL2)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        env = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        observations = {}
        probe_flags = tuple('--timeout=90' if flag == '--timeout=30' else flag for flag in FLAGS)
        for name, rom in (('reference', reference), ('build', built)):
            proc = subprocess.run([str(exe), *probe_flags, str(ROOT / SCRIPT), str(rom)], cwd=ROOT,
                                  env=env, capture_output=True, text=True, timeout=120, check=True)
            observations[name] = parse_probe(proc.stdout, bank0)
            print(f'{name}: {observations[name]["cases"]} controlled state/selector cases', flush=True)
        if observations['reference'] != observations['build']:
            raise ValueError('reference and build state-table observations differ')
        config = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())
        regions = source_regions(config, target['reference']['prg']['offset'])
        result = inventory(bank0, regions)
        if (digest_file(reference) != target['reference']['file']['sha256'] or digest_file(proof_path) != proof_hash
                or digest_file(SDL2) != sdl_hash or verify_emulator(ROOT) != exe or verify_primary(ROOT, target) != proof
                or hashes != {name: digest_file(ROOT / name) for name in INPUTS}):
            raise ValueError('state-table verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/state-table-inventory.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('state-table output escapes its local directory')
        result.update(target='us-v1.5', reference_sha256=target['reference']['file']['sha256'],
                      source_sha256=proof['source_sha256'], build_proof_sha256=proof_hash,
                      input_sha256=hashes, emulator_core_sha256=emulator['core_sha256'],
                      system_sdl2_sha256=sdl_hash, observations=observations)
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'summary': result['summary'], 'output': 'analysis/us-v1.5/state-table-inventory.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'state-table inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
