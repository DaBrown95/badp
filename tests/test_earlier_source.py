"""Source macro boundaries cannot silently drop an instruction or select a duplicate."""
import unittest

from tools.earlier_source import macro_body


class EarlierSourceTests(unittest.TestCase):
    def test_parameterless_and_parameterized_bodies_keep_their_first_line(self):
        for declaration, body in (('.macro Example', '    lda #$17'),
                                  ('.macro Example operand', '    lda operand')):
            source = declaration + '\n' + body + '\n.endmacro\n'
            low, high = macro_body(source, 'Example')
            self.assertEqual(source[low:high], body)

    def test_missing_duplicate_and_unterminated_macros_fail(self):
        source = '.macro Example\n    lda #$17\n.endmacro\n'
        for broken in ('', source + source, source.replace('.endmacro', '')):
            with self.assertRaises(ValueError):macro_body(broken, 'Example')
