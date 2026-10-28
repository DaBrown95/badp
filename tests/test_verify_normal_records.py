import unittest

from tools.verify_normal_records import expected_events, parse_output
from tools.verify_script_only_records import render_script


class NormalRecordVerificationTests(unittest.TestCase):
    def test_all_modes_select_fields_and_preserve_unselected_state(self):
        bank = bytearray(0x8000)
        bank[0x100:0x10a] = bytes([0x10, 0x81, 0x45, 0x23, 0x67, 0x89, 0xab, 0xcd, 0xef, 0x7e])
        bank[0x200:0x20a] = bytes([0x34, 0xff, 0x89, 0xff, 1, 2, 3, 4, 5, 6])
        expected = expected_events(bytes(bank), [0x100, 0x200])
        self.assertIn('RESULT 0 F184 67 89 AB CD EF 75 45 23 45 23 0', expected)
        self.assertIn('RESULT 1 F184 67 55 55 55 55 55 34 12 34 12 0', expected)
        self.assertIn('RESULT 2 F184 67 89 AB CD EF 75 34 12 34 12 0', expected)
        self.assertIn('RESULT 3 F296 55 55 55 55 55 55 34 12 34 12 0', expected)
        output = '\n'.join(expected)
        self.assertEqual(parse_output(output, expected, 2)['cases'], 6)
        for bad in (output.replace(' EF 75 ', ' EF 55 ', 1), output + '\nREAD 1 5 89',
                    output.replace(' F296 ', ' F184 ', 1), output.replace('08100', '00100', 1)):
            with self.subTest(bad=bad[-20:]), self.assertRaises(ValueError):
                parse_output(bad, expected, 2)

    def test_mode_template_remains_distinct_from_single_mode_probe(self):
        template = '{{RECORD_CASES}} {{SCRIPT_LOW_BASE}} {{SCRIPT_HIGH_BASE}}'
        self.assertEqual(render_script(template, [0x100], (0x5b0, 0x5c0), (0, 1, 2)),
                         '{{0x0100,0x00},{0x0100,0x01},{0x0100,0x02}} 0x05B0 0x05C0')
        for modes in ((), (1, 0), (3,), (True,), (0, 0)):
            with self.subTest(modes=modes), self.assertRaises(ValueError):
                render_script(template, [0x100], (0x5b0, 0x5c0), modes)


if __name__ == '__main__':
    unittest.main()
