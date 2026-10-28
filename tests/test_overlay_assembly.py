"""Exercise the real overlay macros with synthetic values and no game ROM."""
import re
import subprocess
import tempfile
from pathlib import Path
import unittest

from tools.setup import ROOT, verified_tools


class OverlayAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.tools = verified_tools()
        except FileNotFoundError as exc:
            raise unittest.SkipTest(f'pinned assembler unavailable: {exc}') from exc
        source = (ROOT / 'src/us-v1.5/rom.s').read_text()
        names = ('BogusJumpBank1', 'BogusSetSlotMode', 'BogusSetSlotD0Bits',
                 'BogusJumpCompactOverlay', 'BogusModeResourceOverlay',
                 'BogusSetJumpRecordOverlay')
        cls.macros = ''
        for name in names:
            match = re.search(r'^\.macro ' + name + r'\b[^\n]*\n.*?^\.endmacro\n',
                              source, re.MULTILINE | re.DOTALL)
            if not match:
                raise AssertionError(f'missing macro {name}')
            cls.macros += match.group(0) + '\n'

    def assemble(self, statements):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input.s').write_text(self.macros + '\nBankStart = $8000\n.segment "CODE"\n' + statements + '\n')
            (root / 'link.cfg').write_text('MEMORY { ROM: start=$8000, size=$8000, file=%O; }\n'
                                           'SEGMENTS { CODE: load=ROM, type=ro; }\n')
            assembler = subprocess.run([str(self.tools['ca65']), 'input.s', '-o', 'input.o'],
                                       cwd=root, capture_output=True, text=True)
            if assembler.returncode:
                return assembler.returncode, assembler.stderr, b''
            linker = subprocess.run([str(self.tools['ld65']), '-C', 'link.cfg', '-o', 'output.bin', 'input.o'],
                                    cwd=root, capture_output=True, text=True)
            output = (root / 'output.bin').read_bytes() if linker.returncode == 0 else b''
            return linker.returncode, linker.stderr, output

    def test_views_emit_the_same_synthetic_fields(self):
        result, error, output = self.assemble('''
BogusJumpCompactOverlay $9356, $5604, $13
BogusModeResourceOverlay $12, $120A
BogusSetJumpRecordOverlay $34, $9456, $345D, $5604, $14
''')
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('04 56 13 0a 12 5d 34 04 56 14'))

    def test_mismatched_views_fail_assembly_or_link(self):
        cases = (
            ('BogusJumpCompactOverlay $9356, $5704, $13', 'jump/compact resource'),
            ('BogusJumpCompactOverlay $9356, $5604, $14', 'jump/compact flags'),
            ('BogusModeResourceOverlay $12, $130A', 'mode/resource'),
            ('BogusSetJumpRecordOverlay $34, $9456, $355D, $5604, $14', 'setter/record'),
            ('BogusSetJumpRecordOverlay $34, $9456, $345D, $5704, $14', 'jump/record script'),
            ('BogusSetJumpRecordOverlay $34, $9456, $345D, $5604, $15', 'jump/record flags'),
        )
        for statement, message in cases:
            with self.subTest(statement=statement):
                result, error, _ = self.assemble(statement)
                self.assertNotEqual(result, 0)
                self.assertIn(message, error)


if __name__ == '__main__':
    unittest.main()
