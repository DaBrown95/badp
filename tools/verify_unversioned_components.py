"""Verify recovered unversioned components before whole-target integration.

This bounded batch covers changed native consumers and the own message region.
It grants no whole-ROM ownership or target acceptance. Fixed external symbol
bindings are scoped to these exact components; data relationships still require
integration with the target's complete shared-source build and inventory.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

from . import palette_assets, ppu_assets, sprite_assets
from .build_variant_source import digest
from .earlier_source import prepare as earlier
from .identify_rom import inspect_rom
from .legacy_source import prepare as shared
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools
from .source_variants import load_profile, replace_once
from .unversioned_source import prepare as own
from .v11_source import include, prepare as v11

# Names describe source scopes, not proven exclusive routine boundaries.
# Each control changes one operation or meaningful operand in its whole span.
CASES = (('UnversionedDirectNativeCall', None, 0xe3e4, 0xe3eb, 'lda RecordBuffer2', 'lda RecordBuffer3', {}),
 ('UnversionedSelectedPairHandlers',
  None,
  0xd7f1,
  0xd854,
  'lda $42,y',
  'lda $43,y',
  {'ScriptDefaultSearchFields': 0xd75b,
   'SelectScriptField': 0xe834,
   'ScriptSetPointerFromOperands': 0xd2e8}),
 ('UnversionedSlotPair57',
  None,
  0xdb83,
  0xdb97,
  'sta $90,x',
  'sta $91,x',
  {'ScriptDefaultSearchFields': 0xd75b}),
 ('UnversionedShadowMask5C', None, 0xdc07, 0xdc19, 'and #$1E', 'and #$1F', {'ScriptOperandOrSlot': 0xd32a}),
 ('UnversionedSelectedPair8D',
  None,
  0xe297,
  0xe2a7,
  'sta $42,y',
  'sta $43,y',
  {'SelectScriptField': 0xe834, 'ScriptIndirectReturn': 0xe2ce}),
 ('AllocateSpriteFindSpace',
  'AllocateSpriteSkipReserved',
  0x8813,
  0x8836,
  '    ldy #$01',
  '    ldy #$02',
  {'MultiplyUnsigned8': 0x9e31, 'AllocateSpriteSkipReserved': 0x8836, 'AllocateSpriteSearchStart': 0x8839}),
 ('PlaceSlotReadSize',
  'PlaceSlotRows',
  0x88e8,
  0x8913,
  '    ldy #$00',
  '    ldy #$01',
  {'PlaceSlotRows': 0x8913}),
 ('SlotQueryDimensions',
  'SlotQueryAdjustFirst',
  0x8a2f,
  0x8a41,
  '    ldy #$01',
  '    ldy #$02',
  {'SlotQueryAdjustFirst': 0x8a41, 'SlotQuerySecondDimension': 0x8a52}),
 ('SlotQuerySecondDimension',
  'SlotQueryScaleSecond',
  0x8a52,
  0x8a61,
  '    iny',
  '    dey',
  {'SlotQueryScaleSecond': 0x8a61}),
 ('SpriteFrameDimensions',
  'SpriteFrameForwardStart',
  0x8d72,
  0x8d9e,
  '    ldy #$01',
  '    ldy #$02',
  {'SpriteFrameFlipVertical': 0x8dd1, 'SpriteFrameFlipHorizontal': 0x8da7}),
 ('SlotRecordSizeFields',
  'SlotRecordWidth',
  0xee52,
  0xee75,
  '    ldy #$02',
  '    ldy #$01',
  {'SlotRecordWidth': 0xee75, 'ShiftALeft3': 0xc7a7}),
 ('SlotRecordWidth',
  'SlotRecordAllocate',
  0xee75,
  0xee91,
  '    ldy #$01',
  '    ldy #$02',
  {'ShiftALeft3': 0xc7a7, 'SlotRecordAllocate': 0xee91}),
 ('UnversionedSplit6D',
  None,
  0xddab,
  0xddc8,
  'ora #$80',
  'ora #$81',
  {'StateBankSelectors': 0xa49c, 'ConfigureSplitScreen': 0xe7a5}),
 ('UnversionedQueue70',
  None,
  0xde0c,
  0xde2a,
  'adc #$02',
  'adc #$03',
  {'ScriptWaitForState': 0xddcc, 'ScriptGetSlotPointer': 0xd50f}),
 ('UnversionedQueue74',
  None,
  0xde9b,
  0xdebe,
  'lda #$74',
  'lda #$75',
  {'ScriptWaitForState': 0xddcc, 'SelectScriptField': 0xe834, 'ScriptOp73Return': 0xde9a}),
 ('UnversionedQueue75', None, 0xdebe, 0xdedf, 'lda #$75', 'lda #$74', {'UnversionedQueueWait': 0xdebb}),
 ('UnversionedRows7C',
  None,
  0xdf9c,
  0xdff7,
  'lda #$1D',
  'lda #$1C',
  {'StopAllAudioVoices': 0x8430, 'ScriptOp0F': 0xd422}),
 ('ScriptOp10', 'ScriptOp11', 0xd430, 0xd462, 'and #$83', 'and #$81', {}),
 ('ScriptOp65Second', 'ScriptOp66', 0xdcc1, 0xdccd, 'ora #$30', 'ora #$20', {}),
 ('ScriptOp68', 'ScriptOp69', 0xdd32, 0xdd42, 'lda #$18', 'lda #$20', {}),
 ('ScriptOp81',
  'ScriptOp82',
  0xe067,
  0xe09d,
  'and #$40',
  'and #$41',
  {'ScriptOperandOrSlot': 0xd32a,
   'NegateA': 0x9e86,
   'UpdateSlotFieldsMode40': 0xed0e,
   'ScriptYieldIfNonnegative': 0xd331}),
 ('ScriptOpABOrBF', 'ScriptOpAC', 0xe577, 0xe59d, 'lda #$AB', 'lda #$AA', {'ScriptWaitForState': 0xddcc}),
 ('RefreshAllSlotRecords',
  'UpdateSlotDrawPositions',
  0xc8c0,
  0xc8ec,
  'cpx #$10',
  'cpx #$11',
  {'PlaceSlotSprites': 0x88a1}),
 ('InitializeSlotDefaults', 'InitializeSlotFromDescriptor', 0xca4c, 0xcaba, 'lda #$18', 'lda #$19', {}),
 ('SelectSlotFlagsOrAbort', 'UpdateSlotAfterScript', 0xe855, 0xe864, 'and #$83', 'and #$81', {}),
 ('UpdateSlotFieldsSecondFlags',
  'UpdateSlotFieldsStoreFlags',
  0xed21,
  0xed2b,
  'ora #$30',
  'ora #$20',
  {'UpdateSlotFieldsStoreFlags': 0xed2b}),
 ('InitializeScrolledSlot',
  'ScrolledSlotAddHorizontal',
  0xf622,
  0xf66b,
  'lda #$FE',
  'lda #$FD',
  {'ReleaseCurrentSlot': 0xce25,
   'InitializeCurrentSlot': 0xca36,
   'SelectSlotHorizontalMotion': 0xf705,
   'ScrolledSlotAddHorizontal': 0xf66b,
   'NegateA': 0x9e86,
   'ScrolledSlotHorizontalFraction': 0xf677}),
 ('ControllerConfiguredAction',
  'ControllerModeSet',
  0xf8bd,
  0xf8da,
  'cpy #$11',
  'cpy #$10',
  {'RequireControllerActive': 0xf881,
   'RequireControllerMode': 0xf9bf,
   'ControllerConfiguredSlot': 0xf8e3,
   'ControllerModeSet': 0xf8da}),
 ('BuildPendingPpuUpdate',
  'PendingPpuCheckPalette',
  0xf174,
  0xf184,
  'sbc #$21',
  'sbc #$20',
  {'PendingPpuCheckPalette': 0xf184, 'PendingPpuStream': 0xf2a5}),
 ('PendingPpuStream',
  'PendingPpuStreamBegin',
  0xf2a5,
  0xf2bf,
  'cmp #$20',
  'cmp #$21',
  {'PendingPpuReleaseStack': 0xf26f, 'CopyToStack': 0xfe9c}),
 ('LoadMapChunkPointer',
  'RequestHorizontalScroll',
  0x8698,
  0x86e9,
  'adc #$40',
  'adc #$41',
  {'ReadBankedPointer': 0x8638, 'MapChunkOffsets': 0xa32d}),
 ('MapChunkOffsetPointer',
  'MapChunkAttributePointer',
  0x9d64,
  0x9da1,
  'ldy #$00',
  'ldy #$01',
  {'ReadBankedPointer': 0x8638, 'MapChunkOffsets': 0xa32d}),
 ('SlotRecordAddressFromIndex',
  'AdvanceScriptPointerTwice',
  0xef43,
  0xef6c,
  'lda #$00',
  'lda #$01',
  {'SlotInitialDescriptors': 0x9f03}),
 ('ScriptOp18',
  'RequireControllerMode',
  0xf9b0,
  0xf9bf,
  'lda #$04                     ; CONTROL_SCRIPT_OP18',
  'lda #$05                     ; CONTROL_SCRIPT_OP18',
  {'StopAudioVoice': 0x842c, 'StartAudioVoice': 0x83e8, 'LegacyOpcode18Audio': 0x9efb}))


def prepared_source(root: Path) -> str:
    profile = load_profile(root, 'us-v1.1')
    source = shared((root / profile['canonical_source']).read_text(), profile)
    source = earlier(source, profile['selector_text'], profile['earlier_definition_text'])
    source = own(v11(source), (root / 'src/variants/native-us-unversioned.inc').read_text())
    # This symbolic normalization is also part of the ordinary variant composer.
    return replace_once(source,
        'lda #$06\n    clc\n    adc $FE\n    sta $FE\n    lda #$9F',
        'lda #<SlotInitialDescriptors\n    clc\n    adc $FE\n    sta $FE\n    lda #>SlotInitialDescriptors')


def macros(source: str) -> dict[str, str]:
    result = {}
    for match in re.finditer(r'(?m)^\.macro (\w+)[^\n]*\n.*?^\.endmacro', source, re.S):
        if match[1] in result:
            raise ValueError('duplicate source macro: ' + match[1])
        result[match[1]] = match[0]
    return result


def assemble(folder: Path, tools: dict, name: str, source: str, start: int, end: int) -> bytes:
    if not 0x8000 <= start < end <= 0x10000:
        raise ValueError('invalid component extent')
    (folder / (name + '.s')).write_text(source)
    (folder / (name + '.cfg')).write_text(
        f'MEMORY {{ ROM: start=${start:04X}, size=${end - start:04X}, file=%O; }}\n'
        'SEGMENTS { CODE: load=ROM, type=ro; }\n')
    subprocess.run([str(tools['ca65']), '-I', '.', '--bin-include-dir', 'inputs',
                    name + '.s', '-o', name + '.o'], cwd=folder, check=True, capture_output=True)
    subprocess.run([str(tools['ld65']), '-C', name + '.cfg', name + '.o',
                    '-o', name + '.bin'], cwd=folder, check=True, capture_output=True)
    result = (folder / (name + '.bin')).read_bytes()
    if len(result) != end - start:
        raise ValueError('component output has the wrong extent: ' + name)
    return result


def native_components(root: Path, folder: Path, tools: dict, prg: bytes) -> list[dict]:
    source = prepared_source(root)
    definitions = macros(source)
    (folder / 'nes.inc').write_text(include((root / 'include/nes.inc').read_text()))
    checks = []
    for name, next_label, start, end, old, new, bindings in CASES:
        if next_label:
            a = source.index('\n' + name + ':')
            b = source.index('\n' + next_label + ':', a)
            body = '\n'.join(line for line in source[a:b].splitlines()
                             if not line.startswith('.assert'))
        else:
            body = definitions[name] + '\n    ' + name
        if old not in body or old == new:
            raise ValueError('missing meaningful native control: ' + name)
        # Unused macro definitions emit no code. The tested macro is included
        # only through its body, so its mutation cannot be shadowed by a copy.
        prefix = '.include "nes.inc"\n' + '\n'.join(
            text for key, text in definitions.items() if key != name)
        prefix += '\nUnversionedRecordBuffer5 = RecordBuffer0 + 5\n'
        prefix += '\n'.join(f'{key} = ${value:04X}' for key, value in bindings.items())
        prefix += f'\n.segment "CODE"\n.org ${start:04X}\n'
        expected = prg[start - 0x8000:end - 0x8000]
        for case, fragment in (('baseline', body), ('changed-operation', body.replace(old, new, 1))):
            text = prefix + fragment + f'\n.assert * = ${end:04X}, error, "component extent"\n'
            actual = assemble(folder, tools, name + '-' + case, text, start, end)
            matches = actual == expected
            if matches != (case == 'baseline'):
                raise ValueError('native component/control comparison failed: ' + name + '-' + case)
            checks.append({'component': name, 'case': case, 'cpu': f'0x{start:04x}',
                           'size': end - start, 'source_sha256': digest(text.encode()),
                           'candidate_sha256': digest(actual), 'matches_reference': matches})
    return checks


def message_component(root: Path, folder: Path, tools: dict, prg: bytes, reference: str) -> dict:
    manifest = json.loads((root / 'config/ppu-messages-us-unversioned.json').read_text())
    inputs = folder / 'inputs'
    inputs.mkdir(exist_ok=True)
    # The subset has its own local editable input until integration with the
    # target's full PPU asset inventory. Never replace an existing local edit.
    asset_path = root / 'extracted/us-unversioned/ppu-message-tiles.json'
    if (root / 'extracted').is_symlink() or asset_path.parent.is_symlink() or asset_path.is_symlink():
        raise ValueError('refusing a symlinked message asset input')
    if asset_path.exists():
        raw = asset_path.read_bytes()
        asset = json.loads(raw)
    else:
        asset = ppu_assets.capture(root, prg, reference, target='us-unversioned', manifest=manifest)
        raw = ppu_assets.serialize(asset)
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(raw)
    streams = ppu_assets.inventory(root, prg, target='us-unversioned', manifest=manifest)
    if len(streams) != 51 or streams[0]['location']['bank_offset'] != 0x37EE:
        raise ValueError('message table/first-record boundary changed')

    def payload_inputs(selected: dict) -> None:
        spans = ppu_assets.encode(root, selected, prg, reference,
                                  target='us-unversioned', manifest=manifest)
        by_offset = {off: data for bank, off, data in spans if bank == 1}
        for i, stream in enumerate(streams):
            start = stream['location']['bank_offset']
            for j, segment in enumerate(stream['segments']):
                if segment['kind'] == 'payload':
                    data = by_offset[start + segment['offset']]
                    (inputs / f'unversioned-message-{i:02d}-{j:02d}.bin').write_bytes(data)

    canonical = (root / 'src/us-v1.5/rom.s').read_text()
    prefix = '\n'.join(macros(canonical).values())
    prefix += '\nPpuStreamTerminator = $00\nBankStart = $8000\n.segment "CODE"\n.org $B77B\n'
    source = (root / 'src/variants/text-us-unversioned.inc').read_text()
    expected = prg[0xB77B:0xCF07]  # Physical PRG offset equals CPU for bank 1.
    cases = [('baseline', source),
             ('changed-ppu-address', replace_once(source,
                 'PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_00_00',
                 'PpuStreamAbsolute $20C4 ; CONTROL_UNVERSIONED_MESSAGE_00_00')),
             ('changed-pointer', replace_once(source, '.word UnversionedMessage00 - BankStart',
                                              '.word UnversionedMessage01 - BankStart'))]
    payload_inputs(asset)
    checks = []
    for case, body in cases:
        text = prefix + body
        actual = assemble(folder, tools, 'messages-' + case, text, 0xB77B, 0xCF07)
        matches = actual == expected
        if matches != (case == 'baseline'):
            raise ValueError('message source/control comparison failed: ' + case)
        checks.append({'case': case, 'source_sha256': digest(text.encode()),
                       'candidate_sha256': digest(actual), 'matches_reference': matches})
    changed = ppu_assets.changed_asset(asset)
    payload_inputs(changed)
    actual = assemble(folder, tools, 'messages-changed-tiles', prefix + source, 0xB77B, 0xCF07)
    wanted = {}
    for stream in asset['streams']:
        for row in stream['payloads']:
            offset = int(stream['encoded_pointer'], 0) + row['offset'] - 0x377B
            wanted[offset] = row['tiles'][0] % 253 + 1
    edits = [i for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
    if edits != sorted(wanted) or any(actual[i] != wanted[i] for i in wanted):
        raise ValueError('fresh message assembly did not change exactly the selected payload tiles')
    payload_inputs(asset)
    return {'cpu_start': '0xb77b', 'cpu_end': '0xcf07', 'component_size': len(expected),
            'message_count': len(streams), 'local_asset_sha256': digest(raw), 'checks': checks,
            'asset_payload_edits': len(edits), 'changed_asset_candidate_sha256': digest(actual)}


def sprite_component(root: Path, folder: Path, tools: dict, prg: bytes, reference: str) -> dict:
    from .sprite_layout import decode_layout
    layout = decode_layout(prg[:0x8000], 0x32F1, 0x3906, 0x4582,
                           header_format='separate-bytes', animation_end=0x370E)
    if len(layout['animations']) != 119 or len(layout['frames']) != 298:
        raise ValueError('own sprite partition changed')
    assets, manifests = {}, {}
    modules = {'sprite-frames': sprite_assets, 'palettes': palette_assets}
    for name in modules:
        manifests[name] = json.loads((root / f'config/{name}-us-unversioned.json').read_text())
        path = root / f'extracted/us-unversioned/{name}.json'
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError('refusing a symlinked sprite/palette input')
        assets[name] = json.loads(path.read_bytes())
    inputs = folder / 'inputs'
    inputs.mkdir(exist_ok=True)

    def payload_inputs(selected: dict) -> None:
        for name, module in modules.items():
            spans = module.encode(root, selected[name], prg, reference,
                                  target='us-unversioned', manifest=manifests[name])
            for i, (bank, offset, data) in enumerate(spans):
                if bank != 0:
                    raise ValueError('sprite/palette payload changed physical bank')
                # Sprite encoder returns header + tiles; palette encoder
                # returns colours alone. Every excluded header is in source.
                payload = data[3:] if name == 'sprite-frames' else data
                filename = (f'unversioned-sprite-{i:03d}.bin' if name == 'sprite-frames'
                            else f'unversioned-palette-{i:02d}.bin')
                (inputs / filename).write_bytes(payload)

    source = (root / 'src/variants/sprites-us-unversioned.inc').read_text()
    prefix = '\n'.join(macros((root / 'src/us-v1.5/rom.s').read_text()).values())
    prefix += '\n.segment "CODE"\n.org $B2F1\n'
    pointer = re.search(r'(?m)^    \.word (\w+) ; CONTROL_UNVERSIONED_ANIMATION_POINTER_000$', source)
    if not pointer:
        raise ValueError('missing animation pointer control')
    cases = [('baseline', source),
             ('changed-animation-pointer', replace_once(source, pointer[0],
                  pointer[0].replace(pointer[1], pointer[1] + ' + 1', 1))),
             ('changed-palette-header', replace_once(source,
                  'PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_15',
                  'PaletteStreamHeader $01, $03, $0B ; CONTROL_UNVERSIONED_PALETTE_15')),
             ('changed-frame-width', replace_once(source,
                  'UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_000',
                  'UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_000'))]
    expected = prg[0x32F1:0x4582]
    checks = []
    payload_inputs(assets)
    for case, body in cases:
        text = prefix + body
        actual = assemble(folder, tools, 'sprites-' + case, text, 0xB2F1, 0xC582)
        matches = actual == expected
        if matches != (case == 'baseline'):
            raise ValueError('sprite source/control comparison failed: ' + case)
        checks.append({'case': case, 'source_sha256': digest(text.encode()),
                       'candidate_sha256': digest(actual), 'matches_reference': matches})
    changed = {name: module.changed_asset(assets[name]) for name, module in modules.items()}
    payload_inputs(changed)
    actual = assemble(folder, tools, 'sprites-changed-assets', prefix + source, 0xB2F1, 0xC582)
    wanted = [int(frame['cpu'], 0) - 0xB2F1 + 3 for frame in assets['sprite-frames']['frames']]
    for stream in assets['palettes']['streams']:
        offset = int(stream['cpu'], 0) - 0xB2F1 + 4
        wanted.append(offset)
        for i, _ in enumerate(stream['updates']):
            wanted.append(offset + 16 + i * stream['group_count'] * 4)
    edits = [i for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
    if edits != sorted(wanted) or any(actual[i] != expected[i] ^ 1 for i in wanted):
        raise ValueError('fresh sprite assembly did not change exactly the selected tiles/colours')
    payload_inputs(assets)
    return {'cpu_start': '0xb2f1', 'cpu_end': '0xc582', 'component_size': len(expected),
            'animation_records': len(layout['animations']), 'sprite_frames': len(layout['frames']),
            'palette_streams': len(assets['palettes']['streams']), 'checks': checks,
            'asset_payload_edits': len(edits), 'changed_asset_candidate_sha256': digest(actual),
            'local_asset_sha256': {name: digest(module.serialize(assets[name]))
                                   for name, module in modules.items()}}


def state_component(root: Path, folder: Path, tools: dict, prg: bytes) -> dict:
    manifest = json.loads((root / 'config/palettes-us-unversioned.json').read_text())
    prefix = '\n'.join(f'UnversionedPalette{i:02d} = ${int(cpu, 0):04X}'
                       for i, cpu in enumerate(manifest['cpu_addresses']))
    prefix += '\n.segment "CODE"\n.org $A487\n'
    source = (root / 'src/variants/state-tables-us-unversioned.inc').read_text()
    # Actual independent consumers establish all four starts. The 6D fallback
    # and bank configuration read the same A49C table through different indices.
    for cpu, opcode, target in ((0xC6B2, 0xBD, 0xA487), (0xC7C5, 0xBD, 0xA49C),
                                (0xDDB1, 0xB9, 0xA49C), (0xC81D, 0xBC, 0xA4B2),
                                (0xC805, 0xBC, 0xA4DC)):
        if prg[cpu - 0x8000:cpu - 0x8000 + 3] != bytes([opcode, target & 255, target >> 8]):
            raise ValueError('state/palette native consumer changed')
    pointer = re.search(r'(?m)^    \.word (\w+) ; CONTROL_UNVERSIONED_STATE_BACKGROUNDPALETTEPOINTERS$', source)
    selector = re.search(r'(?m)^    \.byte (.+) ; CONTROL_UNVERSIONED_STATE_STATEBANKSELECTORS$', source)
    if not pointer or not selector:
        raise ValueError('missing own state controls')
    values = selector[1].split(', ')
    changed_values = f'${int(values[0][1:], 16) ^ 1:02X}' + ', ' + ', '.join(values[1:])
    cases = [('baseline', source),
             ('changed-palette-pointer', replace_once(source, pointer[0],
                  pointer[0].replace(pointer[1], pointer[1] + ' + 1', 1))),
             ('changed-selector', replace_once(source, selector[0],
                  selector[0].replace(selector[1], changed_values, 1)))]
    expected = prg[0x2487:0x2505]
    checks = []
    for case, body in cases:
        text = prefix + body
        actual = assemble(folder, tools, 'states-' + case, text, 0xA487, 0xA505)
        matches = actual == expected
        if matches != (case == 'baseline'):
            raise ValueError('state source/control comparison failed: ' + case)
        checks.append({'case': case, 'source_sha256': digest(text.encode()),
                       'candidate_sha256': digest(actual), 'matches_reference': matches})
    return {'cpu_start': '0xa487', 'cpu_end': '0xa505', 'component_size': len(expected),
            'named_entries_per_table': 21, 'checks': checks,
            'decision': 'Same bank-selector storage serves 6D and bank configuration; all 42 palette '
                        'pointers identify reconstructed palette boundaries. No exclusive-use claim.'}


def verify(root: Path) -> dict:
    target = load_target(root, 'us-unversioned')
    reference = (root / target['input_path']).read_bytes()
    identity = inspect_rom(reference)
    if not all(identity[key] == target['reference'][key] for key in IDENTITY_PARTS):
        raise ValueError('unversioned reference differs from reviewed identity')
    tools = verified_tools(root)
    folder = root / 'analysis/us-unversioned/components'
    if any(path.is_symlink() for path in (root / 'analysis', folder.parent, folder)):
        raise ValueError('refusing a symlinked component proof directory')
    folder.mkdir(parents=True, exist_ok=True)
    paths = ['tools/verify_unversioned_components.py', 'tools/unversioned_source.py',
             'src/variants/native-us-unversioned.inc', 'src/variants/text-us-unversioned.inc',
             'config/ppu-messages-us-unversioned.json', 'src/us-v1.5/rom.s', 'include/nes.inc',
             'tools/ppu_assets.py', 'tools/ppu_streams.py', 'tools/source_variants.py',
             'tools/legacy_source.py', 'tools/earlier_source.py', 'tools/v11_source.py',
             'config/variants/us-v1.1.json', 'tools/sprite_metadata.py', 'tools/sprite_layout.py',
             'tools/sprite_assets.py', 'tools/palette_assets.py',
             'config/sprite-frames-us-unversioned.json', 'config/palettes-us-unversioned.json',
             'src/variants/sprites-us-unversioned.inc', 'src/variants/state-tables-us-unversioned.inc']
    profile = load_profile(root, 'us-v1.1')
    paths.extend(profile['native_definitions'] + profile['earlier_definitions'])
    hashes = {name: digest((root / name).read_bytes()) for name in paths}
    native = native_components(root, folder, tools, reference[16:0x10010])
    messages = message_component(root, folder, tools, reference[16:0x10010], digest(reference))
    sprites = sprite_component(root, folder, tools, reference[16:0x10010], digest(reference))
    states = state_component(root, folder, tools, reference[16:0x10010])
    if digest((root / 'extracted/us-unversioned/ppu-message-tiles.json').read_bytes()) != messages['local_asset_sha256']:
        raise ValueError('message asset changed during verification')
    for name, sha in sprites['local_asset_sha256'].items():
        current_asset = json.loads((root / f'extracted/us-unversioned/{name}.json').read_bytes())
        module = sprite_assets if name == 'sprite-frames' else palette_assets
        if digest(module.serialize(current_asset)) != sha:
            raise ValueError('sprite/palette asset changed during verification')
    if hashes != {name: digest((root / name).read_bytes()) for name in paths}:
        raise ValueError('component source changed during verification')
    if digest((root / target['input_path']).read_bytes()) != digest(reference):
        raise ValueError('reference changed during verification')
    result = {'target': 'us-unversioned', 'reference_sha256': digest(reference),
              'input_sha256': hashes, 'native_checks': native, 'messages': messages, 'sprites': sprites, 'states': states,
              'decision': 'Adopt own word handlers, separate sprite dimensions, PPU commands and '
                          '51-message AB stream format. Whole-target layout, incoming scripts, '
                          'remaining data/assets and complete inventory are not accepted by this proof.',
              'scope': 'Exact isolated source components and changed-source/asset controls only. '
                       'No whole-ROM match, reconstruction coverage or target acceptance credit.'}
    (folder / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main() -> int:
    try:
        result = verify(Path(__file__).resolve().parents[1])
        baseline = [row for row in result['native_checks'] if row['case'] == 'baseline']
        print(json.dumps({'target': result['target'], 'native_components': len(baseline),
                          'native_component_bytes': sum(row['size'] for row in baseline),
                          'message_component_bytes': result['messages']['component_size'],
                          'message_records': result['messages']['message_count'],
                          'sprite_component_bytes': result['sprites']['component_size'],
                          'state_component_bytes': result['states']['component_size'],
                          'scope': result['scope']}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f'unversioned component verification failed: {exc}', file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr.decode(errors='replace'), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
