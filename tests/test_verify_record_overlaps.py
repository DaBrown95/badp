"""Check the overlap trace verifier with invented bank contents."""
import unittest

from tools.script_entries import DESCRIPTORS
from tools.verify_record_overlaps import expected_events, parse_output

SYNTHETIC = {'descriptor_index': 3, 'expected_descriptor': 0x6100, 'command_a': 0x100,
             'command_b': 0x200, 'offsets': (0x28, 0x2c, 0x2d)}


def synthetic_banks():
    bank0, bank1 = bytearray(0x8000), bytearray(0x8000)
    bank0[DESCRIPTORS + 6 * 3:DESCRIPTORS + 6 * 3 + 2] = (0x6100).to_bytes(2, 'little')
    bank1[0x100:0x103] = bytes((0x63, 0x28, 0xff))
    bank1[0x200:0x202] = bytes((0, 0x2c))
    bank1[0x60d8:0x60e2] = bytes((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    bank1[0x612c:0x6137] = bytes((3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13))
    return bytes(bank0), bytes(bank1)


class RecordOverlapVerificationTests(unittest.TestCase):
    def test_complete_trace_and_changed_offset(self):
        expected = expected_events(*synthetic_banks(), **SYNTHETIC)
        self.assertEqual(parse_output('emulator startup\n' + '\n'.join(expected), expected)['cases'], 3)
        self.assertIn('FETCH 0 E0D8 0E0D8 01', expected)
        self.assertIn('FETCH 1 E12C 0E12C 03', expected)
        self.assertIn('FETCH 2 E12D 0E12D 04', expected)
        self.assertIn('RESULT 0 03 55 55 55 55 34 12 0', expected)
        self.assertIn('RESULT 1 07 08 09 0A 0B 05 06 0', expected)

    def test_rejects_missing_wrong_bank_value_or_interrupt(self):
        expected = expected_events(*synthetic_banks(), **SYNTHETIC)
        for changed in (expected[:-1], expected + ['DONE'], expected + ['TIMEOUT'],
                        [s.replace('FETCH 1 E12C 0E12C 03', 'FETCH 1 E12C 0612C 03') for s in expected],
                        [s.replace('MODE 0 FF 02 03', 'MODE 0 FF 02 02') for s in expected],
                        [s.replace('34 12 0', '34 12 1') for s in expected]):
            with self.subTest(first=changed[0], last=changed[-1]), self.assertRaises(ValueError):
                parse_output('\n'.join(changed), expected)

    def test_rejects_invalid_premise_and_skipped_fields(self):
        bank0, bank1 = synthetic_banks()
        bad = bytearray(bank0); bad[DESCRIPTORS + 6 * 3] ^= 1
        with self.assertRaises(ValueError): expected_events(bytes(bad), bank1, **SYNTHETIC)
        bad = bytearray(bank1); bad[0x100] ^= 1
        with self.assertRaises(ValueError): expected_events(bank0, bytes(bad), **SYNTHETIC)
        bad = bytearray(bank1); bad[0x60d9] = 0xff
        with self.assertRaises(ValueError): expected_events(bank0, bytes(bad), **SYNTHETIC)


if __name__ == '__main__':
    unittest.main()
