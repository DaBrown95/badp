"""Palette geometry and failures using invented colours and addresses."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import palette_assets


def synthetic_palettes(root, prg=None):
    data = bytearray(prg if prg is not None else bytes(0x10000))
    data[0x6000:0x6013] = bytes([0, 0, 0] + list(range(16)))
    data[0x6013:0x6036] = bytes([2, 3, 10] + list(range(16)) + list(range(32, 48)))
    manifest = {'schema_version': 1, 'target': 'us-v1.5', 'source': 'synthetic fixture',
                'bank': 0, 'cpu_addresses': ['0xe000', '0xe013'], 'end_cpu': '0xe036'}
    path = root / palette_assets.MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest))
    return bytes(data)


class PaletteAssetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.prg = synthetic_palettes(self.root)
        self.sha = 'a' * 64
        self.asset = palette_assets.capture(self.root, self.prg, self.sha)

    def test_round_trip_initial_and_animated_groups(self):
        spans = palette_assets.encode(self.root, self.asset, self.prg, self.sha)
        self.assertEqual([len(data) for _, _, data in spans], [16, 32])
        self.assertTrue(all(self.prg[offset:offset + len(data)] == data for _, offset, data in spans))
        self.assertEqual(self.asset['streams'][1]['updates'], [list(range(32, 40)), list(range(40, 48))])
        changed = copy.deepcopy(self.asset)
        changed['streams'][1]['updates'][1][2] = 255
        self.assertEqual(palette_assets.encode(self.root, changed, self.prg, self.sha)[1][2][-6], 255)

    def test_controls_reject_extra_changes_missing_stream_and_wrong_value(self):
        reference = b'R' * 16 + self.prg
        changed = palette_assets.changed_asset(self.asset)
        candidate = bytearray(reference)
        for _, offset, data in palette_assets.encode(self.root, changed, self.prg, self.sha):
            candidate[16 + offset:16 + offset + len(data)] = data
        offsets = palette_assets.verify_control(reference, bytes(candidate), 16, self.asset)
        self.assertEqual(offsets, [16 + 0x6004, 16 + 0x6017, 16 + 0x6027, 16 + 0x602f])
        for offset in (offsets[0], offsets[0] + 1):
            bad = bytearray(candidate); bad[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                palette_assets.verify_control(reference, bytes(bad), 16, self.asset)

    def test_rejects_changed_header_order_counts_and_invalid_colours(self):
        for key, value in [('group_count', 1), ('frame_count', 4), ('ticks', True),
                           ('cpu', '0xe014'), ('initial', [0]), ('initial', [True] * 16),
                           ('updates', [[0] * 8]), ('updates', [[256] * 8] * 2)]:
            bad = copy.deepcopy(self.asset); bad['streams'][1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                palette_assets.encode(self.root, bad, self.prg, self.sha)
        for key, value in [('schema_version', True), ('bank', False), ('reference_sha256', 'b' * 64)]:
            bad = copy.deepcopy(self.asset); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                palette_assets.encode(self.root, bad, self.prg, self.sha)

    def test_rejects_incorrect_boundaries_zero_frame_count_and_index_high_byte(self):
        for field, value in ((0x6013, 5), (0x6014, 0), (0x6014, 255), (0x6014, 2)):
            bad = bytearray(self.prg); bad[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                palette_assets.inventory(self.root, bytes(bad))
        manifest = json.loads((self.root / palette_assets.MANIFEST).read_text())
        manifest['cpu_addresses'].reverse()
        (self.root / palette_assets.MANIFEST).write_text(json.dumps(manifest))
        with self.assertRaises(ValueError): palette_assets.inventory(self.root, self.prg)

    def test_local_edits_and_symlink_rejection(self):
        self.assertEqual(palette_assets.select(self.root, self.prg, self.sha)[2], 'reference')
        path = self.root / palette_assets.ASSET_PATH
        path.parent.mkdir(parents=True)
        path.write_bytes(palette_assets.serialize(self.asset))
        self.assertEqual(palette_assets.select(self.root, self.prg, self.sha)[2], 'local')
        path.unlink(); path.symlink_to(self.root / 'absent')
        with self.assertRaises(ValueError): palette_assets.select(self.root, self.prg, self.sha)


if __name__ == '__main__':
    unittest.main()
