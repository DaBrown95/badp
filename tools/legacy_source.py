"""Readable v1.3 source differences; no ROM reads or binary modifications."""
from __future__ import annotations

from .source_variants import replace_once


def controller2_nmi(common: str) -> str:
    """Insert the five second-controller expansions into common NMI source.

    The caller supplies the macros from controller2-us-v1.3.inc. Existing
    first-controller work and instruction mutation markers remain intact.
    """
    common = replace_once(common, '    sta $038F\n    stx $038D\n',
                          '    sta $038F\n    stx $038D\n    ReadSecondController\n')
    common = replace_once(common, '    sta $0394\n    dec $0391\n',
                          '    sta $0394\n    FilterSecondControllerRepeat\n    dec $0391\n')
    common = replace_once(common, '    ora $038F\n    sta $038F\n',
                          '    ora $038F\n    sta $038F\n    MergeSecondControllerRepeat\n')
    common = replace_once(common, '    lda $038D\n    sta $0394\n',
                          '    lda $038D\n    sta $0394\n    SaveSecondControllerRepeat\n')
    if common.count('FrameEngineWork:') != 1:
        raise ValueError('missing or ambiguous common NMI engine boundary')
    before, after = common.split('FrameEngineWork:', 1)
    # Both the empty-input branch and the last first-controller bit proceed to
    # controller 2. Rewriting only those two targets preserves frame work.
    if before.count('FrameEngineWork') != 2:
        raise ValueError('unexpected first-controller dispatch successors')
    before = before.replace('FrameEngineWork', 'DispatchSecondControllerChanges')
    return before + ('DispatchSecondControllerChanges:\n    DispatchSecondController\n'
                     'FrameEngineWork:') + after


def bank_values(common: str, prefix: int = 8) -> str:
    """Retain both sixteen-entry halves used by the v1.3 state selector."""
    if type(prefix) is not int or not 0 <= prefix < 16 or prefix & 1:
        raise ValueError('invalid legacy conflict-table prefix')
    return replace_once(common, 'BankValues:\n    .repeat 8, chrBank\n',
                        'BankValues:\n    .repeat 8, chrBank\n'
                        f'        .byte (${prefix:02X} | (chrBank << 4)), (${prefix|1:02X} | (chrBank << 4))\n'
                        '    .endrepeat\n    .repeat 8, chrBank\n')


# These are source transformations of reviewed native operations, not ROM
# address substitutions. Their physical positions come from the target layout.
INLINE_CALLS = {
    'MainScaleHorizontalBase': 'LegacyShiftPairLeft ScrollTargetXLow, ScrollTargetXHigh',
    'MainScaleVerticalBase': 'LegacyShiftPairLeft ScrollTargetYLow, ScrollTargetYHigh',
    'ScaleWorldShiftRight': 'LegacyShiftAccumulatorRightInto $11',
    'ShiftALeft4': 'LegacyShiftAccumulatorLeft4',
    'RotateSlotCoordinate': 'LegacyRotateAccumulatorRightInto $11',
    'ScalePositionByEight': 'LegacyScalePositionByEight',
    'ShiftReferenceRight': 'LegacyShiftPairRight $0F, $0E',
    'ShiftA4FRight': 'LegacyShiftAccumulatorRightInto $4F',
    'ScriptOp47WritePair': 'LegacyStoreSlotPositionPair',
    'ScriptShiftPointerOffset': 'LegacyShiftAccumulatorLeftInto RecordPointerHigh',
    'ScriptOp89ShiftVertical': 'LegacyShiftLowIntoAccumulator $1C',
    'ScriptOp89ShiftHorizontal': 'LegacyShiftPairLeft $0B, $0C',
    'ScriptGetSecondOffset': 'LegacyGetSecondOffset',
    'ScriptShiftAInto03': 'LegacyShiftAccumulatorLeftInto $03',
    'DoubleFEPointer': 'LegacyShiftPairLeft $FE, $FF',
    'PendingPpuSetSource': 'LegacySetPpuSource',
    'ShiftSearchCoordinateRight': 'LegacyShiftPairRight $5F, $5E',
    'ShiftScrolledSlotHorizontal': 'LegacyShiftIndexedPairRight $07E0, $07D0',
    'ShiftScrolledSlotVertical': 'LegacyShiftRightIntoIndexed $12, $80',
}


def inline_helpers(common: str) -> str:
    """Restore the target's inline forms and omit only absent helper bodies.

    Existing remaining helper entries are retained, even when no direct call
    remains. In particular rotate/position/slot-pair handlers are not removed
    merely because their former callers now inline the operation.
    """
    import re

    for name, replacement in INLINE_CALLS.items():
        pattern = r'(?m)^(\s*)jsr ' + name + r'(?=\s|;|$)'
        common, count = re.subn(pattern, lambda m: m[1] + replacement, common)
        if count == 0:
            raise ValueError('missing legacy inline source call: ' + name)
    # The accumulator-right helper remains at other native entries. Only the
    # note-preparation and record-size callers use the four inline shifts.
    for start_label, end_label in [('PrepareAudioNote:', 'AudioVoiceRegisterAddress:'),
                                    ('SlotRecordSizeFields:', 'SlotRecordAllocate:')]:
        start = common.find('\n' + start_label)
        end = common.find('\n' + end_label, start + 1)
        if start < 0 or end < 0:
            raise ValueError('missing scoped legacy shift caller: ' + start_label)
        block = common[start:end]
        block = replace_once(block, 'jsr ShiftARight4', 'LegacyShiftAccumulatorRight4')
        common = common[:start] + block + common[end:]
    common = replace_once(common,
                          '    jsr ShiftPositionRight\n    jsr ShiftPositionRight\n'
                          '    jsr ShiftPositionRight\n    rts\nShiftPositionRight:',
                          '    LegacyShiftPairRight $12, $11\n'
                          '    LegacyShiftPairRight $12, $11\nShiftPositionRight:')
    # A two-byte audio advance was later factored into a shared fallthrough
    # entry. v1.3 calls the one-byte advance twice instead.
    common, count = re.subn(r'(?m)^(\s*)jsr AdvanceAudioCommandTwo(?=\s|;|$)',
                            lambda m: m[1] + 'jsr AdvanceAudioCommandOne\n    jsr AdvanceAudioCommandOne', common)
    if count != 5:
        raise ValueError('unexpected legacy audio two-byte advance callers')
    common = replace_once(common, 'AdvanceAudioCommandTwo:\n    jsr AdvanceAudioCommandOne   ; CONTROL_ADVANCE_AUDIO_COMMAND_TWO\n', '')
    absent = ('MainScaleHorizontalBase', 'MainScaleVerticalBase', 'ScaleWorldShiftRight',
              'ScalePositionByEight', 'ShiftReferenceRight', 'ScriptShiftPointerOffset',
              'ScriptOp89ShiftVertical', 'ScriptOp89ShiftHorizontal', 'ScriptGetSecondOffset',
              'ScriptShiftAInto03', 'DoubleFEPointer', 'PendingPpuSetSource',
              'ShiftSearchCoordinateRight', 'ShiftScrolledSlotHorizontal')
    for name in absent:
        start = common.find('\n' + name + ':\n')
        end = common.find('\n    rts', start + 1)
        if start < 0 or end < 0:
            raise ValueError('missing absent legacy helper: ' + name)
        common = common[:start] + common[end + len('\n    rts'):]
    # The four-shift left entry's first instruction is absent, while the
    # following three-shift entry and its two later instructions remain.
    common = replace_once(common, 'ShiftALeft4:\n    asl a                         ; CONTROL_SHIFT_LEFT4\n', '')
    return common


def _body(common: str, name: str) -> str:
    start = common.find('\n' + name + ':\n')
    end = common.find('\n    rts', start + 1)
    if start < 0 or end < 0:
        raise ValueError('missing legacy helper body: ' + name)
    return common[start + len('\n' + name + ':\n'):end]


def map_queue_order(common: str) -> str:
    """Restore inline span deductions and the original queue loop ordering."""
    import re
    consume = _body(common, 'MapConsumeAttributeSpan')
    second = _body(common, 'MapQueueSecondNametable')
    # v1.3 falls through the tile-row deduction, copies and resumes its loop.
    common = replace_once(common,
                          '    jsr MapTileRowConsumeSpan\n    jmp MapTileRowCopyNext\n', '')
    common = replace_once(common, '    jmp CopyLinearToBuffer\nMapTileRowMaybeSecond:',
                          '    jsr CopyLinearToBuffer\n    jmp MapTileRowCopyNext\nMapTileRowMaybeSecond:')
    # The attribute-row path has its own inline deduction and copy.
    common = replace_once(common, '    jsr MapTileRowConsumeSpan\n',
                          consume + '\n    jsr CopyLinearToBuffer\n')
    common, count = re.subn(r'(?m)^    jsr MapQueueSecondNametable[^\n]*', lambda _: second, common)
    if count != 3:
        raise ValueError('unexpected legacy second-nametable consumers')
    common = replace_once(common, '\nMapQueueSecondNametable:\n' + second + '\n    rts', '')
    # Keep the merge-path deduction at its physical source position. The
    # column path duplicates it, and the copy/loop tail follows the merge body.
    common = replace_once(common, '    jsr MapConsumeAttributeSpan\n    jsr CopyBitsToBuffer\n'
                          '    jmp MapRowAttributesMergeNext\n', '')
    common = replace_once(common, '    jsr MapConsumeAttributeSpan\n', consume + '\n')
    common = replace_once(common, '\nMapConsumeAttributeSpan:\n' + consume + '\n    rts',
                          '\nMapConsumeAttributeSpan:\n' + consume + '\n    jsr CopyBitsToBuffer\n'
                          '    jmp MapRowAttributesMergeNext')
    # The shared row worker was introduced later; both v1.3 scroll directions
    # carry their own X-coordinate setup and row queue calls.
    row = _body(common, 'QueueScrollRow')
    common, count = re.subn(r'(?m)^    jsr QueueScrollRow[^\n]*', lambda _: row, common)
    if count != 2:
        raise ValueError('unexpected legacy exposed-row consumers')
    common = replace_once(common, '\nQueueScrollRow:\n' + row + '\n    rts', '')
    return common


def native_order(common: str) -> str:
    """Restore the remaining non-inline native order and pointer advances."""
    common = replace_once(common, 'InitializeGame:\n    lda #$7F',
                          'InitializeGame:\n    lda #$FF')
    # The one-bit XY right shift lives between the left-shift entry and its
    # one-bit fallthrough body in this version. Preserve the extra JMP.
    right = _body(common, 'ShiftXYRight1')
    common = replace_once(common, '\nShiftXYRight1:\n' + right + '\n    rts',
                          '\n    jmp ShiftXYRight1')
    common = replace_once(common, '\nShiftXYLeft1:', '\n    jmp ShiftXYLeft1\n'
                          'ShiftXYRight1:\n' + right + '\n    rts\nShiftXYLeft1:')
    # This caller retains the offset calculation inline, while TestSlotOffset
    # itself remains represented at its supported source entry.
    common = replace_once(common, '    jsr TestSlotOffset           ; CONTROL_APPLY_SLOT_OFFSET',
                          '    jsr ClampSlotOffsets           ; CONTROL_APPLY_SLOT_OFFSET\n'
                          '    lda $10\n    jsr QuerySlotAtPosition\n    ldx $10\n    cmp #$00')
    start = common.find('\nUpdateSlotBounds:\n')
    end = common.find('\nUpdateSlotVerticalBound:', start + 1)
    if start < 0 or end < 0:
        raise ValueError('missing legacy bounds wrapper')
    prologue = common[start:end]
    first = next((line for line in prologue.splitlines() if '; CONTROL_SLOT_BOUNDS' in line), None)
    if first is None or '    jsr UpdateSlotMidpoint' not in prologue:
        raise ValueError('unexpected bounds wrapper operands')
    common = common[:start] + common[end:]
    common = replace_once(common, '\nUpdateSlotMidpoint:',
                          '\nUpdateSlotBounds:\n' + first + '\n'
                          '    jsr UpdateSlotMidpoint\n    jsr UpdateSlotVerticalBound\n'
                          '    rts\nUpdateSlotMidpoint:')
    # Stream characters and address commands advance by literal counts, rather
    # than calling the later A-count helper. The number formatter's own count
    # remains two, with LDA/ADC order matching the original inline addition.
    for count in (1, 3):
        old = f'    lda #${count:02X}\n    jsr AdvancePendingPpuSource'
        new = ('    lda $EA\n    clc\n' + f'    adc #${count:02X}\n'
               '    sta $EA\n    lda $EB\n    adc #$00\n    sta $EB')
        common = replace_once(common, old, new)
    import re
    pattern = (r'    lda #\$02\n; Advance the 16-bit stream pointer by A, preserving carry into its high byte\.\n'
               r'AdvancePendingPpuSource:\n([^\n]+; CONTROL_ADVANCE_PENDING_PPU_SOURCE)\n    adc \$EA')
    common, count = re.subn(pattern, lambda m: '    lda $EA\nAdvancePendingPpuSource:\n'
                            + m[1] + '\n    adc #$02', common)
    if count != 1:
        raise ValueError('missing legacy number-format pointer advance')
    return common


def move_opcode18_audio(common: str) -> str:
    """Move the unchanged eight-byte stream to its v1.3 bank-0 location.

    The native opcode-$18 operand selects this bank-0 stream. In the later
    primary source the same command sequence is at bank-1 offset $26C8.
    """
    start = common.find('\nAudioCandidateA6C8:\n')
    end = common.find('\n.assert', start + 1)
    if start < 0 or end < 0:
        raise ValueError('missing shared opcode-18 audio stream')
    stream = common[start:end].replace('AudioCandidateA6C8:', 'LegacyOpcode18Audio:')
    common = common[:start] + common[end:]
    common = replace_once(common, '\nSlotInitialDescriptors:',
                          '\n; v1.3 opcode-$18 audio stream, before the descriptor array.\n'
                          + stream + '\nLegacyOpcode18AudioEnd:\nSlotInitialDescriptors:')
    start = common.find('\nScriptOp18:')
    end = common.find('\n.assert', start + 1)
    if start < 0 or end < 0:
        raise ValueError('missing opcode-18 audio consumer')
    block = replace_once(common[start:end], 'ldx #$C8', 'ldx #<LegacyOpcode18Audio')
    block = replace_once(block, 'ldy #$26', 'ldy #>LegacyOpcode18Audio')
    return common[:start] + block + common[end:]


def palette_before_frames(common: str) -> str:
    """Keep directory headers, palettes, then frame data in v1.3 order."""
    heading = ('; Palette control headers selected by state tables or possible BOGUS paths.\n'
               '; Colour payloads remain local. Some bytes also have candidate script or\n'
               '; sprite uses; the labels do not establish exclusive use or reachability.\n')
    start = common.find(heading + 'PaletteHeaderC7DF:')
    end = common.find('; Initialize engine state and split-screen parameters', start + 1)
    if start < 0 or end < 0:
        raise ValueError('missing palette/frame reorder boundaries')
    palettes = common[start:end]
    common = common[:start] + common[end:]
    return replace_once(common, '\nObservedSpriteDirectHeaderBA23:',
                        '\n' + palettes + '\nObservedSpriteDirectHeaderBA23:')


def shared_return_tail(common: str) -> str:
    """Preserve v1.3's aligned secondary view of the gate's return fragment.

    v1.1-v1.3 retain PLA/PLA/RTS in both banks at the exact CPU address of
    bank 0's mode-gate return tail. There is no claimed ordinary caller in
    bank 1. Keep this native view explicit without naming another routine.
    """
    marker = '    BankNativeCallAlignmentFill'
    if common.count(marker) != 2:
        raise ValueError('unexpected shared native-call alignment sites')
    before, separator, after = common.rpartition(marker)
    return before + ('; Conditional native view of the aligned bank-0 return fragment.\n'
                     '; Original purpose and ordinary bank-1 entry remain unproven.\n'
                     'SharedModeGateReturnTail:\n    LegacyModeGateReturnTail\n'
                     + separator) + after


def typed_fields(common: str, layout) -> str:
    """Relocate declared ROM operands, leaving RAM and arithmetic words alone.

    Branch CPU addresses, encoded stream/resources and encoded native RTS
    addresses have separate rules. Audio/script overlay forms keep their
    authoritative literal music encoding; no speculative script relocation is
    imposed on those bytes.
    """
    import re
    from .source_variants import operands, typed_literal

    roles = {}
    for match in re.finditer(r'(?ms)^\.macro (Bogus\w+)\s+([^\n]+)\n(.*?)^\.endmacro', common):
        name, signature, body = match.groups();params = operands(signature)
        for index, parameter in enumerate(params):
            if re.search(r'(?m)^\s*\.word ' + re.escape(parameter) + r' - \$8000(?:\s|,|$)', body):
                roles.setdefault(name, {})[index] = 'bank1_cpu'
    for name in ('BogusRestartVoice4', 'BogusStartVoice4', 'BogusStartVoice4FromIndexedPair',
                 'BogusSetVoicesFromIndexedRecord', 'BogusQueueStateAB', 'BogusQueueState6E',
                 'BogusSetBackgroundPalettePointer', 'BogusSetSpritePalettePointer',
                 'BogusLoadSlotRecordAtPointer', 'AudioPointerEntry'):
        roles[name] = {0: 'encoded'}
    for name in ('BogusSetVoicePointers', 'AudioVoicePointerRecord'):
        roles[name] = {index: 'encoded' for index in range(4)}
    roles['BogusCallNativeEncoded'] = {0: 'native_rts'}
    roles['SlotScriptOnlyRecord'] = {1: 'encoded'}
    roles['BogusLoadIndexedStateRecord'] = {0: 'encoded'}
    for name in ('SlotRuntimeRecord', 'SlotRecordScriptOverlay', 'SlotRecordVoiceOverlay', 'SlotRecordBranchPrefix'):
        roles[name] = {0: 'encoded', 1: 'encoded'}
    roles['SlotCompactRecord'] = {0: 'encoded'}

    def relocate(value: str, role: str) -> str:
        original = value
        while value.startswith('(') and value.endswith(')'):
            value = value[1:-1].strip()
        if not re.fullmatch(r'\$[0-9A-Fa-f]{4}', value):
            return original
        number = int(value[1:], 16)
        if role == 'bank1_cpu':
            if number < 0x8000 or layout.address(1, number) == number:
                return value
            return f'(Bank1Cpu {{{value}}})'
        if role == 'native_rts':
            cpu = ((number | 0x8000) + 1) & 65535
            if cpu < 0x8000:
                return value
            bank = int(number < 0x8000)
            if layout.address(bank, cpu) == cpu:
                return value
            function = 'Bank1NativeRts' if bank else 'Bank0NativeRts'
            return f'({function} {{{value}}})'
        if number >> 8 in (0, 255):
            return value
        if number == 0x26c8:
            return 'Bank0::LegacyOpcode18Audio'
        return typed_literal(value, 'Bank0Resource' if number >= 0x8000 else 'Bank1Encoded', layout)

    lines = []
    table_role = None
    pointer_remap = False
    pattern = re.compile(r'^(\s*)(\w+)\s+(.+?)\s*$')
    for line in common.splitlines():
        code, sep, comment = line.partition(';')
        if code.strip() == 'DataBE82:':table_role = 'bank1_cpu'
        elif code.strip() in ('DataD05F:', 'DataD09D:'):table_role = 'encoded'
        elif code.lstrip().startswith('.assert'):table_role = None
        if code.strip() == 'ScriptD00D:':pointer_remap = True
        elif code.strip() == 'BogusRemapEnd':pointer_remap = False
        if table_role and code.strip().startswith('.word '):
            fields = operands(code.strip().removeprefix('.word '))
            line = '    .word ' + ', '.join(relocate(value, table_role) for value in fields) + (' ;' + comment if sep else '')
            lines.append(line)
            continue
        if code.startswith('AudioScriptAC40Target = '):
            line = 'AudioScriptAC40Target = ' + relocate(code.split('=', 1)[1].strip(), 'encoded')
            lines.append(line)
            continue
        match = pattern.match(code)
        if pointer_remap and match and match[2] == 'BogusRemapCase':
            fields = operands(match[3])
            if len(fields) != 2:raise ValueError('invalid inventory-pointer remap entry')
            line = '    BogusRemapCase ' + fields[0] + ', ' + relocate(fields[1], 'encoded') + (' ;' + comment if sep else '')
            lines.append(line)
            continue
        if match and match[2] in roles:
            fields = operands(match[3])
            for index, role in roles[match[2]].items():
                if index >= len(fields):
                    raise ValueError('missing typed legacy script operand: ' + match[2])
                fields[index] = relocate(fields[index], role)
            line = match[1] + match[2] + ' ' + ', '.join(fields) + (' ;' + comment if sep else '')
        lines.append(line)
    definitions = ('\n.define Bank1Cpu(n) ' + layout.expression(bank=1)
                   + '\n.define Bank0NativeRts(n) ((Bank0Resource {(n)+1})-1)'
                   + '\n.define Bank1NativeRts(n) ((Bank1Cpu {(n)+$8001})-$8001)\n')
    return replace_once('\n'.join(lines) + '\n', '.include "nes.inc"', '.include "nes.inc"' + definitions)


def prepare(common: str, profile: dict) -> str:
    """Compose reviewed v1.3 native order and physical data moves."""
    common = overlapping_views(common)
    common = inline_helpers(common)
    common = map_queue_order(common)
    common = native_order(common)
    start = common.index('NmiFrameWork:');end = common.index('\n.assert', start)
    common = common[:start] + controller2_nmi(common[start:end]) + common[end:]
    start = common.index('ComputeBankSelection:');end = common.index('\n.assert', start)
    common = common[:start] + profile['selector_text'] + common[end:]
    common = bank_values(common, profile.get('bank_value_prefix', 8))
    common = replace_once(common, '.res $7D88 - (* - BankStart)', '.res $7D70 - (* - BankStart)')
    common = move_opcode18_audio(common)
    common = palette_before_frames(common)
    common = shared_return_tail(common)
    # This old adjacency now contains the inserted audio stream. Keep the
    # controller-table's own end assertion at the left physical boundary.
    _, end = profile['geometry'].span(0, 0x9efe, 0x9f06)
    common = replace_once(common,
                          '.assert (* - BankStart) = $1F06, error, "bank 0 controller delta table end"',
                          f'.assert (* - BankStart - ${end-32768:04X}) = 0, error, "bank 0 controller delta table end"')
    return replace_once(common, '.include "nes.inc"', '.include "nes.inc"\n' + profile['definition_text'])


def compact_constant_maps(common: str, layout) -> str:
    """Resolve literal source-map calls while retaining their logical operand.

    This keeps ca65 inputs small when a release has many relocation ranges.
    Dynamic macro parameters retain their definitions; only literal operands
    are folded, after typed source rendering and before assembly.
    """
    import re
    bank = None;lines = []
    pattern = re.compile(r'\b(TargetOffset|Bank0Resource|Bank1Encoded|Bank1Cpu|Bank0NativeRts|Bank1NativeRts)\s+\{(\$[0-9A-Fa-f]+)\}')
    def expression(name: str, literal: str):
        number = int(literal[1:], 16)
        if name == 'TargetOffset':
            if bank is None:
                raise ValueError('unscoped literal target offset')
            mapped = layout.offset(bank, number)
        elif name == 'Bank0Resource':mapped = layout.address(0, number)
        elif name == 'Bank1Encoded':mapped = layout.offset(1, number)
        elif name == 'Bank1Cpu':mapped = layout.address(1, number)
        elif name == 'Bank0NativeRts':mapped = layout.address(0, number + 1) - 1
        else:mapped = layout.address(1, number + 0x8001) - 0x8001
        return f'({literal} + ({mapped-number}))'
    for line in common.splitlines():
        if line == '.scope Bank0':bank = 0
        elif line == '.scope Bank1':bank = 1
        code, sep, comment = line.partition(';')
        code = pattern.sub(lambda m: expression(m[1], m[2]), code)
        if bank is not None:
            code = re.sub(r'(\.assert \([^\n]+ - BankStart\) = )(\$[0-9A-Fa-f]+)',
                          lambda m: m[1] + expression('TargetOffset', m[2]), code)
            code = re.sub(r'\bTargetOffset (\$[0-9A-Fa-f]+)', lambda m: expression('TargetOffset', m[1]), code)
        lines.append(code + (';' + comment if sep else ''))
    return '\n'.join(lines) + '\n'


def overlapping_views(common: str) -> str:
    """Keep target data while retiring changed primary byte predicates."""
    # The music bytes still encode $2C7F after this stream moves eight bytes.
    # Its conditional BOGUS target therefore no longer names the moved label.
    common = replace_once(common, 'AudioScriptTargetByte BogusBranchIfSlotD0Bits, $5F, (AudioScriptAC7F - BankStart),',
                          'AudioScriptTargetByte BogusBranchIfSlotD0Bits, $5F, $2C7F,')
    common = replace_once(common,
                          '.macro ContactPointerScriptOverlay target, value\n'
                          '    .assert <(target - BankStart) = $64, lderror, "contact/script opcode disagreement"\n'
                          '    .assert >(target - BankStart) = value, lderror, "contact/script operand disagreement"\n'
                          '    BogusSetInvertedState3B value\n.endmacro',
                          '.macro ContactPointerScriptOverlay target, value\n'
                          '    .assert >(target - BankStart) = value, lderror, "contact pointer high field disagreement"\n'
                          '    .word target - BankStart\n.endmacro')
    retired = ('AF00 alternate opcode disagreement', 'candidate DB69 overlapping fields',
               'E006 record/script opcode disagreement', 'E07B record/script opcode disagreement',
               'E0B6 record/script opcode disagreement', 'EB00 record/script opcode disagreement')
    common = replace_once(common,
                          '    BogusBranchPrefix BogusAdvanceAndBranchState1B, $E02F ; CONTROL_SCRIPT_PREFIX_AF02',
                          '    LegacyEncodedPointerAndByte (InteractionScriptAF05 - BankStart), $E0 ; CONTROL_SCRIPT_PREFIX_AF02')
    from .source_variants import operands
    lines = []
    for line in common.splitlines():
        code, separator, comment = line.partition(';')
        if code.strip().startswith('BogusSetJumpRecordOverlay '):
            args = operands(code.strip().split(maxsplit=1)[1])
            if len(args) != 5:
                raise ValueError('unexpected shared jump/record fields')
            # The alternate record's pointer is the jump opcode followed by
            # the relocated jump's low byte. Its actual field value changes;
            # no independent logical relocation of that incidental pointer is
            # asserted. Both byte-level views remain explicit.
            args[3] = f'($04 + (<({args[1]} - BankStart) * $100))'
            args[4] = f'>({args[1]} - BankStart)'
            line = '    BogusSetJumpRecordOverlay ' + ', '.join(args) + (' ;' + comment if separator else '')
        if code.strip().startswith('BogusJumpCompactOverlay '):
            args = operands(code.strip().split(maxsplit=1)[1])
            if len(args) != 3:
                raise ValueError('unexpected shared jump/compact fields')
            args[1] = f'($04 + (<({args[0]} - BankStart) * $100))'
            args[2] = f'>({args[0]} - BankStart)'
            line = '    BogusJumpCompactOverlay ' + ', '.join(args) + (' ;' + comment if separator else '')
        if any('"' + message + '"' in line for message in retired):
            if not line.startswith('.assert'):
                raise ValueError('unexpected primary overlap predicate context')
            line = '; v1.3 changed conditional byte predicate: ' + line
        lines.append(line)
    return '\n'.join(lines) + '\n'
