"""Synthetic parser and classification tests for the map probe."""
import unittest
from tools.trace_map import classify_observations, parse_output


class MapTraceTests(unittest.TestCase):
    def test_complete_trace_and_classification(self):
        text = ('MAP_DONE 16000\nMAP_TOTAL layout 1 1 0\nMAP_TOTAL row 2 2 0\n'
                'MAP_TOTAL column 1 1 0\nMAP_ERRORS 0\n'
                'MAP_DATA layout:1234:1:05 1\nMAP_DATA row:0044:1:05 2\n'
                'MAP_DATA column:0045:1:05 1\n')
        result = parse_output(text)
        static = {'layouts': [{'encoded_pointer': '0x1234', 'location': {'bank': 1}}],
                  'chunk_table_offsets': [68, 68]}
        classified = classify_observations(result['paired'], static)
        self.assertEqual(classified, {'unrecognized_layouts': 0, 'unrecognized_spans': 0,
                                      'chunk_offsets_seen': [68]})

    def test_unrecognized_bank_and_pointer_are_reported(self):
        static = {'layouts': [{'encoded_pointer': '0x1234', 'location': {'bank': 1}}],
                  'chunk_table_offsets': [68]}
        pairs = {'layout:1234:0:05': 2, 'row:0044:0:05': 3,
                 'column:0100:1:05': 4}
        result = classify_observations(pairs, static)
        self.assertEqual(result['unrecognized_layouts'], 2)
        self.assertEqual(result['unrecognized_spans'], 7)

    def test_rejects_incomplete_duplicate_and_inconsistent_trace(self):
        valid = ('MAP_DONE 16000\nMAP_TOTAL layout 1 1 0\nMAP_TOTAL row 1 1 0\n'
                 'MAP_TOTAL column 1 1 0\nMAP_ERRORS 0\n'
                 'MAP_DATA layout:1234:1:05 1\nMAP_DATA row:0044:1:05 1\n'
                 'MAP_DATA column:0045:1:05 1\n')
        cases = (valid.replace('MAP_DONE 16000', 'MAP_DONE 12000'),
                 valid.replace('MAP_ERRORS 0', 'MAP_ERRORS 1'),
                 valid.replace('MAP_TOTAL row 1 1 0', 'MAP_TOTAL row 2 1 0'),
                 valid.replace('MAP_DATA row:0044:1:05 1', 'MAP_DATA row:0044:1:05 0'),
                 valid + 'MAP_DATA row:0044:1:05 1\n',
                 valid.replace('MAP_DATA row:0044:1:05 1', 'MAP_DATA row:0044:9:05 1'))
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                parse_output(case)


if __name__ == '__main__':
    unittest.main()
