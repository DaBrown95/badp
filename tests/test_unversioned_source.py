"""Synthetic descriptor source checks; no game payload or ROM fixture."""
import copy
import unittest

from tools.unversioned_source import descriptor_table


class UnversionedDescriptorTests(unittest.TestCase):
    def setUp(self):
        self.source = '\nSlotInitialDescriptors:\n' + '\n'.join(
            '    SlotDescriptor $4000, $00, $00, $00, $00' for _ in range(114))
        self.source += '\n.assert * = $A000, error, "synthetic old end"\nFollowingData:\n'
        self.variant = {'schema_version': 1, 'target': 'us-unversioned',
                        'shared_entries': 114, 'entries': 123,
                        'record_pointers': ['0x4000'] * 123,
                        'field_overrides': [{'index': 1, 'expected': [0, 0, 0, 0],
                                             'fields': [2, 3, 4, 5]}],
                        'extra_fields': [[6, 7, 8, 9] for _ in range(9)],
                        'known_record_labels': {'0x4000': 'InventedRecord'}}

    def test_shared_field_edits_survive_and_following_source_is_retained(self):
        changed = self.source.replace('SlotDescriptor $4000, $00',
                                      'SlotDescriptor $4000, $01', 1)
        result = descriptor_table(changed, self.variant)
        self.assertIn('UnversionedSlotDescriptor InventedRecord, $01, $00, $00, $00', result)
        self.assertIn('UnversionedSlotDescriptor InventedRecord, $02, $03, $04, $05', result)
        self.assertIn('UnversionedSlotDescriptor InventedRecord, $06, $07, $08, $09', result)
        self.assertTrue(result.endswith('FollowingData:\n'))
        self.assertNotIn('synthetic old end', result)

    def test_changed_override_context_and_invalid_fields_fail_closed(self):
        changed = self.source.replace('SlotDescriptor $4000, $00, $00, $00, $00',
                                      'SlotDescriptor $4000, $01, $00, $00, $00', 2)
        with self.assertRaisesRegex(ValueError, 'override context'):
            descriptor_table(changed, self.variant)
        for kind in ('bool', 'bad_pointer', 'missing_extra', 'duplicate_override', 'unbound_label'):
            variant = copy.deepcopy(self.variant)
            if kind == 'bool': variant['extra_fields'][0][0] = True
            elif kind == 'bad_pointer': variant['record_pointers'][0] = 'address expression'
            elif kind == 'missing_extra': variant['extra_fields'].pop()
            elif kind == 'duplicate_override': variant['field_overrides'] *= 2
            else: variant['known_record_labels']['0x4001'] = 'MissingRecord'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                descriptor_table(self.source, variant)


if __name__ == '__main__':
    unittest.main()
