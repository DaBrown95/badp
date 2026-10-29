"""Assemble a shared-source release using decoded local assets and exact controls."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from .build_rom import assemble, retire_control_intermediates, source_regions
from .build_variant_source import digest
from .identify_rom import inspect_rom
from .native_control_flow import inventory as native_inventory, DISPATCH_LOW, DISPATCH_HIGH, LENGTH_TABLE
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools
from .source_variants import compose, load_profile, source_paths, variant_regions, target_include
from . import variant_controls
from . import variant_assets
from .verify_variant_source import verify as verify_source

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('tools/build_variant.py', 'tools/verify_variant_source.py', 'tools/variant_assets.py', 'tools/asset_paths.py',
          'tools/chr_assets.py', 'tools/map_assets.py', 'tools/map_data.py', 'tools/map_layout_assets.py',
          'tools/text_assets.py', 'tools/menu_assets.py', 'tools/palette_assets.py', 'tools/ppu_assets.py',
          'tools/ppu_streams.py', 'tools/sprite_assets.py', 'tools/sprite_metadata.py', 'tools/packed_text.py')


def input_names(profile: dict, config: dict) -> set[str]:
    return set(INPUTS) | set(variant_assets.MANIFESTS.values()) | set(source_paths(profile)) | {
        'include/nes.inc', config['linker_config'], profile['canonical_source'], profile['canonical_map'],
        profile['reset_source'], f'config/variants/{profile["target"]}.json', f'config/targets/{profile["target"]}.json',
        'tools/source_variants.py', 'tools/build_rom.py', 'tools/setup.py', 'tools/project.py', 'tools/variant_controls.py',
        'tools/identify_rom.py', 'config/catalogues/no-intro-nes.json', 'config/cc65-toolchain.json', 'tools/native_control_flow.py', 'tools/nes6502.py'} | (
        {'tools/legacy_source.py', *({'tools/earlier_source.py'} if profile['target'] in ('us-v1.2', 'us-v1.1') else set())}
        if profile['target'] in ('us-v1.3', 'us-v1.2', 'us-v1.1') else set()) | (
        {'tools/v11_source.py', 'tools/v11_controls.py'} if profile['target'] == 'us-v1.1' else set())


def dispatch_inventory(prg: bytes, layout, native: dict, regions: list[dict], nominal: int = 197) -> dict:
    low, high = layout.offset(0, DISPATCH_LOW), layout.offset(0, DISPATCH_HIGH)
    lengths = layout.offset(0, LENGTH_TABLE)
    if prg[lengths:lengths + 256] != prg[32768 + lengths:32768 + lengths + 256]:
        raise ValueError('variant length lookups differ between physical banks')
    starts = {(row['bank'], int(row['cpu'], 0)) for row in native['instructions']}
    kinds = ['local_asset'] * 65536
    for row in regions:
        start = row['bank'] * 32768 + int(row['cpu'], 0) - 32768
        kinds[start:start + row['size']] = [row['kind']] * row['size']
    rows = []
    for index in range(256):
        target = ((prg[low + index] | prg[high + index] << 8) + 1) & 65535
        row = {'opcode': index, 'target_cpu': f'0x{target:04x}', 'record_length': prg[lengths + index],
               'effective_fetch_bytes': prg[lengths + index] or 256,
               'bank0_instruction_start': (0, target) in starts, 'bank1_instruction_start': (1, target) in starts,
               'physical_uses': [kinds[bank * 32768 + target - 32768] if target >= 32768 else 'outside_prg'
                                 for bank in (0, 1)]}
        if index < nominal and not row['bank0_instruction_start']:
            raise ValueError('nominal variant script handler is not a source instruction start')
        rows.append(row)
    return {'nominal_entries': nominal, 'byte_indices': 256, 'entries': rows,
            'scope': 'Actual target table values and physical representations; additional indices are conditional aliases, not newly declared routines.'}


def reviewed_tail_transfer(source: str, row: dict) -> bool:
    """Recognize only the two existing bank-tail transfers from actual spans.

    RAM/inline-form changes can move a site within the shared macro, so its
    source-associated assembler line is stronger evidence than adding one
    interval delta to the primary site's CPU address.
    """
    if row.get('bank') != 1 or row.get('other_bank_instruction_start') is not True:
        return False
    lines = source.splitlines()
    definitions = [i for i, line in enumerate(lines) if line.startswith('.macro BankTail ')]
    if len(definitions) != 1:
        return False
    start = definitions[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i] == '.endmacro'), None)
    number = row.get('source_line')
    if end is None or type(number) is not int or not start < number - 1 < end:
        return False
    statement = ' '.join(lines[number - 1].partition(';')[0].split())
    return (row.get('operation'), statement) in (
        ('jsr', 'jsr Bank0::NmiFrameWork'), ('jmp', 'jmp Bank0::Boot'))


def build(target_id: str) -> dict:
    profile = load_profile(ROOT, target_id);target = load_target(ROOT, target_id)
    reference_path = ROOT / target['input_path'];reference = reference_path.read_bytes()
    parsed = inspect_rom(reference)
    if any(parsed[part] != target['reference'][part] for part in IDENTITY_PARTS):
        raise ValueError('variant input differs from reviewed reference')
    config = json.loads((ROOT / profile['canonical_map']).read_text())
    regions = source_regions({**config, 'regions': variant_regions(config, profile)}, 16,
                             controls=set(variant_controls.names(profile)), require_all_controls=target_id == 'us-v1.4')
    source = compose((ROOT / profile['canonical_source']).read_text(), (ROOT / profile['reset_source']).read_text(), profile)
    prg, chr_data = reference[16:65552], reference[65552:]
    names = input_names(profile, config)
    hashes = {name: digest((ROOT / name).read_bytes()) for name in sorted(names)}
    selected = variant_assets.select(ROOT, prg, chr_data, parsed['file']['sha256'], profile)
    source_path = ROOT / 'analysis' / target_id / 'source-checkpoint/source-proof.json'
    checkpoint = json.loads(source_path.read_text())
    payloads = variant_assets.spans(selected)
    gaps = variant_assets.encoded_gaps(prg, regions, checkpoint['gaps'], payloads)
    source_proof, source_proof_sha = verify_source(ROOT, target, profile, config, source, regions, gaps, selected['chr']['payload'])
    tools = verified_tools(ROOT)
    base, final = ROOT / 'build', ROOT / 'build' / target_id
    if final.is_symlink():raise ValueError('refusing symlinked variant build')
    base.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'.{target_id}-', dir=base) as temporary:
        work = Path(temporary) / 'proof';(work / 'source').mkdir(parents=True)
        (work / 'source/rom.s').write_text(source)
        (work / 'source/nes.inc').write_text(target_include((ROOT / 'include/nes.inc').read_text(), profile))
        shutil.copyfile(ROOT / config['linker_config'], work / 'source/link.cfg')
        (work / 'inputs').mkdir();(work / 'assets').mkdir()

        def write_inputs(folder: Path, data: dict[str, bytes], chr_payload: bytes):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / 'header.bin').write_bytes(reference[:16])
            (folder / 'chr.bin').write_bytes(chr_payload)
            for name, payload in data.items():(folder / name).write_bytes(payload)

        write_inputs(work / 'inputs', gaps, selected['chr']['payload'])
        for name, row in selected.items():
            (work / 'assets' / (name + '.json')).write_bytes(variant_assets.MODULES[name].serialize(row['asset']))
        candidate_path = assemble(work, tools, Path('source/rom.s'), Path('bible-adventures'))
        candidate = candidate_path.read_bytes()
        if candidate != reference:raise ValueError('decoded-asset variant build differs from the fixed reference')
        native = native_inventory((work / 'bible-adventures.dbg').read_text(), source, prg, regions)
        if native['same_bank_non_instruction_start_targets']:
            raise ValueError('variant direct transfer points into a source instruction')
        for row in native['same_bank_non_code_targets']:
            conditional = profile.get('conditional_native_transfer_sites', {})
            if (row['bank'] == 1 and row['cpu'] in conditional
                    and row['target_cpu'] == conditional[row['cpu']]['target_cpu']
                    and row.get('other_bank_instruction_start') is True):
                continue
            if not reviewed_tail_transfer(source, row):
                raise ValueError('unreviewed variant native bank transition')
        dispatch = dispatch_inventory(prg, profile['geometry'], native, regions, profile.get('nominal_script_entries', 197))
        asset_controls = {}
        for name, row in selected.items():
            module = variant_assets.MODULES[name]
            changed_asset, changed = variant_assets.changed_payload(name, ROOT, row, prg, parsed['file']['sha256'])
            control = work / 'controls' / name;control.mkdir(parents=True)
            (control / 'asset.json').write_bytes(module.serialize(changed_asset))
            if name == 'chr':
                altered_gaps, altered_chr = gaps, changed
            else:
                altered_gaps = variant_assets.encoded_gaps(prg, regions, checkpoint['gaps'], {**payloads, name: changed})
                altered_chr = selected['chr']['payload']
            write_inputs(control / 'inputs', altered_gaps, altered_chr)
            negative_path = assemble(work, tools, Path('source/rom.s'), Path('controls') / name / 'candidate',
                                     Path('controls') / name / 'inputs')
            negative = negative_path.read_bytes()
            if name == 'chr':changed_offsets = module.verify_control(reference, negative, parsed['chr']['offset'])
            elif name == 'map_chunks':changed_offsets = module.verify_control(reference, negative, 16)
            elif name == 'packed_text':changed_offsets = module.verify_control(reference, negative, 16, row['payload'], changed)
            else:changed_offsets = module.verify_control(reference, negative, 16, row['asset'])
            asset_controls[name] = {'candidate_sha256': digest(negative), 'changed_offsets': changed_offsets,
                                    'asset_sha256': digest(module.serialize(changed_asset))}
            retire_control_intermediates(control)
            shutil.rmtree(control / 'inputs')
        if (hashes != {name: digest((ROOT / name).read_bytes()) for name in names}
                or digest(reference_path.read_bytes()) != parsed['file']['sha256']
                or digest(source_path.read_bytes()) != source_proof_sha):
            raise ValueError('variant build inputs changed during verification')
        counts = Counter()
        for row in regions:counts[row['kind']] += row['size']
        proof = {'schema_version': 1, 'target': target_id, 'match': True, 'reference_sha256': parsed['file']['sha256'],
                 'candidate_sha256': digest(candidate), 'source_sha256': digest(source.encode()), 'input_sha256': hashes,
                 'source_control_checkpoint': f'analysis/{target_id}/source-checkpoint/source-proof.json',
                 'source_control_checkpoint_sha256': source_proof_sha,
                 'source_controls': len(source_proof['controls']), 'symbol_controls': len(source_proof['symbol_controls']),
                 'regions': regions, 'gaps': checkpoint['gaps'], 'gap_sha256': {name: digest(data) for name, data in gaps.items()},
                 'assets': {name: {'source': row['source'], 'input_sha256': row['input_sha256'],
                                    'asset_sha256': digest(variant_assets.MODULES[name].serialize(row['asset'])),
                                    'options': row['options']} for name, row in selected.items()},
                 'asset_controls': asset_controls, 'native': {'instructions': native['instruction_count'],
                                    'bytes': native['instruction_code_bytes']},
                 'counts': {'code_bytes': counts['code'], 'data_bytes': counts['data'], 'fill_bytes': counts['fill'],
                            'local_prg_bytes': sum(map(len, gaps.values())), 'local_chr_bytes': len(chr_data)},
                 'build_artifact_sha256': {name: digest((work / name).read_bytes()) for name in
                                           ('bible-adventures.nes', 'bible-adventures.dbg', 'bible-adventures.map',
                                            'source/rom.s', 'source/nes.inc', 'source/link.cfg')}}
        (work / 'native-inventory.json').write_text(json.dumps(native, indent=2) + '\n')
        (work / 'dispatch-inventory.json').write_text(json.dumps(dispatch, indent=2) + '\n')
        (work / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        previous = base / ('.previous-' + target_id)
        if previous.exists():shutil.rmtree(previous)
        if final.exists():final.rename(previous)
        try:work.rename(final)
        except OSError:
            if previous.exists():previous.rename(final)
            raise
        if previous.exists():shutil.rmtree(previous)
    return proof
