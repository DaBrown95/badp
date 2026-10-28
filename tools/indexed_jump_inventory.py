"""Investigate the $F434 indexed jump with controlled, bounded evidence.

The adjacent $3F/$24 path yields at most 31 if the same slot reaches $44
without an intervening write. Direct entry to $44 remains unbounded by that
predecessor. Table words and reference game data stay in ignored analysis.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from . import map_data
from .build_rom import source_regions
from .mesen_runtime import FLAGS, SDL2
from .progress import verify_primary
from .project import input_path
from .script_entries import ROOT, load_audited_banks
from .setup_mesen import digest_file, spec, verify_emulator

TABLE = 0x7435


def field_value(value: int) -> int:
    """Model $3F/$24's selected field, without asserting the input is reachable."""
    if type(value) is not int or not 0 <= value <= 255:
        raise ValueError('invalid slot field')
    return (value >> 4) + ((value & 8) << 1)


def indexed_address(value: int, base: int = TABLE) -> int:
    """Model the 8-bit ASL followed by the pointer addition in opcode $44."""
    if (type(value) is not int or not 0 <= value <= 255
            or type(base) is not int or not 0 <= base <= 0xffff):
        raise ValueError('invalid index or base')
    return (base + ((value << 1) & 0xff)) & 0xffff


def parse_probe(output: str, kind: str) -> dict:
    """Require both carry states for every value in a deterministic order."""
    if kind not in ('FIELD', 'INDEX'):
        raise ValueError('unknown probe kind')
    count = 0
    summary = None
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == kind:
            if len(parts) != (6 if kind == 'FIELD' else 4) or count >= 512:
                raise ValueError('malformed or excess probe observation')
            try:
                value, carry = int(parts[1], 16), int(parts[2])
                observed = [int(part, 16) for part in parts[3:]]
            except ValueError as exc:
                raise ValueError('invalid probe observation') from exc
            if (value, carry) != (count % 256, count // 256):
                raise ValueError('probe observations are out of order')
            expected = ([field_value(value), 0, 5] if kind == 'FIELD'
                        else [indexed_address(value)])
            if observed != expected:
                raise ValueError('probe differs from the source model')
            count += 1
        elif parts[0] == 'DONE':
            if summary is not None or len(parts) != 3:
                raise ValueError('malformed probe summary')
            try:
                summary = tuple(int(part) for part in parts[1:])
            except ValueError as exc:
                raise ValueError('invalid probe summary') from exc
    if count != 512 or summary != (512, 0):
        raise ValueError('incomplete or failed probe')
    return {'cases': count}


def inspect_entries(bank1: bytes, regions: list[dict], layouts: list[tuple[int, int]],
                    base: int = TABLE) -> list[dict]:
    """Describe all 128 distinct indexed reads under physical bank-1 mapping."""
    if len(bank1) != 0x8000 or type(base) is not int or not 0 <= base <= 0x7fff:
        raise ValueError('invalid bank or table base')
    owners = {}
    for region in regions:
        if region['bank'] != 1:
            continue
        start = int(region['cpu'], 0) - 0x8000
        for offset in range(start, start + region['size']):
            owners[offset] = region['kind']
    entries = []
    for index in range(128):
        position = indexed_address(index, base)
        if position + 2 > 0x8000:
            raise ValueError('indexed read crosses the bank boundary')
        categories = sorted({owners.get(position + i, 'local') for i in range(2)})
        layout_bytes = sum(any(start <= position + i < start + size for start, size in layouts)
                           for i in range(2))
        target = int.from_bytes(bank1[position:position + 2], 'little')
        entries.append({'index': index, 'encoded_read': f'0x{position:04x}',
                        'cpu_read': f'0x{position + 0x8000:04x}',
                        'physical_prg_offset': 0x8000 + position,
                        'encoded_target': f'0x{target:04x}', 'source_kinds': categories,
                        'candidate_map_layout_bytes': layout_bytes,
                        'preceded_by_selector_candidate': index < 32,
                        'within_three_source_entries': index < 3})
    return entries


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        if bank1[0x7432:0x7435] != bytes([0x3f, 0x24, 0x44]) or lengths[0x3f] != 2 or lengths[0x44] != 1:
            raise ValueError('the selected script sequence does not match the audited reference')
        proof = verify_primary(ROOT, target)
        reference = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        built = ROOT / 'build/us-v1.5/bible-adventures.nes'
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        scripts = (ROOT / 'tools/mesen_field_selector.lua', ROOT / 'tools/mesen_index_address.lua')
        inputs = (*scripts, ROOT / 'tools/indexed_jump_inventory.py', ROOT / 'tools/mesen_runtime.py',
                  ROOT / 'tools/setup_mesen.py', ROOT / 'tools/map_data.py',
                  ROOT / 'tools/script_entries.py', ROOT / 'config/source-us-v1.5.json',
                  ROOT / 'config/targets/us-v1.5.json')
        hashes = {str(path.relative_to(ROOT)): digest_file(path) for path in inputs}
        proof_hash = digest_file(proof_path)
        sdl_hash = digest_file(SDL2)
        exe = verify_emulator(ROOT)
        emulator = spec(ROOT)
        environment = {key: value for key, value in os.environ.items() if not key.startswith('DYLD_')}
        results = {}
        for name, rom in (('reference', reference), ('build', built)):
            observations = []
            for script, kind in zip(scripts, ('FIELD', 'INDEX')):
                run = subprocess.run([str(exe), *FLAGS, str(script), str(rom)], cwd=ROOT,
                                     env=environment, capture_output=True, text=True,
                                     timeout=60, check=True)
                observations.append(parse_probe(run.stdout, kind))
            results[name] = {'field': observations[0], 'index': observations[1]}
            print(f'{name}: 512 field cases, 512 indexed-address cases', flush=True)
        if results['reference'] != results['build']:
            raise ValueError('reference and build observations differ')
        config = json.loads((ROOT / 'config/source-us-v1.5.json').read_text())
        regions = source_regions(config, target['reference']['prg']['offset'])
        table_regions = [region for region in regions if region['id'] == 'bank1-extended-jump-f435']
        if (len(table_regions) != 1 or table_regions[0]['bank'] != 1
                or int(table_regions[0]['cpu'], 0) != 0xf435 or table_regions[0]['size'] != 6):
            raise ValueError('the three source table entries have changed')
        maps = map_data.inventory(bank0, bank1)
        layouts = [(item['location']['bank_offset'], item['decoded']['size'])
                   for item in maps['layouts'] if item['location']['bank'] == 1]
        entries = inspect_entries(bank1, regions, layouts)
        if (digest_file(reference) != target['reference']['file']['sha256']
                or digest_file(proof_path) != proof_hash or digest_file(SDL2) != sdl_hash
                or verify_emulator(ROOT) != exe
                or {str(path.relative_to(ROOT)): digest_file(path) for path in inputs} != hashes
                or verify_primary(ROOT, target)['source_sha256'] != proof['source_sha256']):
            raise ValueError('indexed-jump verification inputs changed')
        output = ROOT / 'analysis/us-v1.5/indexed-jump-inventory.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to((ROOT / 'analysis').resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps({'target': 'us-v1.5', 'reference_sha256': target['reference']['file']['sha256'],
                                      'source_sha256': proof['source_sha256'], 'build_proof_sha256': proof_hash,
                                      'input_sha256': hashes, 'emulator_core_sha256': emulator['core_sha256'],
                                      'system_sdl2_sha256': sdl_hash, 'observations': results,
                                      'entries': entries,
                                      'scope': 'controlled handler inputs; bank-1 table mapping and uninterrupted predecessor are conditional'},
                                     indent=2) + '\n')
        print('Local indexed-jump evidence saved to analysis/us-v1.5/indexed-jump-inventory.json')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'indexed-jump inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
