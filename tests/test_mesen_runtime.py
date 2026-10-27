"""Runtime evidence parsing tests use synthetic emulator output only."""
import unittest

from tools.mesen_runtime import (FRAMES, PNG_SIGNATURE, RECORD_TARGETS, SCRIPT_TARGETS,
                                 parse_output, validate_scenario)


def synthetic_output(state=1):
    lines = ['BADP_WRITE 0 FFB7 0C 32767 12', 'BADP_WRITE 1 FFC6 0D 65534 13',
             'BADP_APU 1 4000 30', 'BADP_DMA 1 4014 02']
    for frame in FRAMES:
        scene = 0 if frame == 240 else 16 if frame == 650 else state
        scroll = 3 if frame >= 1800 else 0
        png = (PNG_SIGNATURE + (b'moved' if frame >= 1800 else b'initial')).hex()
        lines.append(f'BADP_FRAME {frame} 0 {scene} {scroll} 0 0 {frame * 100} {frame} {png}')
    lines.append('BADP_SUMMARY 2 0 0 1 1 2100 1 1')
    lines.append('BADP_PROBE 4 2')
    lines.extend(f'BADP_TARGET script {address:04X} 0' for address in SCRIPT_TARGETS)
    lines.extend(f'BADP_TARGET record {address:04X} 0' for address in RECORD_TARGETS)
    return '\n'.join(lines) + '\n'


class MesenRuntimeTests(unittest.TestCase):
    def test_valid_synthetic_trace_and_scenario(self):
        evidence, images, events = parse_output(synthetic_output())
        self.assertEqual(evidence['mapper_writes'], 2)
        self.assertEqual(evidence['physical_prg_banks_seen'], [0, 1])
        self.assertEqual(evidence['script_fetch_probes'], 4)
        self.assertEqual(evidence['record_load_probes'], 2)
        self.assertEqual(set(images), set(FRAMES))
        self.assertIn(b'BADP_WRITE', events['mapper'])
        self.assertIn(b'BADP_APU', events['apu'])
        self.assertIn(b'BADP_DMA', events['oam_dma'])
        validate_scenario(evidence, 1)

    def test_missing_duplicate_or_inconsistent_evidence_fails(self):
        text = synthetic_output()
        for invalid in (text.replace('BADP_SUMMARY 2 0 0 1 1 2100 1 1', ''),
                        text + 'BADP_SUMMARY 2 0 0 1 1 2100 1 1\n',
                        text.replace('BADP_TARGET script 3D21 0\n', ''),
                        text.replace('BADP_SUMMARY 2 0 0 1 1 2100 1 1', 'BADP_SUMMARY 2 1 0 1 1 2100 1 1'),
                        text.replace('BADP_APU 1 4000 30', 'BADP_APU 1 4014 30'),
                        text.replace('BADP_WRITE 0 FFB7 0C 32767 12', 'BADP_WRITE 0 FFB7 XX 32767 12')):
            with self.subTest(invalid=invalid[:50]), self.assertRaises(ValueError):
                parse_output(invalid)

    def test_wrong_game_or_no_movement_does_not_pass(self):
        evidence, _, _ = parse_output(synthetic_output(state=5))
        with self.assertRaisesRegex(ValueError, 'expected adventure'):
            validate_scenario(evidence, 1)
        evidence['frames']['1800']['scroll_x'] = evidence['frames']['1400']['scroll_x']
        with self.assertRaisesRegex(ValueError, 'rightward input'):
            validate_scenario(evidence, 5)


if __name__ == '__main__':
    unittest.main()
