"""Build a release's shared-source candidate and its source-change checkpoint.

Local PRG asset gaps are still scaffolding here. A matching candidate is not
target acceptance: target asset codecs/controls and the inventory review must
also be integrated. Never install this checkpoint as a full-build proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from .build_rom import (MUTATIONS, SYMBOL_CONTROLS, assemble, mutate_include, mutate_source,
                        source_regions, verify_control, verify_symbol_control)
from .identify_rom import inspect_rom
from .native_control_flow import inventory as native_inventory
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools
from .source_variants import compose, load_profile, target_regions

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('tools/build_variant_source.py', 'tools/source_variants.py', 'tools/build_rom.py',
          'tools/setup.py', 'tools/project.py', 'tools/identify_rom.py', 'tools/native_control_flow.py',
          'tools/nes6502.py', 'tools/verify_native_opcodes.py', 'include/nes.inc', 'config/cc65-toolchain.json')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_patch(original: str, changed: str) -> dict:
    """One exact replacement range; no duplicate full source per control."""
    if original == changed:
        raise ValueError('source control was erased by variant composition')
    start = 0
    while start < min(len(original), len(changed)) and original[start] == changed[start]:
        start += 1
    suffix = 0
    limit = min(len(original), len(changed)) - start
    while suffix < limit and original[len(original) - suffix - 1] == changed[len(changed) - suffix - 1]:
        suffix += 1
    end = len(original) - suffix
    return {'start': start, 'end': end, 'removed_sha256': digest(original[start:end].encode()),
            'replacement': changed[start:len(changed) - suffix]}


def apply_source_patch(original: str, patch: dict) -> str:
    start, end = patch['start'], patch['end']
    if (type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(original)
            or not isinstance(patch['replacement'], str)
            or digest(original[start:end].encode()) != patch['removed_sha256']):
        raise ValueError('invalid compact source control')
    return original[:start] + patch['replacement'] + original[end:]


def gap_inputs(reference: bytes, config: dict, profile: dict, destination: Path) -> list[dict]:
    """Bind logical input filenames to their target's physical asset gaps."""
    layout = profile['geometry']
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'header.bin').write_bytes(reference[:16])
    (destination / 'chr.bin').write_bytes(reference[16 + 65536:])
    prg = reference[16:16 + 65536]
    result = []
    for bank in (0, 1):
        cursor = 0
        rows = sorted((r for r in config['regions'] if r['bank'] == bank), key=lambda r: int(r['cpu'], 0))
        for row in [*rows, {'cpu': '0x10000', 'size': 0}]:
            end = int(row['cpu'], 0) - 0x8000
            if cursor < end:
                mapped_start, mapped_end = layout.offset(bank, cursor), layout.offset(bank, end)
                if mapped_start >= mapped_end:
                    raise ValueError('target asset gap collapses')
                payload = prg[bank * 32768 + mapped_start:bank * 32768 + mapped_end]
                name = f'bank{bank}_{cursor + 32768:04x}_{end + 32768:04x}.bin'
                (destination / name).write_bytes(payload)
                result.append({'name': name, 'bank': bank, 'cpu': f'0x{mapped_start + 32768:04x}',
                               'size': len(payload), 'sha256': digest(payload)})
            cursor = end + row['size']
    return result


def build(target_id: str, *, all_controls: bool) -> dict:
    profile = load_profile(ROOT, target_id)
    target = load_target(ROOT, target_id)
    reference_path = ROOT / target['input_path']
    reference = reference_path.read_bytes()
    actual = inspect_rom(reference)
    if any(actual[part] != target['reference'][part] for part in IDENTITY_PARTS):
        raise ValueError('variant input differs from reviewed identity')
    if (actual['prg']['offset'], actual['prg']['size'], actual['chr']['offset'], actual['chr']['size']) != (16, 65536, 65552, 65536):
        raise ValueError('unsupported variant container geometry')
    config = json.loads((ROOT / profile['canonical_map']).read_text())
    regions = source_regions({**config, 'regions': target_regions(config, profile['geometry'])}, 16)
    canonical = (ROOT / profile['canonical_source']).read_text()
    reset = (ROOT / profile['reset_source']).read_text()
    source = compose(canonical, reset, profile)
    names = [*INPUTS, f'config/variants/{target_id}.json', f'config/targets/{target_id}.json',
             profile['canonical_source'], profile['canonical_map'], profile['reset_source'], config['linker_config']]
    hashes = {name: digest((ROOT / name).read_bytes()) for name in names}
    paths = (ROOT / 'analysis', ROOT / 'analysis' / target_id,
             ROOT / 'analysis' / target_id / 'source-checkpoint')
    if any(p.is_symlink() for p in paths):
        raise ValueError('refusing symlinked variant checkpoint')
    work = paths[-1]
    (work / 'source').mkdir(parents=True, exist_ok=True)
    tools = verified_tools(ROOT)
    (work / 'source/rom.s').write_text(source)
    shutil.copyfile(ROOT / 'include/nes.inc', work / 'source/nes.inc')
    shutil.copyfile(ROOT / config['linker_config'], work / 'source/link.cfg')
    gaps = gap_inputs(reference, config, profile, work / 'inputs')
    candidate_path = assemble(work, tools, Path('source/rom.s'), Path('candidate'))
    candidate = candidate_path.read_bytes()
    if candidate != reference:
        changed = [i for i, pair in enumerate(zip(reference, candidate)) if pair[0] != pair[1]]
        raise ValueError(f'variant candidate differs: {len(changed)} bytes; first {changed[:8]}')
    native = native_inventory((work / 'candidate.dbg').read_text(), source, reference[16:16 + 65536], regions)
    native_path = ROOT / 'analysis' / target_id / 'native-control-flow.json'
    native_path.write_text(json.dumps(native, indent=2) + '\n')
    selected = list(MUTATIONS) if all_controls else [
        'boot', 'reset_dispatch', 'slot_runtime_d52b', 'overlay_b077', 'partial_resource_ad18',
        'record_da40_prefix', 'record_voice_e01a', 'record_script_e090', 'record_storage_e040',
        'menu_queue_first', 'retained_record_tail_eb08', 'slot_related_address']
    controls = []
    folder = work / 'controls'
    folder.mkdir(exist_ok=True)
    include = (ROOT / 'include/nes.inc').read_bytes()
    common_inputs = {'linker_sha256': hashes[config['linker_config']],
                     'gap_sha256': {row['name']: row['sha256'] for row in gaps},
                     'header_sha256': digest(reference[:16]), 'chr_sha256': digest(reference[65552:]),
                     'tool_sha256': {key: digest(path.read_bytes()) for key, path in tools.items()}}
    common_hash = digest(json.dumps(common_inputs, sort_keys=True).encode())

    def compile_control(name: str, changed: str, changed_include: bytes, verify) -> dict:
        patch = source_patch(source, changed) if source != changed else None
        if patch is not None and apply_source_patch(source, patch) != changed:
            raise ValueError('compact source control does not reproduce compiler input')
        include_patch = source_patch(include.decode(), changed_include.decode()) if changed_include != include else None
        if patch is None and include_patch is None:
            raise ValueError('variant composition erased the source change: ' + name)
        artifact = folder / name
        artifact.mkdir(exist_ok=True)
        context = {'source_sha256': digest(changed.encode()), 'include_sha256': digest(changed_include),
                   'build_inputs_sha256': common_hash}
        receipt = artifact / 'receipt.json'
        cached = json.loads(receipt.read_text()) if receipt.exists() else None
        output = artifact / 'candidate.nes'
        if not (cached and cached.get('context') == context and output.exists()
                and digest(output.read_bytes()) == cached.get('candidate_sha256')):
            (work / 'control-source.s').write_text(changed)
            (work / 'source/nes.inc').write_bytes(changed_include)
            try:
                control_path = assemble(work, tools, Path('control-source.s'), Path('control-candidate'))
                shutil.copyfile(control_path, output)
            finally:
                (work / 'source/nes.inc').write_bytes(include)
        payload = output.read_bytes()
        row = {'control': name, 'context': context, 'source_patch': patch, 'include_patch': include_patch,
               'candidate_sha256': digest(payload), 'changed_offsets': verify(payload)}
        receipt.write_text(json.dumps(row, indent=2) + '\n')
        return row

    for index, name in enumerate(selected, 1):
        if name == 'reset_dispatch':
            changed = compose(canonical, mutate_source(reset, name), profile)
        else:
            changed = compose(mutate_source(canonical, name), reset, profile)
        # Reuse only an identical compiler input with pinned tools, include,
        # linker and gap payloads. This is a per-control compile cache, not a
        # substitution of a reference ROM for assembly.
        row = compile_control(name, changed, include, lambda payload: verify_control(reference, payload, regions, name))
        row['affected_regions'] = [r['id'] for r in regions if r['control'] == name]
        controls.append(row)
        if index % 100 == 0 or index == len(selected):
            print(f'{target_id}: {index}/{len(selected)} source controls', flush=True)
    symbol_controls = []
    if all_controls:
        for name in SYMBOL_CONTROLS:
            changed_include = mutate_include(include.decode(), name).encode()
            row = compile_control('symbol_' + name, source, changed_include,
                                  lambda payload: verify_symbol_control(reference, payload, regions, name))
            symbol_controls.append(row)
    if (digest(reference_path.read_bytes()) != target['reference']['file']['sha256']
            or hashes != {name: digest((ROOT / name).read_bytes()) for name in names}
            or verified_tools(ROOT) != tools
            or common_inputs['tool_sha256'] != {key: digest(path.read_bytes()) for key, path in tools.items()}):
        raise ValueError('variant source inputs changed during verification')
    proof = {'schema_version': 1, 'target': target_id, 'reference_sha256': digest(reference),
             'match': True, 'candidate_sha256': digest(candidate), 'source_sha256': digest(source.encode()),
             'input_sha256': hashes, 'regions': regions, 'gaps': gaps, 'controls': controls,
             'symbol_controls': symbol_controls, 'build_inputs': common_inputs,
             'all_source_controls': all_controls, 'native_instruction_count': native['instruction_count'],
             'native_instruction_bytes': native['instruction_code_bytes'],
             'asset_codec_verification': 'pending', 'inventory_acceptance': 'pending',
             'scope': 'Source-composition checkpoint. Local asset gaps remain scaffolding; this is not a full target acceptance proof.'}
    (work / 'source-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    for name in ('control-source.s', 'control-candidate.o', 'control-candidate.lst',
                 'control-candidate.map', 'control-candidate.dbg', 'control-candidate.nes'):
        (work / name).unlink(missing_ok=True)
    return proof


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True)
    parser.add_argument('--all-controls', action='store_true')
    args = parser.parse_args()
    try:
        proof = build(args.target, all_controls=args.all_controls)
        print(json.dumps({key: proof[key] for key in ('target', 'match', 'all_source_controls',
                          'native_instruction_count', 'native_instruction_bytes', 'asset_codec_verification',
                          'inventory_acceptance')}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f'variant source build failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
