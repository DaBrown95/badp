import unittest

from tools.prg_inventory import summarize
from tools.source_audit import compare_regions, partition


class SourceAuditTests(unittest.TestCase):
    def evidence(self):
        return summarize({'source_data': [(1, 1)],
                          'candidate_script_bytes': [(1, 3)]},
                         bank_size=4, bank_count=2)['evidence_spans']

    def test_counts_once_but_retains_competing_asset_and_script_uses(self):
        result = partition(self.evidence(), {'tiles': [(1, 2)], 'other': [(2, 1)]},
                           bank_size=4, bank_count=2)
        self.assertEqual(result['representation_bytes'],
                         {'local_asset': 1, 'source_data': 1, 'unresolved_local': 6})
        overlap = next(row for row in result['regions'] if row['physical_prg_offset'] == 2)
        self.assertEqual(overlap['local_assets'], ['other', 'tiles'])
        self.assertEqual(overlap['evidence_uses'], ['candidate_script_bytes'])
        self.assertEqual(overlap['review_status'], 'unreviewed')
        self.assertEqual(sum(r['size'] for r in result['regions']), 8)
        self.assertFalse(result['complete_executable_inventory'])

    def test_rejects_missing_duplicate_or_mislocated_evidence(self):
        for change in ('missing', 'duplicate', 'address', 'bank'):
            spans = self.evidence()
            if change == 'missing':
                spans.pop()
            elif change == 'duplicate':
                spans.insert(0, spans[0].copy())
            elif change == 'address':
                spans[0]['cpu_start'] = '0x8001'
            else:
                spans[0]['bank'] = 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                partition(spans, {}, bank_size=4, bank_count=2)

    def test_fill_is_separate_from_source_credit_and_retains_script_view(self):
        evidence = summarize({'source_fill': [(0, 3)], 'candidate_script_bytes': [(1, 2)]},
                             bank_size=4, bank_count=1)['evidence_spans']
        result = partition(evidence, {}, bank_size=4, bank_count=1)
        self.assertEqual(result['representation_bytes'], {'source_fill': 3, 'unresolved_local': 1})
        self.assertEqual(result['regions'][1]['evidence_uses'], ['candidate_script_bytes', 'source_fill'])
        self.assertEqual(result['regions'][1]['review_status'], 'unreviewed')

    def test_rejects_cross_bank_or_out_of_range_assets(self):
        for span in ((3, 2), (7, 2), (-1, 1), (0, 0), (True, 1)):
            with self.subTest(span=span), self.assertRaises(ValueError):
                partition(self.evidence(), {'tiles': [span]}, bank_size=4, bank_count=2)

    def test_revision_comparison_finds_relocation_and_nonunique_overlapping_matches(self):
        regions = [{'representation': 'unresolved_local', 'bank': 0,
                    'physical_prg_offset': 0, 'size': 1},
                   {'representation': 'unresolved_local', 'bank': 0,
                    'physical_prg_offset': 1, 'size': 1}]
        rows = compare_regions(b'aaXX', {'relocated': b'XXaa', 'repeated': b'aaaa',
                                       'absent': b'bbbb'}, regions, minimum_size=2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['size'], 2)
        self.assertEqual(rows[0]['revisions']['relocated']['first_physical_prg_offsets'], [2])
        self.assertEqual(rows[0]['revisions']['repeated']['exact_occurrences'], 3)
        self.assertEqual(rows[0]['revisions']['absent']['exact_occurrences'], 0)
        self.assertEqual(compare_regions(b'aaXX', {}, regions, minimum_size=3), [])


if __name__ == '__main__':
    unittest.main()
