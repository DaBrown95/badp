"""Target identities, relocated tables and uncovered assets use synthetic fixtures."""
from pathlib import Path
import tempfile
import unittest

from test_map_assets import synthetic_prg
from tools import (chr_assets, map_assets, map_data, map_layout_assets, menu_assets,
                   palette_assets, ppu_assets, sprite_assets, text_assets)
from tools.asset_paths import asset_path
from tools.variant_assets import encoded_gaps


class TargetAssetTests(unittest.TestCase):
    def test_target_paths_and_chr_identity_are_separate(self):
        self.assertEqual(asset_path('us-v1.4', 'chr-tiles.json'), Path('extracted/us-v1.4/chr-tiles.json'))
        for target, name in [('../escape', 'x.json'), ('us-v1.4', '../x.json'), ('us-v1.4', 'x.bin'), ([], 'x.json')]:
            with self.assertRaises(ValueError):asset_path(target, name)
        data, sha = bytes(65536), 'a' * 64
        asset = chr_assets.capture(data, sha, target='us-v1.4')
        self.assertEqual(chr_assets.encode(asset, sha, target='us-v1.4'), data)
        with self.assertRaises(ValueError):chr_assets.encode(asset, sha)

    def test_actual_map_table_locations_are_used_and_wrong_geometry_rejected(self):
        original = synthetic_prg();data = bytearray(original)
        table = map_assets.CHUNK_TABLE_OFFSET
        data[0x5000:0x5000 + 292] = original[table:table + 292]
        data[0x5200:0x5200 + 44] = original[map_data.STATE_TABLE_OFFSET:map_data.STATE_TABLE_OFFSET + 44]
        data[map_data.STATE_TABLE_OFFSET:table + 292] = bytes([255]) * (table + 292 - map_data.STATE_TABLE_OFFSET)
        prg, sha = bytes(data), 'b' * 64
        asset = map_assets.capture(prg, sha, target='us-v1.4', chunk_table_offset=0x5000)
        self.assertEqual(map_assets.encode(asset, prg, sha, target='us-v1.4', chunk_table_offset=0x5000),
                         prg[32768:32768 + map_assets.REGION_SIZE])
        with self.assertRaises(ValueError):map_assets.capture(prg, sha)
        geometry = {'state_table_offset': 0x5200, 'chunk_table_offset': 0x5000}
        layouts = map_layout_assets.capture(prg, sha, target='us-v1.4', geometry=geometry)
        self.assertEqual(len(map_layout_assets.encode(layouts, prg, sha, target='us-v1.4', geometry=geometry)), 14)
        with self.assertRaises(ValueError):map_layout_assets.encode(layouts, prg, sha, geometry=geometry)
        for offset in (-1, True, 0x7fff):
            with self.assertRaises(ValueError):map_assets.slots_for_reference(prg, chunk_table_offset=offset)

    def test_supplied_target_manifests_do_not_fall_back_to_primary_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);prg = bytearray(65536);sha = 'c' * 64
            prg[0x1000:0x1004] = bytes((4, 0x11, 0x35, 0x12))
            manifest = {'schema_version': 1, 'target': 'us-v1.4', 'source': 'invented', 'bank': 0,
                        'cpu_addresses': ['0x9000']}
            sprite = sprite_assets.capture(root, bytes(prg), sha, target='us-v1.4', manifest=manifest)
            self.assertEqual(sprite_assets.encode(root, sprite, bytes(prg), sha, target='us-v1.4', manifest=manifest)[0][2],
                             bytes(prg[0x1000:0x1004]))
            with self.assertRaises(ValueError):sprite_assets.capture(root, bytes(prg), sha, manifest=manifest)
            prg[0x1400:0x1413] = bytes((0, 1, 7)) + bytes(range(16))
            palettes = {**manifest, 'cpu_addresses': ['0x9400'], 'end_cpu': '0x9413'}
            asset = palette_assets.capture(root, bytes(prg), sha, target='us-v1.4', manifest=palettes)
            self.assertEqual(palette_assets.encode(root, asset, bytes(prg), sha, target='us-v1.4', manifest=palettes)[0][2], bytes(range(16)))
            prg[0xd000:0xd006] = bytes((255, 0, 0x20, 0x41, 0x42, 0))
            streams = {'schema_version': 1, 'target': 'us-v1.4', 'source': 'invented', 'encoded_pointers': ['0x5000']}
            asset = ppu_assets.capture(root, bytes(prg), sha, target='us-v1.4', manifest=streams)
            self.assertEqual(ppu_assets.encode(root, asset, bytes(prg), sha, target='us-v1.4', manifest=streams),
                             [(1, 0x5003, b'AB')])

    def test_menu_payload_extents_come_from_this_target(self):
        data = bytearray(65536)
        data[0x8500:0x8507] = bytes((0x6e, 0, 0x60, 1, 2, 0, 2))
        data[0x8510:0x8517] = bytes((0x6e, 2, 0x60, 3, 4, 0, 3))
        data[0xe000:0xe005] = bytes((4, 5, 6, 7, 8))
        geometry = {'commands': (('first', 0x8500), ('second', 0x8510)), 'region_start': 0x6000, 'region_end': 0x6005}
        asset = menu_assets.capture(bytes(data), 'd' * 64, target='us-v1.4', geometry=geometry)
        self.assertEqual([len(row[2]) for row in menu_assets.encode(asset, bytes(data), 'd' * 64,
                                                                  target='us-v1.4', geometry=geometry)], [2, 3])
        data[0x8506] = 4
        with self.assertRaises(ValueError):menu_assets.inventory(bytes(data), **geometry)

    def test_text_record_identity_is_target_specific(self):
        data = synthetic_prg();sha = 'e' * 64
        asset = text_assets.capture(data, sha, target='us-v1.4')
        self.assertEqual(len(text_assets.encode(asset, data, sha, target='us-v1.4')), 52)
        with self.assertRaises(ValueError):text_assets.encode(asset, data, sha)

    def test_gap_encoding_cannot_fill_unknown_bytes_or_overwrite_source(self):
        prg = bytes(65536)
        gap = [{'name': 'synthetic.bin', 'bank': 0, 'cpu': '0x9000', 'size': 2}]
        self.assertEqual(encoded_gaps(prg, [], gap, {'tiles': [(0, 0x1000, b'AB')]}), {'synthetic.bin': b'AB'})
        with self.assertRaises(ValueError):encoded_gaps(prg, [], gap, {'tiles': [(0, 0x1000, b'A')]})
        with self.assertRaises(ValueError):encoded_gaps(prg, [], gap, {'one': [(0, 0x1000, b'AB')], 'two': [(0, 0x1001, b'C')]})
        regions = [{'bank': 0, 'cpu': '0x9000', 'size': 1}]
        with self.assertRaises(ValueError):encoded_gaps(prg, regions, gap, {'tiles': [(0, 0x1000, b'AB')]})
        self.assertEqual(encoded_gaps(prg, regions, gap, {'tiles': [(0, 0x1000, b'\0B')]}), {'synthetic.bin': b'\0B'})
