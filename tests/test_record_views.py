"""Record-declaration inventory checks with synthetic source/debug metadata."""
import copy
import unittest

from tools.record_views import inventory


def fixture():
    source = ('.scope Bank1\n    SlotRuntimeRecord $8000, $FFFF, 0, 1, 2, 3, 4\n'
              '    SlotScriptOnlyRecord 0, $FFFF, 0, 1, 2, 3, 4\n'
              '    SlotCompactRecord $8000, 0\n.endscope\n')
    debug = '''file\tid=0,name="source/rom.s"
seg\tid=8,name="PRG1",start=0x8000,size=0x8000,ooffs=32784
span\tid=1,seg=8,start=0,size=9
span\tid=2,seg=8,start=0x10,size=9
span\tid=3,seg=8,start=0x20,size=3
line\tid=1,file=0,line=2,span=1
line\tid=2,file=0,line=3,span=2
line\tid=3,file=0,line=4,span=3
'''
    regions = [{'bank': 1, 'cpu': hex(0x8000 + offset), 'size': size, 'kind': 'data'}
               for offset, size in ((0, 9), (0x10, 9), (0x20, 3), (0x30, 3), (0x33, 3), (0x36, 3))]
    return source, debug, {'regions': regions}


class RecordViewTests(unittest.TestCase):
    def test_declarations_and_fragmented_ownership_are_distinct(self):
        source, debug, mapping = fixture()
        mapping['loader_views'] = [{'id': 'fragmented', 'bank': 1, 'cpu': '0x8030', 'size': 9,
                                    'kind': 'normal', 'basis': 'synthetic overlapping fields'}]
        result = inventory(source, debug, mapping)
        self.assertEqual(len(result), 4)
        self.assertEqual([r['cpu'] for r in result if r['kind'] == 'normal'], ['0x8000', '0x8010', '0x8030'])
        self.assertEqual(next(r for r in result if r['cpu'] == '0x8010')['source_line'], 3)

    def test_missing_or_ambiguous_declared_span_is_rejected(self):
        source, debug, mapping = fixture()
        for bad in (debug.replace('size=9\n', 'size=8\n', 1),
                    debug.replace('file=0,line=2,span=1', 'file=0,line=2,span=99'),
                    debug + 'span\tid=4,seg=8,start=0x40,size=9\nline\tid=4,file=0,line=2,span=4\n',
                    debug.replace('ooffs=32784', 'ooffs=16')):
            with self.subTest(debug=bad[-50:]), self.assertRaises(ValueError):
                inventory(source, bad, mapping)

    def test_declaration_and_explicit_view_require_all_bytes_to_be_data_owned(self):
        source, debug, mapping = fixture()
        for kind in ('code', 'fill', 'missing'):
            bad = copy.deepcopy(mapping)
            if kind == 'missing':
                bad['regions'].pop(0)
            else:
                bad['regions'][0]['kind'] = kind
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'source-owned'):
                inventory(source, debug, bad)
        mapping['loader_views'] = [{'id': 'fragmented', 'bank': 1, 'cpu': '0x8030', 'size': 9,
                                    'kind': 'normal', 'basis': 'synthetic view'}]
        mapping['regions'][-1]['size'] = 2
        with self.assertRaisesRegex(ValueError, 'source-owned'):
            inventory(source, debug, mapping)

    def test_duplicate_bad_geometry_and_wrong_view_size_are_rejected(self):
        source, debug, mapping = fixture()
        base = {'id': 'view', 'bank': 1, 'cpu': '0x8030', 'size': 9, 'kind': 'normal', 'basis': 'test'}
        for patch in ({'cpu': '0x8000'}, {'bank': 0}, {'bank': True}, {'cpu': '0xfff7'},
                      {'size': 3}, {'kind': 'unknown'}, {'basis': ''}):
            bad = copy.deepcopy(mapping);bad['loader_views'] = [{**base, **patch}]
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                inventory(source, debug, bad)
        mapping['loader_views'] = [base, base.copy()]
        with self.assertRaises(ValueError):
            inventory(source, debug, mapping)

    def test_nonrecord_comments_and_macro_definition_are_not_declarations(self):
        source, debug, mapping = fixture()
        source = source.replace('.endscope', '; SlotCompactRecord $8000, 0\n.macro SlotRuntimeRecord args\n.endmacro\n.endscope')
        self.assertEqual(len(inventory(source, debug, mapping)), 3)


if __name__ == '__main__':
    unittest.main()
