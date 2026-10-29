"""Logical-layout and typed-source checks with invented source, never ROM data."""
import copy
import unittest

from tools.build_variant_source import apply_source_patch, source_patch
from tools.source_variants import Layout, operands, target_regions, typed_lines


class SourceVariantTests(unittest.TestCase):
    def layout(self):
        return Layout(((0, 0x9000, 0xa000, -16), (1, 0xf100, 0xf200, -2)))

    def test_pointer_namespaces_do_not_relocate_packed_text_ppu_or_arithmetic_values(self):
        source = ('    SlotRuntimeRecord $9123, $7105, $00, $FF, $00, $00, $00\n'
                  '    .word $9123 ; a direct bank-1 text pointer\n'
                  '    PpuStreamAbsolute $2100\n'
                  '    BogusSetSlotValue $9123\n')
        result = typed_lines(source, self.layout())
        self.assertIn('SlotRuntimeRecord (Bank0Resource {$9123}), (Bank1Encoded {$7105})', result)
        self.assertIn('.word $9123 ; a direct bank-1 text pointer', result)
        self.assertIn('PpuStreamAbsolute $2100', result)
        self.assertIn('BogusSetSlotValue $9123', result)

    def test_reordered_extent_keeps_its_own_end_boundary(self):
        layout = Layout(((0, 0x9000, 0x9100, 0x100), (0, 0x9100, 0x9200, -0x100)),
                        ((0, 0x9000, 0x9100, 0x9100), (0, 0x9100, 0x9200, 0x9000)))
        self.assertEqual(layout.address(0, 0x9100), 0x9000)
        self.assertEqual(layout.span(0, 0x90f0, 0x9100), (0x91f0, 0x9200))
        self.assertEqual(layout.span(0, 0x9100, 0x9120), (0x9000, 0x9020))
        for low, high in [(0x90f0, 0x9110), (0x8ff0, 0x9001), (True, 0x9000)]:
            with self.assertRaises(ValueError):layout.span(0, low, high)
        with self.assertRaises(ValueError):Layout((), ((0, 0x9000, 0x9100, 0xff80),))

    def test_nested_operands_and_malformed_expressions(self):
        self.assertEqual(operands('($1234 + max(1, 2)), {3, 4}, $00'),
                         ['($1234 + max(1, 2))', '{3, 4}', '$00'])
        for text in ('($00', '$00}', '($00}', '$00,, $01', ''):
            with self.subTest(text=text), self.assertRaises(ValueError):
                operands(text)

    def test_physical_banks_and_fixed_endpoints_are_distinct(self):
        layout = self.layout()
        self.assertEqual(layout.address(0, 0x9123), 0x9113)
        self.assertEqual(layout.address(1, 0x9123), 0x9123)
        self.assertEqual(layout.offset(1, 0x7105), 0x7103)
        self.assertEqual(layout.address(1, 0xf200), 0xf200)
        for args in ((2, 0x9000), (0, 0x7fff), (True, 0x9000), (0, 0x10001)):
            with self.assertRaises(ValueError):layout.address(*args)

    def test_collapsed_regions_and_overlapping_layouts_fail_closed(self):
        layout = self.layout()
        with self.assertRaises(ValueError):
            target_regions({'regions': [{'bank': 0, 'cpu': '0x8ff8', 'size': 8}]}, layout)
        with self.assertRaises(ValueError):
            Layout(((0, 0x9000, 0xa000, -16), (0, 0x9f00, 0xa100, -16)))
        with self.assertRaises(ValueError):
            Layout(((0, 0x8000, 0x8100, -1),))

    def test_compact_sources_reconstruct_exactly_and_detect_wrong_baseline(self):
        for original, changed in [('lda #$12\nsta $30\n', 'lda #$13\nsta $30\n'),
                                  ('; µ\nlda #1\n', '; µ\nlda #2\n'), ('abc', 'xyz'), ('', 'insert')]:
            patch = source_patch(original, changed)
            self.assertEqual(apply_source_patch(original, patch), changed)
            altered = copy.deepcopy(patch);altered['removed_sha256'] = '0' * 64
            with self.assertRaises(ValueError):apply_source_patch(original, altered)
        with self.assertRaises(ValueError):source_patch('same', 'same')
