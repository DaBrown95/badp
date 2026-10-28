"""Synthetic checks for the controlled indexed-jump inventory."""
import unittest

from tools.indexed_jump_inventory import field_value, indexed_address, inspect_entries, parse_probe


def observations(kind):
    lines = []
    for case in range(512):
        value, carry = case % 256, case // 256
        if kind == 'FIELD':
            lines.append(f'FIELD {value:02X} {carry} {field_value(value):02X} 00 05')
        else:
            lines.append(f'INDEX {value:02X} {carry} {indexed_address(value):04X}')
    return '\n'.join(lines + ['DONE 512 0'])


class IndexedJumpInventoryTests(unittest.TestCase):
    def test_selector_and_index_models_cover_the_full_byte_domain(self):
        self.assertEqual(set(map(field_value, range(256))), set(range(32)))
        self.assertEqual([field_value(x) for x in (0, 8, 0xf0, 0xf8)], [0, 16, 15, 31])
        self.assertEqual(indexed_address(0), indexed_address(128))
        self.assertEqual(indexed_address(255), indexed_address(127))
        self.assertEqual(indexed_address(0x66), 0x7501)
        self.assertEqual(indexed_address(1, 0xffff), 1)
        for invalid in (-1, 256, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                field_value(invalid)
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                indexed_address(invalid)

    def test_probe_parsers_reject_incomplete_reordered_and_wrong_observations(self):
        for kind in ('FIELD', 'INDEX'):
            with self.subTest(kind=kind):
                text = observations(kind)
                self.assertEqual(parse_probe(text, kind), {'cases': 512})
                lines = text.splitlines()
                failures = (lines[:-2] + lines[-1:], [lines[1], lines[0], *lines[2:]],
                            [*lines[:-1], 'DONE 512 1'], [*lines, 'DONE 512 0'])
                for bad in failures:
                    with self.assertRaises(ValueError):
                        parse_probe('\n'.join(bad), kind)
                bad = lines.copy()
                bad[0] = ('FIELD 00 0 01 00 05' if kind == 'FIELD' else 'INDEX 00 0 7436')
                with self.assertRaises(ValueError):
                    parse_probe('\n'.join(bad), kind)
        with self.assertRaises(ValueError):
            parse_probe('', 'UNKNOWN')

    def test_table_inspection_preserves_physical_and_encoded_locations(self):
        bank = bytearray(0x8000)
        bank[0x100:0x104] = bytes([0x34, 0x12, 0x78, 0x56])
        regions = [{'bank': 1, 'cpu': '0x8100', 'size': 2, 'kind': 'data'},
                   {'bank': 0, 'cpu': '0x8102', 'size': 2, 'kind': 'code'}]
        rows = inspect_entries(bytes(bank), regions, [(0x102, 2)], base=0x100)
        self.assertEqual(len(rows), 128)
        self.assertEqual(rows[0]['encoded_read'], '0x0100')
        self.assertEqual(rows[0]['cpu_read'], '0x8100')
        self.assertEqual(rows[0]['physical_prg_offset'], 0x8100)
        self.assertEqual(rows[0]['encoded_target'], '0x1234')
        self.assertEqual(rows[0]['source_kinds'], ['data'])
        self.assertTrue(rows[0]['within_three_source_entries'])
        self.assertEqual(rows[1]['candidate_map_layout_bytes'], 2)
        self.assertEqual(rows[1]['source_kinds'], ['local'])
        self.assertTrue(rows[31]['preceded_by_selector_candidate'])
        self.assertFalse(rows[32]['preceded_by_selector_candidate'])
        with self.assertRaises(ValueError):
            inspect_entries(bytes(bank), [], [], base=0x7fff)
        with self.assertRaises(ValueError):
            inspect_entries(bytes(4), [], [])


if __name__ == '__main__':
    unittest.main()
