"""Exercise menu streams with invented data, never extracted game bytes."""
import copy
from pathlib import Path
import tempfile
import unittest

from tools import menu_assets


def synthetic_menu_prg(prg=None):
    data = bytearray(prg if prg is not None else bytes(0x10000))
    cursor = menu_assets.REGION_START
    for index, (_, cpu) in enumerate(menu_assets.COMMANDS):
        count = 14 if index == len(menu_assets.COMMANDS) - 1 else 12
        start = 0x8000 + cpu - 0x8000
        data[start:start + 7] = bytes([0x6e, cursor & 255, cursor >> 8,
                                      (index * 3) & 255, (index * 5) & 255, 2, count])
        for n in range(count):
            data[0x8000 + cursor + n] = (index * 29 + n * 7 + 3) & 255
        cursor += count
    assert cursor == menu_assets.REGION_END
    return bytes(data)


class MenuAssetTests(unittest.TestCase):
    def setUp(self):
        self.prg = synthetic_menu_prg()
        self.sha = 'a' * 64
        self.asset = menu_assets.capture(self.prg, self.sha)

    def test_round_trip_and_edit_tile(self):
        spans = menu_assets.encode(self.asset, self.prg, self.sha)
        self.assertEqual(len(spans), 14)
        self.assertTrue(all(self.prg[bank * 0x8000 + offset:bank * 0x8000 + offset + len(data)] == data
                            for bank, offset, data in spans))
        changed = copy.deepcopy(self.asset)
        changed['streams'][0]['tiles'][3] ^= 1
        self.assertEqual(menu_assets.encode(changed, self.prg, self.sha)[0][2][3],
                         spans[0][2][3] ^ 1)

    def test_control_changes_one_tile_per_stream(self):
        reference = b'R' * 16 + self.prg
        candidate = bytearray(reference)
        changed = menu_assets.changed_asset(self.asset)
        for bank, offset, payload in menu_assets.encode(changed, self.prg, self.sha):
            pos = 16 + bank * 0x8000 + offset
            candidate[pos:pos + len(payload)] = payload
        offsets = menu_assets.verify_control(reference, bytes(candidate), 16, self.asset)
        self.assertEqual(len(offsets), 14)
        candidate[offsets[0] + 1] ^= 1
        with self.assertRaises(ValueError):
            menu_assets.verify_control(reference, bytes(candidate), 16, self.asset)

    def test_rejects_bad_identity_layout_and_tiles(self):
        cases = []
        for key, value in [('schema_version', True), ('bank', False), ('reference_sha256', 'b' * 64)]:
            item = copy.deepcopy(self.asset); item[key] = value; cases.append(item)
        for key, value in [('name', 'wrong'), ('row', True), ('source_cpu', '0xf358'),
                           ('tiles', [0]), ('tiles', [256] * 12), ('tiles', [True] * 12)]:
            item = copy.deepcopy(self.asset); item['streams'][0][key] = value; cases.append(item)
        for item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                menu_assets.encode(item, self.prg, self.sha)

    def test_rejects_bad_commands_overlaps_and_boundaries(self):
        first = 0x8000 + menu_assets.COMMANDS[0][1] - 0x8000
        for index, value in [(0, 0), (1, 0), (2, 0xff), (6, 0), (6, 13)]:
            data = bytearray(self.prg); data[first + index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                menu_assets.inventory(bytes(data))
        with self.assertRaises(ValueError):
            menu_assets.inventory(bytes(32))

    def test_local_input_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(menu_assets.select(root, self.prg, self.sha)[2], 'reference')
            path = root / menu_assets.ASSET_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(menu_assets.serialize(self.asset))
            self.assertEqual(menu_assets.select(root, self.prg, self.sha)[2], 'local')
            path.unlink(); path.symlink_to(root / 'elsewhere')
            with self.assertRaises(ValueError):
                menu_assets.select(root, self.prg, self.sha)


if __name__ == '__main__':
    unittest.main()
