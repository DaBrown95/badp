"""Build the complete unversioned PRG0 component from shared readable source.

Own physical assertions, all 32768 emitted bytes and meaningful source edits
are checked. External bank1 map symbols retain their own explicit contracts.
This component is not a whole-ROM build or a target acceptance decision.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from . import map_assets, map_layout_assets, palette_assets, sprite_assets
from .build_rom import digest
from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools
from .source_variants import load_profile, marked_statement, operands, source_paths, replace_once
from .unversioned_source import bank0_source
from .v11_source import include

INPUTS = ('tools/build_unversioned_bank0.py', 'tools/unversioned_source.py',
          'tools/legacy_source.py', 'tools/earlier_source.py', 'tools/v11_source.py',
          'tools/source_variants.py', 'tools/map_assets.py', 'tools/map_data.py',
          'tools/map_layout_assets.py', 'tools/palette_assets.py', 'tools/sprite_assets.py',
          'tools/sprite_metadata.py', 'tools/setup.py', 'tools/project.py',
          'tools/identify_rom.py', 'tools/build_rom.py', 'config/cc65-toolchain.json',
          'config/catalogues/no-intro-nes.json', 'config/targets/us-unversioned.json',
          'config/variants/us-v1.1.json', 'include/nes.inc',
          'config/maps-us-unversioned.json', 'config/positions-us-unversioned.json',
          'config/native-layout-us-unversioned.json',
          'config/palettes-us-unversioned.json', 'config/sprite-frames-us-unversioned.json',
          'src/variants/native-us-unversioned.inc', 'src/variants/maps-us-unversioned.inc',
          'src/variants/state-tables-us-unversioned.inc', 'src/variants/positions-us-unversioned.inc',
          'src/variants/descriptors-us-unversioned.json', 'src/variants/bank0-slots-us-unversioned.inc',
          'src/variants/sprites-us-unversioned.inc')


def asset_inputs(root: Path, folder: Path, prg: bytes, reference: str) -> dict:
    result = {}
    for name, module in (('sprite-frames', sprite_assets), ('palettes', palette_assets),
                         ('map-layouts', map_layout_assets), ('map-chunks', map_assets)):
        path = root / f'extracted/us-unversioned/{name}.json'
        if path.is_symlink() or path.parent.is_symlink() or (root / 'extracted').is_symlink():
            raise ValueError('refusing a symlinked component asset')
        raw = path.read_bytes()
        asset = json.loads(raw)
        options = {'target': 'us-unversioned'}
        if name in ('sprite-frames', 'palettes'):
            options['manifest'] = json.loads((root / f'config/{name}-us-unversioned.json').read_text())
        else:
            maps = json.loads((root / 'config/maps-us-unversioned.json').read_text())
            if name == 'map-layouts':
                options['geometry'] = maps['layout_assets']
            else:
                options.update(chunk_table_offset=int(maps['chunk_table_cpu'], 0) - 0x8000,
                               geometry=maps['chunk_assets'])
        encoded = module.encode(root, asset, prg, reference, **options) if name in ('sprite-frames', 'palettes') \
            else module.encode(asset, prg, reference, **options)
        if name == 'map-chunks':
            (folder / 'unversioned-map-chunks.bin').write_bytes(encoded)
        else:
            for i, (bank, offset, data) in enumerate(encoded):
                if name == 'sprite-frames':
                    filename, data = f'unversioned-sprite-{i:03d}.bin', data[3:]
                elif name == 'palettes':
                    filename = f'unversioned-palette-{i:02d}.bin'
                else:
                    filename = f'unversioned-map-layout-{bank}-{offset + 0x8000 - 2:04x}.bin'
                (folder / filename).write_bytes(data)
        result[str(path.relative_to(root))] = digest(raw)
    return result


def build(root: Path) -> dict:
    target = load_target(root, 'us-unversioned')
    reference = (root / target['input_path']).read_bytes()
    identity = inspect_rom(reference)
    if any(identity[key] != target['reference'][key] for key in IDENTITY_PARTS):
        raise ValueError('component reference differs from reviewed identity')
    layout = json.loads((root / 'config/native-layout-us-unversioned.json').read_text())
    if (layout['reference_sha256'] != digest(reference)
            or layout['reference_bank_sha256'] != digest(reference[16:32784])):
        raise ValueError('section-end contracts refer to another input')
    profile = load_profile(root, 'us-v1.1')
    names = set(INPUTS) | set(source_paths(profile))
    hashes = {name: digest((root / name).read_bytes()) for name in sorted(names)}
    folder = root / 'analysis/us-unversioned/bank0-source'
    if any(path.is_symlink() for path in (root / 'analysis', folder.parent, folder)):
        raise ValueError('refusing a symlinked component output')
    (folder / 'source').mkdir(parents=True, exist_ok=True)
    (folder / 'inputs').mkdir(exist_ok=True)
    assets = asset_inputs(root, folder / 'inputs', reference[16:65552], digest(reference))
    source = bank0_source(root)
    nes = include((root / 'include/nes.inc').read_text())
    (folder / 'source/nes.inc').write_text(nes)
    (folder / 'source/link.cfg').write_text(
        'MEMORY { ROM: start=$8000, size=$8000, file=%O; }\n'
        'SEGMENTS { PRG0: load=ROM, type=ro; }\n')
    tools = verified_tools(root)

    def assemble(name: str, text: str) -> bytes:
        (folder / 'source/rom.s').write_text(text)
        subprocess.run([str(tools['ca65']), '-g', '-l', name + '.lst', '-I', 'source',
                        '--bin-include-dir', 'inputs', 'source/rom.s', '-o', name + '.o'],
                       cwd=folder, check=True, capture_output=True)
        subprocess.run([str(tools['ld65']), '-C', 'source/link.cfg', name + '.o',
                        '-o', name + '.bin', '--dbgfile', name + '.dbg'],
                       cwd=folder, check=True, capture_output=True)
        return (folder / (name + '.bin')).read_bytes()

    expected = reference[16:32784]
    actual = assemble('candidate', source)
    if actual != expected:
        offsets = [f'0x{i + 0x8000:04x}' for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
        raise ValueError('complete PRG0 source differs: ' + ', '.join(offsets[:16]))
    controls = []

    def changed_field(text: str, index: int, value: str) -> str:
        name, arguments = text.split(maxsplit=1)
        fields = operands(arguments)
        fields[index] = value
        return name + ' ' + ', '.join(fields)

    changes = (
        ('nmi-split-address', 'CONTROL_UNVERSIONED_NMI_SPLIT', lambda _: 'lda #$26'),
        ('slot-flag-9d', 'CONTROL_UNVERSIONED_SLOT_FLAG_9D', lambda _: 'lda $C1,x'),
        ('negate-fields-b4', 'CONTROL_UNVERSIONED_NEGATE_B4', lambda _: 'lda RecordBuffer2'),
        ('first-slot-search', 'CONTROL_SCRIPT_OP35', lambda _: 'lda RecordBuffer4'),
        ('selected-field-mask', 'CONTROL_UNVERSIONED_SCRIPT_FIELD_MASK', lambda _: 'and #$01'),
        ('descriptor-list-id', 'CONTROL_UNVERSIONED_DESCRIPTOR_LIST_A229',
         lambda text: replace_once(text, '$0E', '$0F')),
        ('descriptor-first-field', 'CONTROL_SLOT_DESCRIPTOR',
         lambda text: changed_field(text, 1, '$01')),
        ('position-constructor', 'CONTROL_UNVERSIONED_POSITION_CONSTRUCTOR_A559',
         lambda text: changed_field(text, 3, '$01')),
    )
    for name, marker, mutate in changes:
        changed = marked_statement(source, marker, mutate)
        candidate = assemble(name, changed)
        offsets = [i for i, (a, b) in enumerate(zip(candidate, expected)) if a != b]
        if len(candidate) != 32768 or not offsets:
            raise ValueError('meaningful PRG0 source control was erased: ' + name)
        controls.append({'control': name, 'source_sha256': digest(changed.encode()),
                         'candidate_sha256': digest(candidate),
                         'changed_bank0_cpu': [f'0x{i + 0x8000:04x}' for i in offsets]})
        for suffix in ('.o', '.lst', '.dbg'):
            (folder / (name + suffix)).unlink()
    (folder / 'source/rom.s').write_text(source)
    if hashes != {name: digest((root / name).read_bytes()) for name in sorted(names)}:
        raise ValueError('component source changed during build')
    if any(digest((root / path).read_bytes()) != value for path, value in assets.items()):
        raise ValueError('component asset changed during build')
    if digest((root / target['input_path']).read_bytes()) != digest(reference):
        raise ValueError('component reference changed during build')
    result = {'target': 'us-unversioned', 'bank': 0, 'bytes': len(actual), 'match': True,
              'reference_sha256': digest(reference), 'reference_bank_sha256': digest(expected),
              'candidate_sha256': digest(actual), 'source_sha256': digest(source.encode()),
              'include_sha256': digest(nes.encode()), 'input_sha256': hashes,
              'asset_input_sha256': assets, 'controls': controls,
              'tool_sha256': {name: digest(path.read_bytes()) for name, path in tools.items()},
              'scope': 'Complete PRG0 exact source component, with own physical bounds and eight meaningful '
                       'fresh-build controls. External bank1 map symbols are explicit contracts. '
                       'Shared section ends use the own reviewed layout contracts. '
                       'No whole-ROM match, full-target control coverage or inventory acceptance is claimed.'}
    (folder / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main() -> int:
    try:
        result = build(Path(__file__).resolve().parents[1])
        print(json.dumps({key: result[key] for key in ('target', 'bank', 'bytes', 'match', 'candidate_sha256', 'scope')}, indent=2))
    except (OSError, ValueError, TypeError, KeyError, subprocess.CalledProcessError) as exc:
        print(f'unversioned PRG0 build failed: {exc}', file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr.decode(errors='replace'), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
