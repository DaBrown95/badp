"""Slot-record access analysis uses synthetic banks only."""
import unittest

from tools.script_entries import BANK_SIZE
from tools.slot_record_flow import record_script_overlaps, record_used_offsets, resolve_access, trace


def fixture():
    return bytearray(BANK_SIZE), bytearray(BANK_SIZE), bytearray([1] * 197)


class SlotRecordFlowTests(unittest.TestCase):
    def test_add_subtract_and_compact_flag(self):
        b0, b1, _ = fixture()
        b1[0x120:0x12a] = bytes([0x34, 0x81, 0x78, 0x56, 0x40, 1, 2, 3, 4, 5])
        b1[0x100:0x10a] = bytes([0x22, 0x82, 0x33, 0, 0, 0, 0, 0, 0, 0])
        plus = resolve_access(bytes(b0), bytes(b1), 0x110, 0x10, 0)
        minus = resolve_access(bytes(b0), bytes(b1), 0x110, 0x10, 0xff)
        self.assertEqual(plus['encoded_pointer'], '0x0120')
        self.assertEqual(plus['location']['bank'], 1)
        self.assertEqual(plus['fields']['encoded_script_pointer'], 0x5678)
        self.assertEqual(minus['encoded_pointer'], '0x0100')
        self.assertEqual(minus['fields']['sprite_pointer'], 0x8222)
        self.assertEqual(minus['negative_mode_flags'], 0x33)
        self.assertIsNone(plus['negative_mode_flags'])

    def test_crossing_fetch_and_invalid_parameters(self):
        b0, b1, _ = fixture()
        result = resolve_access(bytes(b0), bytes(b1), 0x7fff, 0, 0)
        self.assertEqual(result['status'], 'fetch_crosses_bank_boundary')
        self.assertNotIn('fields', result)
        for offset, mode in ((256, 0), (0, -1), (True, 0), (0, True)):
            with self.subTest(offset=offset, mode=mode), self.assertRaises(ValueError):
                resolve_access(bytes(b0), bytes(b1), 0x100, offset, mode)

    def test_zero_mode_installs_script_and_negative_mode_uses_same_base(self):
        b0, b1, lengths = fixture()
        lengths[0x00], lengths[0x63] = 2, 3
        b1[0x20:0x22] = bytes([0x00, 9])
        b1[0x30:0x34] = bytes([0x63, 3, 0xff, 0x16])
        b1[0x109:0x113] = bytes([0x34, 0x81, 0x30, 0, 0x40, 1, 2, 3, 4, 0x11])
        b1[0xfd:0x107] = bytes([0x22, 0x82, 0x33, 0, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(len(result['contexts']), 2)
        refs = {r['command']: r for r in result['references']}
        self.assertEqual(refs['0x0020']['encoded_pointer'], '0x0109')
        self.assertEqual(refs['0x0030']['encoded_pointer'], '0x00fd')
        self.assertEqual(refs['0x0030']['negative_mode_flags'], 0x33)
        self.assertFalse(result['unprocessed_contexts'])
        limited = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)], limit=1)
        self.assertEqual(limited['unprocessed_contexts'], [{'base': '0x0100', 'entry': '0x0030'}])

    def test_script_sentinel_can_resume_the_existing_pointer(self):
        b0, b1, lengths = fixture()
        lengths[0x00] = 2
        b1[0x20:0x23] = bytes([0, 0, 0x16])
        b1[0x100:0x10a] = bytes([0, 0x81, 0x30, 0xff, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(len(result['contexts']), 2)
        self.assertFalse(result['references'][0]['fields']['script_installable_in_zero_mode'])
        self.assertEqual(result['possible_retained_pointer_resumes'], [
            {'base': '0x0100', 'command': '0x0020', 'next_entry': '0x0022'}])
        with self.assertRaises(ValueError):
            trace(bytes(b0), bytes(b1), bytes(lengths), [], limit=0)

    def test_zero_mode_63_can_retain_pointer_after_sentinel(self):
        b0, b1, lengths = fixture()
        lengths[0x63] = 3
        b1[0x20:0x24] = bytes([0x63, 4, 0, 0x16])
        b1[0x104:0x10e] = bytes([0, 0xff, 0, 0xff, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(result['possible_retained_pointer_resumes'], [
            {'base': '0x0100', 'command': '0x0020', 'next_entry': '0x0023'}])
        limited = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)], limit=1)
        self.assertEqual(limited['unprocessed_contexts'], [
            {'base': '0x0100', 'entry': '0x0023'}])

    def test_direct_record_pointer_explores_unknown_mode_classes(self):
        b0, b1, lengths = fixture()
        lengths[0x16] = 3
        b1[0x20:0x24] = bytes([0x16, 0x40, 1, 0x17])
        b1[0x30] = 0x17
        b1[0x140:0x14a] = bytes([0, 0xff, 0x30, 0, 0, 0, 0, 0, 0, 0])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual({r['mode_class'] for r in result['references']},
                         {'zero', 'one', 'other_nonnegative', 'negative'})
        self.assertEqual({r['encoded_pointer'] for r in result['references']}, {'0x0140'})
        self.assertEqual({c['entry'] for c in result['contexts']}, {'0x0020', '0x0023', '0x0030'})
        self.assertEqual(result['possible_direct_pointer_resumes'][0]['next_entry'], '0x0023')

    def test_zero_direct_operand_uses_runtime_slot_pointer(self):
        b0, b1, lengths = fixture()
        lengths[0x16] = 3
        b1[0x20:0x24] = bytes([0x16, 0, 0, 0x17])
        result = trace(bytes(b0), bytes(b1), bytes(lengths), [(0x100, 0x20)])
        self.assertEqual(result['references'], [])
        self.assertEqual(result['dynamic_direct_pointers'][0]['next_entry'], '0x0023')
        self.assertEqual({c['entry'] for c in result['contexts']}, {'0x0020', '0x0023'})

    def test_merged_graph_reports_conflicting_context_decodes(self):
        b0, b1, lengths = fixture()
        lengths[0x09] = lengths[0x00] = 2
        b1[0x20:0x23] = bytes([0x09, 0x00, 0x11])
        result = trace(bytes(b0), bytes(b1), bytes(lengths),
                       [(0x100, 0x20), (0x120, 0x21)])
        self.assertTrue(all(c['overlapping_script_bytes'] == 0 for c in result['contexts']))
        self.assertEqual(result['merged_script_flow']['overlapping_physical_bytes'], 2)
        self.assertFalse(result['merged_script_flow']['unprocessed'])

    def test_record_script_overlap_ignores_fetched_but_unused_bytes(self):
        b0, b1, _ = fixture()
        b1[0x100:0x10a] = bytes([0x34, 0x81, 0x40, 0x55, 0x66, 1, 2, 3, 4, 5])
        ref = resolve_access(bytes(b0), bytes(b1), 0x100, 0, 0xff)
        ref.update({'base': '0x0100', 'command': '0x0020'})
        graph = {'nodes': [{'location': {'bank': 1, 'bank_offset': 0x102}, 'length': 2}]}
        result = record_script_overlaps([ref], graph)
        self.assertEqual(result['physical_bytes'], 1)
        self.assertEqual(result['references'][0]['locations'][0]['bank_offset'], 0x102)
        graph['nodes'][0]['location']['bank_offset'] = 0x103
        self.assertEqual(record_script_overlaps([ref], graph)['physical_bytes'], 0)

    def test_used_fields_respect_modes_and_sentinels(self):
        b0, b1, _ = fixture()
        b1[0x100:0x10a] = bytes([0x34, 0x81, 0x40, 0x55, 0x66, 1, 2, 3, 4, 5])
        for mode, expected in ((0, set(range(9))), (1, {0, 1, 4}),
                               (2, {0, 1, 4, 5, 6, 7, 8}), (0xff, {0, 1, 2})):
            with self.subTest(mode=mode):
                ref = resolve_access(bytes(b0), bytes(b1), 0x100, 0, mode)
                self.assertEqual(record_used_offsets(ref), expected)
        b1[0x101], b1[0x103] = 0xff, 0xff
        ref = resolve_access(bytes(b0), bytes(b1), 0x100, 0, 0)
        self.assertEqual(record_used_offsets(ref), {1, 3})
        self.assertEqual(record_used_offsets({'status': 'fetch_crosses_bank_boundary'}), set())


if __name__ == '__main__':
    unittest.main()
