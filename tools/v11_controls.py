"""Controls for v1.1 additions and changed physical representations.

Mutations edit the composed readable source. They never edit ROM output or
weaken the independent comparison and physical-ownership requirements.
"""
from .source_variants import marked_statement, operands

NEW = ('v11_extra_descriptors', 'v11_extra_palettes', 'v11_af02_script',
       'v11_position_extra', 'v11_fetched_storage', 'v11_coordinates',
       'v11_secondary_controller', 'v11_menu_palettes')


def change_field(statement: str, index: int) -> str:
    name, arguments = statement.split(maxsplit=1)
    fields = operands(arguments)
    fields[index] = '(' + fields[index] + ' + 1)'
    return name + ' ' + ', '.join(fields)


def mutate(source: str, name: str) -> str:
    if name == 'v11_extra_palettes':
        for index in range(26, 31):
            source = marked_statement(source, f'CONTROL_V11_PALETTE_EXTRA_{index}',
                                      lambda statement: 'PaletteStreamHeader $01, $01, $00')
        return source
    marker, field = {
        'v11_extra_descriptors': ('CONTROL_V11_EXTRA_DESCRIPTORS', 0),
        'v11_af02_script': ('CONTROL_V11_AF02_SCRIPT', 0),
        'v11_position_extra': ('CONTROL_V11_POSITION_EXTRA', 3),
        'v11_fetched_storage': ('CONTROL_V11_D68F_FETCHED_STORAGE', 0),
        'v11_coordinates': ('CONTROL_V11_D68F_COORDINATES', 0),
        'v11_secondary_controller': ('CONTROL_V11_SECONDARY_CONTROLLER', 0),
        'v11_menu_palettes': ('CONTROL_V11_MENU_PALETTES', 0),
    }[name]
    if name == 'v11_secondary_controller':
        return marked_statement(source, marker, lambda statement: 'lda $0621,x')
    return marked_statement(source, marker, lambda statement: change_field(statement, field))

# These whole extents are absent, rather than merely changed instructions in
# surviving regions. Profile reasons identify their replacement evidence.
RETIRED = frozenset(('inferred_b0b0', 'direct_next_script_b0b3', 'slot_runtime_d6d7',
                     'bogus_d6e0', 'extended_script_ee62', 'sweep_record_d3c0',
                     'script_opc4', 'store_record_field_0a', 'fade_palette_load',
                     'fade_wait_vblank'))

ADAPTED = frozenset(('background_palette_pointers', 'sprite_palette_pointers',
                     'allocate_sprite_find_space', 'allocate_sprite_search',
                     'slot_flow_d5cc', 'context_f401', 'bogus_babd',
                     'contact_script_dc26', 'contact_script_e08a',
                     'context_contact_script_d67c', 'context_direct_record_d68f',
                     'bogus_f0d1', 'successor_script_af59', 'successor_script_b34a',
                     'branch_script_fd65', 'overlay_ee65', 'script_op5f', 'script_op60',
                     'slot_update_limits', 'slot_draw_check_release',
                     'select_slot_horizontal_motion', 'select_slot_vertical_motion'))


def scoped(source: str, start: str, end: str, old: str, new: str) -> str:
    from .source_variants import replace_once
    low = source.index('\n' + start + ':')
    high = source.index('\n' + end + ':', low)
    return source[:low] + replace_once(source[low:high], old, new) + source[high:]


def adapt(source: str, name: str) -> str:
    ram = {
        'script_op5f': ('$07F0', '$07F1'), 'script_op60': ('$07F0', '$07F1'),
        'slot_update_limits': ('$05D0', '$05D1'),
        'slot_draw_check_release': ('$C0', '$C1'),
        'select_slot_horizontal_motion': ('$C0', '$C1'),
        'select_slot_vertical_motion': ('$C0', '$C1'),
    }
    if name in ram:
        from .build_rom import MUTATIONS
        from .source_variants import replace_once
        old, new = ram[name]
        return marked_statement(source, MUTATIONS[name][0],
                                lambda text: replace_once(text, old, new))
    if name in ('background_palette_pointers', 'sprite_palette_pointers'):
        marker = ('CONTROL_BACKGROUND_PALETTE_POINTERS' if name.startswith('background')
                  else 'CONTROL_SPRITE_PALETTE_POINTERS')
        return marked_statement(source, marker, lambda text: change_field(text, 0))
    if name in ('context_contact_script_d67c', 'successor_script_af59'):
        marker = ('CONTROL_CONTEXT_CONTACT_SCRIPT_D67C' if name.startswith('context')
                  else 'CONTROL_SUCCESSOR_SCRIPT_AF59')
        return marked_statement(source, marker, lambda text: change_field(text, 0))
    if name in ('context_direct_record_d68f', 'slot_flow_d5cc'):
        marker = ('CONTROL_CONTEXT_DIRECT_RECORD_D68F' if name.startswith('context')
                  else 'CONTROL_SLOT_FLOW_D5CC')
        return marked_statement(source, marker, lambda text: change_field(text, 0))
    if name in ('contact_script_dc26', 'contact_script_e08a'):
        marker = 'CONTROL_' + name.upper()
        # The high pointer field is shared with the preceding contact record;
        # change an actual retained flag, preserving that pointer relationship.
        return marked_statement(source, marker, lambda text: change_field(text, 1))
    if name == 'overlay_ee65':
        return marked_statement(source, 'CONTROL_OVERLAY_EE65',
                                lambda text: text.replace('ScriptEFF3', '(ScriptEFF3 + 1)'))
    start, end, old, new = {
        'allocate_sprite_find_space': ('AllocateSpriteFindSpace', 'AllocateSpriteSkipReserved',
                                      'ldy #$01', 'ldy #$02'),
        'allocate_sprite_search': ('AllocateSpriteSearchCandidate', 'AllocateSpriteSearchCount',
                                  'ldx $03E3', 'ldx $03E2'),
        'context_f401': ('ContextScriptF401', 'CandidateScriptF40A',
                         'BogusStoreSlotValueArray $23', 'BogusStoreSlotValueArray $22'),
        'bogus_babd': ('ScriptBAB8', 'ScriptBAD1',
                       'BogusReadSlotValue $11', 'BogusReadSlotValue $10'),
        'bogus_f0d1': ('CandidateF0D1', 'CandidateF0F0',
                       'BogusBranchIfSlot0620Bit10 CandidateF0F0',
                       'BogusBranchIfSlot0620Bit10 CandidateF0F0 + 1'),
        'successor_script_b34a': ('SuccessorScriptB34A', 'ExtendedScriptB35B',
                                 'BogusSetDispatchCounter $07', 'BogusSetDispatchCounter $06'),
        'branch_script_fd65': ('BranchScriptFD65', 'V11SecondaryControllerTail',
                               'BogusSetMainState $15', 'BogusSetMainState $14'),
    }[name]
    return scoped(source, start, end, old, new)
