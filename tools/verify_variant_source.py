"""Reuse a source checkpoint only for identical maintained and compiler inputs."""
from __future__ import annotations

import json
from pathlib import Path

from .build_rom import MUTATIONS, SYMBOL_CONTROLS, verify_control, verify_symbol_control
from .build_variant_source import INPUTS, apply_source_patch, digest
from .setup import verified_tools


def verify(root: Path, target: dict, profile: dict, config: dict, source: str,
           regions: list[dict], gaps: dict[str, bytes], chr_payload: bytes) -> tuple[dict, str]:
    directory = root / 'analysis' / target['id'] / 'source-checkpoint'
    path = directory / 'source-proof.json'
    raw = path.read_bytes();proof = json.loads(raw)
    expected_inputs = set(INPUTS) | {f'config/variants/{target["id"]}.json', f'config/targets/{target["id"]}.json',
                                    profile['canonical_source'], profile['canonical_map'], profile['reset_source'], config['linker_config']}
    if (proof.get('schema_version') != 1 or proof.get('target') != target['id'] or proof.get('match') is not True
            or proof.get('all_source_controls') is not True
            or proof.get('reference_sha256') != target['reference']['file']['sha256']
            or proof.get('source_sha256') != digest(source.encode()) or proof.get('regions') != regions
            or set(proof.get('input_sha256', {})) != expected_inputs
            or any(digest((root / name).read_bytes()) != value for name, value in proof['input_sha256'].items())):
        raise ValueError('variant source checkpoint is missing, incomplete or stale')
    reference = (root / target['input_path']).read_bytes()
    if digest(reference) != proof['reference_sha256']:
        raise ValueError('variant reference differs from its source checkpoint')
    include = (root / 'include/nes.inc').read_bytes()
    tools = verified_tools(root)
    common = {'linker_sha256': digest((root / config['linker_config']).read_bytes()),
              'gap_sha256': {name: digest(payload) for name, payload in gaps.items()},
              'header_sha256': digest(reference[:16]), 'chr_sha256': digest(chr_payload),
              'tool_sha256': {name: digest(binary.read_bytes()) for name, binary in tools.items()}}
    if common != proof['build_inputs'] or (directory / 'source/rom.s').read_text() != source:
        raise ValueError('decoded asset or compiler inputs differ from the source-control checkpoint')
    common_sha = digest(json.dumps(common, sort_keys=True).encode())
    controls, symbols = proof.get('controls', []), proof.get('symbol_controls', [])
    if (len(controls) != len(MUTATIONS) or {row['control'] for row in controls} != set(MUTATIONS)
            or len(symbols) != len(SYMBOL_CONTROLS)
            or {row['control'] for row in symbols} != {'symbol_' + name for name in SYMBOL_CONTROLS}):
        raise ValueError('variant source or symbol controls are incomplete or duplicated')
    # The unchanged input fingerprint above includes the producer, source
    # renderer and mutation catalogue. Reconstruct its exact compiler inputs
    # from compact patches, then recheck every retained negative ROM against
    # this target and its current physical ownership map.
    for row in controls + symbols:
        name = row['control'];symbol = name.startswith('symbol_')
        changed_source = apply_source_patch(source, row['source_patch']) if row['source_patch'] else source
        changed_include = apply_source_patch(include.decode(), row['include_patch']).encode() if row['include_patch'] else include
        if (row['context'] != {'source_sha256': digest(changed_source.encode()),
                               'include_sha256': digest(changed_include), 'build_inputs_sha256': common_sha}
                or (not symbol and (row['source_patch'] is None or row['include_patch'] is not None))
                or (symbol and (row['source_patch'] is not None or row['include_patch'] is None))):
            raise ValueError('invalid reconstructed variant control input: ' + name)
        candidate = (directory / 'controls' / name / 'candidate.nes').read_bytes()
        observed = (verify_symbol_control(reference, candidate, regions, name.removeprefix('symbol_')) if symbol
                    else verify_control(reference, candidate, regions, name))
        if digest(candidate) != row['candidate_sha256'] or observed != row['changed_offsets']:
            raise ValueError('variant source-control artifact differs: ' + name)
    if path.read_bytes() != raw:
        raise ValueError('source checkpoint changed during validation')
    return proof, digest(raw)
