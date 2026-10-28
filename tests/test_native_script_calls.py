"""Candidate native-call inventory checks with synthetic PRG banks."""
import copy
import unittest

from test_native_control_flow import fixture
from tools.native_control_flow import BANK_SIZE
from tools.native_script_calls import inventory, origin_statements


def call_fixture():
    debug, source, prg, regions = fixture()
    bank0 = prg[:BANK_SIZE]
    bank1 = bytearray(prg[BANK_SIZE:])
    bank1[0x100:0x103] = bytes([0x9b, 0x07, 0x00])
    bank1[0x104:0x107] = bytes([0x9b, 0xff, 0xff])
    graph = {'unprocessed': [], 'nodes': [
        {'encoded_pointer': '0x0100', 'location': {'bank': 1, 'cpu_address': '0x8100',
                                                  'bank_offset': 0x100, 'physical_prg_offset': BANK_SIZE + 0x100},
         'opcode': 0x9b, 'length': 3, 'operands': [0x07, 0x00],
         'status': 'candidate', 'successors': [{'kind': 'next', 'target': '0x0104'}]},
        {'encoded_pointer': '0x0104', 'location': {'bank': 1, 'cpu_address': '0x8104',
                                                  'bank_offset': 0x104, 'physical_prg_offset': BANK_SIZE + 0x104},
         'opcode': 0x9b, 'length': 3, 'operands': [0xff, 0xff],
         'status': 'candidate', 'successors': []},
    ]}
    return graph, bank0, bytes(bank1), debug, source, regions


class NativeScriptCallTests(unittest.TestCase):
    def test_secondary_selection_and_rts_wrap_keep_bank_alternatives(self):
        calls = inventory(*call_fixture())['candidate_calls']
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]['target_cpu'], '0x8008')
        self.assertEqual(calls[0]['selection'], 'secondary_write')
        self.assertEqual(calls[0]['origin']['ownership'], 'local')
        self.assertEqual(calls[0]['bank0_target'], {'ownership': 'code', 'span_start': True})
        self.assertEqual(calls[0]['bank1_target'], {'ownership': 'data', 'span_start': False})
        self.assertEqual(calls[1]['target_cpu'], '0x0000')
        self.assertEqual(calls[1]['selection'], 'current_mapping')
        self.assertEqual(calls[1]['bank0_target']['ownership'], 'outside_prg')
        self.assertEqual(calls[1]['parents'], [{'script_pointer': '0x0100', 'edge': 'next'}])

    def test_exact_declared_call_is_distinguished_from_other_source_bytes(self):
        graph, b0, b1, debug, source, regions = call_fixture()
        source += '    BogusCallNativeEncoded $0007 ; reviewed candidate\n    .word $FFFF\n'
        debug += ('span\tid=5,seg=8,start=0x100,size=3\n'
                  'span\tid=6,seg=8,start=0x104,size=2\n'
                  'line\tid=5,file=0,line=6,span=5\n'
                  'line\tid=6,file=0,line=7,span=6\n')
        result = inventory(graph, b0, b1, debug, source, regions)
        self.assertEqual(result['source_origin_counts'],
                         {'declared_bogus_call': 1, 'inside_other_source_statement': 1})
        self.assertEqual(result['candidate_calls'][0]['source_origin']['statements'][0]['line'], 6)
        self.assertFalse(result['candidate_calls'][1]['source_origin']['statements'][0]['declared_call'])
        alias = inventory(graph, b0, b1, debug, source.replace('BogusCallNativeEncoded $0007',
                          'BogusCallNativeBank1 $8008'), regions)
        self.assertEqual(alias['source_origin_counts'], result['source_origin_counts'])

    def test_operand_entry_parent_span_and_comment_do_not_declare_calls(self):
        debug, source, _, _ = fixture()
        source += '    BogusCallNativeEncoded $8000\n    .word $1234 ; BogusCallNativeEncoded\n'
        debug += ('span\tid=5,seg=8,start=0x100,size=6\n'
                  'span\tid=6,seg=8,start=0x104,size=2\n'
                  'line\tid=5,file=0,line=6,span=5\n'
                  'line\tid=6,file=0,line=7,span=6\n')
        rows = origin_statements(debug, source, {(1, 0x8100), (1, 0x8101), (1, 0x8104), (0, 0x8100)})
        for key in ((1, 0x8100), (1, 0x8101), (1, 0x8104)):
            self.assertEqual(rows[key]['classification'], 'inside_other_source_statement')
        self.assertEqual(rows[(1, 0x8101)]['statements'][0]['opcode_offset'], 1)
        self.assertEqual(rows[(1, 0x8104)]['statements'][0]['statement'], '.word $1234')
        self.assertEqual(rows[(0, 0x8100)]['classification'], 'no_named_source_statement')

    def test_rejects_incomplete_wrong_bytes_and_duplicate_candidates(self):
        graph, bank0, bank1, debug, source, regions = call_fixture()
        for kind in ('pending', 'wrong_bytes', 'wrong_bank', 'wrong_physical_offset', 'duplicate'):
            altered = copy.deepcopy(graph)
            if kind == 'pending':
                altered['unprocessed'] = ['0x0100']
            elif kind == 'wrong_bytes':
                altered['nodes'][0]['operands'][0] ^= 1
            elif kind == 'wrong_bank':
                altered['nodes'][0]['location']['bank'] = 0
            elif kind == 'wrong_physical_offset':
                altered['nodes'][0]['location']['physical_prg_offset'] += 1
            else:
                altered['nodes'].append(copy.deepcopy(altered['nodes'][0]))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                inventory(altered, bank0, bank1, debug, source, regions)

    def test_low_encoded_7fff_switches_before_wrapping_to_zero(self):
        graph, bank0, bank1, debug, source, regions = call_fixture()
        graph['nodes'][0]['operands'] = [0xff, 0x7f]
        updated = bytearray(bank1)
        updated[0x101:0x103] = bytes([0xff, 0x7f])
        call = inventory(graph, bank0, bytes(updated), debug, source, regions)['candidate_calls'][0]
        self.assertEqual((call['selection'], call['target_cpu']), ('secondary_write', '0x0000'))


if __name__ == '__main__':
    unittest.main()
