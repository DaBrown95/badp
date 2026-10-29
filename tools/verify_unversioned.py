"""Check retained full-build freshness and replay the own control definitions."""
from __future__ import annotations

import json
from pathlib import Path

from .build_rom import digest
from .build_unversioned import (CONTROLS, TARGET, asset_control_offsets, checked_differences,
                                input_names, map_matches, mutate)
from .build_variant_source import apply_source_patch
from .identify_rom import inspect_rom
from .native_control_flow import inventory as native_inventory
from .project import IDENTITY_PARTS
from .setup import verified_tools
from .unversioned_assets import GROUPS, load as load_assets, encode as encode_assets, changed as changed_assets
from .unversioned_inventory import source_partition
from .unversioned_source import full_source
from .v11_source import include


def verify(root: Path, target: dict) -> dict:
    if target['id'] != TARGET:raise ValueError('incorrect own verification target')
    folder = root / 'build' / TARGET
    proof = json.loads((folder / 'proof.json').read_text())
    reference = (root / target['input_path']).read_bytes()
    identity = inspect_rom(reference)
    if any(identity[key] != target['reference'][key] for key in IDENTITY_PARTS):
        raise ValueError('own reference differs from reviewed input')
    hashes = {name: digest((root / name).read_bytes()) for name in sorted(input_names(root))}
    source, nes = full_source(root), include((root / 'include/nes.inc').read_text())
    actual = (folder / 'bible-adventures.nes').read_bytes()
    debug = (folder / 'bible-adventures.dbg').read_text()
    if (proof['target'] != TARGET or proof['match'] is not True or actual != reference
            or proof['reference_sha256'] != digest(reference) or proof['output_sha256'] != digest(actual)
            or proof['input_sha256'] != hashes or proof['source_sha256'] != digest(source.encode())
            or proof['include_sha256'] != digest(nes.encode()) or proof['debug_sha256'] != digest(debug.encode())
            or (folder / 'source/rom.s').read_text() != source
            or (folder / 'source/nes.inc').read_text() != nes
            or (folder / 'source/link.cfg').read_bytes() != (root / 'config/link-us-v1.5.cfg').read_bytes()
            or proof['tool_sha256'] != {name: digest(path.read_bytes()) for name, path in verified_tools(root).items()}
            or proof['component_matches'] != {key: True for key in IDENTITY_PARTS}):
        raise ValueError('own complete build proof is stale, uncontrolled or mismatching')
    assets, asset_hashes = load_assets(root)
    payloads = encode_assets(root, assets, reference)
    if (proof['asset_input_sha256'] != asset_hashes
            or proof['payload_sha256'] != {name: digest(data) for name, data in payloads.items()}
            or any((folder / 'inputs' / name).read_bytes() != data for name, data in payloads.items())):
        raise ValueError('own editable-input build evidence is stale')
    config_bytes = (root / 'config/source-us-unversioned.json').read_bytes()
    config = json.loads(config_bytes)
    rows = source_partition(debug, source, actual[16:65552], payloads)
    if (not map_matches(rows, config) or proof['regions'] != config['regions']
            or proof['source_map_sha256'] != digest(config_bytes)):
        raise ValueError('own physical source map is stale')
    counts = {kind: sum(row['size'] for row in rows if row['kind'] == kind)
              for kind in ('code', 'data', 'fill', 'asset')}
    if proof['representation_bytes'] != counts:
        raise ValueError('own representation totals differ')
    if proof['counts'] != {'code_bytes': counts['code'], 'data_bytes': counts['data'],
                           'fill_bytes': counts['fill'], 'local_prg_bytes': counts['asset'], 'local_chr_bytes': 65536}:
        raise ValueError('own public build counts differ')
    native = native_inventory(debug, source, actual[16:65552], config['regions'])
    if native != json.loads((folder / 'native-inventory.json').read_text()):
        raise ValueError('own native inventory is stale')
    allowed = {16 + row['bank'] * 32768 + int(row['cpu'], 0) - 32768 + i
               for row in rows if row['kind'] != 'asset' for i in range(row['size'])}
    if len(proof['source_controls']) != len(CONTROLS):raise ValueError('missing own source controls')
    for control, row in zip(CONTROLS, proof['source_controls']):
        changed = mutate(source, control)
        candidate = (folder / 'controls' / (control[0] + '.nes')).read_bytes()
        if (row['control'] != control[0] or apply_source_patch(source, row['source_patch']) != changed
                or row['source_sha256'] != digest(changed.encode()) or row['candidate_sha256'] != digest(candidate)
                or row['changed_offsets'] != checked_differences(reference, candidate, allowed)):
            raise ValueError('invalid own changed-source control: ' + control[0])
    if len(proof['asset_controls']) != len(GROUPS):raise ValueError('missing own asset controls')
    for group, row in zip(GROUPS, proof['asset_controls']):
        selected = changed_assets(root, assets, group)
        files = encode_assets(root, selected, reference)
        wanted = asset_control_offsets(rows, payloads, files)
        candidate = (folder / 'controls' / ('asset-' + group + '.nes')).read_bytes()
        if (row['group'] != group or row['candidate_sha256'] != digest(candidate)
                or row['changed_asset_sha256'] != digest(json.dumps(selected[group], sort_keys=True).encode())
                or row['changed_offsets'] != checked_differences(reference, candidate, set(wanted))
                or row['changed_offsets'] != sorted(wanted) or any(candidate[i] != value for i, value in wanted.items())):
            raise ValueError('invalid own changed-asset control: ' + group)
    return {'code_bytes': counts['code'], 'data_bytes': counts['data'], 'fill_bytes': counts['fill'],
            'source_sha256': proof['source_sha256'], 'source_map_sha256': proof['source_map_sha256'],
            'toolchain_revision': json.loads((root / 'config/cc65-toolchain.json').read_text())['revision']}
