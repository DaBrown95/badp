import unittest

from tools.verify_script_overlap import expected_events, parse_output


class ScriptOverlapParserTests(unittest.TestCase):
    def setUp(self):
        # Synthetic events describe the parser protocol, not game data.
        self.events = [['FETCH 0 1234 01 5678', 'TARGET 0 1357'],
                       ['FETCH 1 4321 02 8765', 'WAIT 1 2468']]
        self.output = '\n'.join(self.events[0] + ['RESULT 0 target 0'] +
                                self.events[1] + ['RESULT 1 wait 1', 'DONE 2'])

    def test_accepts_complete_ordered_cases(self):
        self.assertEqual(parse_output(self.output, self.events),
                         {'cases': 2, 'interrupts': [0, 1], 'outcomes': ['target', 'wait']})

    def test_rejects_incomplete_or_changed_cases(self):
        cases = [self.output.replace('FETCH 0 1234 01 5678\n', ''),
                 self.output.replace('TARGET 0 1357', 'TARGET 0 1358'),
                 self.output.replace('RESULT 1 wait 1', 'RESULT 1 target 1'),
                 self.output.replace('DONE 2', 'DONE 1'),
                 self.output + '\nFETCH 1 4321 02 8765',
                 self.output.replace('RESULT 0 target 0', 'RESULT 0 target 4'),
                 self.output.replace('RESULT 0 target 0', 'RESULT 0 target x')]
        for output in cases:
            with self.subTest(output=output), self.assertRaises(ValueError):
                parse_output(output, self.events)

    def test_rejects_wrong_bank_lengths(self):
        with self.assertRaises(ValueError):
            expected_events(bytes(32), bytes(32))
        with self.assertRaises(ValueError):
            expected_events(bytes(0x8000), bytes(0x8000))


if __name__ == '__main__':
    unittest.main()
