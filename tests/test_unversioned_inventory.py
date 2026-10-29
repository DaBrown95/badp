"""Synthetic physical source partitions; no game payload fixtures."""
import unittest

from tools.unversioned_inventory import source_partition


class OwnPartitionTests(unittest.TestCase):
    def setUp(self):
        self.source = 'nop\n.res $7FFF, $00\n.incbin "synthetic.bin"\n.byte $EA\n'
        self.prg = bytes([0xea]) + bytes(32767) + bytes([1]) * 32768
        self.payloads = {'synthetic.bin': bytes([1]) * 32768}
        self.debug = ('file\tid=0,name="source/rom.s"\n'
                      'seg\tid=0,name="PRG0",start=0x8000,size=0x8000,ooffs=16\n'
                      'seg\tid=1,name="PRG1",start=0x8000,size=0x8000,ooffs=32784\n'
                      'span\tid=0,seg=0,start=0,size=1\n'
                      'span\tid=1,seg=0,start=1,size=32767\n'
                      'span\tid=2,seg=1,start=0,size=32768\n'
                      'line\tid=0,file=0,line=1,span=0\n'
                      'line\tid=1,file=0,line=2,span=1\n'
                      'line\tid=2,file=0,line=3,span=2\n')

    def test_consistent_instructions_fill_and_complete_editable_payload(self):
        rows = source_partition(self.debug, self.source, self.prg, self.payloads)
        self.assertEqual([(r['kind'], r['size']) for r in rows], [('code', 1), ('fill', 32767), ('asset', 32768)])
        self.assertEqual(rows[-1]['asset'], 'synthetic.bin')

    def test_missing_and_wrong_native_emission_fail(self):
        for source in (self.source.replace('nop', '; omitted'), self.source.replace('nop', 'rts')):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, 'unrepresented'):
                source_partition(self.debug, source, self.prg, self.payloads)

    def test_binary_inputs_require_known_identity_and_complete_payload(self):
        for payloads in ({}, {'synthetic.bin': bytes(32768)}, {'synthetic.bin': bytes([1]) * 32767}):
            with self.subTest(size=len(payloads)), self.assertRaisesRegex(ValueError, 'binary|asset leaf'):
                source_partition(self.debug, self.source, self.prg, payloads)

    def test_conflicting_emission_and_crossing_span_fail(self):
        extra = self.debug + 'line\tid=3,file=0,line=4,span=0\n'
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            source_partition(extra, self.source, self.prg, self.payloads)
        with self.assertRaisesRegex(ValueError, 'crosses'):
            source_partition(self.debug.replace('start=1,size=32767', 'start=1,size=32768'), self.source, self.prg, self.payloads)

    def test_geometry_and_source_origin_are_bound(self):
        for debug in (self.debug.replace('ooffs=32784', 'ooffs=16'), self.debug.replace('source/rom.s', 'other.s')):
            with self.subTest(debug=debug), self.assertRaisesRegex(ValueError, 'geometry|source'):
                source_partition(debug, self.source, self.prg, self.payloads)


if __name__ == '__main__':
    unittest.main()
