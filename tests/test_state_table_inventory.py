"""Test the state-table model and trace parser using invented bytes only."""
import unittest

from tools.state_table_inventory import SELECTORS, af_result, cpu_region, inventory, parse_probe, read_plan


def synthetic_bank():
    return bytes((i * 37 + 11) & 255 for i in range(0x8000))


def synthetic_output(bank):
    lines = []
    for case in range(len(SELECTORS) * 256):
        state = case % 256
        selector = SELECTORS[case // 256]
        result = af_result(bank, state, selector)
        reads = 0 if selector == 0x0f else 1 if selector == 0xaa else 123 if selector == 0x4d else 12345
        lines.append(f'STATE {case} {state:02X} {selector:02X} {result & 255:02X} {result >> 8:02X} 6915 0 {reads} 0')
    lines.append(f'DONE {len(SELECTORS) * 256}')
    return '\n'.join(lines)


class StateTableInventoryTests(unittest.TestCase):
    def test_af_wraps_pointer_index_but_not_byte_table_index(self):
        bank = synthetic_bank()
        self.assertEqual(af_result(bank, 0x00, 0x4d), af_result(bank, 0x80, 0x4d))
        self.assertNotEqual(af_result(bank, 0x00, 0xaa), af_result(bank, 0x80, 0xaa))
        self.assertEqual(af_result(bank, 0xff, 0x0f), 0xff)
        for state, selector in ((256, 0x4d), (True, 0x4d), (0, 256)):
            with self.subTest(state=state, selector=selector), self.assertRaises(ValueError):
                af_result(bank, state, selector)

    def test_probe_requires_all_cases_results_mapping_and_no_interrupt(self):
        bank = synthetic_bank(); output = synthetic_output(bank)
        self.assertEqual(parse_probe(output, bank)['cases'], 65536)
        first = output.splitlines()[0]
        bad_result = first.split()
        bad_result[4] = f'{(int(bad_result[4], 16) ^ 1):02X}'
        mutations = [output.replace(first, first.replace(' 6915 0 ', ' 6916 0 '), 1),
                     output.replace(first, first.replace(' 6915 0 ', ' 6915 1 '), 1),
                     output.replace(first, ' '.join(bad_result), 1),
                     output.replace(first, first.rsplit(' ', 2)[0] + ' 1 0', 1),
                     output.replace(first, first.rsplit(' ', 1)[0] + ' 1', 1),
                     output.replace('DONE 65536', 'DONE 65535'), output.split('\n', 1)[1],
                     output + '\nSTATE 0 00 00 00 00 6915 0 12345 0']
        for value in mutations:
            with self.subTest(value=value[:100]), self.assertRaises(ValueError):
                parse_probe(value, bank)

    def test_palette_reads_wrap_and_preserve_io_regions(self):
        plan = read_plan(0xffff, sprite=False)
        self.assertEqual([x['cpu'] for x in plan['header']], ['0xffff', '0x0000', '0x0001'])
        self.assertEqual(plan['initial_payload'][0]['cpu'], '0x0002')
        self.assertEqual([x['region'] for x in plan['header']], ['program_rom', 'internal_ram', 'internal_ram'])
        sprite = read_plan(0xfffc, sprite=True)
        self.assertEqual(sprite['initial_payload'][0]['cpu'], '0x0000')
        self.assertEqual(len(sprite['initial_payload']), 15)
        self.assertEqual(cpu_region(0x2003), 'ppu_register')
        self.assertEqual(cpu_region(0x4016), 'apu_or_controller')
        self.assertEqual(cpu_region(0x6000), 'cartridge_low')
        with self.assertRaises(ValueError):
            read_plan(-1, sprite=False)

    def test_inventory_keeps_state_and_pointer_index_bounds_separate(self):
        bank = synthetic_bank()
        result = inventory(bank, [{'bank': 0, 'cpu': '0x8000', 'size': 0x8000, 'kind': 'data'}])
        rows = result['states']
        self.assertEqual(len(rows), 256)
        self.assertTrue(rows[0]['pointer_index_in_nominal_table'])
        self.assertFalse(rows[22]['pointer_index_in_nominal_table'])
        self.assertFalse(rows[128]['byte_index_in_nominal_table'])
        self.assertTrue(rows[128]['pointer_index_in_nominal_table'])
        for summary in result['summary'].values():
            self.assertEqual(sum(summary.values()), 212)
        with self.assertRaises(ValueError):
            inventory(bank, [{'bank': 0, 'cpu': '0x7fff', 'size': 2, 'kind': 'data'}])


if __name__ == '__main__':
    unittest.main()
