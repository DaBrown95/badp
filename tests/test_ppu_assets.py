"""PPU tile assets use synthetic command streams in both physical banks."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import ppu_assets


def synthetic_ppu_assets(root, prg=None):
    data = bytearray(prg if prg is not None else bytes(0x10000))
    for bank in (0, 1):
        start = bank * 0x8000 + 0x7800
        data[start:start + 11] = bytes([0xff, 0x20, 0, 0x41, 0x42, 0xfe, 0, 3, 0x43, 0xfd, 0])
    path = root / ppu_assets.MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'schema_version': 1, 'target': 'us-v1.5', 'source': 'synthetic',
                                'encoded_pointers': ['0x7800', '0xf800']}))
    return bytes(data)


class PpuAssetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.prg = synthetic_ppu_assets(self.root)
        self.sha = 'a' * 64
        self.asset = ppu_assets.capture(self.root, self.prg, self.sha)

    def test_round_trip_preserves_physical_banks_and_control_operands(self):
        spans = ppu_assets.encode(self.root, self.asset, self.prg, self.sha)
        self.assertEqual([(bank, offset) for bank, offset, _ in spans],
                         [(1, 0x7803), (1, 0x7808), (0, 0x7803), (0, 0x7808)])
        self.assertTrue(all(data == self.prg[bank * 0x8000 + p:bank * 0x8000 + p + len(data)]
                            for bank, p, data in spans))
        changed = copy.deepcopy(self.asset)
        changed['streams'][0]['payloads'][1]['tiles'][1] = 1
        self.assertEqual(ppu_assets.encode(self.root, changed, self.prg, self.sha)[1][2], bytes([0x43, 1]))

    def test_control_checks_every_payload_and_rejects_extra_changes(self):
        reference = b'R' * 16 + self.prg
        candidate = bytearray(reference)
        for bank, offset, data in ppu_assets.encode(self.root, ppu_assets.changed_asset(self.asset), self.prg, self.sha):
            start = 16 + bank * 0x8000 + offset
            candidate[start:start + len(data)] = data
        offsets = ppu_assets.verify_control(reference, bytes(candidate), 16, self.asset)
        self.assertEqual(len(offsets), 4)
        candidate[16 + 0x7801] ^= 1
        with self.assertRaises(ValueError): ppu_assets.verify_control(reference, bytes(candidate), 16, self.asset)

    def test_rejects_control_bytes_changed_offsets_and_pointer_aliases(self):
        for tiles in ([0, 0x42], [0xfe, 0x42], [0xff, 0x42], [True, 0x42], [1]):
            changed = copy.deepcopy(self.asset); changed['streams'][0]['payloads'][0]['tiles'] = tiles
            with self.subTest(tiles=tiles), self.assertRaises(ValueError):
                ppu_assets.encode(self.root, changed, self.prg, self.sha)
        changed = copy.deepcopy(self.asset); changed['streams'][0]['payloads'][0]['offset'] += 1
        with self.assertRaises(ValueError): ppu_assets.encode(self.root, changed, self.prg, self.sha)
        changed = copy.deepcopy(self.asset); changed['streams'][0]['encoded_pointer'] = '0xf800'
        with self.assertRaises(ValueError): ppu_assets.encode(self.root, changed, self.prg, self.sha)
        manifest = json.loads((self.root / ppu_assets.MANIFEST).read_text())
        manifest['encoded_pointers'] = ['0x7800', '0x7803']
        (self.root / ppu_assets.MANIFEST).write_text(json.dumps(manifest))
        with self.assertRaises(ValueError): ppu_assets.inventory(self.root, self.prg)

    def test_local_input_and_symlink(self):
        self.assertEqual(ppu_assets.select(self.root, self.prg, self.sha)[2], 'reference')
        path = self.root / ppu_assets.ASSET_PATH
        path.parent.mkdir(parents=True)
        path.write_bytes(ppu_assets.serialize(self.asset))
        self.assertEqual(ppu_assets.select(self.root, self.prg, self.sha)[2], 'local')
        path.unlink(); path.symlink_to(self.root / 'absent')
        with self.assertRaises(ValueError): ppu_assets.select(self.root, self.prg, self.sha)


if __name__ == '__main__':
    unittest.main()
