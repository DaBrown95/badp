import unittest

from tools.verify_script_only_records import expected_events, parse_output, render_script, symbol_bases


class ScriptOnlyVerificationTests(unittest.TestCase):
    def test_fetch_order_sentinel_reads_and_skipped_fields(self):
        bank = bytearray(0x8000)
        bank[0x100:0x10a] = bytes([0x12, 0xff, 0x45, 0x23, 1, 2, 3, 4, 5, 6])
        bank[0x200:0x20a] = bytes([0x34, 0xff, 0x89, 0xff, 7, 8, 9, 10, 11, 12])
        expected = expected_events(bytes(bank), [0x100, 0x200])
        self.assertIn('READ 0 2 45', expected)
        self.assertNotIn('READ 1 2 89', expected)
        self.assertEqual(sum(line.endswith(' A5') for line in expected), 20)
        output = '\n'.join(expected)
        self.assertTrue(parse_output(output, expected, 2)['unselected_fields_preserved'])
        for changed in (output.replace('08100', '00100'), output + '\nREAD 1 0 34',
                        output.replace('55 55', '54 55', 1), output.replace('READ 0 0 A5', 'READ 0 0 00'),
                        output + '\nTIMEOUT'):
            with self.subTest(changed=changed[-20:]), self.assertRaises(ValueError):
                parse_output(changed, expected, 2)

    def test_rejects_invalid_pointers_template_and_non_sentinel(self):
        template = 'local cases={{RECORD_CASES}};local low={{SCRIPT_LOW_BASE}};local high={{SCRIPT_HIGH_BASE}}'
        bases = (0x5b0, 0x5c0)
        for addresses in ([], [True], [0x7ff7], [0x200, 0x100], [0x100, 0x100]):
            with self.subTest(addresses=addresses), self.assertRaises(ValueError):
                render_script(template, addresses, bases)
        self.assertEqual(render_script(template, [0x100], bases),
                         'local cases={0x0100};local low=0x05B0;local high=0x05C0')
        self.assertEqual(symbol_bases('SlotScriptPointerLow = $05B0\nSlotScriptPointerHigh = $05C0\n'), bases)
        with self.assertRaises(ValueError): symbol_bases('SlotScriptPointerLow = $05B0\n')
        with self.assertRaises(ValueError): render_script('missing', [0x100], bases)
        with self.assertRaises(ValueError): expected_events(bytes(0x8000), [0x100])


if __name__ == '__main__':
    unittest.main()
