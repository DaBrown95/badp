"""Exercise sprite assets with invented frame contents, never game bytes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import sprite_assets


class SpriteAssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / sprite_assets.MANIFEST
        self.manifest.parent.mkdir(parents=True)
        self.listing = {'schema_version': 1, 'target': 'us-v1.5', 'source': 'synthetic frames', 'bank': 0,
                        'cpu_addresses': ['0x9000', '0x9010']}
        self.manifest.write_text(json.dumps(self.listing))
        data = bytearray(0x10000)
        data[0x1000:0x1006] = bytes([0x84, 0x21, 0x35, 0x14, 0x36, 0x28])
        data[0x1010:0x1014] = bytes([0x07, 0x11, 0x51, 0x73])
        self.prg = bytes(data)
        self.sha = 'a' * 64
        self.asset = sprite_assets.capture(self.root, self.prg, self.sha)

    def test_round_trip_and_both_tile_fields_are_editable(self):
        spans = sprite_assets.encode(self.root, self.asset, self.prg, self.sha)
        self.assertEqual([x[2] for x in spans], [self.prg[0x1000:0x1006], self.prg[0x1010:0x1014]])
        edited = copy.deepcopy(self.asset)
        edited['frames'][0]['tile_rows'][0][1] = [9, 10]
        self.assertEqual(sprite_assets.encode(self.root, edited, self.prg, self.sha)[0][2][-2:], bytes([9, 10]))

    def test_control_changes_one_tile_per_frame(self):
        changed = sprite_assets.changed_asset(self.asset)
        reference = b'R' * 16 + self.prg
        candidate = bytearray(reference)
        for bank, start, payload in sprite_assets.encode(self.root, changed, self.prg, self.sha):
            pos = 16 + bank * 0x8000 + start
            candidate[pos:pos + len(payload)] = payload
        self.assertEqual(sprite_assets.verify_control(reference, bytes(candidate), 16, self.asset), [0x1012, 0x1022])
        candidate[0x1013] ^= 1
        with self.assertRaises(ValueError):
            sprite_assets.verify_control(reference, bytes(candidate), 16, self.asset)

    def test_rejects_changed_identity_header_shape_and_invalid_pairs(self):
        cases = []
        for key, value in [('reference_sha256', 'b' * 64), ('bank', 1)]:
            obj = copy.deepcopy(self.asset); obj[key] = value; cases.append(obj)
        for key, value in [('cpu', '0x9001'), ('columns', 1), ('large_sprites', False), ('rows', True),
                           ('tile_rows', [[[256, 0], [1, 2]]]), ('tile_rows', [[[True, 0], [1, 2]]]),
                           ('tile_rows', [[[1, 2]]])]:
            obj = copy.deepcopy(self.asset); obj['frames'][0][key] = value; cases.append(obj)
        for obj in cases:
            with self.subTest(asset=obj), self.assertRaises(ValueError):
                sprite_assets.encode(self.root, obj, self.prg, self.sha)

    def test_rejects_duplicate_overlap_wrap_and_bank_crossing(self):
        for addresses in (['0x9000', '0x9000'], ['0x9001', '0x9000'], ['0x9000', '0x9004']):
            self.listing['cpu_addresses'] = addresses; self.manifest.write_text(json.dumps(self.listing))
            with self.subTest(addresses=addresses), self.assertRaises(ValueError):
                sprite_assets.inventory(self.root, self.prg)
        self.listing['cpu_addresses'] = ['0x9000']; self.manifest.write_text(json.dumps(self.listing))
        for dimensions in (0x00, 0xff):
            data = bytearray(self.prg); data[0x1001] = dimensions
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                sprite_assets.inventory(self.root, bytes(data))
        self.listing['cpu_addresses'] = ['0xfffd']; self.manifest.write_text(json.dumps(self.listing))
        data = bytearray(self.prg); data[0x7ffe] = 0x11
        with self.assertRaises(ValueError):
            sprite_assets.inventory(self.root, bytes(data))

    def test_local_asset_staleness_and_symlink_rejected(self):
        selected = sprite_assets.select(self.root, self.prg, self.sha)
        self.assertEqual(selected[2], 'reference')
        path = self.root / sprite_assets.ASSET_PATH
        path.parent.mkdir(parents=True)
        path.write_bytes(sprite_assets.serialize(self.asset))
        self.assertEqual(sprite_assets.select(self.root, self.prg, self.sha)[2], 'local')
        path.unlink(); path.symlink_to(self.manifest)
        with self.assertRaises(ValueError):
            sprite_assets.select(self.root, self.prg, self.sha)


if __name__ == '__main__':
    unittest.main()
