"""Direct-record inventory tests use synthetic data only."""
import unittest
from tools.direct_record_flow import direct_inventory, source_script_seeds
from tools.script_entries import BANK_SIZE


class SourceScriptSeedTests(unittest.TestCase):
    def setUp(self):
        self.regions = [{'bank': 1, 'kind': 'data', 'cpu': '0x9000', 'size': 0x20}]

    def test_only_explicit_bank_one_script_labels_are_seeds(self):
        source = ('.scope Bank0\nRuntimeScript9000:\n.endscope\n.scope Bank1\n'
                  'RuntimeScript9000:\nCandidate9003:\nData9006:\nRestoreScript9009:\n.endscope\nScript9004:\n')
        self.assertEqual(source_script_seeds(source, self.regions), [0x1000, 0x1003, 0x1009])

    def test_rejects_unowned_or_duplicate_labels(self):
        for source in ('.scope Bank1\nScript9000:\n',
                       '.scope Bank1\nScript9020:\n.endscope\n',
                       '.scope Bank1\nScript9000:\nCandidate9000:\n.endscope\n',
                       '.scope Bank1\nData9000:\n.endscope\n',
                       '.scope Bank1\n.scope Bank1\nScript9000:\n'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                source_script_seeds(source, self.regions)


class DirectRecordInventoryTests(unittest.TestCase):
    def test_mode_classes_and_script_overlap_are_reported(self):
        bank0 = bytes(BANK_SIZE)
        bank1 = bytearray(BANK_SIZE)
        bank1[0x100:0x10a] = bytes([0x34, 0x81, 0x30, 0xff, 0, 1, 2, 3, 4, 5])
        graph = {'nodes': [
            {'opcode': 0x16, 'operands': [0, 1], 'encoded_pointer': '0x0020',
             'location': {'bank': 1, 'bank_offset': 0x20}, 'length': 3},
            {'opcode': 0x16, 'operands': [0, 0], 'encoded_pointer': '0x0030',
             'location': {'bank': 1, 'bank_offset': 0x30}, 'length': 3},
            {'opcode': 0x09, 'encoded_pointer': '0x0100',
             'location': {'bank': 1, 'bank_offset': 0x100}, 'length': 2},
        ]}
        result = direct_inventory(bank0, bytes(bank1), graph)
        self.assertEqual({r['mode_class'] for r in result['references']},
                         {'zero', 'one', 'other_nonnegative', 'negative'})
        self.assertEqual({r['encoded_pointer'] for r in result['references']}, {'0x0100'})
        self.assertEqual(result['dynamic_slot_pointer_commands'], ['0x0030'])
        self.assertEqual(result['record_script_overlaps']['physical_bytes'], 2)

    def test_boundary_crossing_is_reported_without_inventing_fields(self):
        node = {'opcode': 0x16, 'operands': [0xff, 0x7f], 'encoded_pointer': '0x0010',
                'location': {'bank': 1, 'bank_offset': 0x10}, 'length': 3}
        result = direct_inventory(bytes(BANK_SIZE), bytes(BANK_SIZE), {'nodes': [node]})
        self.assertTrue(all(r['status'] == 'fetch_crosses_bank_boundary'
                            for r in result['references']))
        self.assertEqual(result['record_script_overlaps']['physical_bytes'], 0)


if __name__ == '__main__':
    unittest.main()
