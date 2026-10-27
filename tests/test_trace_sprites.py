import unittest
from tools.trace_sprites import parse_output


class TraceSpriteTests(unittest.TestCase):
    def test_valid_trace(self):
        result = parse_output('SPRITE_DONE 16000\nSPRITE_TOTAL frame 3 1\n'
                              'SPRITE_TOTAL header 1 0\nSPRITE_READ frame 1234:1122 2\n'
                              'SPRITE_READ header 5678:3344 1\n')
        self.assertEqual(result['totals']['frame'], [3, 1])
        self.assertEqual(result['reads']['frame'], {'1234:1122': 2})

    def test_incomplete_duplicate_or_inconsistent_trace_is_rejected(self):
        cases = ('SPRITE_TOTAL frame 0 0\nSPRITE_TOTAL header 0 0',
                 'SPRITE_DONE 16000\nSPRITE_TOTAL frame 0 0\nSPRITE_TOTAL header 0 0',
                 'SPRITE_DONE 12000\nSPRITE_TOTAL frame 0 0\nSPRITE_TOTAL header 0 0',
                 'SPRITE_DONE 16000\nSPRITE_TOTAL frame 1 0\nSPRITE_TOTAL header 0 0',
                 'SPRITE_DONE 16000\nSPRITE_TOTAL frame 0 1\nSPRITE_TOTAL header 0 0',
                 'SPRITE_DONE 16000\nSPRITE_TOTAL frame 2 0\nSPRITE_TOTAL header 0 0\n'
                 'SPRITE_READ frame x 1\nSPRITE_READ frame x 1')
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                parse_output(case)


if __name__ == '__main__':
    unittest.main()
