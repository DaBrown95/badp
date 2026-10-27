"""Slot-record access analysis uses synthetic banks only."""
import unittest

from tools.script_entries import BANK_SIZE
from tools.slot_record_flow import resolve_access, trace


def fixture():
    return bytearray(BANK_SIZE), bytearray(BANK_SIZE), bytearray([1] * 197)


class SlotRecordFlowTests(unittest.TestCase):
    def test_add_subtract_and_compact_flag(self):
        b0, b1, _ = fixture()
        b1[0x120:0x12a] = bytes([0x34, 0x81, 0x78, 0x56, 0x40, 1, 2, 3, 4, 5])
        b1[0x100:0x10a] = bytes([0x22, 0x82, 0x33, 0, 0, 0, 0, 0, 0, 0])
        plus = resolve_access(bytes(b0), bytes(b1), 0x110, 0x10, 0)
        minus = resolve_access(bytes(b0), bytes(b1), 0x110, 0x10, 0xff)
        self.assertEqual(plus['encoded_pointer'], '0x0120')
        self.assertEqual(plus['location']['bank'], 1)
        self.assertEqual(plus['fields']['encoded_script_pointer'], 0x5678)
        self.assertEqual(minus['encoded_pointer'], '0x0100')
        self.assertEqual(minus['fields']['sprite_pointer'], 0x8222)
        self.assertEqual(minus['negative_mode_flags'], 0x33)
        self.assertIsNone(plus['negative_mode_flags'])

    def test_crossing_fetch_and_invalid_parameters(self):
        b0, b1, _ = fixture()
        result = resolve_access(bytes(b0), bytes(b1), 0x7fff, 0, 0)
        self.assertEqual(result['status'], 'fetch_crosses_bank_boundary')
        self.assertNotIn('fields', result)
        for offset, mode in ((256, 0), (0, -1), (True, 0), (0, True)):
            with self.subTest(offset=offset, mode=mode), self.assertRaises(ValueError):
                resolve_access(bytes(b0), bytes(b1), 0x100, offset, mode)

    def test_zero_mode_installs_script_and_negative_mode_uses_same_base(self):
        b0, b1, lengths = fixture()
        lengths[0x00], lengths[0x63] = 2, 3
        b1[0x20:0x22] = bytes([0x00, 9])
        b1[0x30:0x34] = bytes([0x63, 3, 0xff, 0x11])
        b1[0x109:0x113] = bytes([0x34, 0x81, 0x30, 0, 0x40, 1, 2, 3, 4, 0x11])
        b1[0xfd:0x107] = bytes([0x22, 0x82, 0x33, 0, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(len(result['contexts']), 2)
        refs = {r['command']: r for r in result['references']}
        self.assertEqual(refs['0x0020']['encoded_pointer'], '0x0109')
        self.assertEqual(refs['0x0030']['encoded_pointer'], '0x00fd')
        self.assertEqual(refs['0x0030']['negative_mode_flags'], 0x33)
        self.assertFalse(result['unprocessed_contexts'])
        limited = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)], limit=1)
        self.assertEqual(limited['unprocessed_contexts'], [{'base': '0x0100', 'entry': '0x0030'}])

    def test_script_sentinel_does_not_schedule_another_context(self):
        b0, b1, lengths = fixture()
        lengths[0x00] = 2
        b1[0x20:0x22] = bytes([0, 0])
        b1[0x100:0x10a] = bytes([0, 0x81, 0x30, 0xff, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(len(result['contexts']), 1)
        self.assertFalse(result['references'][0]['fields']['script_installable_in_zero_mode'])
        with self.assertRaises(ValueError):
            trace(bytes(b0), bytes(b1), bytes(lengths), [], limit=0)


if __name__ == '__main__':
    unittest.main()
