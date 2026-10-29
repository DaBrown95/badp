import copy
import unittest

from tools.v11_source import descriptors, script_descriptor_indices, script_fragments, palette_pointers


class DescriptorVariants(unittest.TestCase):
    def setUp(self):
        self.source = '\nSlotInitialDescriptors:\n' + (
            '    SlotDescriptor $1234, $01, $02, $03, $04\n' * 114
        ) + '.assert * = $9000\n'
        self.variant = {
            'schema_version': 1, 'target': 'us-v1.1', 'shared_entries': 114, 'entries': 127,
            'unavailable_indices': [2],
            'field_overrides': [{'index': 3, 'expected': [1, 2, 3, 4], 'fields': [5, 6, 7, 8]}],
            'extra_entries': [{'record': '0x2222', 'fields': [9, 10, 11, 12]} for _ in range(13)],
        }

    def test_preserves_shared_pointer_mutation_and_exact_extent(self):
        changed = self.source.replace('$1234', '$1235', 1)
        result = descriptors(changed, self.variant)
        self.assertIn('SlotDescriptor $1235, $01, $02, $03, $04', result)
        self.assertIn('SlotDescriptor $FFFF, $01, $02, $03, $04', result)
        self.assertIn('SlotDescriptor $1234, $05, $06, $07, $08', result)
        self.assertEqual(result.count('    SlotDescriptor '), 127)

    def test_rejects_stale_fields_duplicate_changes_and_missing_entries(self):
        for change in ('stale', 'duplicate', 'extent'):
            variant = copy.deepcopy(self.variant)
            if change == 'stale':
                variant['field_overrides'][0]['expected'][0] = 99
            elif change == 'duplicate':
                variant['field_overrides'] *= 2
            else:
                variant['extra_entries'].pop()
            with self.subTest(change=change), self.assertRaises(ValueError):
                descriptors(self.source, variant)

    def test_remaps_descriptor_role_without_changing_generic_values(self):
        source = ('    BogusCreateSlotFromValue $53, $00\n'
                  '    BogusSetSlotValue $0053\n'
                  '    BogusCreateSlotFromValue dynamicIndex, $53\n')
        variant = {'target': 'us-v1.1', 'script_index_remap': {'0x53': 118},
                   'script_index_roles': {'BogusCreateSlotFromValue': 0,
                                          'BogusInitializeOtherSlotRelative': 0,
                                          'BogusInitializeOtherSlotAbsolute': 0,
                                          'BogusCountSlotsByRecord': 0, 'BogusCreateLinkedSlot': 0}}
        result = script_descriptor_indices(source, variant)
        self.assertIn('BogusCreateSlotFromValue $76, $00', result)
        self.assertIn('BogusSetSlotValue $0053', result)
        self.assertIn('BogusCreateSlotFromValue dynamicIndex, $53', result)

    def test_fragment_edit_is_scoped_and_rejects_a_stale_statement(self):
        source = '\nA:\n    BogusWait $02\nB:\n    BogusWait $02\nC:\n'
        variant = {'script_fragments': [{'start': 'A', 'end': 'B', 'remove': ['    BogusWait $02']}]}
        result = script_fragments(source, variant)
        self.assertEqual(result.count('BogusWait $02'), 1)
        with self.assertRaises(ValueError):
            script_fragments(result, variant)

    def test_conditional_descriptor_roles_preserve_coordinate_and_link_selectors(self):
        variant = {'target': 'us-v1.1', 'script_index_remap': {'0x53': 118},
                   'script_index_roles': {'BogusCreateSlotFromValue': 0,
                       'BogusInitializeOtherSlotRelative': 0,
                       'BogusInitializeOtherSlotAbsolute': 0, 'BogusCountSlotsByRecord': 0,
                       'BogusCreateLinkedSlot': 0},
                   'conditional_script_index_roles': {
                       'BogusBranchIfMatchingSlotReady': {'selector': 1, 'index': 2, 'excluded_selectors': [0]},
                       'BogusMarkMatchingSlots': {'selector': 1, 'index': 2, 'excluded_selectors': [0, 255]},
                       'BogusSelectRelativeSlotAndYield': {'selector': 2, 'index': 3, 'excluded_selectors': [0, 35]}}}
        source = ('    BogusCreateLinkedSlot $53, $53, $00, $00\n'
                  '    BogusMarkMatchingSlots $00, $01, $53, $00\n'
                  '    BogusMarkMatchingSlots $00, $FF, $53, $00\n'
                  '    BogusMarkMatchingSlots $00, $00, $53, $00\n'
                  '    BogusSelectRelativeSlotAndYield $00, $00, $23, $53, $00\n')
        result = script_descriptor_indices(source, variant)
        self.assertIn('BogusCreateLinkedSlot $76, $53, $00, $00', result)
        self.assertIn('BogusMarkMatchingSlots $00, $01, $76, $00', result)
        self.assertIn('BogusMarkMatchingSlots $00, $FF, $53, $00', result)
        self.assertIn('BogusMarkMatchingSlots $00, $00, $53, $00', result)
        self.assertIn('BogusSelectRelativeSlotAndYield $00, $00, $23, $53, $00', result)
        variant['conditional_script_index_roles']['BogusMarkMatchingSlots']['selector'] = 0
        with self.assertRaises(ValueError):script_descriptor_indices(source, variant)

    def test_repeated_fragment_statements_require_the_declared_count(self):
        source = '\nA:\n    BogusWait $02\n    BogusWait $02\nB:\n'
        change = {'start': 'A', 'end': 'B', 'remove': ['    BogusWait $02']}
        with self.assertRaises(ValueError):script_fragments(source, {'script_fragments': [change]})
        change['remove'] *= 2
        self.assertNotIn('BogusWait', script_fragments(source, {'script_fragments': [change]}))
        change = {'start': 'A', 'end': 'B', 'replace': [
            {'old': '    BogusWait $02', 'new': '    BogusWait $03', 'count': 2}]}
        self.assertEqual(script_fragments(source, {'script_fragments': [change]}).count('BogusWait $03'), 2)
        change['replace'][0]['count'] = 3
        with self.assertRaises(ValueError):script_fragments(source, {'script_fragments': [change]})

    def test_palette_selections_reject_stale_fields_and_duplicate_indices(self):
        source = '\nBackgroundPalettePointers:\n    .word ' + ', '.join(['OldPalette'] * 22)
        source += '\nSpritePalettePointers:\n    .word ' + ', '.join(['OldPalette'] * 22) + '\n.assert * = $9000\n'
        variant = {'palette_pointer_overrides': [
            {'table': 'BackgroundPalettePointers', 'index': 0, 'expected': 'OldPalette', 'target': 'NewPalette'}]}
        self.assertEqual(palette_pointers(source, variant).count('NewPalette'), 1)
        stale = source.replace('OldPalette', 'ChangedPalette', 1)
        with self.assertRaises(ValueError):palette_pointers(stale, variant)
        variant['palette_pointer_overrides'] *= 2
        with self.assertRaises(ValueError):palette_pointers(source, variant)


if __name__ == '__main__':
    unittest.main()
