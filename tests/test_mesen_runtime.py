"""Runtime evidence parsing tests use synthetic emulator output only."""
import json
from pathlib import Path
import tempfile
import unittest
import zlib

from tools.mesen_runtime import (FRAMES, SLOT_FRAMES, PNG_SIGNATURE, MOSES_SUCCESS_SCREEN_SHA256,
                                 MOSES_LEVEL_TWO_SUCCESS_SHA256,
                                 RECORD_TARGETS, SCRIPT_TARGETS,
                                 evidence_difference_paths, parse_output, retain_runtime_failure, validate_scenario)


def synthetic_output(state=1, *, inventory=False):
    lines = ['BADP_WRITE 0 FFB7 0C 32767 12', 'BADP_WRITE 1 FFC6 0D 65534 13',
             'BADP_APU 1 4000 30', 'BADP_DMA 1 4014 02']
    for frame in FRAMES:
        scene = 0 if frame == 240 else 16 if frame == 650 else state
        if state == 5 and frame in (3400, 3450, 3650):
            scene = 16
        elif state == 5 and frame in (3700, 3750, 3800, 3825, 3850, 3900, 4050, 4150, 4300, 4400, 4500, 4600, 4650, 4750, 4900, 5000, 5100, 5200, 5250, 5300, 5375, 5450, 5500, 5550):
            scene = 6
        if state == 5 and frame in (5575, 5625, 5650):
            scene = 16
        elif state == 5 and frame >= 5700:
            scene = 7
        if inventory and frame in (1800, 2100, 2300):
            scene = 16
        scroll = (0 if frame >= 5575 else 1984 if frame >= 5550 else 1963 if frame >= 5500 else 1899 if frame >= 5450 else 1799 if frame >= 5375 else 1703 if frame >= 5300 else 1635 if frame >= 5250 else 1567 if frame >= 5200 else 1470 if frame >= 5100 else 1338 if frame >= 5000 else 1202 if frame >= 4900 else 1002 if frame >= 4750 else 874 if frame >= 4650 else 860 if frame >= 4600 else 728 if frame >= 4500 else 596 if frame >= 4400 else 460 if frame >= 4300 else 260 if frame >= 4150 else 128 if frame >= 4050 else 0 if frame >= 3700 else 1984 if frame >= 3250 else 1925 if frame == 3200 else 1808 if frame == 3100
                  else 1692 if frame == 3000 else 1636 if frame == 2800 else 1390 if frame == 2600 else 1126 if frame == 2400
                  else 990 if frame == 2300 else 790 if frame == 2150 else 726 if frame == 2100
                  else 190 if frame >= 1700 else 0) if state == 5 else (3 if frame >= 1800 else 0)
        png = (PNG_SIGNATURE + (b'moved' if frame >= 1800 else b'initial')).hex()
        lines.append(f'BADP_FRAME {frame} 0 {scene} {scroll} 0 0 {frame * 100} {frame} {png}')
        if frame in SLOT_FRAMES:
            link = 255 if frame in (1400, 3250) else 1
            y = 160 if frame == 1400 else 130
            third_link = 1 if 3900 <= frame <= 5550 or frame in (5950, 6000, 6040, 6100, 6160, 6200, 6260, 6300, 6340) else 255
            x = 60 if frame == 6100 else 140 if frame == 6340 else 96
            player_y = 120 if frame == 6340 else 144
            lines.append(f'BADP_SLOT {frame} 1 106 {link} 96 {y} {x} {player_y} 106 {third_link} {x} 80')
    lines.append('BADP_SUMMARY 2 0 0 1 1 6340 1 1')
    lines.append('BADP_PROBE 4 2')
    lines.append(f'BADP_STAGE2_RECORD {int(state == 5)}')
    lines.append(f'BADP_POSITION_EVENT {int(state == 11)} 0')
    lines.append('BADP_INVENTORY 1 6 0' if inventory else 'BADP_INVENTORY 0 0 0')
    lines.extend(f'BADP_TARGET script {address:04X} 0' for address in SCRIPT_TARGETS)
    lines.extend(f'BADP_TARGET record {address:04X} 0' for address in RECORD_TARGETS)
    return '\n'.join(lines) + '\n'


def synthetic_moses_evidence():
    evidence, _, _ = parse_output(synthetic_output(state=5))
    evidence['frames']['3450']['screenshot_sha256'] = MOSES_SUCCESS_SCREEN_SHA256
    evidence['frames']['5625']['screenshot_sha256'] = MOSES_LEVEL_TWO_SUCCESS_SHA256
    return evidence


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
        for invalid in (text.replace('BADP_SUMMARY 2 0 0 1 1 6340 1 1', ''),
                        text + 'BADP_SUMMARY 2 0 0 1 1 6340 1 1\n',
                        text.replace('BADP_TARGET script 3D21 0\n', ''),
                        text.replace('BADP_INVENTORY 0 0 0\n', ''),
                        text.replace('BADP_STAGE2_RECORD 0\n', ''),
                        text + 'BADP_STAGE2_RECORD 0\n',
                        text.replace('BADP_STAGE2_RECORD 0', 'BADP_STAGE2_RECORD -1'),
                        text.replace('BADP_POSITION_EVENT 0 0\n', ''),
                        text + 'BADP_POSITION_EVENT 0 0\n',
                        text.replace('BADP_POSITION_EVENT 0 0', 'BADP_POSITION_EVENT -1 0'),
                        text + 'BADP_INVENTORY 0 0 0\n',
                        text.replace('BADP_INVENTORY 0 0 0', 'BADP_INVENTORY -1 0 0'),
                        text + 'BADP_WRITE 5700 FFB7 0C 32767 12\n',
                        text.replace('BADP_SLOT 1400 1 106 255 96 160 96 144 106 255 96 80\n', ''),
                        text + 'BADP_SLOT 1400 1 106 255 96 160 96 144 106 255 96 80\n',
                        text.replace('BADP_SLOT 1400 1 106 255', 'BADP_SLOT 1400 1 106 256'),
                        text.replace('BADP_SUMMARY 2 0 0 1 1 6340 1 1', 'BADP_SUMMARY 2 1 0 1 1 6340 1 1'),
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

    def test_david_requires_a_matched_native_position_event(self):
        evidence, _, _ = parse_output(synthetic_output(state=11))
        validate_scenario(evidence, 11)
        evidence['position_event_matches'] = 0
        with self.assertRaisesRegex(ValueError, 'position event'):
            validate_scenario(evidence, 11)
        evidence['position_event_matches'] = 1
        evidence['position_event_mismatches'] = 1
        with self.assertRaisesRegex(ValueError, 'position event'):
            validate_scenario(evidence, 11)

    def test_moses_requires_pickup_and_carry(self):
        evidence = synthetic_moses_evidence()
        validate_scenario(evidence, 5)
        for frame, field, value in (('1400', 'object_link', 1), ('1496', 'object_link', 255),
                                    ('1700', 'object_link', 255), ('1700', 'object_x', 0),
                                    ('1511', 'object_y', 160), ('1550', 'object_descriptor', 0),
                                    ('2800', 'object_link', 255), ('3250', 'object_link', 1),
                                    ('3300', 'object_link', 255)):
            with self.subTest(frame=frame, field=field):
                broken = synthetic_moses_evidence()
                broken['slots'][frame][field] = value
                with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
                    validate_scenario(broken, 5)
        for frame, value in (('2150', 726), ('3200', 1889), ('4050', 127), ('4300', 449), ('4600', 849), ('4900', 1189), ('5200', 1549), ('5550', 1983)):
            broken = synthetic_moses_evidence()
            broken['frames'][frame]['scroll_x'] = value
            with self.subTest(frame=frame), self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
                validate_scenario(broken, 5)
        broken = synthetic_moses_evidence()
        broken['stage2_record_mode2'] = 0
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(broken, 5)
        evidence['frames']['3450']['screenshot_sha256'] = 'not-the-success-screen'
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(evidence, 5)
        evidence = synthetic_moses_evidence()
        evidence['frames']['3700']['state'] = 16
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(evidence, 5)
        for frame, field, value in (('5625', 'screenshot_sha256', 'wrong-screen'),
                                    ('5700', 'state', 6), ('5950', 'state', 6)):
            broken = synthetic_moses_evidence()
            broken['frames'][frame][field] = value
            with self.subTest(frame=frame, field=field), self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
                validate_scenario(broken, 5)
        for frame, field, value in (('3750', 'third_link', 1), ('3900', 'third_link', 255),
                                    ('3900', 'third_descriptor', 0), ('3900', 'third_x', 0),
                                    ('3900', 'third_y', 144), ('4300', 'third_link', 255),
                                    ('4300', 'third_descriptor', 0), ('4300', 'third_x', 0),
                                    ('4300', 'third_y', 144), ('4600', 'third_link', 255),
                                    ('4600', 'third_descriptor', 0), ('4600', 'third_x', 0),
                                    ('4600', 'third_y', 144), ('4900', 'third_link', 255),
                                    ('4900', 'third_descriptor', 0), ('4900', 'third_x', 0),
                                    ('4900', 'third_y', 144), ('5200', 'third_link', 255),
                                    ('5200', 'third_descriptor', 0), ('5200', 'third_x', 0),
                                    ('5200', 'third_y', 144), ('5550', 'third_link', 255),
                                    ('5550', 'third_descriptor', 0), ('5550', 'third_x', 0),
                                    ('5550', 'third_y', 144), ('5700', 'third_link', 1),
                                    ('5700', 'third_descriptor', 0), ('5880', 'third_link', 1),
                                    ('5950', 'third_link', 255), ('5950', 'third_x', 0),
                                    ('6000', 'third_descriptor', 0), ('6000', 'third_y', 144),
                                    ('6040', 'third_link', 255), ('6100', 'third_link', 255),
                                    ('6260', 'third_link', 255), ('6340', 'third_link', 255)):
            broken = synthetic_moses_evidence()
            broken['slots'][frame][field] = value
            with self.subTest(frame=frame, field=field), self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
                validate_scenario(broken, 5)

    def test_moses_third_level_requires_movement_while_carrying(self):
        evidence = synthetic_moses_evidence()
        evidence['slots']['6100']['player_x'] = evidence['slots']['6000']['player_x']
        evidence['slots']['6100']['third_x'] = evidence['slots']['6100']['player_x']
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(evidence, 5)

    def test_moses_third_level_requires_rightward_and_upward_progress(self):
        evidence = synthetic_moses_evidence()
        evidence['slots']['6340']['player_x'] = evidence['slots']['6100']['player_x']
        evidence['slots']['6340']['third_x'] = evidence['slots']['6340']['player_x']
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(evidence, 5)
        evidence = synthetic_moses_evidence()
        evidence['slots']['6340']['player_y'] = evidence['slots']['6100']['player_y']
        with self.assertRaisesRegex(ValueError, 'pickup, carry and recovery'):
            validate_scenario(evidence, 5)

    def test_difference_summary_handles_missing_fields_and_limits(self):
        self.assertEqual(evidence_difference_paths({'a': {'x': 1}, 'b': [1, 2]},
                                                   {'a': {'x': 2, 'y': 3}, 'b': [2, 3]}, limit=2),
                         ['/a/x', '/a/y'])
        with self.assertRaises(ValueError):
            evidence_difference_paths({}, {}, limit=0)

    def test_failed_comparison_retains_both_sides_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference = {'frames': {'240': {'state': 0}}}
            candidate = {'frames': {'240': {'state': 1}}}
            frames = {240: PNG_SIGNATURE + b'synthetic'}
            ref_events = {'mapper': b'original', 'apu': b'audio', 'oam_dma': b'dma'}
            candidate_events = {**ref_events, 'mapper': b'different'}
            out = retain_runtime_failure(Path(tmp), 'moses', 'different evidence',
                                         {'source_sha256': 'test'}, reference, candidate,
                                         frames, frames, ref_events, candidate_events)
            saved = json.loads((out / 'comparison.json').read_text())
            self.assertEqual(saved['reference'], reference)
            self.assertEqual(saved['build'], candidate)
            self.assertEqual(saved['reason'], 'different evidence')
            self.assertEqual(saved['different_evidence_paths'], ['/frames/240/state'])
            self.assertEqual(saved['different_event_streams'], ['mapper'])
            self.assertEqual(saved['different_screenshots'], [])
            self.assertEqual((out / 'reference-240.png').read_bytes(), frames[240])
            self.assertEqual(zlib.decompress((out / 'build-mapper.txt.zlib').read_bytes()), b'different')
            with self.assertRaisesRegex(ValueError, 'invalid runtime failure scenario'):
                retain_runtime_failure(Path(tmp), '../unsafe', '', {}, {}, {}, {}, {}, {}, {})

    def test_inventory_must_open_read_both_tables_and_return(self):
        evidence, _, _ = parse_output(synthetic_output(inventory=True))
        validate_scenario(evidence, 1, inventory=True)
        for field in ('inventory_list_index_zero', 'inventory_template_index_zero'):
            broken, _, _ = parse_output(synthetic_output(inventory=True))
            broken[field] = 0
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'inventory opening'):
                validate_scenario(broken, 1, inventory=True)
        evidence['frames']['2800']['state'] = 16
        with self.assertRaisesRegex(ValueError, 'expected adventure'):
            validate_scenario(evidence, 1, inventory=True)


if __name__ == '__main__':
    unittest.main()
