"""Runtime extent accounting uses synthetic banks and trace data only."""

import unittest
from unittest.mock import patch

from tools.runtime_extents import coverage, validate_identity
from tools.script_entries import BANK_SIZE
from tools.trace_runtime_extents import capture, capture_script


def fixture():
    bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
    bank0[0x10] = bank1[0x10] = 1
    bank1[0x20:0x2a] = bytes([0, 0xff, 0x12, 0x34, 0, 0, 0, 0, 0, 0])
    bank0[0x20:0x2a] = bytes([0x12, 0x34, 0x56, 0, 0, 0, 0, 0, 0, 0])
    trace = {'inline_summary': [2, 0, 0, 0],
             'results': {'code': {'08011': 2},
                         'scripts': {'0010:01': 3, '8010:FE': 2},
                         'records': {'0020:01:00': 4, '8020:01:FF': 1},
                         'inline': {'95:08011': 4, 'B1:00030': 4}}}
    gaps = {BANK_SIZE + 0x11, BANK_SIZE + 0x23}
    return bank0, bank1, bytes([1, 3]), gaps, trace


class RuntimeExtentTests(unittest.TestCase):
    def test_capture_selects_roof_route_and_rejects_ambiguous_stop(self):
        script = capture_script('before\n  emu.stop(0)\nafter', 'PROBE\n', 'RESULT\n')
        self.assertTrue(script.startswith('local SCENARIO=4\n'))
        self.assertIn('RESULT\n  emu.stop(0)', script)
        for invalid in ('no stop', '  emu.stop(0)\n  emu.stop(0)'):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, 'stop marker'):
                capture_script(invalid, '', '')

    def test_command_operands_and_mode_selected_record_fields(self):
        b0, b1, lengths, gaps, trace = fixture()
        result = coverage(bytes(b0), bytes(b1), lengths, gaps, trace)
        self.assertEqual(result['script_pointer_bank_pairs'], 2)
        self.assertEqual(result['script_fetches'], 5)
        self.assertEqual(result['script_physical_bytes'], 6)
        self.assertEqual(result['script_local_spans'], [{'start': BANK_SIZE + 0x11, 'size': 1}])
        self.assertEqual(result['record_pointer_bank_modes'], 2)
        self.assertEqual(result['record_used_physical_bytes'], 6)
        self.assertEqual(result['record_local_spans'], [{'start': BANK_SIZE + 0x23, 'size': 1}])
        self.assertEqual(result['native_gap_instruction_executions'], 2)
        self.assertEqual(result['inline_fetches'], 2)
        self.assertEqual(result['inline_physical_bytes'], 2)
        self.assertEqual(result['inline_local_spans'], [{'start': BANK_SIZE + 0x11, 'size': 1}])

    def test_mapper_bank_and_sentinel_skip_are_not_counted_as_local_reads(self):
        b0, b1, lengths, gaps, trace = fixture()
        trace['results']['scripts'] = {'0010:00': 1}
        trace['results']['records'] = {'0020:01:FF': 1}
        trace['results']['code'] = {}
        result = coverage(bytes(b0), bytes(b1), lengths, gaps, trace)
        self.assertEqual(result['script_local_bytes'], 0)
        self.assertEqual(result['record_used_physical_bytes'], 1)
        self.assertEqual(result['record_local_bytes'], 0)

    def test_inline_bytes_deduplicate_handlers_and_report_non_prg_reads(self):
        b0, b1, lengths, gaps, trace = fixture()
        trace['results']['inline'] = {'95:08011': 4, 'B1:08011': 3}
        trace['inline_summary'] = [2, 0, 1, 0]
        result = coverage(bytes(b0), bytes(b1), lengths, gaps, trace)
        self.assertEqual(result['inline_physical_bytes'], 1)
        self.assertEqual(result['inline_local_bytes'], 1)
        self.assertEqual(result['inline_non_prg_reads'], 1)

    def test_malformed_trace_and_invalid_extents_fail_closed(self):
        for change in ('missing', 'count', 'opcode', 'script_crossing', 'record_crossing', 'code_outside_gap',
                       'inline_pending', 'inline_mismatch', 'inline_address'):
            b0, b1, lengths, gaps, trace = fixture()
            if change == 'missing':
                del trace['results']['records']
            elif change == 'count':
                trace['results']['scripts']['0010:01'] = True
            elif change == 'opcode':
                b1[0x10] = 255
            elif change == 'script_crossing':
                trace['results']['scripts'] = {'7FFF:01': 1}
                b1[-1] = 1
            elif change == 'record_crossing':
                trace['results']['records'] = {'7FF8:01:00': 1}
            elif change == 'code_outside_gap':
                trace['results']['code'] = {'00000': 1}
            elif change == 'inline_pending':
                trace['inline_summary'][3] = 1
            elif change == 'inline_mismatch':
                trace['inline_summary'][0] = 3
            else:
                trace['results']['inline'] = {'95:10000': 8}
            with self.subTest(change=change), self.assertRaises(ValueError):
                coverage(bytes(b0), bytes(b1), lengths, gaps, trace)

    def test_trace_identity_requires_each_current_input(self):
        expected = {'reference_sha256': 'reference', 'source_sha256': 'source',
                    'source_map_sha256': 'map', 'build_proof_sha256': 'proof',
                    'collector_sha256': 'collector', 'runtime_input_sha256': {'lua': 'runtime'},
                    'emulator_core_sha256': 'emulator'}
        validate_identity(dict(expected), expected)
        for key in expected:
            stale = dict(expected)
            stale[key] = None
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'trace identity'):
                validate_identity(stale, expected)

    def test_capture_rejects_another_target_before_reading_inputs(self):
        with patch.dict('os.environ', {'BADP_TARGET': 'us-v1.4'}):
            with self.assertRaisesRegex(ValueError, 'us-v1.5 only'):
                capture()


if __name__ == '__main__':
    unittest.main()
