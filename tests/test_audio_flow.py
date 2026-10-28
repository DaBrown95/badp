"""Candidate audio traversal tests use synthetic source and banks only."""
import unittest

from tools.audio_flow import literal_seeds, walk
from tools.script_entries import BANK_SIZE


class AudioFlowTests(unittest.TestCase):
    def test_voice_overlays_contribute_only_valid_literal_starts(self):
        def note_args(values):
            return ', '.join(f'${part:02X}' for value in values for part in (value >> 5, value & 31))

        words = (0x1234, 0x5678, 0x3456, 0x6789)
        encoded = [0x31] + [part for word in words for part in (word & 0xff, word >> 8)]
        voices = ('    AudioScriptFourWords BogusSetVoicePointers, $31, '
                  + ', '.join(f'${word:04X}' for word in words) + ', ' + note_args(encoded))
        single = ('    AudioScriptWord BogusRestartVoice4, $49, $2345, '
                  + note_args([0x49, 0x45, 0x23]))
        preserve = ('    AudioScriptWord BogusStartVoice4, $50, $0000, '
                    + note_args([0x50, 0, 0]))
        record = ('    SlotRecordVoiceOverlay $AB31, $1234, $56, $78, $7A, $7B, $7C, '
                  '$34AB, $5612, $7A78, $7C7B')
        stopped_record = ('    SlotRecordVoiceOverlay $AA31, $FFFF, $00, $00, $00, $00, $00, '
                          '$FFAA, $00FF, $0000, $0000')
        native = '''
ScriptOp18:
    ldx #$34
    ldy #$12
    jsr StartAudioVoice
.assert 1, error, "synthetic"
'''
        source = '\n'.join((voices, single, preserve, record, stopped_record, native))
        self.assertEqual(literal_seeds(source),
                         sorted({0x1234, 0x5678, 0x3456, 0x6789, 0x2345,
                                 0x34ab, 0x5612, 0x7a78, 0x7c7b}))
        failures = (
            voices.replace('$31', '$30', 1),
            voices.replace('$1234', 'Label', 1),
            voices.rsplit(',', 1)[0],
            voices.replace('$01, $11', '$01, $10', 1),
            single.replace('AudioScriptWord', 'AudioScriptTarget', 1),
            single.replace('$2345', 'Label', 1),
            record.replace('$34AB', '$34AA', 1),
            record.replace('$AB31', '$AB30', 1),
            record.rsplit(',', 1)[0],
        )
        for bad in failures:
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'overlay'):
                literal_seeds(bad + native)

    def test_literal_starts_ignore_stop_and_preserve_operands(self):
        source = '''
    BogusSetVoicePointers $1234, $0000, $FFFF, $2A58
    BogusStartVoice4 $2769 ; a comment
    BogusRestartVoice4 $0000
    BogusStartVoice4FromIndexedPair $4444
    AudioPointerEntry $5678
    AudioVoicePointerRecord $FFFF, $0000, $3456, $6789
ScriptOp18:
    lda #$04
    jsr StopAudioVoice
    ldx #$C8
    ldy #$26
    lda #$04
    jsr StartAudioVoice
    rts
.assert 1, error, "synthetic"
'''
        self.assertEqual(literal_seeds(source), [0x1234, 0x26c8, 0x2769, 0x2a58, 0x3456, 0x5678, 0x6789])
        with self.assertRaisesRegex(ValueError, 'unsupported audio pointer'):
            literal_seeds(source.replace('$2769', 'SomeLabel'))
        with self.assertRaisesRegex(ValueError, 'unsupported audio pointer'):
            literal_seeds(source.replace('AudioPointerEntry $5678', 'AudioPointerEntry SomeLabel'))
        with self.assertRaisesRegex(ValueError, 'unsupported audio pointer'):
            literal_seeds(source.replace('AudioVoicePointerRecord $FFFF, $0000, $3456, $6789',
                                         'AudioVoicePointerRecord $FFFF, $0000, $3456'))
        with self.assertRaisesRegex(ValueError, 'native opcode'):
            literal_seeds(source.replace('jsr StartAudioVoice', 'jsr OtherRoutine'))
        with self.assertRaisesRegex(ValueError, 'audio boundaries'):
            literal_seeds(source.replace('.assert', '.missing_assert'))

    def test_loop_tracks_target_and_exit_without_revisiting_context(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x108] = bytes([0xe0, 0xfb, 3, 0xc0, 2, 1, 1, 0xe8])
        result = walk(bytes(bank0), bytes(bank1), [0x100])
        by_pointer = {n['encoded_pointer']: n for n in result['nodes']}
        self.assertEqual(set(by_pointer), {'0x0100', '0x0101', '0x0103', '0x0107'})
        self.assertEqual(by_pointer['0x0103']['successors'], [
            {'kind': 'possible_loop', 'encoded_pointer': '0x0101'},
            {'kind': 'possible_loop_exit', 'encoded_pointer': '0x0107'}])
        self.assertEqual(by_pointer['0x0107']['status'], 'voice_stopped')
        self.assertEqual(result['physical_bytes'], 8)
        self.assertEqual(result['overlapping_decode_bytes'], 0)
        self.assertFalse(result['unprocessed'])

    def test_restore_advances_from_the_voice_start(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x102] = bytes([0xe0, 0xc4])
        result = walk(bytes(bank0), bytes(bank1), [0x100])
        self.assertEqual(result['nodes'][1]['successors'], [
            {'kind': 'restore_then_advance', 'encoded_pointer': '0x0101'}])
        self.assertEqual(len(result['nodes']), 2)

    def test_overlaps_crossings_and_limits_remain_visible(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        bank1[0x100:0x102] = bytes([0xec, 0xe8])
        result = walk(bytes(bank0), bytes(bank1), [0x100, 0x101, 0x7ffd])
        self.assertEqual(result['overlapping_decode_bytes'], 1)
        self.assertEqual(result['crossing_fetches'], 1)
        limited = walk(bytes(bank0), bytes(bank1), [0x100], limit=1)
        self.assertTrue(limited['unprocessed'])
        with self.assertRaises(ValueError):
            walk(bytes(bank0), bytes(bank1), [0x100], limit=0)


if __name__ == '__main__':
    unittest.main()
