"""Synthetic tests of NES 2bpp tile conversion and CHR controls."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import chr_assets as c
from tools.identify_rom import inspect_rom
from tools.project import IDENTITY_PARTS


class ChrAssetsTests(unittest.TestCase):
    def test_tile_bit_order_and_planes(self):
        rows = ['01230123', '32103210'] + ['00000000'] * 6
        tile = c.encode_tile(rows)
        self.assertEqual(tile[:2], bytes((0x55, 0xaa)))
        self.assertEqual(tile[8:10], bytes((0x33, 0xcc)))
        self.assertEqual(c.decode_tile(tile), rows)
        for invalid in (rows[:7], rows[:7] + ['00000004'], rows[:7] + ['0000000']):
            with self.assertRaises(ValueError):
                c.encode_tile(invalid)

    def test_all_tiles_roundtrip_and_control(self):
        raw = bytes((i * 29 + 7) & 255 for i in range(c.CHR_SIZE))
        asset = c.capture(raw, 'a' * 64)
        self.assertEqual(c.encode(asset, 'a' * 64), raw)
        changed = c.encode(c.changed_asset(asset), 'a' * 64)
        reference = bytes(16 + 65536) + raw
        candidate = bytes(16 + 65536) + changed
        self.assertEqual(len(c.verify_control(reference, candidate, 16 + 65536)), 8)
        bad = bytearray(candidate); bad[-1] ^= 1
        with self.assertRaises(ValueError):
            c.verify_control(reference, bytes(bad), 16 + 65536)

    def test_invalid_identity_layout_and_local_override(self):
        raw = bytes(c.CHR_SIZE); asset = c.capture(raw, 'a' * 64)
        for change in ('target', 'count', 'row'):
            bad = copy.deepcopy(asset)
            if change == 'target': bad['reference_sha256'] = 'b' * 64
            if change == 'count': bad['tiles'].pop()
            if change == 'row': bad['tiles'][3][2] = '0000000x'
            with self.subTest(change=change), self.assertRaises(ValueError):
                c.encode(bad, 'a' * 64)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(c.select(root, raw, 'a' * 64)[2], 'reference')
            path = root / c.ASSET_PATH; path.parent.mkdir(parents=True)
            edited = c.changed_asset(asset); path.write_bytes(c.serialize(edited))
            _, payload, source, _ = c.select(root, raw, 'a' * 64)
            self.assertEqual(source, 'local')
            self.assertNotEqual(payload, raw)


    def test_export_audits_single_input_and_preserves_existing_edits(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            image = b'NES\x1a' + bytes((4, 8)) + bytes(10) + bytes(0x20000)
            actual = inspect_rom(image)
            target = {'input_path': 'input.nes', 'reference': {k: actual[k] for k in IDENTITY_PARTS}}
            rom = root / 'input.nes'; rom.write_bytes(image)
            with patch.object(c, 'ROOT', root), patch.object(c, 'load_target', return_value=target), \
                    patch.dict(os.environ, {'BADP_TARGET': '', 'BADP_ROM': ''}), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                altered = bytearray(image); altered[-1] ^= 1
                rom.write_bytes(altered)
                self.assertEqual(c.main(), 1)
                self.assertFalse((root / c.ASSET_PATH).exists())
                rom.write_bytes(image)
                self.assertEqual(c.main(), 0)
                path = root / c.ASSET_PATH
                edited = c.changed_asset(json.loads(path.read_bytes()))
                edited_raw = c.serialize(edited); path.write_bytes(edited_raw)
                self.assertEqual(c.main(), 1)
                self.assertEqual(path.read_bytes(), edited_raw)


if __name__ == '__main__':
    unittest.main()
