"""Conservative script-flow tracing on synthetic banks only."""
import unittest

from tools.script_entries import BANK_SIZE
from tools.script_flow import walk


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
        for offset, opcode in ((0x20, 0x00), (0x30, 0x19), (0x40, 0x95)):
            b1[offset] = opcode
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths),
                                [0x10, 0x20, 0x30, 0x40]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_possible_yield')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next_or_possible_resume', 'encoded_pointer': '0x0011'}])
        for pointer in ('0x0020', '0x0030', '0x0040'):
            self.assertEqual(nodes[pointer]['status'], 'unreviewed_or_dynamic_handler')
            self.assertEqual(nodes[pointer]['successors'], [])

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
