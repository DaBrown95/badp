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

    def test_v11_symbol_addresses_use_own_layout_and_absent_field_is_not_required(self):
        from tools.variant_controls import symbol_names, mutate_symbol
        self.assertNotIn('SpriteRecordReserveCount', symbol_names({'target': 'us-v1.1'}))
        self.assertIn('SpriteRecordReserveCount', symbol_names({'target': 'us-v1.2'}))
        self.assertEqual(mutate_symbol('SlotScriptWait = $0520\n', 'SlotScriptWait', 'us-v1.1'),
                         'SlotScriptWait = $0521\n')
        reference = bytes((0xad, 0x20, 0x05, 0x60))
        candidate = bytes((0xad, 0x21, 0x05, 0x60))
        regions = [{'id': 'native', 'kind': 'code', 'file_offset': 0, 'size': 4}]
        self.assertEqual(verify_symbol(reference, candidate, regions, 'SlotScriptWait', 'us-v1.1'), [1])
        with self.assertRaises(ValueError):verify_symbol(reference, candidate, regions, 'SlotScriptWait', 'us-v1.2')

    def test_bank_tail_transfer_uses_own_source_span_and_rejects_other_calls(self):
        from tools.build_variant import reviewed_tail_transfer
        source = ('jsr Bank0::NmiFrameWork\n.macro BankTail value, index\n'
                  '    jsr Bank0::NmiFrameWork ; shared NMI continuation\n'
                  '    jmp Bank0::Boot\n    jsr OtherRoutine\n.endmacro\n')
        row = {'bank': 1, 'other_bank_instruction_start': True, 'source_line': 3,
               'operation': 'jsr', 'cpu': '0xe123'}
        self.assertTrue(reviewed_tail_transfer(source, row))
        self.assertTrue(reviewed_tail_transfer(source, {**row, 'source_line': 4, 'operation': 'jmp'}))
        for change in ({'bank': 0}, {'other_bank_instruction_start': False},
                       {'source_line': 1}, {'source_line': 5}, {'source_line': 99},
                       {'operation': 'jmp'}):
            with self.subTest(change=change):
                self.assertFalse(reviewed_tail_transfer(source, {**row, **change}))
