"""Check the orphan-loop probe using an invented movement/sound payload."""
import unittest

from tools.verify_orphan_loop import expected_events, parse_output


def synthetic_bank():
    bank = bytearray(0x8000)
    # VM forms and internal addresses match the probe's stated premises;
    # movement bytes and the sound pointer are invented, not game payloads.
    body = (bytes([0x2d, 0, 0x81, 7, 1, 0x2d, 0, 0x42, 7, 1, 0x49])
            + (0x1234).to_bytes(2, 'little') + bytes([0x1b])
            + (0x7c9c).to_bytes(2, 'little') + bytes([0, 4])
            + (0x7c88).to_bytes(2, 'little') + bytes([4]) + (0x7c9c).to_bytes(2, 'little'))
    bank[0x7c88:0x7c9f] = body
    for op, length in ((0x2d, 3), (7, 2), (0x49, 3), (0x1b, 4), (4, 3)):
        bank[0x7da7 + op] = length
    return bytes(bank)


class OrphanLoopTests(unittest.TestCase):
    def test_two_branch_outcomes_and_fields(self):
        events = expected_events(synthetic_bank())
        self.assertIn('STEP 0 8 05568 7C9C 7C9C 00 42 01 20 C0 1234 10', events)
        self.assertIn('STEP 1 8 05568 7C8B 7C8B 00 81 01 20 C0 1234 00', events)
        result = parse_output('emulator startup\n' + '\n'.join(events), events)
        self.assertEqual(result['branch_outcomes'], ['terminal_loop', 'repeat_loop'])

    def test_reads_include_opcode_prefetch_and_copy(self):
        events = expected_events(synthetic_bank())
        self.assertEqual(sum(line.startswith('READ 0 ') for line in events), 31)
        self.assertEqual(events[:2], ['READ 0 1 FC88 0FC88 2D'] * 2)
        self.assertEqual(sum(line.startswith('STEP ') for line in events), 16)

    def test_missing_extra_or_changed_observation_fails(self):
        events = expected_events(synthetic_bank())
        output = '\n'.join(events)
        for bad in ('\n'.join(events[1:]), output + '\nDONE 2', output + '\nTIMEOUT',
                    output.replace('0FC88', '07C88', 1), output.replace(' C0 1234 ', ' 00 1234 ', 1),
                    output.replace('STEP 0 6 05568 7C9C', 'STEP 0 6 05568 7C99', 1),
                    output.replace('RESULT 1 0', 'RESULT 1 1')):
            with self.subTest(tail=bad[-20:]), self.assertRaises(ValueError):
                parse_output(bad, events)

    def test_unexpected_command_pointer_or_length_fails(self):
        bank = synthetic_bank()
        for address, value in ((0x7c88, 0), (0x7c89, 1), (0x7c94, 0), (0x7c96, 0),
                               (0x7da7 + 0x2d, 2)):
            changed = bytearray(bank);changed[address] = value
            with self.subTest(address=address), self.assertRaises(ValueError):
                expected_events(bytes(changed))
        with self.assertRaises(ValueError):
            expected_events(bank[:-1])


if __name__ == '__main__':
    unittest.main()
