"""Exercise the indexed-audio verifier with synthetic banks and traces."""
import unittest

from tools.verify_indexed_audio import expected_events, fragment_events, parse_output


def synthetic_banks():
    bank0 = bytearray(0x8000)
    bank1 = bytearray(0x8000)
    bank0[0x3104:0x3108] = bytes((0x21, 0x81, 0x14, 0x28))
    # Invented register values; only the audio command grammar is significant.
    bank1[0x2814:0x2821] = bytes((0xe1, 0xf9, 1, 0x9c, 0xee, 4, 0xfb, 8, 0xe8, 0xe2, 0xf9, 5, 6))
    bank1[0x4d9a:0x4d9c] = bytes((0x17, 0x28))
    bank0[0x49bc:0x49be] = bytes((0x18, 0x28))
    bank0[0x49c0:0x49c2] = bytes((0x18, 0x28))
    bank0[0x126f] = 0x80
    bank1[0x541a:0x541e] = bytes((0x11, 0x81, 0x54, 0x2c))
    bank1[0x2c54:0x2c5c] = bytes((0xa1, 0xe2, 0xa1, 0xe8, 0xe3, 0xa0, 4, 5))
    bank1[0x26f6:0x26f9] = bytes((0xfb, 6, 0xe8))
    bank1[0x2757:0x2760] = bytes((0xe0, 0xf9, 7, 8, 9, 10, 0xfb, 7, 0xe8))
    bank1[0x28a4:0x28ad] = bytes((0xe3, 0xf9, 11, 12, 13, 14, 0xfb, 9, 0xe8))
    bank1[0x2c53] = 0xe1
    return bytes(bank0), bytes(bank1)


class IndexedAudioTests(unittest.TestCase):
    def test_complete_trace_and_wrap_alias(self):
        events = expected_events(*synthetic_banks())
        result = parse_output('emulator startup\n' + '\n'.join(events), events)
        self.assertEqual(result['alias_cases'], 4)
        self.assertEqual(result['changed_index_controls'], 2)
        self.assertIn('PAIR 0 B106 03106 14', events)
        self.assertIn('PAIR 1 B106 03106 14', events)
        self.assertIn('PAIR 2 B104 03104 21', events)
        self.assertIn('PAIR 3 D41C 0D41C 54', events)
        self.assertIn('PAIR 4 D41C 0D41C 54', events)
        self.assertIn('PAIR 5 D41A 0D41A 11', events)

    def test_trace_fails_closed_on_missing_mapping_changed_read_or_interrupt(self):
        events = expected_events(*synthetic_banks())
        for changed in (events[:-1], events + ['DONE 9'],
                        [x.replace('PAIR 0 B106 03106', 'PAIR 0 B106 0B106') for x in events],
                        [x.replace('RESULT 1 0', 'RESULT 1 1') for x in events],
                        [x.replace('AUDIO 0 A814 0A814 E1', 'AUDIO 0 A814 0A814 E0') for x in events],
                        events + ['TIMEOUT']):
            with self.subTest(first=changed[0], last=changed[-1]), self.assertRaises(ValueError):
                parse_output('\n'.join(changed), events)

    def test_isolated_fragments_include_every_fetch_and_terminal_outcome(self):
        _, bank = synthetic_banks()
        events = fragment_events(bank)
        self.assertEqual(sum(x.startswith('AUDIO ') for x in events), 75)
        self.assertEqual(sum(x.startswith('AFTER ') for x in events), 15)
        self.assertIn('AFTER 9 5 C0 06 F8 26', events)
        self.assertIn('AFTER 12 25 00 01 58 2C', events)
        full = expected_events(*synthetic_banks())
        for changed in ([x for x in full if not x.startswith('AUDIO 10 A75B ')],
                        [x.replace('AUDIO 11 A8A4 0A8A4', 'AUDIO 11 A8A4 028A4') for x in full],
                        [x.replace('AFTER 12 25 00', 'AFTER 12 25 88') for x in full]):
            with self.assertRaises(ValueError):
                parse_output('\n'.join(changed), full)

    def test_isolated_fragments_reject_wrong_command_or_channel(self):
        _, bank = synthetic_banks()
        for position, value in ((0x26f6, 0xe8), (0x2757, 0xe1), (0x28ac, 0xe3), (0x2c53, 0xe0)):
            bad = bytearray(bank);bad[position] = value
            with self.subTest(position=position), self.assertRaises(ValueError):
                fragment_events(bytes(bad))

    def test_wrong_pointer_or_command_structure_is_rejected(self):
        b0, b1 = synthetic_banks()
        bad = bytearray(b0); bad[0x3106] ^= 1
        with self.assertRaises(ValueError):
            expected_events(bytes(bad), b1)
        bad = bytearray(b0); bad[0x3105] = 0
        with self.assertRaises(ValueError):
            expected_events(bytes(bad), b1)
        bad = bytearray(b1); bad[0x2815] = 0xe8
        with self.assertRaises(ValueError):
            expected_events(b0, bytes(bad))
        with self.assertRaises(ValueError):
            expected_events(b0[:-1], b1)


if __name__ == '__main__':
    unittest.main()
