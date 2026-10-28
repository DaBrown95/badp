"""Candidate PPU-stream tests use synthetic commands and banks only."""
import unittest

from tools.ppu_streams import decode_stream, inventory, literal_seeds
from tools.script_entries import BANK_SIZE


class PpuStreamTests(unittest.TestCase):
    def test_zero_operands_do_not_terminate_address_commands(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x109] = bytes([0x41, 0xfe, 0, 0x20, 0x42, 0xff, 0x20, 0x21, 0])
        result = decode_stream(bytes(bank0), bytes(bank1), 0x100)
        self.assertEqual((result['size'], result['characters']), (9, 2))
        self.assertEqual((result['relative_addresses'], result['absolute_addresses']), (1, 1))
        self.assertEqual(result['location']['physical_prg_offset'], BANK_SIZE + 0x100)
        self.assertFalse(result['lookahead_crossing_possible'])

    def test_truncation_limit_and_possible_lookahead_crossing(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x104] = bytes([0x41, 0x42, 0x43, 0])
        with self.assertRaisesRegex(ValueError, 'unterminated'):
            decode_stream(bytes(bank0), bytes(bank1), 0x100, limit=2)
        bank1[-1] = 0xff
        with self.assertRaisesRegex(ValueError, 'truncated'):
            decode_stream(bytes(bank0), bytes(bank1), 0x7fff)
        bank1[-2] = 0
        self.assertTrue(decode_stream(bytes(bank0), bytes(bank1), 0x7ffe)['lookahead_crossing_possible'])

    def test_aliases_and_overlapping_starts_count_physical_bytes_once(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x103] = bytes([0x41, 0x42, 0])
        result = inventory(bytes(bank0), bytes(bank1), [0x100, 0x100, 0x101])
        self.assertEqual(len(result['streams']), 2)
        self.assertEqual(result['physical_bytes'], 3)
        self.assertEqual(result['overlapping_stream_bytes'], 2)

    def test_candidate_seeds_require_complete_literal_remap(self):
        bank1 = bytearray(BANK_SIZE)
        for table in (0x505f, 0x509d):
            for i in range(4):
                bank1[table + i * 2:table + i * 2 + 2] = (0x100 + i).to_bytes(2, 'little')
        source = '\n    BogusQueueStateAB $0200\n    BogusQueueStateAB $0000\nScriptD00D:\n'
        source += ''.join(f'    BogusRemapCase ${0x8000+i:04X}, ${0x300+i:04X}\n' for i in range(8))
        source += '    BogusRemapEnd\n'
        seeds = literal_seeds(source, bytes(bank1))
        self.assertEqual(seeds, [0x100, 0x101, 0x102, 0x103, 0x200, *range(0x300, 0x308)])
        with self.assertRaisesRegex(ValueError, 'eight inventory'):
            literal_seeds(source.replace('BogusRemapCase $8007', 'NotARemap $8007'), bytes(bank1))
        with self.assertRaisesRegex(ValueError, 'unsupported direct'):
            literal_seeds(source.replace('$0200', 'SomeLabel', 1), bytes(bank1))
        with self.assertRaisesRegex(ValueError, 'remap boundaries'):
            literal_seeds(source.replace('BogusRemapEnd', 'MissingEnd'), bytes(bank1))


if __name__ == '__main__':
    unittest.main()
