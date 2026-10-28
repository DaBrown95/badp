import unittest
from tools.trace_audio import parse_output


class TraceAudioTests(unittest.TestCase):
    def test_complete_trace(self):
        result = parse_output('unrelated emulator message\nAUDIO_DONE 16000 0 2 2 0 0\n'
                              'AUDIO_READ 1234:0102030405 2\n')
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['reads'], {'1234:0102030405': 2})
        self.assertEqual(parse_output('AUDIO_DONE 4300 0 1 1 0 0\nAUDIO_READ 1234:0102030405 1\n',
                                      frames=4300)['count'], 1)
        with self.assertRaises(ValueError):
            parse_output('AUDIO_DONE 4300 0 1 1 0 0\nAUDIO_READ 1234:0102030405 1\n')
        for frames in (0, -1, True):
            with self.subTest(frames=frames), self.assertRaises(ValueError):
                parse_output('', frames=frames)

    def test_rejects_incomplete_or_duplicate_trace(self):
        bad = ('AUDIO_DONE 16000 1 1 1 0 0\nAUDIO_READ 1234:0102030405 1',
               'AUDIO_DONE 12000 0 1 1 0 0\nAUDIO_READ 1234:0102030405 1',
               'AUDIO_DONE 16000 0 0 0 0 0',
               'AUDIO_READ 1234:0102030405 1',
               'AUDIO_DONE 16000 0 2 1 0 0\nAUDIO_READ 1234:0102030405 1',
               'AUDIO_DONE 16000 0 1 1 1 0\nAUDIO_READ 1234:0102030405 1',
               'AUDIO_DONE 16000 0 2 2 0 0\nAUDIO_READ x 1\nAUDIO_READ x 1',
               'AUDIO_DONE 16000 0 0 0 0 0\nAUDIO_READ x 0')
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_output(value)


if __name__ == '__main__':
    unittest.main()
