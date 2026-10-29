"""Consumer-supported unversioned native differences from the v1.1 forms.

This unfinished source adapter reads no ROM and never patches emitted bytes.
Own layout, data/asset relationships and complete-target controls remain open.
"""
import re

from .source_variants import replace_once


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


def prepare(source: str, definitions: str) -> str:
    source = sprite_dimensions(source)
    source = replace_once(source, '.include "nes.inc"', '.include "nes.inc"\n' + definitions)
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
