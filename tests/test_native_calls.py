"""Conditional native-call checks with synthetic banks and observation streams."""
import unittest

from tools.native_script_calls import call_contract
from tools.verify_native_calls import cases, expected_events, parse_output


def banks():
    data = bytearray(0x8000)
    data[0x7fb7:0x7fb9] = bytes((0x0c, 0x0d))
    return bytes(data), bytes(data)


class NativeCallTests(unittest.TestCase):
    def test_all_operands_have_paired_targets_but_distinct_selection_rules(self):
        targets = set()
        for low in range(0x8000):
            first, second = call_contract(low), call_contract(low + 0x8000)
            expected = 0 if low == 0x7fff else 0x8001 + low
            self.assertEqual(first['target_cpu'], f'0x{expected:04x}')
            self.assertEqual(first['target_cpu'], second['target_cpu'])
            self.assertEqual(first['target_bank_rule'], 'secondary_mapper_write')
            self.assertEqual(second['target_bank_rule'], 'current_mapping')
            self.assertEqual(first['normal_return_bank_rule'], 'default_mapper_write')
            self.assertTrue(second['requires_normal_helper_return'])
            targets.add(expected)
        self.assertEqual(len(targets), 0x8000)
        self.assertNotIn(0x8000, targets)

    def test_invalid_operands_are_rejected(self):
        for value in (-1, 0x10000, True, 1.0, '0xffff', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                call_contract(value)

    def test_probe_covers_both_entries_and_opposite_restore_mappings(self):
        rows = cases()
        self.assertEqual(len(rows), 192)
        self.assertEqual(len(set(rows)), 192)
        self.assertEqual(sum(row[3] < 0x8000 for row in rows), 96)
        self.assertEqual(sum(row[3] & 0x7fff == 0x7fff for row in rows), 64)
        events = expected_events(*banks())
        observations = parse_output('\n'.join(events), events)
        self.assertEqual(observations['cases'], 192)
        self.assertEqual(len([e for e in events if e.startswith('WRITE ')]), 480)
        self.assertEqual(len([e for e in events if e.startswith('CONTINUE ')]), 192)
        # Case zero enters bank 0 but the matrix also restores bank 1 after
        # entering bank 0; restore is independent of the original entry bank.
        opposite = next(i for i, row in enumerate(rows) if row[0] == 0 and row[1] == 1)
        self.assertTrue(any(e.startswith(f'RETURN {opposite} 0FD88') for e in events))

    def test_missing_reordered_and_changed_mapping_or_stack_observations_fail(self):
        expected = expected_events(*banks())
        variants = [expected[:-1], expected[1:], [expected[1], expected[0], *expected[2:]]]
        for prefix, old, new in (('ENTRY ', '07D88', '0FD88'),
                                 ('TARGET ', 'DE 98 FD', 'E0 98 FD'),
                                 ('RETURN ', '1234 0', '1234 1')):
            altered = expected.copy()
            index = next(i for i, event in enumerate(altered) if event.startswith(prefix))
            altered[index] = altered[index].replace(old, new)
            self.assertNotEqual(altered, expected)
            variants.append(altered)
        for variant in variants:
            with self.subTest(variant=variant[:2]), self.assertRaises(ValueError):
                parse_output('\n'.join(variant), expected)
        for failure in ('TIMEOUT', 'LOAD_FAILED'):
            with self.assertRaises(ValueError):
                parse_output('\n'.join(expected + [failure]), expected)

    def test_rom_geometry_and_bank_table_changes_are_rejected(self):
        first, second = banks()
        with self.assertRaises(ValueError):
            expected_events(first[:-1], second)
        altered = bytearray(second);altered[0x7fb8] ^= 1
        with self.assertRaises(ValueError):
            expected_events(first, bytes(altered))


if __name__ == '__main__':
    unittest.main()
