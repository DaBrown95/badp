import unittest
from tools.audio_commands import decode_command, inventory_observed


class AudioCommandTests(unittest.TestCase):
    def test_notes_and_instrument(self):
        self.assertEqual(decode_command(bytes([0x9F]))['duration_index'], 4)
        self.assertEqual(decode_command(bytes([0x9F]))['note_index'], 31)
        self.assertEqual(decode_command(bytes([0xB2]))['instrument'], 18)

    def test_loop_is_exact_opcode_and_little_endian(self):
        self.assertEqual(decode_command(bytes([0xC0, 3, 0x34, 0x12])),
                         {'kind': 'loop', 'opcode': 0xC0, 'size': 4,
                          'count': 3, 'target': 0x1234})
        self.assertEqual(decode_command(bytes([0xE0]))['kind'], 'select_channel')

    def test_mask_commands_take_precedence_over_channel_selection(self):
        self.assertEqual(decode_command(bytes([0xC2]))['kind'], 'set_channel_mask')
        self.assertEqual(decode_command(bytes([0xC3]))['kind'], 'clear_channel_mask')
        self.assertEqual(decode_command(bytes([0xE2]))['channel'], 2)

    def test_write_five_consumes_only_four_source_values(self):
        self.assertEqual(decode_command(bytes([0xD9, 1, 2, 3, 4, 5])),
                         {'kind': 'write_five', 'opcode': 0xD9, 'size': 5,
                          'source_values': [1, 2, 3, 4]})

    def test_other_parameter_lengths_and_truncation(self):
        self.assertEqual(decode_command(bytes([0xCF, 0x12]))['register'], 3)
        self.assertEqual(decode_command(bytes([0xDB, 0x23]))['duration'], 0x23)
        for data in (b'', bytes([0xC0, 1, 2]), bytes([0xCC]),
                     bytes([0xD9, 1, 2, 3]), bytes([0xDB])):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_command(data)

    def test_remaining_dispatch_cases(self):
        for op, kind in ((0xC4, 'restore_pointer'), (0xC8, 'stop_voice'),
                         (0xD0, 'restart_channel'), (0xD4, 'enable_channel'),
                         (0xD8, 'select_all_channels'), (0xDA, 'default_control'),
                         (0xDC, 'default_control')):
            with self.subTest(op=op):
                self.assertEqual(decode_command(bytes([op]))['kind'], kind)

    def test_restore_command_retains_all_low_bit_encodings(self):
        for opcode in range(0xE4, 0xE8):
            with self.subTest(opcode=opcode):
                self.assertEqual(decode_command(bytes([opcode])),
                                 {'kind': 'restore_pointer', 'opcode': opcode, 'size': 1})


class AudioInventoryTests(unittest.TestCase):
    def setUp(self):
        self.bank0 = bytearray(0x8000)
        self.bank1 = bytes(0x8000)
        self.bank0[8:13] = bytes([0xC0, 2, 0x12, 0x34, 0xE8])

    def test_validates_and_deduplicates_observations(self):
        trace = {'results': {
            'first': {'reads': {'0008:C0021234E8': 2}},
            'second': {'reads': {'0008:C0021234E8': 1}}}}
        result = inventory_observed(trace, bytes(self.bank0), self.bank1)
        self.assertEqual(result['command_bytes'], 4)
        self.assertEqual(result['commands'][0]['scenarios'], {'first': 2, 'second': 1})
        self.assertEqual(result['conflicts'], [])

    def test_conflicting_entry_is_reported(self):
        trace = {'results': {'first': {'reads': {
            '0008:C0021234E8': 1, '0009:021234E800': 1}}}}
        result = inventory_observed(trace, bytes(self.bank0), self.bank1)
        self.assertEqual(result['conflicts'][0]['physical_prg_offset'], 9)

    def test_rejects_wrong_bytes_crossings_and_counts(self):
        for key, count in (('0008:C002123400', 1), ('7FFF:0000000000', 1),
                           ('0008:C0021234E8', 0), ('0008:ZZZZZZZZZZ', 1)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                inventory_observed({'results': {'x': {'reads': {key: count}}}},
                                   bytes(self.bank0), self.bank1)


if __name__ == '__main__':
    unittest.main()
