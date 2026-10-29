"""Source controls cannot credit copied bytes or fabricate symbol operands."""
import unittest

from tools.variant_controls import changed_owned, coverage, verify_symbol


class VariantControlTests(unittest.TestCase):
    def test_negative_must_change_real_owned_source_and_cover_each_region(self):
        reference = bytes(12)
        regions = [{'id': 'code', 'kind': 'code', 'file_offset': 2, 'size': 3},
                   {'id': 'data', 'kind': 'data', 'file_offset': 7, 'size': 2}]
        for changed in (reference, reference[:9] + b'\x01' + reference[10:]):
            with self.assertRaises(ValueError):changed_owned(reference, changed, regions)
        candidate = reference[:3] + b'\x01' + reference[4:]
        offsets = changed_owned(reference, candidate, regions)
        result = coverage(regions, [{'changed_offsets': offsets}])
        self.assertFalse(result['complete']);self.assertEqual(result['uncontrolled_regions'], ['data'])
        self.assertTrue(coverage(regions, [{'changed_offsets': offsets}, {'changed_offsets': [7]}])['complete'])

    def test_symbol_changes_are_actual_operands_with_the_declared_xor(self):
        # Two synthetic LDA $0530 operands; the target may have a different
        # use count from the primary. Other code bytes cannot substitute.
        reference = bytes((0xad, 0x30, 0x05, 0xad, 0x30, 0x05, 0x60))
        regions = [{'id': 'native', 'kind': 'code', 'file_offset': 0, 'size': 7}]
        candidate = bytes((0xad, 0x31, 0x05, 0xad, 0x31, 0x05, 0x60))
        self.assertEqual(verify_symbol(reference, candidate, regions, 'SlotScriptWait', 'us-v1.3'), [1, 4])
        for altered in (bytes((0xac, 0x31, 0x05, 0xad, 0x31, 0x05, 0x60)),
                        bytes((0xad, 0x32, 0x05, 0xad, 0x31, 0x05, 0x60)),
                        bytes((0xad, 0x31, 0x06, 0xad, 0x31, 0x05, 0x60))):
            with self.assertRaises(ValueError):verify_symbol(reference, altered, regions, 'SlotScriptWait', 'us-v1.3')
