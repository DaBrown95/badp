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
        names = ('BogusJumpBank1', 'BogusSetSlotMode', 'BogusSetSlotD0Bits', 'BogusSetDispatchCounter',
                 'BogusSelectRelativeSlotAndYield', 'AudioNote', 'AudioLoop', 'AudioWriteFive',
                 'AudioWriteRegister', 'AudioRestorePointer', 'AudioSelectChannel', 'AudioInstrument',
                 'BogusOrSlotValue', 'BogusSetSlot07F0', 'BogusBranchIfSlotD0Bits',
                 'BogusBranchIfSlot07C0Equal', 'BogusBranchPrefix',
                 'AudioBranchNoteRestoreChannelInstrument', 'AudioBranchNotesRestore',
                 'AudioLongBranchNotesRestoreChannel',
                 'BogusJumpCompactOverlay', 'BogusModeResourceOverlay',
                 'BogusSetJumpRecordOverlay', 'AudioNoteBogusOverlay',
                 'BogusSetSlotC0', 'BogusSetSlot0670Pair', 'BogusMaskSlotValue',
                 'BogusBranchAndClearSlot0620Bit08', 'BogusBranchIfSlot0520AtMost',
                 'BogusBranchIfMatchingSlotReady', 'BogusMarkMatchingSlots',
                 'BogusSetVoicePointers', 'BogusAddSelectedFieldClamped',
                 'BogusSetInvertedState3B', 'ContactPointerScriptOverlay',
                 'SlotRuntimeRecord', 'SlotCompactRecord', 'BogusAddSlotFields00', 'SlotRecordVoiceOverlay', 'SlotRecordScriptOverlay', 'SlotRecordBranchPrefix',
                 'AudioNoteView', 'AudioScriptByte', 'AudioScriptPair', 'AudioScriptTriple',
                 'AudioScriptWord', 'AudioScriptTarget', 'AudioScriptTargetByte',
                 'AudioScriptTargetTriple', 'AudioScriptQuad', 'AudioScriptFourWords')
        cls.macros = '\n'.join(re.findall(r'^BogusActionOpcode_\w+ = \$[0-9A-F]{2}$', source, re.MULTILINE)) + '\n'
        cls.macros += '\n'.join(re.findall(r'^AudioOpcode\w+ = \$[0-9A-F]{2}$', source, re.MULTILINE)) + '\n'
        cls.macros += '\n'.join(re.findall(r'^BogusOpcodeLoadRecordAndClearSavedState = \$[0-9A-F]{2}$', source, re.MULTILINE)) + '\n'
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
                emitted = re.search(r'\.byte\s+(\$[0-9A-F]{2}|BogusActionOpcode_\w+)(?:\s|,|$)', macro.group(1))
                self.assertIsNotNone(emitted)
                self.assertIn(emitted.group(1), (f'${opcode}', f'BogusActionOpcode_{name}'))

    def test_record_load_and_dispatch_share_the_opcode_byte(self):
        result, error, output = self.assemble('''
    .byte BogusOpcodeLoadRecordAndClearSavedState
    .assert BogusActionOpcode_BogusSetDispatchCounter = $2C, error, "record offset mismatch"
    BogusSetDispatchCounter $35
''')
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes([0x00, 0x2c, 0x35]))
        result, error, _ = self.assemble('.assert BogusActionOpcode_BogusSetDispatchCounter = $2D, error, "record offset mismatch"')
        self.assertNotEqual(result, 0)
        self.assertIn('record offset mismatch', error)

    def test_views_emit_the_same_synthetic_fields(self):
        result, error, output = self.assemble('''
BogusJumpCompactOverlay $9356, $5604, $13
BogusModeResourceOverlay $12, $120A
BogusSetJumpRecordOverlay $34, $9456, $345D, $5604, $14
AudioNoteBogusOverlay $01, $05, $25
ContactPointerScriptOverlay $9364, $13
SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, $34AB, $5612, $7A78, $7C7B
''')
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('04 56 13 0a 12 5d 34 04 56 14 25 64 13 31 ab 34 12 56 78 7a 7b 7c'))

    def test_record_script_overlay_preserves_each_shared_opcode(self):
        good = 'SlotRecordScriptOverlay $B912, $1234, $40, $33, $44, $62, $55, $12'
        result, error, output = self.assemble(good)
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('12 b9 34 12 40 33 44 62 55'))
        failures = (
            ('SlotRecordScriptOverlay $B912, $1234, $40, $33, $44, $62, $55, $13', 'prior branch'),
            ('SlotRecordScriptOverlay $B812, $1234, $40, $33, $44, $62, $55, $12', 'pair opcode'),
            ('SlotRecordScriptOverlay $B912, $1234, $41, $33, $44, $62, $55, $12', 'mask opcode'),
            ('SlotRecordScriptOverlay $B912, $1234, $40, $33, $44, $63, $55, $12', 'branch opcode'),
        )
        for statement, message in failures:
            with self.subTest(statement=statement):
                result, error, _ = self.assemble(statement)
                self.assertNotEqual(result, 0)
                self.assertIn(message, error)

    def test_contact_pointer_high_byte_can_start_a_script_command(self):
        statement = '''
    .assert >$6751 = BogusActionOpcode_BogusSelectRelativeSlotAndYield, error, "contact/script opcode disagreement"
    BogusSelectRelativeSlotAndYield $01, $02, $03, $04, $05
'''
        result, error, output = self.assemble(statement)
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('67 01 02 03 04 05'))
        result, error, _ = self.assemble(statement.replace('>$6751', '>$6651'))
        self.assertNotEqual(result, 0)
        self.assertIn('contact/script opcode disagreement', error)

    def test_record_prefix_can_share_a_branch_opcode(self):
        statement = 'SlotRecordBranchPrefix $1293, $3456, $78, $79, $7A, $7B'
        result, error, output = self.assemble(statement)
        self.assertEqual(result, 0, error)
        self.assertEqual(output, bytes.fromhex('93 12 56 34 78 79 7a 7b'))
        result, error, _ = self.assemble(statement.replace('$1293', '$1292'))
        self.assertNotEqual(result, 0)
        self.assertIn('record/script branch prefix disagreement', error)

    def test_resource_high_byte_can_start_pair_bit_command(self):
        for opcode, action in ((0xB9, 'BogusClearSlot0640PairBits'),
                               (0xBA, 'BogusSetSlot0640PairBits')):
            with self.subTest(opcode=opcode):
                statement = (f'.assert >${opcode:02X}12 = BogusActionOpcode_{action}, error, "record/script opcode disagreement"\n'
                             f'.word ${opcode:02X}12, $3456')
                result, error, output = self.assemble(statement)
                self.assertEqual(result, 0, error)
                self.assertEqual(output, bytes([0x12, opcode, 0x56, 0x34]))
                wrong = statement.replace(f'>${opcode:02X}12', '>$BB12')
                result, error, _ = self.assemble(wrong)
                self.assertNotEqual(result, 0)
                self.assertIn('record/script opcode disagreement', error)

    def test_compact_record_and_command_share_all_synthetic_bytes(self):
        record = ".assert <$A108 = BogusActionOpcode_BogusAddSlotFields00, error, \"opcode disagreement\"\nSlotCompactRecord $A108, $27"
        command = "BogusAddSlotFields00 $A1, $27"
        result, error, record_bytes = self.assemble(record)
        self.assertEqual(result, 0, error)
        result, error, command_bytes = self.assemble(command)
        self.assertEqual(result, 0, error)
        self.assertEqual(record_bytes, command_bytes)
        result, error, _ = self.assemble(record.replace("$A108", "$A109"))
        self.assertNotEqual(result, 0)
        self.assertIn("opcode disagreement", error)

    def test_audio_loop_prefix_and_overlapping_script_commands(self):
        statements = """
.assert AudioOpcodeLoop = BogusActionOpcode_BogusOrSlotValue, error, "loop opcode disagreement"
.assert >$2C52 = BogusActionOpcode_BogusSetDispatchCounter, error, "dispatch opcode disagreement"
AudioLoop $03, $2C52
AudioWriteFive $71, $72, $73, $74
"""
        result, error, audio = self.assemble(statements)
        self.assertEqual(result, 0, error)
        result, error, first = self.assemble('BogusOrSlotValue $5203')
        self.assertEqual(result, 0, error)
        result, error, second = self.assemble('BogusSetDispatchCounter $F9')
        self.assertEqual(result, 0, error)
        self.assertEqual(audio[:3], first)
        self.assertEqual(audio[3:5], second)
        result, error, _ = self.assemble(statements.replace('>$2C52', '>$2D52'))
        self.assertNotEqual(result, 0)
        self.assertIn('dispatch opcode disagreement', error)

    def test_audio_register_value_can_start_a_script_command(self):
        result, error, audio = self.assemble("""
AudioWriteRegister $01, BogusActionOpcode_BogusSetSlot07F0
AudioWriteRegister $02, $67
""")
        self.assertEqual(result, 0, error)
        result, error, script = self.assemble('BogusSetSlot07F0 $EE')
        self.assertEqual(result, 0, error)
        self.assertEqual(audio[1:3], script)

    def test_mixed_audio_branch_views_and_selector_bounds(self):
        cases = (
            ('AudioBranchNoteRestoreChannelInstrument BogusBranchIfSlot0520AtMost, $22, $01, $02, $02, $09',
             'AudioNote $01, $02\nAudioRestorePointer\nAudioSelectChannel $02\nAudioInstrument $09'),
            ('AudioBranchNotesRestore BogusBranchIfSlotD0Bits, $5F, $3031, $02, $1F, $01, $11, $01, $10',
             'AudioNote $02, $1F\nAudioNote $01, $11\nAudioNote $01, $10\nAudioRestorePointer'),
            ('AudioLongBranchNotesRestoreChannel BogusBranchIfMatchingSlotReady, $35, $3937, $38, $02, $01, $15, $01, $17, $01, $19, $01, $18',
             'AudioNote $01, $15\nAudioNote $01, $17\nAudioNote $01, $19\nAudioNote $01, $18\nAudioRestorePointer\nAudioSelectChannel $02'),
        )
        for script, audio in cases:
            with self.subTest(script=script):
                result, error, script_bytes = self.assemble(script)
                self.assertEqual(result, 0, error)
                result, error, audio_bytes = self.assemble(audio)
                self.assertEqual(result, 0, error)
                self.assertEqual(script_bytes, audio_bytes)
        bad = cases[0][0].replace('$02, $09', '$04, $09')
        result, error, _ = self.assemble(bad)
        self.assertNotEqual(result, 0)
        self.assertIn('invalid audio selector', error)
        bad = cases[2][0].replace('$02, $01, $15', '$04, $01, $15')
        result, error, _ = self.assemble(bad)
        self.assertNotEqual(result, 0)
        self.assertIn('invalid audio channel', error)
        bad = cases[1][0].replace('$02, $1F', '$02, $1E')
        result, error, _ = self.assemble(bad)
        self.assertNotEqual(result, 0)
        self.assertIn('audio/script byte disagreement', error)

    def test_branch_prefix_shares_its_final_byte_with_following_data(self):
        result, error, prefix = self.assemble('BogusBranchPrefix BogusBranchIfSlot07C0Equal, $3456')
        self.assertEqual(result, 0, error)
        result, error, branch = self.assemble('BogusBranchIfSlot07C0Equal BankStart + $3456, $78')
        self.assertEqual(result, 0, error)
        self.assertEqual(prefix, branch[:3])

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
            ('SlotRecordVoiceOverlay $AB30, $1234, $56, $78, $7A, $7B, $7C, $34AB, $5612, $7A78, $7C7B', 'record/voice opcode'),
            ('SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, $34AA, $5612, $7A78, $7C7B', 'record/voice 0'),
            ('SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, $34AB, $5613, $7A78, $7C7B', 'record/voice 1'),
            ('SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, $34AB, $5612, $7A79, $7C7B', 'record/voice 2'),
            ('SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, $34AB, $5612, $7A78, $7C7A', 'record/voice 3'),
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
