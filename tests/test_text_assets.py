"""Editable packed-text asset checks with entirely synthetic messages."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_map_assets import synthetic_prg
from tools import text_assets


class TextAssetTests(unittest.TestCase):
    def setUp(self):
        self.prg = synthetic_prg()
        self.reference = 'a' * 64
        self.asset = text_assets.capture(self.prg, self.reference)

    def test_all_records_round_trip_without_touching_headers(self):
        spans = text_assets.encode(self.asset, self.prg, self.reference)
        self.assertEqual(len(spans), 52)
        for bank, offset, payload in spans:
            start = bank * text_assets.BANK_SIZE + offset
            self.assertEqual(payload, self.prg[start:start + len(payload)])

    def test_each_record_changes_and_control_rejects_other_bytes(self):
        original = text_assets.encode(self.asset, self.prg, self.reference)
        changed = text_assets.changed_asset(self.asset, self.prg)
        edited = text_assets.encode(changed, self.prg, self.reference)
        self.assertTrue(all(a[2] != b[2] for a, b in zip(original, edited)))
        reference = bytes(16) + self.prg + bytes(65536)
        candidate = bytearray(reference)
        for bank, offset, payload in edited:
            start = 16 + bank * text_assets.BANK_SIZE + offset
            candidate[start:start + len(payload)] = payload
        changes = text_assets.verify_control(reference, bytes(candidate), 16, original, edited)
        self.assertGreaterEqual(len(changes), 52)
        candidate[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'outside'):
            text_assets.verify_control(reference, bytes(candidate), 16, original, edited)
        with self.assertRaisesRegex(ValueError, 'missed a record'):
            text_assets.verify_control(reference, bytes(candidate), 16, original, [original[0], *edited[1:]])

    def test_original_duplicate_encoding_is_preserved_and_width_is_enforced(self):
        primary = bytearray(range(32))
        primary[1] = primary[2] = ord('X')
        primary[3] = ord('Y')
        secondary = bytearray(range(32))
        secondary[1] = ord('Z')
        slot = [{'kind': 'primary', 'index': 2}]
        self.assertEqual(text_assets._edited_tokens('X', slot, bytes(primary), bytes(secondary)), slot)
        self.assertEqual(text_assets._edited_tokens('Y', slot, bytes(primary), bytes(secondary)),
                         [{'kind': 'primary', 'index': 3}])
        primary[4] = ord('\n')
        newline_glyph = [{'kind': 'primary', 'index': 4}]
        self.assertEqual(text_assets._edited_tokens('\n', newline_glyph, bytes(primary), bytes(secondary)), newline_glyph)
        self.assertEqual(text_assets._edited_tokens('X', [{'kind': 'line_break'}], bytes(primary), bytes(secondary)),
                         [{'kind': 'primary', 'index': 1}])
        with self.assertRaisesRegex(ValueError, 'two-symbol'):
            text_assets._edited_tokens('Y', [{'kind': 'secondary', 'index': 1}], bytes(primary), bytes(secondary))

    def test_identity_shape_metadata_and_unencodable_edits_fail(self):
        for kind in ('identity', 'length', 'glyph', 'slots', 'padding'):
            asset = copy.deepcopy(self.asset)
            record = asset['records'][0]
            if kind == 'identity':
                asset['reference_sha256'] = 'b' * 64
            elif kind == 'length':
                record['text'] += 'A'
            elif kind == 'glyph':
                record['text'] = '€' + record['text'][1:]
            elif kind == 'slots':
                record['encoding_slots'][0]['index'] = 2
            else:
                record['padding_value'] ^= 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                text_assets.encode(asset, self.prg, self.reference)

    def test_export_is_idempotent_and_preserves_existing_edits(self):
        target = {'reference': {'file': {'sha256': self.reference}}}
        banks = (target, self.prg[:text_assets.BANK_SIZE], self.prg[text_assets.BANK_SIZE:], b'')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / text_assets.ASSET_PATH
            with (patch.object(text_assets, 'ROOT', root), patch.object(text_assets, 'load_audited_banks', return_value=banks),
                  contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO())):
                self.assertEqual(text_assets.main(), 0)
                self.assertEqual(text_assets.main(), 0)
                edit = b'{"user_edit":true}\n'
                path.write_bytes(edit)
                self.assertEqual(text_assets.main(), 1)
                self.assertEqual(path.read_bytes(), edit)


if __name__ == '__main__':
    unittest.main()
