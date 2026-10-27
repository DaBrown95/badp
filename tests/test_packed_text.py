"""Packed-text decoding with invented character tables and records."""
import unittest
from unittest.mock import patch

from tools.packed_text import decode_record, decode_records, encode_record, main
from tools.script_entries import BANK_SIZE


PRIMARY = bytes(range(32, 64))
SECONDARY = bytes(range(64, 96))


def record(symbols, header=b'\x12\x34'):
    bits = ''.join(f'{s:05b}' for s in symbols)
    bits += '0' * (-len(bits) % 8)
    return header + bytes(int(bits[p:p + 8], 2) for p in range(0, len(bits), 8))


class PackedTextTests(unittest.TestCase):
    def test_escape_break_and_terminator(self):
        data = record([1, 0, 3, 11, 2, 26])
        decoded = decode_record(data, 0, len(data), PRIMARY, SECONDARY)
        self.assertEqual(decoded['header'], [0x12, 0x34])
        self.assertEqual(decoded['text'], chr(PRIMARY[1]) + chr(SECONDARY[3])
                         + '\n' + chr(PRIMARY[2]))
        self.assertEqual(decoded['symbols_consumed'], 6)
        self.assertEqual(decoded['line_breaks'], 1)
        self.assertEqual(decoded['padding_bits'], 2)
        self.assertEqual(encode_record(decoded), data)

    def test_nonzero_padding_round_trips_and_invalid_tokens_fail(self):
        data = bytearray(record([1, 26]))
        data[-1] |= 0x15
        decoded = decode_record(bytes(data), 0, len(data), PRIMARY, SECONDARY)
        self.assertEqual(decoded['padding_value'], 0x15)
        self.assertEqual(encode_record(decoded), bytes(data))
        decoded['tokens'][0]['index'] = 26
        with self.assertRaisesRegex(ValueError, 'control symbol'):
            encode_record(decoded)
        decoded['tokens'][0]['index'] = 1
        decoded['padding_value'] = 0x40
        with self.assertRaisesRegex(ValueError, 'padding'):
            encode_record(decoded)

    def test_rejects_unterminated_trailing_bytes_and_bad_tables(self):
        bad = record([1, 2])
        with self.assertRaisesRegex(ValueError, 'unterminated'):
            decode_record(bad, 0, len(bad), PRIMARY, SECONDARY)
        extra = record([26]) + b'\x00'
        with self.assertRaisesRegex(ValueError, 'unaccounted'):
            decode_record(extra, 0, len(extra), PRIMARY, SECONDARY)
        with self.assertRaisesRegex(ValueError, 'character tables'):
            decode_record(record([26]), 0, 3, b'', SECONDARY)

    def test_record_pointers_are_bounded_ordered_and_cpu_relative(self):
        first, second = record([1, 26]), record([2, 26])
        bank = bytearray(BANK_SIZE)
        start = 0x200
        end = start + len(first) + len(second)
        bank[0x100:0x104] = (0x8000 + start).to_bytes(2, 'little') + (
            0x8000 + start + len(first)).to_bytes(2, 'little')
        bank[start:end] = first + second
        records = decode_records(bytes(bank), 0x100, 2, end, PRIMARY, SECONDARY)
        self.assertEqual([r['cpu_address'] for r in records], ['0x8200', '0x8204'])
        self.assertEqual([r['text'] for r in records], [chr(PRIMARY[1]), chr(PRIMARY[2])])
        bank[0x102:0x104] = (0x8200).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'ordered'):
            decode_records(bytes(bank), 0x100, 2, end, PRIMARY, SECONDARY)
        bank[0x100:0x102] = (0x0001).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'ordered'):
            decode_records(bytes(bank), 0x100, 2, end, PRIMARY, SECONDARY)

    def test_wrong_target_is_rejected_before_loading_reference(self):
        with patch.dict('os.environ', {'BADP_TARGET': 'us-v1.4'}), \
                patch('tools.script_entries.load_target') as loader:
            self.assertEqual(main(), 1)
            loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
