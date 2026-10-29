"""Shared engine composition and explicit unversioned source differences.

Composition reads no ROM and never patches emitted bytes. Own layout, editable
asset relationships, full-build controls and reviewed acceptance are separate.
"""
import json
from pathlib import Path
import re

from .source_variants import operands, replace_once


def sprite_dimensions(source: str) -> str:
    """This target stores width and height in separate frame-header bytes.

    Allocation, placement, collision queries and slot-size updates independently
    consume offsets 1 and 2. The flags byte at offset 0 retains its row-height
    bit. Later revisions combine the dimensions in one byte.
    """
    edits = {
        'AllocateSpriteFindSpace': [(
            '    lsr a\n' * 4 + '    tax\n    lda ($FE),y\n    and #$0F',
            '    tax\n    iny\n    lda ($FE),y')],
        'PlaceSlotReadSize': [(
            '    lsr a\n' * 4 + '    pha\n    lda ($FE),y\n    and #$0F',
            '    pha\n    iny\n    lda ($FE),y')],
        'SlotQueryDimensions': [('    lsr a\n' * 4, '')],
        'SlotQuerySecondDimension': [(
            '    lda ($FE),y                   ; CONTROL_SLOT_QUERY_COORDINATES\n    and #$0F',
            '    iny                          ; CONTROL_SLOT_QUERY_COORDINATES\n    lda ($FE),y')],
        'SpriteFrameDimensions': [(
            '    lsr a\n' * 4 + '    sta $03E2\n    lda ($FE),y\n    and #$0F',
            '    sta $03E2\n    iny\n    lda ($FE),y')],
        'SlotRecordSizeFields': [(
            '    ldy #$01\n    lda ($55),y\n    and #$0F',
            '    ldy #$02\n    lda ($55),y')],
        'SlotRecordWidth': [('    LegacyShiftAccumulatorRight4\n', '')],
    }
    for label, replacements in edits.items():
        start = source.index('\n' + label + ':')
        end = source.index('\n\n', start)
        fragment = source[start:end]
        for old, new in replacements:
            fragment = replace_once(fragment, old, new)
        source = source[:start] + fragment + source[end:]
    return source


def messages(source: str, definitions: str) -> str:
    """Replace the later packed-message subsystem with own AB stream source.

    Its own caller, 51 pointers and complete PPU control/payload extents are
    recovered together. Names inherited from the common script identify source
    relationships; they do not retain the later target's physical addresses.
    """
    start = source.index('\n; Set the two-byte text pointer, call the banked decoder')
    end = source.index('\nScriptCFC7:', start)
    return source[:start] + '\n' + definitions + source[end:]


def sprite_resources(source: str, definitions: str) -> str:
    """Keep the shared header macros and replace this release's directory/data."""
    start = source.index('\n; Complete contiguous animation directory,')
    end = source.index('\n; Initialize engine state and split-screen parameters', start)
    return source[:start] + '\n' + definitions + source[end:]


def state_tables(source: str, definitions: str) -> str:
    """Use the own 21-entry tables and recovered palette relationships."""
    start = source.index('\nInitialVerticalBaseSeeds:')
    end = source.index('\n.assert', source.index('\nSpritePalettePointers:', start))
    end = source.index('\n', end + 1)
    return source[:start] + '\n' + definitions + source[end:]


def descriptor_table(source: str, variant: dict) -> str:
    """Share the six-byte format and unchanged fields; keep own record words.

    Bank0's records/scripts begin immediately after entry122. Larger byte
    indices can overlap those representations without declaring more entries.
    This emits source only and reads no ROM.
    """
    if (not isinstance(variant, dict) or variant.get('schema_version') != 1 or variant.get('target') != 'us-unversioned'
            or variant.get('shared_entries') != 114 or variant.get('entries') != 123):
        raise ValueError('invalid own descriptor source identity')
    start = source.index('\nSlotInitialDescriptors:')
    end = source.index('\n.assert', start)
    fields = []
    for line in source[start:end].splitlines():
        text = line.partition(';')[0].strip()
        if text.startswith('SlotDescriptor '):
            row = operands(text.removeprefix('SlotDescriptor '))
            if len(row) != 5 or any(not re.fullmatch(r'\$[0-9A-Fa-f]{2}', x) for x in row[1:]):
                raise ValueError('changed common descriptor byte fields')
            fields.append([int(x[1:], 16) for x in row[1:]])
    if len(fields) != 114:
        raise ValueError('changed common descriptor extent')
    overrides = variant['field_overrides']
    seen = set()
    for row in overrides:
        index = row['index']
        if (type(index) is not int or not 0 <= index < 114 or index in seen
                or row['expected'] != fields[index]):
            raise ValueError('changed descriptor override context')
        seen.add(index)
        fields[index] = row['fields']
    fields += variant['extra_fields']
    pointers, labels = variant['record_pointers'], variant['known_record_labels']
    if (len(fields) != 123 or len(pointers) != 123
            or any(len(row) != 4 or any(type(x) is not int or not 0 <= x <= 255 for x in row)
                   for row in fields)
            or any(not re.fullmatch(r'0x[0-9a-f]{4}', pointer) for pointer in pointers)
            or any(key not in pointers or not re.fullmatch(r'\w+', value) for key, value in labels.items())):
        raise ValueError('invalid own descriptor fields or record pointers')
    # Explicit target words must not be rebased as primary-target literals.
    # The wrapper shares the unchanged typed six-byte source definition.
    lines = ['\n.macro UnversionedSlotDescriptor pointer, first, second, third, fourth',
             '    SlotDescriptor pointer, first, second, third, fourth', '.endmacro',
             'SlotInitialDescriptors:']
    for index, (pointer, row) in enumerate(zip(pointers, fields)):
        value = labels.get(pointer, f'${int(pointer, 0):04X}')
        marker = ' ; CONTROL_SLOT_DESCRIPTOR' if index == 0 else f' ; index ${index:02X}'
        lines.append('    UnversionedSlotDescriptor ' + value + ', '
                     + ', '.join(f'${x:02X}' for x in row) + marker)
    lines.append('.assert * = $A1E5, error, "unversioned descriptor table end"')
    # The following shared assertion belonged to the old table boundary.
    next_line = source.index('\n', end + 1)
    return source[:start] + '\n'.join(lines) + source[next_line:]


def bank0_source(root: Path, *, external_bank1_maps: bool = True) -> str:
    """Compose the complete own PRG0 source, without reading a ROM.

    This component source retains own physical bounds. Shared-section layout
    assertions use this target's reviewed section ends.
    Its bank1 symbols are external map-data contracts, not copied bytes.
    Whole-target acceptance and its complete control/inventory gates remain
    separate from this one-bank composition.
    """
    from .source_variants import load_profile
    from .legacy_source import prepare as shared
    from .earlier_source import prepare as earlier
    from .v11_source import prepare as v11
    profile = load_profile(root, 'us-v1.1')
    source = shared((root / profile['canonical_source']).read_text(), profile)
    source = earlier(source, profile['selector_text'], profile['earlier_definition_text'])
    source = prepare(v11(source), (root / 'src/variants/native-us-unversioned.inc').read_text())
    start, end = source.index('CheckResetState:'), source.index('InitializeGame:')
    source = source[:start] + (root / profile['reset_source']).read_text() + '\n' + source[end:]
    for old, new in (
        ('ldy $A1B3,x', 'ldy SlotRelatedAddressTable+1,x'),
        ('lda $A1B2,x', 'lda SlotRelatedAddressTable,x'),
        ('lda #$06\n    clc\n    adc $FE\n    sta $FE\n    lda #$9F',
         'lda #<SlotInitialDescriptors\n    clc\n    adc $FE\n    sta $FE\n    lda #>SlotInitialDescriptors')):
        source = replace_once(source, old, new)
    source = descriptor_table(source, json.loads((root / 'src/variants/descriptors-us-unversioned.json').read_text()))
    marker = '.assert * = $A1E5, error, "unversioned descriptor table end"'
    source = replace_once(source, marker, marker + '\n'
                          + (root / 'src/variants/bank0-slots-us-unversioned.inc').read_text()
                          + '\n    UnversionedBank0SlotScripts\n')
    start = source.index('\nSlotRelatedAddressTable:')
    end = source.index('\nInitialVerticalBaseSeeds:', start)
    source = source[:start] + '\n' + (root / 'src/variants/maps-us-unversioned.inc').read_text() \
        + '\n    UnversionedBank0MapData\n' + source[end:]
    source = state_tables(source, (root / 'src/variants/state-tables-us-unversioned.inc').read_text())
    start = source.index('\nPositionRecordPointersA:')
    end = source.index('\n; Observed sprite metadata,', start)
    source = source[:start] + '\n' + (root / 'src/variants/positions-us-unversioned.inc').read_text() \
        + '\n    UnversionedPositionData\n' + source[end:]
    source = sprite_resources(source, (root / 'src/variants/sprites-us-unversioned.inc').read_text())
    prefix = source[:source.index('.segment "HEADER"')]
    start = source.index('.segment "PRG0"')
    end = source.index('.segment "PRG1"', start)
    bounds = json.loads((root / 'config/native-layout-us-unversioned.json').read_text())
    if (bounds['schema_version'] != 1 or bounds['target'] != 'us-unversioned' or bounds['bank'] != 0):
        raise ValueError('invalid own native layout contracts')
    used, lines = set(), []
    for line in source[start:end].splitlines():
        if line.lstrip().startswith('.assert (* - BankStart'):
            message = re.search(r'error, "([^\"]+)"', line)
            if not message or message[1] not in bounds['bank0_bounds'] or message[1] in used:
                raise ValueError('missing or duplicate own section-end contract')
            key = message[1]
            cpu = int(bounds['bank0_bounds'][key], 0)
            if not 0x8000 <= cpu <= 0x10000:
                raise ValueError('invalid own section end')
            used.add(key)
            line = f'.assert * = ${cpu:04X}, error, "{key}"'
        lines.append(line)
    if used != set(bounds['bank0_bounds']):
        raise ValueError('unused own section-end contracts')
    body = '\n'.join(lines) + '\n'
    maps = json.loads((root / 'config/maps-us-unversioned.json').read_text())
    if maps['target'] != 'us-unversioned':
        raise ValueError('invalid external map contract')
    labels = []
    for row in maps['layouts']:
        cpu = int(row['cpu'], 0)
        if row['bank'] == 1:
            labels.append(f'UnversionedMapLayout{cpu:04X} = ${cpu:04X}')
    external = '\n.scope Bank1\n' + '\n'.join(labels) + '\n.endscope\n'
    return prefix + (external if external_bank1_maps else '') + body


def full_source(root: Path) -> str:
    """Compose both complete banks from maintained source and editable assets.

    Composition reads no reference ROM. Full-byte/control verification and the
    review of provisional interpretations are separate build/inventory gates.
    """
    source = bank0_source(root, external_bank1_maps=False)
    maps = (root / 'src/variants/maps-us-unversioned.inc').read_text()
    source = replace_once(source, maps + '\n    UnversionedBank0MapData',
                          '    UnversionedBank0MapData')
    # ca65 requires a scope to exist before a qualified reference and cannot
    # reopen a named scope. Keep forward map addresses as explicit contracts,
    # then assert each against the actual bank1 label after its emission.
    contracts, checks = [], []
    for row in json.loads((root / 'config/maps-us-unversioned.json').read_text())['layouts']:
        if row['bank'] != 1:
            continue
        cpu = int(row['cpu'], 0)
        name = f'UnversionedBank1MapContract{cpu:04X}'
        contracts.append(f'{name} = ${cpu:04X}')
        maps = maps.replace(f'Bank1::UnversionedMapLayout{cpu:04X}', name)
        checks.append(f'.assert UnversionedMapLayout{cpu:04X} = ::{name}, error, "own map pointer contract"')
    boundary = source.index('.segment "PRG0"')
    target = json.loads((root / 'config/targets/us-unversioned.json').read_text())
    header = bytes.fromhex(target['reference']['header_claims']['hex'])
    if target['id'] != 'us-unversioned' or len(header) != 16:
        raise ValueError('invalid own fixed header source')
    source = source[:boundary] + '\n'.join(contracts) + '\n' + maps + '\n.segment "HEADER"\n    .byte ' \
        + ', '.join(f'${value:02X}' for value in header) + '\n' + source[boundary:]
    source += '\n.segment "PRG1"\n.scope Bank1\nCurrentBank = 1\nBankStart:\n'
    source += '    .incbin "unversioned-map-chunks.bin"\n'
    source += '.assert * = $A640, error, "own map chunks end"\n'
    for filename, macro in (('audio', 'UnversionedBank1Audio'),
                             ('opening-scripts', 'UnversionedBank1OpeningScripts')):
        source += (root / f'src/variants/{filename}-us-unversioned.inc').read_text()
        source += '\n    ' + macro + '\n'
    source += (root / 'src/variants/text-us-unversioned.inc').read_text()
    source += (root / 'src/variants/main-scripts-us-unversioned.inc').read_text()
    source += '\n    UnversionedBank1MainScripts\n    UnversionedBank1MapData\n'
    source += '\n'.join(checks) + '\n'
    source += (root / 'src/variants/retained-resource-us-unversioned.inc').read_text()
    source += ('\n    .res $7DA0 - (* - BankStart), $00 ; CONTROL_UNVERSIONED_BANK1_ZERO_STORAGE\n'
               '.assert * = $FDA0, error, "own bank1 zero storage end"\n'
               'ScriptRecordLengths:\n    ScriptTable 0\n'
               '.assert * = $FE5F, error, "own bank1 command lengths end"\n'
               '    BankHelpers\n'
               '.assert * = $FFB2, error, "own bank1 helpers end"\n'
               '    BankTail SecondaryBankValue, SecondaryBankIndex\n'
               '.assert * = $10000, error, "own bank1 end"\n.endscope\n'
               '.segment "CHR"\n    .incbin "chr.bin"\n')
    return source


def prepare(source: str, definitions: str) -> str:
    source = sprite_dimensions(source)
    source = source.replace('; The frame header packs column and row counts in the high and low nibbles.',
                            '; This release stores column and row counts in separate header bytes.')
    source = source.replace('; Compute the number of tiles from the packed dimensions.',
                            '; Compute the number of tiles from the separate width and height bytes.')
    source = source.replace('; Read packed dimensions and update slot geometry.',
                            '; Read the separate dimension bytes and update slot geometry.')
    source = replace_once(source, '.include "nes.inc"', '.include "nes.inc"\n' + definitions)
    start = source.index('\nApplyNmiPpuState:')
    end = source.index('\nApplyNmiPpuCtrl:', start)
    body = replace_once(source[start:end], 'bne ApplyNmiPpuCtrl', 'bne UnversionedNmiSplit')
    source = source[:start] + body + '\n    UnversionedNmiSplitSequence\n' + source[end:]
    source = replace_once(source,
                          'ScriptOp9B:\n    jmp CallScriptNativeBanked   ; CONTROL_SCRIPT_OP9B',
                          'ScriptOp9B:\n    UnversionedDirectNativeCall')
    # The actual low/high table distance and length-table consumer establish
    # 191 entries. BF-C3 have no nominal entries in this target.
    count, lines = 0, []
    for line in source.splitlines():
        if re.match(r'^    ScriptOp \d+, Bank0::\w+, part', line):
            count += 1
            changes = {
                0x37: ('ScriptOp37To3A', 'UnversionedScriptOp37'),
                0x38: ('ScriptOp37To3A', 'UnversionedScriptOp38'),
                0x39: ('ScriptOp37To3A', 'UnversionedScriptOp39'),
                0x57: ('ScriptOp57To58', 'UnversionedScriptOp57'),
                0x5C: ('ScriptOp5CTo5D', 'UnversionedScriptOp5C'),
                0x6D: ('ScriptOp6DTo6E', 'UnversionedScriptOp6D'),
                0x70: ('ScriptOp70To71', 'UnversionedScriptOp70'),
                0x75: ('ScriptOp75To76', 'UnversionedScriptOp75'),
                0x7C: ('ScriptOp7CTo7D', 'UnversionedScriptOp7C'),
                0x8D: ('ScriptOp8DTo8F', 'UnversionedScriptOp8DTo8E'),
                0x8E: ('ScriptOp8DTo8F', 'UnversionedScriptOp8DTo8E'),
                0xB4: ('ScriptOpB4ToB5', 'UnversionedScriptOpB4'),
            }
            if count - 1 in changes:
                old, new = changes[count - 1]
                line = replace_once(line, 'Bank0::' + old, 'Bank0::' + new)
            if count > 191:
                continue
        lines.append(line)
    if count != 196:
        raise ValueError('changed v1.1 nominal dispatch definition')
    source = '\n'.join(lines) + '\n'
    start = source.index('\n; $BF shares the previously reconstructed $AB handler.')
    end = source.index('\n.assert', start)
    source = source[:start] + '\n; BF-C3 are absent from the own191-entry table.\n' + source[end:]
    source = replace_once(source, '\nScriptOp37To3A:',
                          '\n    UnversionedSelectedPairHandlers\nScriptOp37To3A:')
    for label, macro in (('ScriptOp57To58', 'UnversionedSlotPair57'),
                         ('ScriptOp5CTo5D', 'UnversionedShadowMask5C'),
                         ('ScriptOp6DTo6E', 'UnversionedSplit6D'),
                         ('ScriptOp70To71', 'UnversionedQueue70'),
                         ('ScriptOp75To76', 'UnversionedQueue75'),
                         ('ScriptOp7CTo7D', 'UnversionedRows7C'),
                         ('ScriptOp8DTo8F', 'UnversionedSelectedPair8D')):
        source = replace_once(source, '\n' + label + ':',
                              '\n    ' + macro + '\n' + label + ':')
    source = replace_once(source, '\nScriptOpB4ToB5:',
                          '\n    UnversionedNegateFieldsB4\nScriptOpB4ToB5:')
    source = replace_once(source, 'ScriptOp9D:\n    rts                          ; CONTROL_SCRIPT_OP9D',
                          '    UnversionedSlotFlag9D')
    source = replace_once(source, '    bcc ScriptOp9D', '    bcc UnversionedSlotFlag9DReturn')
    source = replace_once(source, 'ScriptFieldMask:\n    and #$01',
                          'ScriptFieldMask:\n    and #$03 ; CONTROL_UNVERSIONED_SCRIPT_FIELD_MASK')
    # This version returns after the first matching slot has a negative flag;
    # the later six-byte rescan successor is absent.
    source = replace_once(source, '    bmi ScriptOp35Next', '    bmi ScriptFindSlotReturn')
    source = replace_once(source,
        'ScriptOp35Next:\n    jsr ScriptFindNextSlot\n    jmp ScriptOp35Check\n', '')
    source = replace_once(source,
        'ScriptOp74:\n    jmp ScriptWaitForState       ; CONTROL_SCRIPT_OP74',
        '    UnversionedQueue74')
    # These are operand/branch changes in otherwise shared bodies.
    for label, end_label, edits in (
        ('ScriptOp10', 'ScriptOp11', [('and #$81', 'and #$83'), ('and #$6E', 'and #$6C')]),
        ('ScriptOp65Second', 'ScriptOp66', [('ora #$20', 'ora #$30')]),
        ('ScriptOp68', 'ScriptOp69', [('lda #$20', 'lda #$18')]),
        ('InitializeSlotDefaults', 'InitializeSlotFromDescriptor', [('lda #$20', 'lda #$18')]),
        ('SelectSlotFlagsOrAbort', 'UpdateSlotAfterScript', [('and #$81', 'and #$83')]),
        ('UpdateSlotFieldsSecondFlags', 'UpdateSlotFieldsStoreFlags', [('ora #$20', 'ora #$30')]),
        ('InitializeScrolledSlot', 'ScrolledSlotAddHorizontal', [(
            '    lda $0620,x\n    ora #$02\n    sta $0620,x\n', '')]),
        ('ControllerConfiguredAction', 'ControllerModeSet', [('cpy #$10', 'cpy #$11')]),
        ('ScriptOp81', 'ScriptOp82', [
            ('bne ScriptOp81NegateFirst\n    lda #$00', 'beq ScriptOp81Second'),
            ('bne ScriptOp81NegateSecond\n    lda #$00', 'beq ScriptOp81Call')]),
        ('ScriptOpABOrBF', 'ScriptOpAC', [
            ('    ldy RecordBuffer0                     ; CONTROL_SCRIPT_OPAB\n', ''),
            ('    sty $E4', '    lda #$AB                   ; CONTROL_SCRIPT_OPAB\n    sta $E4')]),
    ):
        a = source.index('\n' + label + ':')
        b = source.index('\n' + end_label + ':', a)
        body = source[a:b]
        for old, new in edits:
            body = replace_once(body, old, new)
        source = source[:a] + body + source[b:]
    # The older refresh entry loops inline. There is no separate per-slot
    # caller after removal of the absent C3 command.
    source = replace_once(source,
        'RefreshSlotRecordsLoop:\n    jsr RefreshSlotRecordPosition\n    inx\n'
        '    cpx #$10\n    bne RefreshSlotRecordsLoop\n    rts\n', '')
    source = replace_once(source, 'RefreshSlotRecordReturn:\n    rts',
        'RefreshSlotRecordReturn:\n    inx\n    cpx #$10\n'
        '    bne RefreshSlotRecordPosition\n    rts')
    # Only AB selects the banked byte stream here. The later BF direct-memory
    # alternative and its helper are absent from the actual consumer.
    source = replace_once(source,
        '    beq PendingPpuStreamJump\n    cmp #$BF\n    bne PendingPpuCheckPalette',
        '    bne PendingPpuCheckPalette')
    a = source.index('\nCopyDirectToStack:')
    b = source.index('\n; Types $AB/$BF', a)
    source = source[:a] + source[b:]
    a = source.index('\nPendingPpuStream:')
    b = source.index('\nPendingPpuStreamBegin:', a)
    source = source[:a] + replace_once(source[a:b],
        '    ldx $E4\n    cpx #$BF\n    bne PendingPpuStreamBanked\n'
        '    jsr CopyDirectToStack\n    jmp PendingPpuStreamBegin\n'
        'PendingPpuStreamBanked:\n', '') + source[b:]
    # No resident wrapper occupies the later versions' fixed call window.
    # The length table starts at FDA0; both references retain zero storage
    # immediately before it. Its full preceding extent still needs own layout.
    if source.count('    BankScriptNativeCall\n') != 2:
        raise ValueError('changed common native-call emission sites')
    source = source.replace('    BankScriptNativeCall\n', '')
    source = replace_once(source, '.res $7D70 - (* - BankStart)',
                          '.res $7DA0 - (* - BankStart)')
    # v1.1's copied controller fragment is absent from its bank-1 location.
    # Its removal here is provisional until the own script end/layout matches.
    start = source.index('\nV11SecondaryControllerTail:')
    end = source.index('\n    BankNativeCallAlignmentFill', start)
    source = source[:start] + '\n' + source[end:]
    return source
