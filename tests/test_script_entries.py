"""Script-entry inventory tests use synthetic banks, never game data."""
import unittest
from unittest.mock import patch

from tools.script_entries import BANK_SIZE, _locate, decode_slot_record, inventory, main, record_fetch_plan


def banks():
    return bytearray(BANK_SIZE), bytearray(BANK_SIZE)


def put_word(data, offset, value):
    data[offset:offset + 2] = value.to_bytes(2, 'little')


class ScriptEntryTests(unittest.TestCase):
    def test_slot_record_decodes_used_fields_and_separate_lookahead(self):
        result = decode_slot_record(bytes([0x34, 0x81, 0x78, 0x56, 0x40,
                                           1, 2, 3, 4, 0x99]))
        self.assertEqual(result['sprite_pointer'], 0x8134)
        self.assertEqual(result['encoded_script_pointer'], 0x5678)
        self.assertEqual(result['mode_flags'], 0x40)
        self.assertEqual(result['fields_0690_to_06c0'], [1, 2, 3, 4])
        self.assertEqual(result['lookahead'], 0x99)
        self.assertTrue(result['sprite_fields_present'])
        self.assertTrue(result['script_installable_in_zero_mode'])
        empty = decode_slot_record(bytes([0, 0xff, 0, 0xff, 0, 0, 0, 0, 0, 0]))
        self.assertFalse(empty['sprite_fields_present'])
        self.assertFalse(empty['script_installable_in_zero_mode'])
        with self.assertRaisesRegex(ValueError, 'ten fetched'):
            decode_slot_record(bytes(9))

    def test_banked_records_aliases_and_first_command(self):
        b0, b1 = banks()
        for start, ptr in ((0, 0x20), (6, 0x20), (12, 0x30)):
            put_word(b0, start, ptr)
        put_word(b1, 0x22, 0x40)
        put_word(b1, 0x32, 0x40)
        b1[0x40:0x43] = bytes([2, 12, 34])
        got = inventory(bytes(b0), bytes(b1), 0, 3, bytes([1, 2, 3]))
        self.assertEqual(len(got['records']), 2)
        self.assertEqual(got['records'][0]['descriptor_indices'], [0, 1])
        self.assertEqual(len(got['entries']), 1)
        self.assertEqual(got['entries'][0]['status'], 'decoded_first_command')
        self.assertEqual(got['entries'][0]['operands'], [12, 34])
        self.assertEqual(got['entries'][0]['location'],
                         {'bank': 1, 'bank_offset': 0x40, 'cpu_address': '0x8040',
                          'physical_prg_offset': BANK_SIZE + 0x40})

    def test_direct_bank_and_high_byte_sentinel(self):
        b0, b1 = banks()
        put_word(b0, 0, 0x8020)
        put_word(b0, 6, 0x30)
        put_word(b0, 0x22, 0x8040)
        put_word(b1, 0x32, 0xff12)
        b0[0x40:0x42] = bytes([1, 77])
        got = inventory(bytes(b0), bytes(b1), 0, 2, bytes([1, 2]))
        self.assertEqual(got['entries'][0]['location']['bank'], 0)
        self.assertEqual(got['entries'][0]['operands'], [77])
        self.assertEqual(got['records'][1]['script_status'], 'not_installed_high_byte_ff')
        self.assertEqual(len(got['entries']), 1)

    def test_boundary_and_invalid_opcode_are_reported(self):
        b0, b1 = banks()
        put_word(b0, 0, 0xffff)
        put_word(b0, 6, 0x20)
        put_word(b1, 0x22, 0x40)
        b1[0x40] = 4
        got = inventory(bytes(b0), bytes(b1), 0, 2, bytes([1, 1]))
        self.assertEqual(got['records'][0]['status'], 'crosses_bank_boundary')
        self.assertEqual(got['records'][0]['fetch_plan'], record_fetch_plan(0xffff))
        self.assertEqual(got['entries'][0]['status'], 'opcode_outside_length_table')

    def test_record_fetch_wraps_into_runtime_ram_not_another_rom_bank(self):
        for encoded, selection in ((0xffff, 'current_mapping'), (0x7fff, 'secondary_write')):
            plan = record_fetch_plan(encoded)
            self.assertTrue(plan['wraps_cpu_address_space'])
            self.assertEqual(plan['segments'], [
                {'kind': 'prg_window', 'cpu_start': '0xffff', 'bank_offset': 0x7fff,
                 'length': 1, 'selection': selection},
                {'kind': 'cpu_internal_ram', 'cpu_start': '0x0000', 'ram_offset': 0,
                 'length': 9, 'values': 'runtime_dependent'}])
        self.assertEqual([s['length'] for s in record_fetch_plan(0xfffb)['segments']], [5, 5])
        self.assertEqual([s['length'] for s in record_fetch_plan(0xfff7)['segments']], [9, 1])
        self.assertFalse(record_fetch_plan(0xfff6)['wraps_cpu_address_space'])
        self.assertEqual(record_fetch_plan(0xfff6)['segments'][0]['length'], 10)
        for invalid in (-1, 0x10000, True):
            with self.subTest(encoded=invalid), self.assertRaises(ValueError):
                record_fetch_plan(invalid)

    def test_zero_length_and_command_crossing_are_reported(self):
        b0, b1 = banks()
        put_word(b0, 0, 0x20)
        put_word(b0, 6, 0x30)
        put_word(b1, 0x22, 0x40)
        put_word(b1, 0x32, 0x7fff)
        b1[0x40] = 0
        b1[-1] = 1
        got = inventory(bytes(b0), bytes(b1), 0, 2, bytes([0, 2]))
        self.assertEqual([x['status'] for x in got['entries']],
                         ['zero_length', 'crosses_bank_boundary'])

    def test_rejects_invalid_inputs(self):
        b0, b1 = banks()
        for args in ((b'', bytes(b1), 0, 1, b'\x01'),
                     (bytes(b0), bytes(b1), -1, 1, b'\x01'),
                     (bytes(b0), bytes(b1), 0, 0, b'\x01'),
                     (bytes(b0), bytes(b1), BANK_SIZE - 5, 1, b'\x01'),
                     (bytes(b0), bytes(b1), 0, 1, b'')):
            with self.subTest(args=(len(args[0]), args[2:])), self.assertRaises(ValueError):
                inventory(*args)
        for ptr in (-1, 0x10000, True):
            with self.subTest(ptr=ptr), self.assertRaises(ValueError):
                _locate(ptr)

    def test_wrong_target_fails_before_loading_rom(self):
        with patch.dict('os.environ', {'BADP_TARGET': 'us-v1.4'}), \
                patch('tools.script_entries.load_target') as loader:
            self.assertEqual(main(), 1)
            loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
