"""Controlled record-boundary evidence checks using synthetic PRG data."""
import unittest

from tools.script_entries import BANK_SIZE, DESCRIPTORS
from tools.verify_record_boundary import BASES, DESCRIPTOR_INDICES, parse_descriptor_output, parse_output


def synthetic_output():
    bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
    bank0[-5:] = bytes([0x11, 0x22, 0x33, 0x44, 0x55])
    bank1[-5:] = bytes([0x66, 0x77, 0x88, 0x99, 0xaa])
    lines = []
    for case, base in enumerate(BASES):
        for index in range(10):
            address = ((base | 0x8000) + index) & 0xffff
            if address >= 0x8000:
                bank = 1 if case == 2 else 0
                kind, physical = 'prg', bank * BANK_SIZE + address - 0x8000
                value = (bank0, bank1)[bank][address - 0x8000]
            else:
                kind, physical = 'ram', address
                value = 0x30 + address + (0x40 if case == 1 and address == 4 else 0)
            lines.append(f'COPY {case} {index} {address:04X} {kind} {physical:05X} {value:02X}')
        y = 0 if case == 2 else 10
        lines.append(f'CASE {case} 10 0 00 {y:02X} {base >> 8:02X} 0')
    lines.append('DONE 4 0')
    return '\n'.join(lines), bytes(bank0), bytes(bank1)


class RecordBoundaryEvidenceTests(unittest.TestCase):
    def test_accepts_both_cpu_wrap_and_changed_ram_control(self):
        output, bank0, bank1 = synthetic_output()
        result = parse_output(output, bank0, bank1)
        self.assertEqual((result['cases'], result['copied_bytes'], result['ram_control_changed_indices']),
                         (4, 40, [5]))
        self.assertEqual([s['kind'] for s in result['fetch_plans'][0]['segments']],
                         ['prg_window', 'cpu_internal_ram'])

    def test_rejects_wrong_mapping_wrong_value_missing_read_and_interrupt(self):
        output, bank0, bank1 = synthetic_output()
        invalid = (
            output.replace('COPY 0 1 0000 ram 00000 30\n', ''),
            output.replace('COPY 0 1 0000 ram 00000 30', 'COPY 0 1 0000 prg 08000 30'),
            output.replace('COPY 1 5 0004 ram 00004 74', 'COPY 1 5 0004 ram 00004 34'),
            output.replace('COPY 2 0 FFFF prg 0FFFF AA', 'COPY 2 0 FFFF prg 07FFF AA'),
            output.replace('CASE 3 10 0 00 0A FF 0', 'CASE 3 10 1 00 0A FF 0'),
            output.replace('DONE 4 0', 'DONE 4 1'),
        )
        for value in invalid:
            with self.subTest(case=value[:60]), self.assertRaises(ValueError):
                parse_output(value, bank0, bank1)

    def test_descriptor_path_validates_every_pointer_and_comparison_case(self):
        bank = bytearray(BANK_SIZE)
        lines = []
        for number, index in enumerate(DESCRIPTOR_INDICES):
            pointer = 0xffff if number < 5 else 0x1234
            offset = DESCRIPTORS + index * 6
            bank[offset:offset + 2] = pointer.to_bytes(2, 'little')
            lines.append(f'DESC {index:02X} {pointer:04X} 00 0A 0')
        lines.append('DONE 6')
        output = '\n'.join(lines)
        result = parse_descriptor_output(output, bytes(bank))
        self.assertEqual((result['cases'], result['wrap_cases']), (6, 5))
        invalid = (output.replace('DESC 40 FFFF 00 0A 0\n', ''),
                   output.replace('DESC 46 FFFF 00 0A 0', 'DESC 46 FFFE 00 0A 0'),
                   output.replace('DESC 47 FFFF 00 0A 0', 'DESC 47 FFFF 01 0A 0'),
                   output.replace('DESC 4C FFFF 00 0A 0', 'DESC 4C FFFF 00 0A 1'),
                   output.replace('DONE 6', 'DONE 5'))
        for value in invalid:
            with self.subTest(case=value[:60]), self.assertRaises(ValueError):
                parse_descriptor_output(value, bytes(bank))


if __name__ == '__main__':
    unittest.main()
