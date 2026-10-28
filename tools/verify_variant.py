"""Validate a complete target build against current source, assets and controls."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from .build_rom import source_regions
from .build_variant import input_names, dispatch_inventory
from .build_variant_source import digest
from .identify_rom import inspect_rom
from .native_control_flow import inventory as native_inventory
from .project import IDENTITY_PARTS
from .source_variants import compose, load_profile, target_regions
from .verify_variant_source import verify as verify_source
from . import variant_assets

ARTIFACTS = ('bible-adventures.nes', 'bible-adventures.dbg', 'bible-adventures.map',
             'source/rom.s', 'source/nes.inc', 'source/link.cfg')


def verify(root: Path, target: dict) -> dict:
    directory = root / 'build' / target['id']
    raw = (directory / 'proof.json').read_bytes();proof = json.loads(raw)
    profile = load_profile(root, target['id'])
    config = json.loads((root / profile['canonical_map']).read_text())
    source = compose((root / profile['canonical_source']).read_text(), (root / profile['reset_source']).read_text(), profile)
    regions = source_regions({**config, 'regions': target_regions(config, profile['geometry'])}, 16)
    hashes = {name: digest((root / name).read_bytes()) for name in input_names(profile, config)}
    reference = (root / target['input_path']).read_bytes();parsed = inspect_rom(reference)
    if (any(parsed[part] != target['reference'][part] for part in IDENTITY_PARTS)
            or proof.get('schema_version') != 1 or proof.get('target') != target['id']
            or proof.get('match') is not True or proof.get('reference_sha256') != digest(reference)
            or proof.get('candidate_sha256') != digest(reference)
            or proof.get('source_sha256') != digest(source.encode()) or proof.get('regions') != regions
            or proof.get('input_sha256') != hashes):
        raise ValueError('variant build inputs are missing, incomplete or stale')
    if (proof.get('build_artifact_sha256') != {name: digest((directory / name).read_bytes()) for name in ARTIFACTS}
            or (directory / 'bible-adventures.nes').read_bytes() != reference
            or (directory / 'source/rom.s').read_text() != source
            or (directory / 'source/nes.inc').read_bytes() != (root / 'include/nes.inc').read_bytes()
            or (directory / 'source/link.cfg').read_bytes() != (root / config['linker_config']).read_bytes()):
        raise ValueError('variant retained build or source artifact differs')
    prg = reference[16:65552]
    selected = variant_assets.select(root, prg, reference[65552:], parsed['file']['sha256'], profile)
    expected_assets = {name: {'source': row['source'], 'input_sha256': row['input_sha256'],
                             'asset_sha256': digest(variant_assets.MODULES[name].serialize(row['asset'])),
                             'options': json.loads(json.dumps(row['options']))} for name, row in selected.items()}
    if proof.get('assets') != expected_assets:
        raise ValueError('variant local asset selection differs from the build')
    for name, row in selected.items():
        if (directory / 'assets' / (name + '.json')).read_bytes() != variant_assets.MODULES[name].serialize(row['asset']):
            raise ValueError('variant retained decoded asset differs: ' + name)
    gaps = variant_assets.encoded_gaps(prg, regions, proof['gaps'], variant_assets.spans(selected))
    checkpoint, checkpoint_sha = verify_source(root, target, profile, config, source, regions, gaps, selected['chr']['payload'])
    if (proof.get('source_control_checkpoint') != f'analysis/{target["id"]}/source-checkpoint/source-proof.json'
            or proof.get('source_control_checkpoint_sha256') != checkpoint_sha
            or proof.get('gaps') != checkpoint['gaps']
            or proof.get('source_controls') != len(checkpoint['controls'])
            or proof.get('symbol_controls') != len(checkpoint['symbol_controls'])
            or proof.get('gap_sha256') != {name: digest(data) for name, data in gaps.items()}):
        raise ValueError('variant source-control or decoded-gap evidence differs')
    if ((directory / 'inputs/header.bin').read_bytes() != reference[:16]
            or (directory / 'inputs/chr.bin').read_bytes() != selected['chr']['payload']
            or any((directory / 'inputs' / name).read_bytes() != data for name, data in gaps.items())):
        raise ValueError('variant compiler asset inputs differ')
    if set(proof.get('asset_controls', {})) != set(selected):
        raise ValueError('variant asset controls are incomplete')
    for name, row in selected.items():
        module = variant_assets.MODULES[name]
        changed_asset, changed = variant_assets.changed_payload(name, root, row, prg, parsed['file']['sha256'])
        control = directory / 'controls' / name
        candidate = (control / 'candidate.nes').read_bytes()
        if name == 'chr':offsets = module.verify_control(reference, candidate, parsed['chr']['offset'])
        elif name == 'map_chunks':offsets = module.verify_control(reference, candidate, 16)
        elif name == 'packed_text':offsets = module.verify_control(reference, candidate, 16, row['payload'], changed)
        else:offsets = module.verify_control(reference, candidate, 16, row['asset'])
        expected = {'candidate_sha256': digest(candidate), 'changed_offsets': offsets,
                    'asset_sha256': digest(module.serialize(changed_asset))}
        if proof['asset_controls'][name] != expected or (control / 'asset.json').read_bytes() != module.serialize(changed_asset):
            raise ValueError('variant asset control differs: ' + name)
    native = native_inventory((directory / 'bible-adventures.dbg').read_text(), source, prg, regions)
    dispatch = dispatch_inventory(prg, profile['geometry'], native, regions)
    if (json.loads((directory / 'native-inventory.json').read_text()) != native
            or json.loads((directory / 'dispatch-inventory.json').read_text()) != dispatch
            or proof.get('native') != {'instructions': native['instruction_count'], 'bytes': native['instruction_code_bytes']}):
        raise ValueError('variant native inventory differs')
    counts = Counter()
    for row in regions:counts[row['kind']] += row['size']
    expected_counts = {'code_bytes': counts['code'], 'data_bytes': counts['data'], 'fill_bytes': counts['fill'],
                       'local_prg_bytes': sum(map(len, gaps.values())), 'local_chr_bytes': len(reference[65552:])}
    if proof.get('counts') != expected_counts or sum(expected_counts[k] for k in ('code_bytes', 'data_bytes', 'fill_bytes', 'local_prg_bytes')) != 65536:
        raise ValueError('variant physical ownership counts differ')
    if (raw != (directory / 'proof.json').read_bytes()
            or hashes != {name: digest((root / name).read_bytes()) for name in hashes}):
        raise ValueError('variant build inputs changed during verification')
    return {**{key: expected_counts[key] for key in ('code_bytes', 'data_bytes', 'fill_bytes')},
            'source_sha256': proof['source_sha256'],
            'source_map_sha256': digest(json.dumps({'target': target['id'], 'regions': regions}, sort_keys=True).encode()),
            'toolchain_revision': json.loads((root / 'config/cc65-toolchain.json').read_text())['revision']}
