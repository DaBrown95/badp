"""Candidate audio traversal tests use synthetic source and banks only."""
import unittest

from tools.audio_flow import literal_seeds, walk
from tools.script_entries import BANK_SIZE


class AudioFlowTests(unittest.TestCase):
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
