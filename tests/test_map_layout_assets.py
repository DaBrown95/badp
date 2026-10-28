"""Map layout asset tests using synthetic banks only."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_map_assets import synthetic_prg
from tools import map_layout_assets as layouts


class MapLayoutAssetTests(unittest.TestCase):
    def setUp(self):
        self.prg = synthetic_prg()
        self.reference = 'a' * 64
        self.asset = layouts.capture(self.prg, self.reference)

    def test_round_trip_keeps_headers_and_physical_grid_addresses(self):
        spans = layouts.encode(self.asset, self.prg, self.reference)
        self.assertEqual(len(spans), 14)
        self.assertEqual(sum(len(data) for _, _, data in spans), 126)
        for bank, offset, data in spans:
            start = bank * layouts.BANK_SIZE + offset
            self.assertEqual(data, self.prg[start:start + len(data)])

    def test_edited_cells_change_every_layout_and_only_expected_rom_bytes(self):
        original = layouts.gap_payloads(self.prg, [], layouts.encode(self.asset, self.prg, self.reference))
        changed = layouts.changed_asset(self.asset)
        updated = layouts.gap_payloads(self.prg, [], layouts.encode(changed, self.prg, self.reference))
        self.assertEqual([name for name in original if original[name] != updated[name]], ['bank1_8000_10000.bin'])
        ref = bytes(16) + self.prg + bytes(65536)
        candidate = bytearray(ref)
        positions = [16 + layouts.BANK_SIZE + 0x2802 + index * 11 for index in range(14)]
        for pos in positions:
            candidate[pos] ^= 1
        self.assertEqual(layouts.verify_control(ref, bytes(candidate), 16, self.asset), positions)
        candidate[positions[0]] ^= 2
        with self.assertRaisesRegex(ValueError, 'exactly'):
            layouts.verify_control(ref, bytes(candidate), 16, self.asset)

    def test_wrong_header_identity_and_shape_fail(self):
        for kind in ('identity', 'header', 'order', 'shape'):
            asset = copy.deepcopy(self.asset)
            if kind == 'identity':
                asset['reference_sha256'] = 'b' * 64
            elif kind == 'header':
                asset['layouts'][0]['width_chunks'] += 1
            elif kind == 'order':
                asset['layouts'][0], asset['layouts'][1] = asset['layouts'][1], asset['layouts'][0]
            else:
                asset['layouts'][0]['chunk_rows'][0].pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                layouts.encode(asset, self.prg, self.reference)

    def test_owned_and_overlapping_grid_spans_fail(self):
        spans = layouts.encode(self.asset, self.prg, self.reference)
        bank, offset, grid = spans[0]
        regions = [{'bank': bank, 'cpu': hex(0x8000 + offset), 'size': 1}]
        with self.assertRaisesRegex(ValueError, 'local gap'):
            layouts.gap_payloads(self.prg, regions, spans)
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            layouts.gap_payloads(self.prg, [], spans + [(bank, offset, grid)])

    def test_optional_owned_overlap_splits_gap_and_rejects_conflicting_edits(self):
        spans = layouts.encode(self.asset, self.prg, self.reference)
        bank, offset, grid = spans[0]
        regions = [{'bank': bank, 'cpu': hex(0x8000 + offset + 3), 'size': 2}]
        gaps = layouts.gap_payloads(self.prg, regions, spans, allow_owned=True)
        left = f'bank{bank}_8000_{0x8000 + offset + 3:04x}.bin'
        right = f'bank{bank}_{0x8000 + offset + 5:04x}_10000.bin'
        self.assertEqual(gaps[left][offset:offset + 3], grid[:3])
        self.assertEqual(gaps[right][:len(grid) - 5], grid[5:])
        edited = bytearray(grid)
        edited[3] ^= 1
        with self.assertRaisesRegex(ValueError, 'source-owned'):
            layouts.gap_payloads(self.prg, regions, [(bank, offset, bytes(edited))], allow_owned=True)
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            layouts.gap_payloads(self.prg, regions, spans + [(bank, offset + 3, grid[3:5])],
                                 allow_owned=True)
        with self.assertRaisesRegex(ValueError, 'bank boundary'):
            layouts.gap_payloads(self.prg, regions, [(bank, layouts.BANK_SIZE - 1, b'123')],
                                 allow_owned=True)

    def test_export_preserves_existing_edits(self):
        target = {'reference': {'file': {'sha256': self.reference}}}
        banks = (target, self.prg[:layouts.BANK_SIZE], self.prg[layouts.BANK_SIZE:], b'')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / layouts.ASSET_PATH
            with (patch.object(layouts, 'ROOT', root), patch.object(layouts, 'load_audited_banks', return_value=banks),
                  contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO())):
                self.assertEqual(layouts.main(), 0)
                self.assertEqual(layouts.main(), 0)
                user_edit = b'{"user_edit":true}\n'
                path.write_bytes(user_edit)
                self.assertEqual(layouts.main(), 1)
                self.assertEqual(path.read_bytes(), user_edit)


if __name__ == '__main__':
    unittest.main()
