"""Native control-flow inventory tests using synthetic source and ROM bytes."""
import unittest

from tools.native_control_flow import BANK_SIZE, inventory


def fixture():
    source = 'start:\n    bne start\n    jsr $8008\n    jmp ($1234)\n    rts\n'
    prg = bytearray(2 * BANK_SIZE)
    prg[:9] = bytes([0xd0, 0xfe, 0x20, 0x08, 0x80, 0x6c, 0x34, 0x12, 0x60])
    debug = '''file\tid=0,name="source/rom.s"
seg\tid=7,name="PRG0",start=0x8000,size=0x8000,ooffs=16
seg\tid=8,name="PRG1",start=0x8000,size=0x8000,ooffs=32784
span\tid=1,seg=7,start=0,size=2
span\tid=2,seg=7,start=2,size=3
span\tid=3,seg=7,start=5,size=3
span\tid=4,seg=7,start=8,size=1
line\tid=1,file=0,line=2,span=1
line\tid=2,file=0,line=3,span=2
line\tid=3,file=0,line=4,span=3
line\tid=4,file=0,line=5,span=4
'''
    regions = [{'bank': 0, 'cpu': '0x8000', 'size': 9, 'kind': 'code'},
               {'bank': 1, 'cpu': '0x8008', 'size': 1, 'kind': 'data'}]
    return debug, source, bytes(prg), regions


class NativeControlFlowTests(unittest.TestCase):
    def test_direct_target_banks_indirect_and_returns(self):
        result = inventory(*fixture())
        self.assertEqual(result['source_code_bytes'], 9)
        self.assertEqual(result['covered_code_bytes'], 9)
        self.assertEqual(result['direct_transfer_count'], 2)
        branch, call, jump, ret = result['transfers']
        self.assertEqual(branch['target_cpu'], '0x8000')
        self.assertEqual(branch['same_physical_bank']['ownership'], 'code')
        self.assertNotIn('other_physical_bank', branch)
        self.assertEqual(call['target_cpu'], '0x8008')
        self.assertEqual(call['same_physical_bank'], {'ownership': 'code', 'span_start': True})
        self.assertEqual(call['other_physical_bank']['ownership'], 'data')
        self.assertEqual(jump['target_kind'], 'indirect')
        self.assertEqual(jump['pointer'], '0x1234')
        self.assertEqual(ret['target_kind'], 'stack_or_interrupt')

    def test_local_and_non_span_boundary_are_not_credited(self):
        debug, source, prg, regions = fixture()
        changed = bytearray(prg)
        changed[3] = 1  # target is the second byte of the branch
        result = inventory(debug, source, bytes(changed), regions)
        self.assertEqual(len(result['same_bank_non_span_start_targets']), 1)
        changed[3] = 10  # outside reconstructed region
        result = inventory(debug, source, bytes(changed), regions)
        self.assertEqual(result['same_bank_non_code_targets'][0]['same_physical_bank']['ownership'], 'local')

    def test_additional_target_classification_preserves_bank_and_boundary(self):
        debug, source, prg, regions = fixture()
        result = inventory(debug, source, prg, regions,
                           extra_targets=((0, 0x8001), (0, 0x8008), (1, 0x8008), (0, 0)))
        self.assertEqual([item['ownership'] for item in result['extra_targets']],
                         ['code', 'code', 'data', 'outside_prg'])
        self.assertEqual([item['span_start'] for item in result['extra_targets']],
                         [False, True, False, False])
        with self.assertRaisesRegex(ValueError, 'duplicate extra target'):
            inventory(debug, source, prg, regions, extra_targets=((0, 0x8008), (0, 0x8008)))

    def test_invalid_debug_geometry_and_missing_coverage_are_rejected(self):
        debug, source, prg, regions = fixture()
        with self.assertRaisesRegex(ValueError, 'geometry'):
            inventory(debug.replace('ooffs=32784', 'ooffs=16'), source, prg, regions)
        with self.assertRaisesRegex(ValueError, 'cover'):
            inventory(debug.replace('span\tid=4,seg=7,start=8,size=1\n', ''), source, prg, regions)
        with self.assertRaisesRegex(ValueError, 'duplicate debug span'):
            inventory(debug + 'span\tid=1,seg=7,start=0,size=2\n', source, prg, regions)

    def test_instruction_mismatch_and_region_overlap_are_rejected(self):
        debug, source, prg, regions = fixture()
        changed = bytearray(prg)
        changed[2] = 0xea
        with self.assertRaisesRegex(ValueError, 'does not match'):
            inventory(debug, source, bytes(changed), regions)
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            inventory(debug, source, prg, regions + [regions[0]])

    def test_script_dispatch_decodes_rts_targets_and_detects_table_drift(self):
        debug, source, prg, regions = fixture()
        changed = bytearray(prg)
        changed[0x5585] = 7
        changed[0x564a] = 0x80
        changed[0x7da7] = changed[BANK_SIZE + 0x7da7] = 3
        result = inventory(debug, source, bytes(changed), regions, include_script_dispatch=True)
        first = result['script_dispatch']['entries'][0]
        self.assertEqual(first['target_cpu'], '0x8008')
        self.assertEqual(first['record_length'], 3)
        self.assertEqual(first['bank0']['ownership'], 'code')
        self.assertEqual(first['bank1']['ownership'], 'data')
        self.assertEqual(result['script_dispatch']['nominal_entries'], 197)
        changed[BANK_SIZE + 0x7da7] = 4
        with self.assertRaisesRegex(ValueError, 'length tables differ'):
            inventory(debug, source, bytes(changed), regions, include_script_dispatch=True)

    def test_parent_span_may_cross_ownership_boundaries(self):
        debug, source, prg, regions = fixture()
        debug += 'span\tid=5,seg=7,start=0,size=10\n'
        self.assertEqual(inventory(debug, source, prg, regions)['covered_code_bytes'], 9)


if __name__ == '__main__':
    unittest.main()
