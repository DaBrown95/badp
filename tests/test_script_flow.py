"""Conservative script-flow tracing on synthetic banks only."""
import unittest

from tools.script_entries import BANK_SIZE
from tools.script_flow import scan_lookup_table, walk


def fixture():
    return bytearray(BANK_SIZE), bytearray(BANK_SIZE), bytearray([1] * 197)


def by_pointer(result):
    return {node['encoded_pointer']: node for node in result['nodes']}


class ScriptFlowTests(unittest.TestCase):
    def test_jump_cycle_and_unknown_handler_stop(self):
        b0, b1, lengths = fixture()
        lengths[0x09] = 2
        lengths[0x04] = 3
        b1[0x10:0x15] = bytes([0x09, 0x55, 0x04, 0x10, 0])
        b1[0x20] = 0x80
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x20])
        nodes = by_pointer(result)
        self.assertEqual(set(nodes), {'0x0010', '0x0012', '0x0020'})
        self.assertEqual(nodes['0x0012']['successors'],
                         [{'kind': 'target', 'encoded_pointer': '0x0010'}])
        self.assertEqual(nodes['0x0020']['status'], 'unreviewed_or_dynamic_handler')
        self.assertEqual(nodes['0x0020']['successors'], [])
        self.assertFalse(result['unprocessed'])

    def test_conditional_and_yield_edges_remain_candidates(self):
        b0, b1, lengths = fixture()
        lengths[0x22] = 4
        lengths[0x07] = 2
        b1[0x10:0x14] = bytes([0x22, 0x20, 0, 9])
        b1[0x14:0x16] = bytes([0x07, 3])
        b1[0x16] = b1[0x20] = 0x80
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_conditional')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0020'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0014']['successors'],
                         [{'kind': 'possible_resume', 'encoded_pointer': '0x0016'}])

    def test_dynamic_handlers_stop_and_possible_yield_remains_uncertain(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x12] = bytes([0x2d, 0x80])
        for offset, opcode in ((0x20, 0x00), (0x30, 0x19), (0x40, 0x17)):
            b1[offset] = opcode
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths),
                                [0x10, 0x20, 0x30, 0x40]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_possible_yield')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next_or_possible_resume', 'encoded_pointer': '0x0011'}])
        for pointer in ('0x0020', '0x0030', '0x0040'):
            self.assertEqual(nodes[pointer]['status'], 'unreviewed_or_dynamic_handler')
            self.assertEqual(nodes[pointer]['successors'], [])

    def test_slot_comparisons_branch_and_bounds_update_falls_through(self):
        b0, b1, lengths = fixture()
        lengths[0x93] = lengths[0x94] = 4
        lengths[0xa9] = 3
        b1[0x10:0x14] = bytes([0x93, 0x30, 0, 5])
        b1[0x14:0x18] = bytes([0x94, 0x40, 0, 6])
        b1[0x18:0x1b] = bytes([0xa9, 1, 2])
        b1[0x1b] = b1[0x30] = b1[0x40] = 0x80
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0014']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0040'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0018'}])
        self.assertEqual(nodes['0x0018']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x001b'}])

    def test_record_mode_and_slot_action_control_successors(self):
        b0, b1, lengths = fixture()
        lengths[0x63], lengths[0x1e] = 3, 2
        b1[0x10:0x15] = bytes([0x63, 9, 2, 0x1e, 2])
        b1[0x15] = 0x80
        b1[0x20:0x23] = bytes([0x63, 9, 0])
        b1[0x30:0x32] = bytes([0x1e, 0])
        b1[0x40:0x42] = bytes([0x1e, 1])
        b1[0x50:0x54] = bytes([0x63, 3, 0xff, 0x80])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths),
                                [0x10, 0x20, 0x30, 0x40, 0x50]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_next', 'encoded_pointer': '0x0013'}])
        self.assertEqual(nodes['0x0013']['successors'], [
            {'kind': 'possible_resume', 'encoded_pointer': '0x0015'}])
        self.assertEqual(nodes['0x0020']['status'], 'unreviewed_or_dynamic_handler')
        self.assertEqual(nodes['0x0050']['successors'], [
            {'kind': 'possible_next', 'encoded_pointer': '0x0053'}])
        for pointer in ('0x0030', '0x0040'):
            self.assertEqual(nodes[pointer]['status'], 'reviewed_yield_release_slot')
            self.assertEqual(nodes[pointer]['successors'], [])

    def test_inline_lookup_matches_and_two_byte_terminator(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x1c] = bytes([0x95, 0x20, 0, 1, 2, 0x30, 0, 3, 4, 0, 0, 0x80])
        b1[0x20] = b1[0x30] = 0x80
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x10])
        nodes = by_pointer(result)
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_inline_lookup_terminated')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_table_match', 'encoded_pointer': '0x0020'},
            {'kind': 'possible_table_match', 'encoded_pointer': '0x0030'},
            {'kind': 'possible_no_match', 'encoded_pointer': '0x001b'}])
        self.assertEqual(nodes['0x0010']['lookup_records'][-1]['size'], 2)
        self.assertEqual(result['overlapping_physical_bytes'], 0)

    def test_inline_lookup_stops_at_limit_and_bank_boundary(self):
        b0, b1, _ = fixture()
        b1[0x10:0x18] = bytes([0x20, 0, 1, 2, 0x30, 0, 3, 4])
        limited = scan_lookup_table((bytes(b0), bytes(b1)), 0x10, limit=1)
        self.assertEqual(limited['status'], 'limit')
        self.assertEqual(len(limited['records']), 1)
        crossing = scan_lookup_table((bytes(b0), bytes(b1)), 0x7ffd)
        self.assertEqual(crossing['status'], 'crosses_bank_boundary')
        self.assertNotIn('continuation', crossing)

    def test_busy_state_may_retry_and_spatial_test_may_branch(self):
        b0, b1, lengths = fixture()
        lengths[0xab], lengths[0x7b] = 3, 5
        b1[0x10:0x18] = bytes([0xab, 1, 2, 0x7b, 0x30, 0, 4, 5])
        b1[0x18] = b1[0x30] = 0x80
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_retry', 'encoded_pointer': '0x0010'},
            {'kind': 'possible_next', 'encoded_pointer': '0x0013'}])
        self.assertEqual(nodes['0x0013']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0018'}])

    def test_encoded_bank_transition(self):
        b0, b1, lengths = fixture()
        b1[-1] = 0x21
        b0[0] = 0x80
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x7fff]))
        self.assertEqual(nodes['0x7fff']['location']['bank'], 1)
        self.assertEqual(nodes['0x8000']['location']['bank'], 0)

    def test_overlaps_are_flagged_by_physical_byte(self):
        b0, b1, lengths = fixture()
        lengths[0x09] = 2
        b1[0x10:0x14] = bytes([9, 9, 0x80, 0x80])
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x11])
        nodes = by_pointer(result)
        self.assertEqual(result['overlapping_physical_bytes'], 2)
        self.assertEqual(nodes['0x0010']['overlaps'], ['0x0011'])
        self.assertEqual(nodes['0x0011']['overlaps'], ['0x0010', '0x0012'])

    def test_invalid_length_opcode_and_bounds_stop(self):
        b0, b1, lengths = fixture()
        lengths[0x04] = 2
        lengths[0x09] = 0
        lengths[0x0b] = 2
        b1[0x10] = 4
        b1[0x20] = 9
        b1[0x30] = 250
        b1[-1] = 0x0b
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths),
                                [0x10, 0x20, 0x30, 0x7fff]))
        self.assertEqual(nodes['0x0010']['status'], 'missing_pointer_operands')
        self.assertEqual(nodes['0x0020']['status'], 'zero_length')
        self.assertEqual(nodes['0x0030']['status'], 'opcode_outside_length_table')
        self.assertEqual(nodes['0x7fff']['status'], 'crosses_bank_boundary')

    def test_budget_and_bad_inputs_fail_closed(self):
        b0, b1, lengths = fixture()
        b1[:3] = bytes([0x21, 0x21, 0x21])
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0], limit=1)
        self.assertEqual(result['unprocessed'], ['0x0001'])
        for args in ((b'', bytes(b1), bytes(lengths), [0], 1),
                     (bytes(b0), bytes(b1), b'', [0], 1),
                     (bytes(b0), bytes(b1), bytes(lengths), [0], 0),
                     (bytes(b0), bytes(b1), bytes(lengths), [0x10000], 1)):
            with self.subTest(args=(len(args[0]), args[-2:])), self.assertRaises(ValueError):
                walk(*args)


if __name__ == '__main__':
    unittest.main()
