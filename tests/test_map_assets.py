"""Local map-asset round trips and rejection tests using synthetic bytes."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import map_assets


def synthetic_prg():
    prg = bytearray(2 * map_assets.BANK_SIZE)
    indices = [index for index in range(map_assets.SLOT_COUNT) if index != 22] + [0]
    for i, index in enumerate(indices):
        offset = index * map_assets.CHUNK_SIZE
        start = map_assets.CHUNK_TABLE_OFFSET + i * 2
        prg[start:start + 2] = offset.to_bytes(2, 'little')
    for index in range(map_assets.REGION_SIZE):
        prg[map_assets.BANK_SIZE + index] = (index * 13 + 5) & 255
    return bytes(prg)


class MapAssetTests(unittest.TestCase):
    def setUp(self):
        self.prg = synthetic_prg()
        self.reference = 'a' * 64
        self.asset = map_assets.capture(self.prg, self.reference)

    def test_all_slots_round_trip_and_one_is_opaque(self):
        encoded = map_assets.encode(self.asset, self.prg, self.reference)
        self.assertEqual(encoded, self.prg[map_assets.BANK_SIZE:map_assets.BANK_SIZE + map_assets.REGION_SIZE])
        self.assertEqual(sum(x['kind'] == 'chunk' for x in self.asset['slots']), 145)
        self.assertEqual(self.asset['slots'][22]['kind'], 'unclassified')
        self.assertEqual(len(self.asset['slots'][0]['tile_rows']), 8)
        self.assertEqual(len(self.asset['slots'][0]['attribute_rows']), 2)

    def test_changed_tile_is_explicit_and_does_not_mutate_original(self):
        changed = map_assets.changed_asset(self.asset)
        baseline = map_assets.encode(self.asset, self.prg, self.reference)
        encoded = map_assets.encode(changed, self.prg, self.reference)
        self.assertEqual([i for i, (a, b) in enumerate(zip(baseline, encoded)) if a != b], [0])
        self.assertNotEqual(changed['slots'][0]['tile_rows'][0][0], self.asset['slots'][0]['tile_rows'][0][0])

    def test_wrong_identity_geometry_and_opaque_edits_fail(self):
        for change in ('identity', 'order', 'shape', 'opaque'):
            asset = copy.deepcopy(self.asset)
            if change == 'identity':
                asset['reference_sha256'] = 'b' * 64
            elif change == 'order':
                asset['slots'][0], asset['slots'][1] = asset['slots'][1], asset['slots'][0]
            elif change == 'shape':
                asset['slots'][0]['tile_rows'][0].pop()
            else:
                asset['slots'][22]['bytes_hex'] = '00' * map_assets.CHUNK_SIZE
            with self.subTest(change=change), self.assertRaises(ValueError):
                map_assets.encode(asset, self.prg, self.reference)

    def test_invalid_table_and_extra_slot_use_are_rejected(self):
        bad = bytearray(self.prg)
        bad[map_assets.CHUNK_TABLE_OFFSET:map_assets.CHUNK_TABLE_OFFSET + 2] = (1).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'unaligned'):
            map_assets.capture(bytes(bad), self.reference)
        bad = bytearray(self.prg)
        bad[map_assets.CHUNK_TABLE_OFFSET:map_assets.CHUNK_TABLE_OFFSET + 2] = (22 * map_assets.CHUNK_SIZE).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'reviewed slot'):
            map_assets.capture(bytes(bad), self.reference)

    def test_local_selection_and_changed_input_are_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset, payload, source, _ = map_assets.select(root, self.prg, self.reference)
            self.assertEqual(source, 'reference')
            path = root / map_assets.ASSET_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(map_assets.serialize(map_assets.changed_asset(asset)))
            _, changed, source, _ = map_assets.select(root, self.prg, self.reference)
            self.assertEqual(source, 'local')
            self.assertNotEqual(changed, payload)

    def test_export_is_idempotent_and_preserves_existing_edits(self):
        target = {'reference': {'file': {'sha256': self.reference}}}
        banks = (target, self.prg[:map_assets.BANK_SIZE], self.prg[map_assets.BANK_SIZE:], b'')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / map_assets.ASSET_PATH
            with (patch.object(map_assets, 'ROOT', root),
                  patch.object(map_assets, 'load_audited_banks', return_value=banks),
                  contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO())):
                self.assertEqual(map_assets.main(), 0)
                first = path.read_bytes()
                self.assertEqual(map_assets.main(), 0)
                self.assertEqual(path.read_bytes(), first)
                user_edit = b'{"user_edit":true}\n'
                path.write_bytes(user_edit)
                self.assertEqual(map_assets.main(), 1)
                self.assertEqual(path.read_bytes(), user_edit)

    def test_control_requires_exactly_one_selected_change(self):
        reference = bytes(16) + self.prg + bytes(65536)
        candidate = bytearray(reference)
        candidate[16 + map_assets.BANK_SIZE] ^= 1
        self.assertEqual(map_assets.verify_control(reference, bytes(candidate), 16), [16 + map_assets.BANK_SIZE])
        candidate[16 + map_assets.BANK_SIZE] ^= 2
        with self.assertRaisesRegex(ValueError, 'exactly'):
            map_assets.verify_control(reference, bytes(candidate), 16)
        candidate[16 + map_assets.BANK_SIZE] ^= 2
        candidate[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'exactly'):
            map_assets.verify_control(reference, bytes(candidate), 16)


if __name__ == '__main__':
    unittest.main()
