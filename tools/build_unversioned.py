"""Build the complete unversioned release with own source and asset controls.

This target shares the readable engine and codecs. It has its own physical
layout, record/script source, exact reference and review decision ledger.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .build_rom import digest
from .build_unversioned_bank0 import INPUTS as BANK0_INPUTS
from .build_variant_source import source_patch
from .identify_rom import inspect_rom
from .native_control_flow import inventory as native_inventory
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools
from .source_variants import load_profile, marked_statement, operands, source_paths
from .unversioned_assets import GROUPS, INPUTS as ASSET_INPUTS, ensure_inputs, load as load_assets, encode as encode_assets, changed as changed_assets
from .unversioned_inventory import source_partition
from .unversioned_source import full_source
from .v11_source import include

TARGET = 'us-unversioned'
INPUTS = ('tools/build_unversioned.py', 'tools/unversioned_inventory.py',
          'tools/verify_unversioned.py',
          'tools/native_control_flow.py', 'tools/nes6502.py', 'tools/build_variant_source.py',
          'tools/build_unversioned_bank0.py', 'config/source-us-unversioned.json',
          'src/variants/audio-us-unversioned.inc', 'src/variants/opening-scripts-us-unversioned.inc',
          'src/variants/main-scripts-us-unversioned.inc', 'src/variants/text-us-unversioned.inc',
          'src/variants/retained-resource-us-unversioned.inc', 'config/link-us-v1.5.cfg')
# Connected replacement scopes, each changed in an isolated complete fresh build.
# Data fields are kept distinct from native instruction changes.
CONTROLS = (
    ('boot-interrupt-mask', 'CONTROL_BOOT', None, 'cli'),
    ('mapper-write-index', 'CONTROL_SWITCH', None, 'sta BankValues + 1,y'),
    ('nmi-split-address', 'CONTROL_UNVERSIONED_NMI_SPLIT', None, 'lda #$26'),
    ('slot-flag-9d', 'CONTROL_UNVERSIONED_SLOT_FLAG_9D', None, 'lda $C1,x'),
    ('negate-fields-b4', 'CONTROL_UNVERSIONED_NEGATE_B4', None, 'lda RecordBuffer2'),
    ('first-slot-search', 'CONTROL_SCRIPT_OP35', None, 'lda RecordBuffer4'),
    ('selected-field-mask', 'CONTROL_UNVERSIONED_SCRIPT_FIELD_MASK', None, 'and #$01'),
    ('direct-native-word', 'CONTROL_UNVERSIONED_DIRECT_NATIVE_CALL', None, 'lda RecordBuffer3'),
    ('selected-word-compare', 'CONTROL_UNVERSIONED_SELECTED_PAIR_COMPARE', None, 'lda $43,y'),
    ('descriptor-first-field', 'CONTROL_SLOT_DESCRIPTOR', 1, '$01'),
    ('descriptor-list-id', 'CONTROL_UNVERSIONED_DESCRIPTOR_LIST_A229', 0, '$0F'),
    ('position-constructor', 'CONTROL_UNVERSIONED_POSITION_CONSTRUCTOR_A559', 3, '$01'),
    ('audio-pointer', 'CONTROL_UNVERSIONED_AUDIO_POINTER', 0, '(UnversionedAudioA66A - BankStart)'),
    ('audio-register', 'CONTROL_UNVERSIONED_AUDIO_REGISTER_VALUES', 0, '$9C'),
    ('audio-note', 'CONTROL_UNVERSIONED_AUDIO_NOTE', 1, '$1E'),
    ('audio-loop', 'CONTROL_UNVERSIONED_AUDIO_LOOP', 0, '$05'),
    ('opening-resource', 'CONTROL_UNVERSIONED_PREFIX_AA48', 0, '$BD2D'),
    ('opening-dispatch', 'CONTROL_UNVERSIONED_PREFIX_AAEA', 0, '$8E'),
    ('opening-indexed-base', 'CONTROL_UNVERSIONED_PREFIX_B5A8', 0, 'UnversionedStateBytesB5E8 + 1'),
    ('message-pointer', 'CONTROL_UNVERSIONED_MESSAGE_POINTERS', 0, 'UnversionedMessage00 - BankStart + 1'),
    ('main-resource', 'CONTROL_UNVERSIONED_MAIN_D393', 0, '$C290'),
    ('main-indexed-target', 'CONTROL_UNVERSIONED_MAIN_E71C', 0, '$E72D'),
    ('menu-source-pointer', 'CONTROL_UNVERSIONED_MAIN_F22D', 0, '$73EF'),
    ('final-slot-release', 'CONTROL_UNVERSIONED_MAIN_F426', None, 'BogusCopyLinkedMotionFields'),
    ('retained-resource-word', 'CONTROL_UNVERSIONED_RETAINED_RESOURCE_WORD', 0, 'UnversionedRetainedFrameFC39 - BankStart + 1'),
    ('map-grid-width', 'CONTROL_UNVERSIONED_MAP_HEADER_F42C', 0, '$35'),
)


def input_names(root: Path) -> set[str]:
    return set(INPUTS) | set(BANK0_INPUTS) | set(ASSET_INPUTS) | set(source_paths(load_profile(root, 'us-v1.1')))


def mutate(source: str, control: tuple) -> str:
    _, marker, index, value = control
    def change(text: str) -> str:
        if index is None:return value
        name, args = text.split(maxsplit=1)
        fields = operands(args)
        if not 0 <= index < len(fields):raise ValueError('own control field leaves statement')
        fields[index] = value
        return name + ' ' + ', '.join(fields)
    return marked_statement(source, marker, change)


def checked_differences(reference: bytes, candidate: bytes, allowed: set[int]) -> list[int]:
    if len(reference) != len(candidate):raise ValueError('own control changed ROM size')
    offsets = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if not offsets or not set(offsets) <= allowed:
        raise ValueError('own control was erased or changed another representation')
    return offsets


def map_matches(rows: list[dict], config: dict) -> bool:
    source = [{k: v for k, v in row.items() if k != 'id'} for row in config['regions']]
    expected = sorted(source + config['asset_regions'], key=lambda row: (row['bank'], int(row['cpu'], 0)))
    return rows == expected


def asset_control_offsets(rows: list[dict], before: dict, after: dict) -> dict[int, int]:
    wanted = {}
    if before.keys() != after.keys():raise ValueError('asset control changed input identities')
    for row in rows:
        if row['kind'] != 'asset':continue
        name = row['asset'];a, b = before[name], after[name]
        if len(a) != len(b) or len(a) != row['size']:
            raise ValueError('asset control changed encoded extent')
        start = 16 + row['bank'] * 32768 + int(row['cpu'], 0) - 32768
        wanted.update((start + i, value) for i, (old, value) in enumerate(zip(a, b)) if old != value)
    a, b = before['chr.bin'], after['chr.bin']
    if len(a) != len(b) or len(a) != 65536:raise ValueError('asset control changed CHR extent')
    wanted.update((65552 + i, value) for i, (old, value) in enumerate(zip(a, b)) if old != value)
    if not wanted:raise ValueError('own asset control changed no encoded byte')
    return wanted


def build(root: Path) -> dict:
    target = load_target(root, TARGET)
    reference = (root / target['input_path']).read_bytes()
    identity = inspect_rom(reference)
    if any(identity[key] != target['reference'][key] for key in IDENTITY_PARTS):
        raise ValueError('own reference differs from reviewed identity')
    names = input_names(root)
    hashes = {name: digest((root / name).read_bytes()) for name in sorted(names)}
    ensure_inputs(root, reference)
    assets, asset_hashes = load_assets(root)
    payloads = encode_assets(root, assets, reference)
    source, nes = full_source(root), include((root / 'include/nes.inc').read_text())
    config = json.loads((root / 'config/source-us-unversioned.json').read_text())
    tools = verified_tools(root)
    build_root = root / 'build'
    destination = build_root / TARGET
    if any(p.is_symlink() for p in (build_root, destination)):
        raise ValueError('refusing a symlinked own build output')
    build_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.unversioned-full-', dir=build_root) as directory:
        work = Path(directory)
        for name in ('source', 'inputs', 'controls'): (work / name).mkdir()
        (work / 'source/nes.inc').write_text(nes)
        (work / 'source/link.cfg').write_bytes((root / 'config/link-us-v1.5.cfg').read_bytes())
        def write_inputs(files):
            for name, data in files.items():(work / 'inputs' / name).write_bytes(data)
        def assemble(text, name, *, keep_debug=False):
            (work / 'source/rom.s').write_text(text)
            try:
                subprocess.run([str(tools['ca65']), '-g', '-I', 'source', '--bin-include-dir', 'inputs',
                                'source/rom.s', '-o', 'candidate.o'], cwd=work, check=True, capture_output=True)
                command = [str(tools['ld65']), '-C', 'source/link.cfg', 'candidate.o', '-o', name]
                if keep_debug:command += ['--dbgfile', 'bible-adventures.dbg']
                subprocess.run(command, cwd=work, check=True, capture_output=True)
            except subprocess.CalledProcessError as exc:
                raise ValueError('own assembly failed: ' + exc.stderr.decode(errors='replace')) from exc
            return (work / name).read_bytes()
        write_inputs(payloads)
        actual = assemble(source, 'bible-adventures.nes', keep_debug=True)
        if actual != reference:raise ValueError('own complete ROM source does not match')
        debug = (work / 'bible-adventures.dbg').read_text()
        rows = source_partition(debug, source, actual[16:65552], payloads)
        if not map_matches(rows, config):raise ValueError('own physical source map differs from emitted representations')
        native = native_inventory(debug, source, actual[16:65552], config['regions'])
        (work / 'native-inventory.json').write_text(json.dumps(native, indent=2) + '\n')
        allowed = {16 + row['bank'] * 32768 + int(row['cpu'], 0) - 32768 + i
                   for row in rows if row['kind'] != 'asset' for i in range(row['size'])}
        controls = []
        for control in CONTROLS:
            changed = mutate(source, control)
            name = 'controls/' + control[0] + '.nes'
            candidate = assemble(changed, name)
            offsets = checked_differences(reference, candidate, allowed)
            patch = source_patch(source, changed)
            controls.append({'control': control[0], 'source_sha256': digest(changed.encode()),
                             'source_patch': patch, 'candidate_sha256': digest(candidate), 'changed_offsets': offsets})
        asset_controls = []
        for group in GROUPS:
            selected = changed_assets(root, assets, group)
            files = encode_assets(root, selected, reference)
            wanted = asset_control_offsets(rows, payloads, files)
            write_inputs(files)
            candidate = assemble(source, 'controls/asset-' + group + '.nes')
            offsets = checked_differences(reference, candidate, set(wanted))
            if offsets != sorted(wanted) or any(candidate[i] != value for i, value in wanted.items()):
                raise ValueError('fresh own asset build did not preserve exactly the scoped edits')
            asset_controls.append({'group': group, 'candidate_sha256': digest(candidate), 'changed_offsets': offsets,
                                   'changed_asset_sha256': digest(json.dumps(selected[group], sort_keys=True).encode())})
        write_inputs(payloads)
        (work / 'source/rom.s').write_text(source)
        (work / 'candidate.o').unlink()
        if hashes != {name: digest((root / name).read_bytes()) for name in sorted(names)}:
            raise ValueError('own source changed during full build')
        if asset_hashes != load_assets(root)[1] or (root / target['input_path']).read_bytes() != reference:
            raise ValueError('own editable inputs or reference changed during full build')
        counts = Counter()
        for row in rows:counts[row['kind']] += row['size']
        proof = {'schema_version': 1, 'target': TARGET, 'match': True, 'reference_sha256': digest(reference),
                 'output_sha256': digest(actual), 'source_sha256': digest(source.encode()),
                 'source_map_sha256': digest((root / 'config/source-us-unversioned.json').read_bytes()),
                 'include_sha256': digest(nes.encode()), 'input_sha256': hashes, 'asset_input_sha256': asset_hashes,
                 'payload_sha256': {name: digest(data) for name, data in payloads.items()},
                 'debug_sha256': digest(debug.encode()), 'tool_sha256': {name: digest(path.read_bytes()) for name, path in tools.items()},
                 'component_matches': {key: inspect_rom(actual)[key] == identity[key] for key in IDENTITY_PARTS},
                 'counts': {'code_bytes': counts['code'], 'data_bytes': counts['data'],
                            'fill_bytes': counts['fill'], 'local_prg_bytes': counts['asset'], 'local_chr_bytes': 65536},
                 'regions': config['regions'], 'representation_bytes': dict(counts),
                 'source_controls': controls, 'asset_controls': asset_controls,
                 'scope': 'Whole ROM and components exact from shared native source, own structured source and nine editable input groups. Inventory acceptance is separately derived from evidence-backed decisions.'}
        (work / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        # Install only after all checks, retaining the previous proof until this
        # complete build succeeds. All retired files are generated outputs.
        backup = build_root / '.unversioned-previous'
        if backup.exists():raise ValueError('unretired own previous build exists')
        if destination.exists():destination.rename(backup)
        work.rename(destination)
        if backup.exists():shutil.rmtree(backup)
    return proof
