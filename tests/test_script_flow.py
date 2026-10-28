"""Conservative script-flow tracing on synthetic banks only."""
import unittest

from tools.script_entries import BANK_SIZE
from tools.script_flow import scan_lookup_table, walk


def fixture():
    return bytearray(BANK_SIZE), bytearray(BANK_SIZE), bytearray([1] * 197)


def by_pointer(result):
    return {node['encoded_pointer']: node for node in result['nodes']}


class ScriptFlowTests(unittest.TestCase):
    def test_slot_field_and_stack_buffer_normal_return_paths(self):
        b0, b1, lengths = fixture()
        lengths[0x76] = lengths[0x8a] = lengths[0x84] = 2
        b1[0x10:0x18] = bytes([0x76, 3, 0x8a, 0xff, 0x84, 7, 0x79, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0012'}])
        self.assertEqual(nodes['0x0012']['status'], 'reviewed_possible_stack_buffer_return')
        self.assertEqual(nodes['0x0012']['successors'], [
            {'kind': 'possible_normal_return', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0014']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0016'}])
        self.assertEqual(nodes['0x0016']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0017'}])

    def test_shared_swap_and_related_slot_handlers_preserve_command_boundaries(self):
        b0, b1, lengths = fixture()
        lengths[0x8d] = lengths[0x8e] = lengths[0xa4] = lengths[0xbd] = 2
        lengths[0xbc] = 3
        b1[0x10:0x1c] = bytes([0x8d, 0x51, 0x8e, 0x42, 0xa4, 1,
                                0xbc, 2, 3, 0xbd, 4, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        for start, end in ((0x10, 0x12), (0x12, 0x14), (0x14, 0x16),
                           (0x16, 0x19), (0x19, 0x1b)):
            self.assertEqual(nodes[f'0x{start:04x}']['successors'], [
                {'kind': 'next', 'encoded_pointer': f'0x{end:04x}'}])
        self.assertEqual(nodes['0x001b']['status'], 'unreviewed_or_dynamic_handler')

    def test_jump_cycle_and_unknown_handler_stop(self):
        b0, b1, lengths = fixture()
        lengths[0x09] = 2
        lengths[0x04] = 3
        b1[0x10:0x15] = bytes([0x09, 0x55, 0x04, 0x10, 0])
        b1[0x20] = 0x16
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
        b1[0x16] = b1[0x20] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_conditional')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0020'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0014']['successors'],
                         [{'kind': 'possible_resume', 'encoded_pointer': '0x0016'}])

    def test_reviewed_slot_updates_and_audio_voice_branch(self):
        b0, b1, lengths = fixture()
        lengths[0x65] = lengths[0xb9] = lengths[0xba] = 3
        lengths[0xb2] = 2
        lengths[0x77] = 7
        b1[0x10:0x1d] = bytes([0x65, 1, 2, 0xa2, 0xad, 0xb2, 3,
                                0xb8, 0xb9, 4, 5, 0xba, 6])
        b1[0x1d:0x26] = bytes([7, 0x11, 0x77, 0x30, 0, 0, 1, 2, 3])
        b1[0x26] = b1[0x30] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        for start, end in ((0x10, 0x13), (0x13, 0x14),
                           (0x15, 0x17), (0x17, 0x18), (0x18, 0x1b), (0x1b, 0x1e)):
            self.assertEqual(nodes[f'0x{start:04x}']['successors'], [
                {'kind': 'next', 'encoded_pointer': f'0x{end:04x}'}])
        self.assertEqual(nodes['0x0014']['status'], 'reviewed_possible_indexed_stack_write_return')
        self.assertEqual(nodes['0x0014']['successors'], [
            {'kind': 'possible_normal_return', 'encoded_pointer': '0x0015'}])
        self.assertEqual(nodes['0x001e']['status'], 'reviewed_possible_yield')
        self.assertEqual(nodes['0x001f']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0026'}])

    def test_saved_script_pointer_can_leave_current_pointer_unchanged(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x12] = bytes([0x17, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_saved_pointer_or_next')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_next_without_saved_pointer', 'encoded_pointer': '0x0011'}])
        self.assertEqual(nodes['0x0011']['status'], 'unreviewed_or_dynamic_handler')

    def test_state_table_selection_returns_to_following_command(self):
        b0, b1, lengths = fixture()
        lengths[0xaf] = 2
        b1[0x10:0x13] = bytes([0xaf, 0x4d, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0012'}])
        self.assertEqual(nodes['0x0012']['status'], 'unreviewed_or_dynamic_handler')

    def test_relative_slot_and_indexed_state_only_offer_possible_resumes(self):
        b0, b1, lengths = fixture()
        lengths[0x67], lengths[0x89] = 6, 3
        b1[0x10:0x1a] = bytes([0x67, 1, 2, 3, 4, 5, 0x89, 0x20, 0, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_resume', 'encoded_pointer': '0x0016'}])
        self.assertEqual(nodes['0x0016']['status'], 'reviewed_possible_relative_resume')
        self.assertEqual(nodes['0x0016']['successors'], [
            {'kind': 'possible_relative_resume', 'encoded_pointer': '0x0019'}])

    def test_dynamic_handlers_stop_and_possible_yield_remains_uncertain(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x12] = bytes([0x2d, 0x16])
        for offset, opcode in ((0x20, 0x00), (0x30, 0x16)):
            b1[offset] = opcode
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths),
                                [0x10, 0x20, 0x30]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_possible_yield')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next_or_possible_resume', 'encoded_pointer': '0x0011'}])
        for pointer in ('0x0020', '0x0030'):
            self.assertEqual(nodes[pointer]['status'], 'unreviewed_or_dynamic_handler')
            self.assertEqual(nodes[pointer]['successors'], [])

    def test_audio_restart_and_empty_handler_fall_through(self):
        b0, b1, lengths = fixture()
        lengths[0x18], lengths[0x9d] = 1, 2
        b1[0x10:0x14] = bytes([0x18, 0x9d, 0x32, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0011'}])
        self.assertEqual(nodes['0x0011']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0013'}])
        self.assertEqual(nodes['0x0013']['status'], 'unreviewed_or_dynamic_handler')

    def test_bank_configuration_and_disabled_slot_can_return_normally(self):
        b0, b1, lengths = fixture()
        lengths[0xaa], lengths[0xbe] = 2, 1
        b1[0x10:0x14] = bytes([0xaa, 0, 0xbe, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0012'}])
        self.assertEqual(nodes['0x0012']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0013'}])

    def test_state_save_continuation_requires_possible_restoration(self):
        b0, b1, lengths = fixture()
        lengths[0x98], lengths[0x0f], lengths[0x99] = 2, 2, 1
        b1[0x10:0x13] = bytes([0x98, 0x12, 0x16])
        b1[0x20:0x22] = bytes([0x0f, 1])
        b1[0x30] = 0x99
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x20, 0x30]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_possible_state_restore_resume')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_resume_after_restore', 'encoded_pointer': '0x0012'}])
        self.assertEqual(nodes['0x0020']['successors'], [])
        self.assertEqual(nodes['0x0030']['successors'], [])

    def test_slot_comparisons_branch_and_bounds_update_falls_through(self):
        b0, b1, lengths = fixture()
        lengths[0x93] = lengths[0x94] = 4
        lengths[0xa9] = 3
        b1[0x10:0x14] = bytes([0x93, 0x30, 0, 5])
        b1[0x14:0x18] = bytes([0x94, 0x40, 0, 6])
        b1[0x18:0x1b] = bytes([0xa9, 1, 2])
        b1[0x1b] = b1[0x30] = b1[0x40] = 0x16
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
        b1[0x15] = 0x16
        b1[0x20:0x23] = bytes([0x63, 9, 0])
        b1[0x30:0x32] = bytes([0x1e, 0])
        b1[0x40:0x42] = bytes([0x1e, 1])
        b1[0x50:0x54] = bytes([0x63, 3, 0xff, 0x16])
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
        b1[0x10:0x1c] = bytes([0x95, 0x20, 0, 1, 2, 0x30, 0, 3, 4, 0, 0, 0x16])
        b1[0x20] = b1[0x30] = 0x16
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

    def test_inline_remap_is_data_and_does_not_branch_to_values(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x18] = bytes([0xb1, 0x20, 0, 3, 4, 0, 0, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_inline_remap_terminated')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0017'}])
        self.assertEqual(nodes['0x0010']['lookup_records'][0]['value'], 0x20)
        self.assertEqual(nodes['0x0010']['lookup_records'][0]['replacement'], [3, 4])
        self.assertNotIn('0x0020', nodes)

    def test_busy_state_may_retry_and_spatial_test_may_branch(self):
        b0, b1, lengths = fixture()
        lengths[0xab], lengths[0x7b] = 3, 5
        b1[0x10:0x18] = bytes([0xab, 1, 2, 0x7b, 0x30, 0, 4, 5])
        b1[0x18] = b1[0x30] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_retry', 'encoded_pointer': '0x0010'},
            {'kind': 'possible_next', 'encoded_pointer': '0x0013'}])
        self.assertEqual(nodes['0x0013']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0018'}])

    def test_only_reviewed_indirect_addresses_and_native_target_continue(self):
        b0, b1, lengths = fixture()
        lengths[0x91] = lengths[0x9b] = 3
        b1[0x10:0x19] = bytes([0x91, 0x55, 0, 0x91, 0x56, 0, 0x9b, 0xe9, 0x3e])
        b1[0x19:0x1c] = bytes([0x9b, 0x1b, 0xb5])
        b1[0x1c] = 0x16
        b1[0x30:0x33] = bytes([0x91, 0x53, 0])
        b1[0x40:0x43] = bytes([0x9b, 0xea, 0x3e])
        b1[0x50:0x54] = bytes([0x91, 0xe2, 0x05, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x30, 0x40, 0x50]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_text_pointer_write')
        self.assertEqual(nodes['0x0013']['status'], 'reviewed_text_pointer_write')
        self.assertEqual(nodes['0x0016']['status'], 'reviewed_packed_text_native_call')
        self.assertEqual(nodes['0x0019']['status'], 'reviewed_palette_fade_native_call')
        self.assertIn('0x001c', nodes)
        self.assertEqual(nodes['0x0030']['status'], 'unreviewed_or_dynamic_handler')
        self.assertEqual(nodes['0x0040']['status'], 'unreviewed_or_dynamic_handler')
        self.assertEqual(nodes['0x0050']['status'], 'reviewed_slot_field_write')
        self.assertEqual(nodes['0x0050']['successors'], [
            {'kind': 'possible_next', 'encoded_pointer': '0x0053'}])

    def test_selector_branch_uses_later_target_and_short_variant_stops(self):
        b0, b1, lengths = fixture()
        lengths[0x58], lengths[0x57] = 4, 3
        b1[0x10:0x14] = bytes([0x58, 0x32, 0x30, 0])
        b1[0x14] = b1[0x30] = 0x16
        b1[0x40:0x43] = bytes([0x57, 0x32, 0x30])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x40]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0040']['status'], 'unreviewed_or_dynamic_handler')

    def test_main_state_change_stops_before_following_data(self):
        b0, b1, lengths = fixture()
        lengths[0x0f] = 2
        b1[0x10:0x12] = bytes([0x99, 0x3e])
        b1[0x30:0x33] = bytes([0x0f, 0x10, 0x69])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10, 0x30]))
        self.assertEqual(nodes['0x0010']['status'], 'reviewed_main_state_change')
        self.assertEqual(nodes['0x0010']['successors'], [])
        self.assertNotIn('0x0011', nodes)
        self.assertEqual(nodes['0x0030']['status'], 'reviewed_main_state_change')
        self.assertEqual(nodes['0x0030']['successors'], [])
        self.assertNotIn('0x0032', nodes)

    def test_offset_probe_branches_and_indexed_voice_restores_pointer(self):
        b0, b1, lengths = fixture()
        lengths[0x66], lengths[0xb3] = 4, 3
        b1[0x10:0x17] = bytes([0x66, 0x30, 0, 6, 0xb3, 0x34, 0x12])
        b1[0x17] = b1[0x30] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0014'}])
        self.assertEqual(nodes['0x0014']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0017'}])

    def test_state_gate_branches_and_slot_initialization_may_continue(self):
        b0, b1, lengths = fixture()
        lengths[0x3d], lengths[0x1f] = 3, 5
        b1[0x10:0x18] = bytes([0x3d, 0x30, 0, 0x1f, 1, 2, 3, 4])
        b1[0x18] = b1[0x30] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'target', 'encoded_pointer': '0x0030'},
            {'kind': 'fallthrough', 'encoded_pointer': '0x0013'}])
        self.assertEqual(nodes['0x0013']['successors'], [
            {'kind': 'next', 'encoded_pointer': '0x0018'}])

    def test_slot_wait_and_fixed_mode_record_load(self):
        b0, b1, lengths = fixture()
        lengths[0xc4] = 2
        b1[0x10:0x14] = bytes([0x19, 0xc4, 2, 0x16])
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'possible_retry', 'encoded_pointer': '0x0010'},
            {'kind': 'possible_next', 'encoded_pointer': '0x0011'}])
        self.assertEqual(nodes['0x0011']['status'], 'reviewed_nonzero_mode_record_load')
        self.assertEqual(nodes['0x0011']['successors'], [
            {'kind': 'possible_next', 'encoded_pointer': '0x0013'}])

    def test_indexed_jump_requires_explicit_bounds_and_tracks_table_bytes(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x15] = bytes([0x44, 0x20, 0, 0x30, 0])
        b1[0x20] = b1[0x30] = 0x16
        unbounded = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x10]))
        self.assertEqual(unbounded['0x0010']['status'], 'unreviewed_or_dynamic_handler')
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x10], indexed_jumps={0x10: 2})
        nodes = by_pointer(result)
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'bounded_index_target', 'encoded_pointer': '0x0020'},
            {'kind': 'bounded_index_target', 'encoded_pointer': '0x0030'}])
        self.assertEqual(len(nodes['0x0010']['jump_records']), 2)
        self.assertEqual(result['overlapping_physical_bytes'], 0)
        with self.assertRaisesRegex(ValueError, 'entry count'):
            walk(bytes(b0), bytes(b1), bytes(lengths), [0x10], indexed_jumps={0x10: 129})

    def test_indexed_jump_stops_at_a_bank_boundary(self):
        b0, b1, lengths = fixture()
        b1[0x7ffe] = 0x44
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x7ffe],
                      indexed_jumps={0x7ffe: 1})
        node = by_pointer(result)['0x7ffe']
        self.assertEqual(node['status'], 'indexed_jump_crosses_bank_boundary')
        self.assertEqual(node['successors'], [])

    def test_observed_indices_are_followed_without_claiming_a_bound(self):
        b0, b1, lengths = fixture()
        b1[0x10:0x17] = bytes([0x44, 0x20, 0, 0x30, 0, 0x40, 0])
        b1[0x20] = b1[0x30] = b1[0x40] = 0x16
        result = walk(bytes(b0), bytes(b1), bytes(lengths), [0x10],
                      indexed_jumps={0x10: (0, 2)})
        nodes = by_pointer(result)
        self.assertEqual(nodes['0x0010']['status'], 'observed_indexed_jump_incomplete')
        self.assertEqual(nodes['0x0010']['successors'], [
            {'kind': 'observed_index_target', 'encoded_pointer': '0x0020'},
            {'kind': 'observed_index_target', 'encoded_pointer': '0x0040'}])
        self.assertEqual([record['index'] for record in nodes['0x0010']['jump_records']], [0, 2])
        self.assertNotIn('0x0030', nodes)
        for entries in ((), (0, 0), (128,), (-1,), (True,), [0, 1]):
            with self.subTest(entries=entries), self.assertRaisesRegex(ValueError, 'entry count'):
                walk(bytes(b0), bytes(b1), bytes(lengths), [0x10], indexed_jumps={0x10: entries})

    def test_encoded_bank_transition(self):
        b0, b1, lengths = fixture()
        b1[-1] = 0x21
        b0[0] = 0x16
        nodes = by_pointer(walk(bytes(b0), bytes(b1), bytes(lengths), [0x7fff]))
        self.assertEqual(nodes['0x7fff']['location']['bank'], 1)
        self.assertEqual(nodes['0x8000']['location']['bank'], 0)

    def test_overlaps_are_flagged_by_physical_byte(self):
        b0, b1, lengths = fixture()
        lengths[0x09] = 2
        b1[0x10:0x14] = bytes([9, 9, 0x16, 0x16])
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
