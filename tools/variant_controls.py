"""Target source-control applicability and actual source-owned output changes."""
from __future__ import annotations

from copy import deepcopy

from .build_rom import MUTATIONS, SYMBOL_CONTROLS, mutate_source, verify_control, verify_symbol_control
from .nes6502 import OPCODES
from .source_variants import replace_once, marked_statement, compose

EXTRA = {
    'v13_controller2_port': ('definition_text', '.macro ReadSecondController', '    lda $4017', '    lda JOY1'),
    'v13_inline_shift': ('definition_text', '.macro LegacyShiftPairLeft', '    asl lowOperand', '    lsr lowOperand'),
    'v13_shared_return_tail': ('definition_text', '.macro LegacyModeGateReturnTail', '    pla', '    pha'),
    'v13_pointer_af02': ('definition_text', '.macro LegacyEncodedPointerAndByte', '    .word pointer', '    .word pointer + 1'),
    'v13_mapper_prefix': ('bank_value_prefix', None, 8, 10),
}
RETIRED = frozenset(('shift_left4', 'double_fe_pointer', 'scale_position_by_eight', 'shift_reference_right',
                     'scale_world_shift', 'shift_search_coordinate_right', 'shift_scrolled_slot_horizontal',
                     'pending_ppu_set_source', 'advance_audio_command_two', 'script_prefix_af02', 'main_state_scale'))
RETIRED_12 = RETIRED | {'reset_dispatch', 'scroll_x_tile_coordinate', 'scroll_y_tile_coordinate'}
EXTRA_12 = {
    'v12_initial_map': ('.macro V12InitialMapTilePosition', '    lda ScrollTargetXLow', '    lda ScrollTargetXHigh'),
    'v12_main_xy_shift': ('.macro V12MainShiftXYRight3', '        lsr a', '        asl a'),
    'v12_mode_return': ('.macro V12ModeGateReturnTail', '    bne returnReady', '    beq returnReady'),
    'v12_inline_mapper': ('.macro V12RestoreDefaultBankInline', '    sta BankValues,y', '    sta BankValues+1,y'),
    'v12_audio_return': ('.macro V12AudioShadowReturnTail', '    jmp StopAudioVoiceReturn', '    jmp StopAudioVoiceReturn + 1'),
}
NEW_12 = [*EXTRA_12, 'v12_reset_mapper', 'v12_reset_table', 'v12_xy_right_target']


def names(profile: dict) -> list[str]:
    if profile['target'] == 'us-v1.4':
        return list(MUTATIONS)
    if profile['target'] not in ('us-v1.3', 'us-v1.2', 'us-v1.1'):
        raise ValueError('missing target source-control catalogue')
    retired = profile.get('retired_primary_controls', {})
    required = RETIRED_12 if profile['target'] in ('us-v1.2', 'us-v1.1') else RETIRED
    if profile['target'] == 'us-v1.1':
        from .v11_controls import RETIRED as retired11
        required = required | retired11
    if (set(retired) != required or any(not isinstance(reason, str) or not reason.strip() for reason in retired.values())):
        raise ValueError('target primary-control retirements lack explicit decisions')
    additions = (['v13_controller2_port', 'v13_inline_shift', 'v13_pointer_af02'] + NEW_12
                 if profile['target'] in ('us-v1.2', 'us-v1.1') else list(EXTRA))
    if profile['target'] == 'us-v1.1':
        from .v11_controls import NEW
        additions = [name for name in additions if name != 'v12_mode_return'] + list(NEW)
    return [name for name in MUTATIONS if name not in required] + additions


def mutate(canonical: str, reset: str, profile: dict, name: str) -> str:
    if name not in names(profile):
        raise ValueError('unknown or retired source control')
    if profile['target'] == 'us-v1.1':
        from .v11_controls import NEW, ADAPTED, mutate as mutate11, adapt
        if name in NEW or name in ADAPTED:
            source = compose(canonical, reset, profile)
            return mutate11(source, name) if name in NEW else adapt(source, name)
    candidate_profile = deepcopy(profile)
    if name in EXTRA_12 or (profile['target'] in ('us-v1.2', 'us-v1.1') and name == 'set_initial_map_tile_position'):
        scope, original, replacement = EXTRA_12['v12_initial_map' if name == 'set_initial_map_tile_position' else name]
        text = candidate_profile['earlier_definition_text']
        start = text.index(scope);end = text.index('.endmacro', start)
        candidate_profile['earlier_definition_text'] = text[:start] + replace_once(text[start:end], original, replacement) + text[end:]
    elif name in ('v12_reset_mapper', 'v12_reset_table'):
        old, new = (('lda #$0C', 'lda #$08') if name == 'v12_reset_mapper'
                    else ('MapperConflict08:\n    .byte $08', 'MapperConflict08:\n    .byte $00'))
        reset = replace_once(reset, old, new)
    elif name == 'v12_xy_right_target':
        start = canonical.index('\nShiftXYRight3:');end = canonical.index('\nShiftXYRight1:', start)
        body = canonical[start:end]
        if body.count('jsr ShiftXYRight1') != 2:raise ValueError('changed generic XY shift calls')
        canonical = canonical[:start] + body.replace('jsr ShiftXYRight1', 'jsr ShiftXYRight1 + 1', 1) + canonical[end:]
    elif profile['target'] in ('us-v1.2', 'us-v1.1') and name == 'queue_scroll_row':
        start = canonical.index('\nQueueScrollRow:');end = canonical.index('\n.assert', start)
        canonical = canonical[:start] + replace_once(canonical[start:end], 'stx MapTileXLow', 'stx MapTileXHigh') + canonical[end:]
    elif name in EXTRA:
        key, scope, original, replacement = EXTRA[name]
        if scope is None:
            if candidate_profile.get(key) != original:
                raise ValueError('changed target control parameter')
            candidate_profile[key] = replacement
        else:
            text = candidate_profile[key]
            start = text.find(scope);end = text.find('.endmacro', start + 1)
            if start < 0 or end < 0:
                raise ValueError('missing target source-control macro')
            body = text[start:end]
            # A return fragment has two PLAs; change the first instruction.
            if name == 'v13_shared_return_tail':
                if body.count(original) != 2:raise ValueError('changed return-fragment shape')
                body = body.replace(original, replacement, 1)
            else:body = replace_once(body, original, replacement)
            candidate_profile[key] = text[:start] + body + text[end:]
    elif name == 'reset_dispatch':reset = mutate_source(reset, name)
    elif profile['target'] in ('us-v1.3', 'us-v1.2', 'us-v1.1') and name == 'compute_bank_selection':
        candidate_profile['selector_text'] = mutate_source(profile['selector_text'], name)
    elif profile['target'] in ('us-v1.3', 'us-v1.2', 'us-v1.1') and name == 'apply_slot_offset':
        start = canonical.index('\nApplySlotOffsetIfClear:');end = canonical.index('\n.assert', start)
        block = replace_once(canonical[start:end], 'lda $03A6', 'lda $03A7')
        canonical = canonical[:start] + block + canonical[end:]
    elif profile['target'] in ('us-v1.3', 'us-v1.2', 'us-v1.1') and name in ('record_voice_e01a', 'record_voice_e023'):
        # The primary script-pointer edit becomes a relocated ROM pointer in
        # this target. Mutate the actual record mode instead, retaining the
        # corresponding conditional voice word rather than breaking its assertion.
        marker, original, _ = MUTATIONS[name]
        changed = replace_once(original, '$FFFF, $00,', '$FFFF, $01,')
        changed = replace_once(changed, '$FFB8, $00FF,', '$FFB8, $01FF,')
        canonical = marked_statement(canonical, marker, lambda statement: replace_once(statement, original, changed))
    elif profile['target'] in ('us-v1.3', 'us-v1.2', 'us-v1.1') and name in ('script_op08', 'script_op2d', 'prepare_audio_note',
                                                   'script_op9f', 'script_opa0', 'convert_slot_position',
                                                   'pending_ppu_copy_banked'):
        # Literal primary addresses can coincide with the relocated positive
        # target; removed JSRs cannot carry a call-target mutation into an inline
        # macro. Change a surviving operand in the same caller instead.
        label, old, new = {
            'script_op08': ('ScriptOp08', 'jsr UpdateSlotFieldsMode00', 'jsr UpdateSlotFieldsMode00 + 1'),
            'script_op2d': ('ScriptOp2D', 'jsr UpdateSlotFieldsMode80', 'jsr UpdateSlotFieldsMode80 + 1'),
            'prepare_audio_note': ('PrepareAudioNote', 'and #$FE', 'and #$FC'),
            'script_op9f': ('ScriptOp9F', 'jmp ScriptCompareOffset', 'jmp ScriptCompareOffset + 1'),
            'script_opa0': ('ScriptOpA0', 'lda #$00', 'lda #$01'),
            'convert_slot_position': ('ConvertSlotPosition', 'lda $51', 'lda $50'),
            'pending_ppu_copy_banked': ('PendingPpuCopyBanked', 'lda $E7', 'lda $E6'),
        }[name]
        start = canonical.index('\n' + label + ':')
        next_label = {'script_op9f': 'ScriptGetSecondOffset', 'script_opa0': 'ScriptShiftAInto03',
                      'convert_slot_position': 'ScalePositionByEight',
                      'pending_ppu_copy_banked': 'PendingPpuSetSource'}.get(name)
        end = (canonical.index('\n' + next_label + ':', start) if next_label
               else canonical.index('\n.assert', start))
        block = replace_once(canonical[start:end], old, new)
        canonical = canonical[:start] + block + canonical[end:]
    else:canonical = mutate_source(canonical, name)
    return compose(canonical, reset, candidate_profile)


def changed_owned(reference: bytes, candidate: bytes, regions: list[dict]) -> list[int]:
    if len(reference) != len(candidate):
        raise ValueError('target source control changed output size')
    owned = set()
    for row in regions:owned.update(range(row['file_offset'], row['file_offset'] + row['size']))
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if not changed or any(i not in owned for i in changed):
        raise ValueError('target source control is ineffective or changes a local asset/container byte')
    return changed


def verify_source(reference: bytes, candidate: bytes, regions: list[dict], name: str, target: str) -> list[int]:
    if target == 'us-v1.4':return verify_control(reference, candidate, regions, name)
    return changed_owned(reference, candidate, regions)


def affected(regions: list[dict], offsets: list[int]) -> list[str]:
    changed = set(offsets)
    return [row['id'] for row in regions if any(i in changed for i in range(row['file_offset'], row['file_offset'] + row['size']))]


def verify_symbol(reference: bytes, candidate: bytes, regions: list[dict], name: str, target: str) -> list[int]:
    if target == 'us-v1.4':return verify_symbol_control(reference, candidate, regions, name)
    changed = changed_owned(reference, candidate, regions)
    address = symbol_address(name, target)
    operand_bytes = set()
    for row in regions:
        if row['kind'] != 'code':continue
        start, end = row['file_offset'], row['file_offset'] + row['size']
        while start < end:
            if reference[start] not in OPCODES:
                raise ValueError('symbol control encountered a non-instruction source window')
            size = OPCODES[reference[start]][2]
            if start + size > end or candidate[start] != reference[start]:
                raise ValueError('symbol control changes an opcode or instruction boundary')
            operand_bytes.update(range(start + 1, start + size));start += size
    if any(i not in operand_bytes or reference[i] != (address & 255) or candidate[i] != ((address ^ 1) & 255)
           or (address >= 256 and (i + 1 not in operand_bytes or reference[i + 1] != address >> 8 or candidate[i + 1] != address >> 8))
           for i in changed):
        raise ValueError('target symbol control does not change its actual source operands')
    return changed


def coverage(regions: list[dict], controls: list[dict]) -> dict:
    """Require a demonstrated output change in every physical source region."""
    offsets = {i for row in controls for i in row['changed_offsets']}
    missing = [row['id'] for row in regions
               if not any(i in offsets for i in range(row['file_offset'], row['file_offset'] + row['size']))]
    return {'regions': len(regions), 'controlled_regions': len(regions) - len(missing),
            'uncontrolled_regions': missing, 'complete': not missing}


def symbol_names(profile: dict) -> list[str]:
    return [name for name in SYMBOL_CONTROLS
            if profile['target'] != 'us-v1.1' or name != 'SpriteRecordReserveCount']


def symbol_address(name: str, target: str) -> int:
    address = SYMBOL_CONTROLS[name][0]
    if target == 'us-v1.1':
        if name == 'SpriteRecordStride':return 10
        if 0x04B0 <= address < 0x0800:return address - 16
    return address


def mutate_symbol(include: str, name: str, target: str) -> str:
    address = symbol_address(name, target)
    return replace_once(include, f'{name} = ${address:04X}', f'{name} = ${address ^ 1:04X}')
