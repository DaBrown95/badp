"""Official opcode facts and source syntax; no game fixtures are used."""
import unittest

from tools.nes6502 import MNEMONICS, OPCODES, source_mode_matches


class Nes6502Tests(unittest.TestCase):
    def test_official_forms_and_mode_exceptions(self):
        self.assertEqual((len(OPCODES), len(MNEMONICS)), (151, 56))
        for opcode, expected in ((0xa9, ('lda', 'imm', 2)), (0xb6, ('ldx', 'zpy', 2)),
                                 (0xbe, ('ldx', 'absy', 3)), (0x96, ('stx', 'zpy', 2)),
                                 (0x6c, ('jmp', 'ind', 3)), (0xea, ('nop', 'imp', 1))):
            self.assertEqual(OPCODES[opcode], expected)
        for unofficial in (0x02, 0x89, 0xeb, 0xff):
            self.assertNotIn(unofficial, OPCODES)

    def test_addressing_syntax_and_width_overrides(self):
        for mnemonic, operand, mode in (('lda', '#<value', 'imm'), ('lda', 'a:value', 'abs'),
                                       ('lda', 'z:value,x', 'zpx'), ('ldx', 'value,y', 'zpy'),
                                       ('lda', '(pointer,x)', 'indx'), ('lda', '(pointer),y', 'indy'),
                                       ('jmp', '(pointer)', 'ind'), ('asl', 'a', 'acc'),
                                       ('ror', '', 'acc'), ('rts', '', 'imp'), ('bne', 'label', 'rel')):
            self.assertTrue(source_mode_matches(mnemonic, operand, mode))
        for mnemonic, operand, mode in (('lda', '#value', 'zp'), ('lda', 'a:value', 'zp'),
                                       ('lda', 'z:value', 'abs'), ('lda', '(pointer),y', 'absy'),
                                       ('rts', 'value', 'imp'), ('bne', '#value', 'rel')):
            self.assertFalse(source_mode_matches(mnemonic, operand, mode))


if __name__ == '__main__':
    unittest.main()
