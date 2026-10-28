"""Audio-bank evidence validation uses synthetic PRG data only."""
import unittest

from tools.verify_audio_bank import parse_mapping, parse_selector


def synthetic_banks():
    bank = bytearray(0x8000)
    for n in range(8):
        bank[0x7FB7 + 1 + n * 2] = 0x0D + n * 0x10
    return bytes(bank), bytes(bank)


def selector_output(bank):
    lines = []
    conflicts = 0
    for case in range(256):
        a, carry = case % 128, case // 128
        n = (a % 32) // 2
        value, index = 0x0D + n * 0x10, 1 + n * 2
        rom = bank[0x7FB7 + index]
        if rom != value:
            conflicts += 1
            lines.append(f'CONFLICT {a:02X} {carry} {value:02X} {index:02X} {rom:02X}')
        lines.append(f'SELECT {a:02X} {carry} {value:02X} {index:02X} {value:02X} {index:02X}')
    lines.append(f'DONE 256 0 {conflicts}')
    return '\n'.join(lines)


def mapping_output(bank):
    lines = []
    changed = 0
    for n in range(16):
        value, index, pointer = 0x0D + n * 0x10, 1 + n * 2, 0x8123
        rom = bank[0x7FB7 + index]
        physical = pointer - 0x8000 + ((value & rom) & 1) * 0x8000
        changed += physical < 0x8000
        lines.append(f'BANK {n} {value:02X} {index:02X} {rom:02X} {pointer:04X} {physical:05X} {pointer:05X} {value:02X} {index:02X}')
    lines.append(f'DONE 100 16 {changed} 0')
    return '\n'.join(lines)


class AudioBankEvidenceTests(unittest.TestCase):
    def test_selector_requires_all_cases_and_consistent_conflicts(self):
        bank0, bank1 = synthetic_banks();output = selector_output(bank0)
        self.assertEqual(parse_selector(output, bank0, bank1), {'cases': 256, 'table_mismatches': 128})
        for invalid in (output.replace('SELECT 00 0 0D 01 0D 01\n', ''),
                        output.replace('SELECT 00 0 0D 01 0D 01', 'SELECT 00 0 1D 01 0D 01'),
                        output.replace('DONE 256 0 128', 'DONE 256 0 127')):
            with self.subTest(invalid=invalid[:60]), self.assertRaises(ValueError):
                parse_selector(invalid, bank0, bank1)

    def test_mapping_rejects_missing_or_wrong_physical_bank(self):
        bank0, bank1 = synthetic_banks();output = mapping_output(bank0)
        self.assertEqual(parse_mapping(output, bank0, bank1)['bank0_cases'], 8)
        for invalid in (output.replace('BANK 0 0D 01 0D 8123 08123 08123 0D 01\n', ''),
                        output.replace('BANK 0 0D 01 0D 8123 08123 08123 0D 01',
                                       'BANK 0 0D 01 0D 8123 00123 08123 0D 01'),
                        output.replace('BANK 0 0D 01 0D 8123 08123 08123 0D 01',
                                       'BANK 0 0D 01 0D 8123 08123 08123 1D 01'),
                        output.replace('DONE 100 16 8 0', 'DONE 100 16 0 0')):
            with self.subTest(invalid=invalid[:60]), self.assertRaises(ValueError):
                parse_mapping(invalid, bank0, bank1)


if __name__ == '__main__':
    unittest.main()
