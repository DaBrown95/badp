"""Investigate indexed jumps with controlled, bounded evidence.

The adjacent $3F/$24 path yields at most 31 if the same slot reaches $44
without an intervening write. Direct entry to $44 remains unbounded by that
predecessor. Table words and reference game data stay in ignored analysis.
"""
from __future__ import annotations

from collections import Counter
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
from .script_entries import ROOT, _locate, _location, load_audited_banks
from .script_flow import PRIMARY_INDEXED_JUMPS, PredecessorIndexedJump
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
                    base: int = TABLE, *, predecessor_count: int = 32,
                    source_entry_count: int = 3, chunks: tuple[tuple[int, int], ...] = ()) -> list[dict]:
    """Describe all 128 distinct indexed reads under physical bank-1 mapping."""
    if (len(bank1) != 0x8000 or type(base) is not int or not 0 <= base <= 0x7fff
            or type(predecessor_count) is not int or not 1 <= predecessor_count <= 128
            or type(source_entry_count) is not int or not 0 <= source_entry_count <= 128):
        raise ValueError('invalid bank or table base')
    for start, size in (*layouts, *chunks):
        if (type(start) is not int or type(size) is not int or start < 0 or size <= 0
                or start + size > 0x8000):
            raise ValueError('invalid candidate map span')
    owners = {}
    for region in regions:
        start = int(region['cpu'], 0) - 0x8000
        if (type(region['bank']) is not int or region['bank'] not in (0, 1)
                or type(region['size']) is not int or region['size'] <= 0 or start < 0
                or start + region['size'] > 0x8000 or region['kind'] not in ('code', 'data')):
            raise ValueError('invalid source region')
        for offset in range(start, start + region['size']):
            owners[(region['bank'], offset)] = region['kind']
    entries = []
    for index in range(128):
        position = indexed_address(index, base)
        if position + 2 > 0x8000:
            raise ValueError('indexed read crosses the bank boundary')
        categories = sorted({owners.get((1, position + i), 'local') for i in range(2)})
        layout_bytes = sum(any(start <= position + i < start + size for start, size in layouts)
                           for i in range(2))
        chunk_bytes = sum(any(start <= position + i < start + size for start, size in chunks)
                          for i in range(2))
        target = int.from_bytes(bank1[position:position + 2], 'little')
        target_bank, target_offset = _locate(target)
        entries.append({'index': index, 'encoded_read': f'0x{position:04x}',
                        'cpu_read': f'0x{position + 0x8000:04x}',
                        'physical_prg_offset': 0x8000 + position,
                        'encoded_target': f'0x{target:04x}', 'source_kinds': categories,
                        'candidate_target_location': _location(target_bank, target_offset),
                        'candidate_target_source_kind': owners.get((target_bank, target_offset), 'local'),
                        'candidate_map_layout_bytes': layout_bytes,
                        'candidate_map_chunk_bytes': chunk_bytes,
                        'within_predecessor_scope': index < predecessor_count,
                        'within_structured_entries': index < source_entry_count})
    return entries


def summarize_entries(entries: list[dict]) -> dict:
    """Count candidate reads outside the predecessor path, not execution."""
    if len(entries) != 128 or [row['index'] for row in entries] != list(range(128)):
        raise ValueError('indexed entries are incomplete or out of order')
    if any(type(row['within_predecessor_scope']) is not bool for row in entries):
        raise ValueError('invalid predecessor-scope marker')
    outside = [row for row in entries if not row['within_predecessor_scope']]
    targets = Counter(row['candidate_target_source_kind'] for row in outside)
    if set(targets) - {'code', 'data', 'local'}:
        raise ValueError('invalid candidate target ownership')
    return {'outside_predecessor_entries': len(outside),
            'outside_reads_touching_local_entries': sum('local' in row['source_kinds'] for row in outside),
            'outside_reads_touching_map_chunks': sum(row['candidate_map_chunk_bytes'] > 0 for row in outside),
            'outside_reads_touching_map_layouts': sum(row['candidate_map_layout_bytes'] > 0 for row in outside),
            'outside_candidate_target_kinds': {kind: targets[kind] for kind in ('code', 'data', 'local')}}


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
                  ROOT / 'tools/script_entries.py', ROOT / 'tools/script_flow.py',
                  ROOT / 'config/source-us-v1.5.json',
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
        chunks = tuple((item['location']['bank_offset'], map_data.CHUNK_SIZE)
                       for item in maps['chunks'])
        entries = inspect_entries(bank1, regions, layouts, chunks=chunks)
        other_tables = []
        for site, config_entry in PRIMARY_INDEXED_JUMPS.items():
            if not isinstance(config_entry, PredecessorIndexedJump):
                continue
            if bank1[site] != 0x44:
                raise ValueError('predecessor-bounded site is not an indexed jump')
            rows = inspect_entries(bank1, regions, layouts, site + 1,
                                   predecessor_count=config_entry.count,
                                   source_entry_count=config_entry.count, chunks=chunks)
            if any(row['source_kinds'] != ['data'] for row in rows[:config_entry.count]):
                raise ValueError('predecessor-bounded source table is not fully owned data')
            other_tables.append({'site': f'0x{site + 0x8000:04x}',
                                 'condition': config_entry.condition,
                                 'predecessor_candidate_entries': config_entry.count,
                                 'summary': summarize_entries(rows),
                                 'entries': rows})
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
                                      'entries': entries, 'summary': summarize_entries(entries),
                                      'predecessor_tables': other_tables,
                                      'scope': 'controlled handler inputs; bank-1 table mapping and uninterrupted predecessor are conditional'},
                                     indent=2) + '\n')
        print(json.dumps({'f434': summarize_entries(entries),
                          'predecessor_tables': [{'site': table['site'], **table['summary']}
                                                 for table in other_tables],
                          'output': 'analysis/us-v1.5/indexed-jump-inventory.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'indexed-jump inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
