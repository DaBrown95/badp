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
        names = ('BogusJumpBank1', 'BogusSetSlotMode', 'BogusSetSlotD0Bits', 'AudioNote',
                 'BogusJumpCompactOverlay', 'BogusModeResourceOverlay',
                 'BogusSetJumpRecordOverlay', 'AudioNoteBogusOverlay',
                 'BogusSetSlotC0', 'BogusSetSlot0670Pair', 'BogusMaskSlotValue',
                 'BogusBranchAndClearSlot0620Bit08', 'BogusBranchIfSlot0520AtMost',
                 'BogusBranchIfMatchingSlotReady', 'BogusMarkMatchingSlots',
                 'BogusSetVoicePointers', 'BogusAddSelectedFieldClamped',
                 'BogusSetInvertedState3B', 'ContactPointerScriptOverlay',
                 'AudioNoteView', 'AudioScriptByte', 'AudioScriptPair', 'AudioScriptTriple',
                 'AudioScriptWord', 'AudioScriptTarget', 'AudioScriptTargetByte',
                 'AudioScriptTargetTriple', 'AudioScriptQuad', 'AudioScriptFourWords')
        cls.macros = '\n'.join(re.findall(r'^BogusActionOpcode_\w+ = \$[0-9A-F]{2}$', source, re.MULTILINE)) + '\n'
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

    def test_action_opcode_constants_match_script_macro_definitions(self):
        source = (ROOT / 'src/us-v1.5/rom.s').read_text()
        constants = re.findall(r'^BogusActionOpcode_(Bogus\w+) = \$([0-9A-F]{2})$', source, re.MULTILINE)
        self.assertTrue(constants)
        for name, opcode in constants:
            with self.subTest(action=name):
                macro = re.search(r'^\.macro ' + name + r'\b[^\n]*\n(.*?)^\.endmacro',
                                  source, re.MULTILINE | re.DOTALL)
                self.assertIsNotNone(macro)
                emitted = re.search(r'\.byte\s+\$([0-9A-F]{2})(?:\s|,|$)', macro.group(1))
                self.assertIsNotNone(emitted)
                self.assertEqual(emitted.group(1), opcode)

    def test_views_emit_the_same_synthetic_fields(self):
        result, error, output = self.assemble('''
BogusJumpCompactOverlay $9356, $5604, $13
BogusModeResourceOverlay $12, $120A
BogusSetJumpRecordOverlay $34, $9456, $345D, $5604, $14
AudioNoteBogusOverlay $01, $05, $25
ContactPointerScriptOverlay $9364, $13
''')
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('04 56 13 0a 12 5d 34 04 56 14 25 64 13'))

    def test_multi_byte_audio_script_forms(self):
        # Synthetic commands exercise every operand layout, including target
        # encoding and little-endian words, without reading a game image.
        examples = (
            ('Byte', 'BogusSetSlotC0', 0x09, ('$12',), bytes([0x09, 0x12])),
            ('Pair', 'BogusSetSlot0670Pair', 0x0c, ('$22', '$34'), bytes([0x0c, 0x22, 0x34])),
            ('Triple', 'BogusAddSelectedFieldClamped', 0x38, ('$12', '$34', '$56'), bytes([0x38, 0x12, 0x34, 0x56])),
            ('Word', 'BogusMaskSlotValue', 0x40, ('$1256',), bytes([0x40, 0x56, 0x12])),
            ('Target', 'BogusBranchAndClearSlot0620Bit08', 0x27, ('$3456',), bytes([0x27, 0x56, 0x34])),
            ('TargetByte', 'BogusBranchIfSlot0520AtMost', 0x22, ('$3456', '$12'), bytes([0x22, 0x56, 0x34, 0x12])),
            ('TargetTriple', 'BogusBranchIfMatchingSlotReady', 0x35, ('$3456', '$12', '$34', '$56'), bytes([0x35, 0x56, 0x34, 0x12, 0x34, 0x56])),
            ('Quad', 'BogusMarkMatchingSlots', 0x36, ('$12', '$34', '$56', '$78'), bytes([0x36, 0x12, 0x34, 0x56, 0x78])),
            ('FourWords', 'BogusSetVoicePointers', 0x31, ('$1256', '$1234', '$3456', '$5678'), bytes([0x31, 0x56, 0x12, 0x34, 0x12, 0x56, 0x34, 0x78, 0x56])),
        )
        for shape, action, opcode, args, expected in examples:
            with self.subTest(shape=shape):
                notes = [part for byte in expected for part in (f'${byte >> 5:02X}', f'${byte & 31:02X}')]
                statement = ', '.join([f'AudioScript{shape} {action}', f'${opcode:02X}', *args, *notes])
                result, error, output = self.assemble(statement)
                self.assertEqual(result, 0, error)
                self.assertEqual(output, expected)
                # A note inconsistent with the command must fail before linking.
                notes[-1] = f'${(expected[-1] & 31) ^ 1:02X}'
                bad = ', '.join([f'AudioScript{shape} {action}', f'${opcode:02X}', *args, *notes])
                result, error, _ = self.assemble(bad)
                self.assertNotEqual(result, 0)
                self.assertIn('audio/script byte disagreement', error)

    def test_audio_note_components_are_bounded(self):
        for duration, note in ((-1, 0), (5, 0), (0, -1), (0, 32)):
            with self.subTest(duration=duration, note=note):
                result, error, _ = self.assemble(f'AudioNoteBogusOverlay {duration}, {note}, $00')
                self.assertNotEqual(result, 0)
                self.assertTrue('invalid audio note' in error or 'Range error' in error)
                result, error, _ = self.assemble(f'AudioNoteView {duration}, {note}, $00')
                self.assertNotEqual(result, 0)
                self.assertIn('invalid audio note', error)

    def test_mismatched_views_fail_assembly_or_link(self):
        cases = (
            ('ContactPointerScriptOverlay $9365, $13', 'contact/script opcode'),
            ('ContactPointerScriptOverlay $9364, $12', 'contact/script operand'),
            ('AudioNoteBogusOverlay $01, $05, $24', 'audio/script opcode'),
            ('BogusJumpCompactOverlay $9356, $5704, $13', 'jump/compact resource'),
            ('BogusJumpCompactOverlay $9356, $5604, $14', 'jump/compact flags'),
            ('BogusModeResourceOverlay $12, $130A', 'mode/resource'),
            ('BogusSetJumpRecordOverlay $34, $9456, $355D, $5604, $14', 'setter/record'),
            ('BogusSetJumpRecordOverlay $34, $9456, $345D, $5704, $14', 'jump/record script'),
            ('BogusSetJumpRecordOverlay $34, $9456, $345D, $5604, $15', 'jump/record flags'),
        )
        cases += (
            ('AudioScriptByte BogusSetSlotC0, $08, $12, $00, $08, $00, $12', 'BOGUS action opcode'),
        )
        for statement, message in cases:
            with self.subTest(statement=statement):
                result, error, _ = self.assemble(statement)
                self.assertNotEqual(result, 0)
                self.assertIn(message, error)


if __name__ == '__main__':
    unittest.main()
