"""Synthetic fixtures only: container boundaries and identity failure cases."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.identify_rom import inspect_rom


def image(*, trainer=b"", chr_data=b"C" * 8192, extra=b"", flags7=0):
    header = bytearray(b"NES\x1a" + bytes(12))
    header[4] = 1
    header[5] = len(chr_data) // 8192
    header[6] = 0xB0 | (4 if trainer else 0)
    header[7] = flags7
    return bytes(header) + trainer + b"P" * 16384 + chr_data + extra


class IdentifyRomTests(unittest.TestCase):
    def test_payload_boundaries_and_known_hashes(self):
        report = inspect_rom(image())
        self.assertEqual(report["header_claims"]["mapper"], 11)
        self.assertEqual(report["prg"]["offset"], 16)
        self.assertEqual(report["chr"]["offset"], 16400)
        self.assertEqual(report["prg"]["sha256"], hashlib.sha256(b"P" * 16384).hexdigest())
        self.assertEqual(report["chr"]["sha1"], hashlib.sha1(b"C" * 8192).hexdigest())
        self.assertEqual(report["file"]["size"], 24592)

    def test_header_difference_does_not_change_payload_identity(self):
        original = image()
        changed = bytearray(original)
        changed[6] ^= 1
        a, b = inspect_rom(original), inspect_rom(bytes(changed))
        self.assertNotEqual(a["file"]["sha256"], b["file"]["sha256"])
        self.assertNotEqual(a["header_claims"]["hex"], b["header_claims"]["hex"])
        self.assertEqual(a["prg_chr"], b["prg_chr"])

    def test_trainer_is_excluded_from_prg_chr(self):
        a = inspect_rom(image())
        b = inspect_rom(image(trainer=b"T" * 512))
        self.assertEqual(b["trainer"]["size"], 512)
        self.assertEqual(b["prg"]["offset"], 528)
        self.assertEqual(a["prg_chr"]["sha256"], b["prg_chr"]["sha256"])
        self.assertNotEqual(a["file"]["sha256"], b["file"]["sha256"])

    def test_missing_chr_is_not_a_truncated_file(self):
        report = inspect_rom(image(chr_data=b""))
        self.assertEqual(report["chr"]["size"], 0)
        self.assertEqual(report["file"]["size"], 16400)

    def test_trailing_data_is_preserved_in_identity(self):
        report = inspect_rom(image(extra=b"unclassified"))
        self.assertEqual(report["trailing"]["size"], 12)
        self.assertEqual(report["trailing"]["offset"], 24592)
        self.assertTrue(report["notes"])
        self.assertEqual(report["file"]["sha256"], hashlib.sha256(image(extra=b"unclassified")).hexdigest())

    def test_nes2_extended_mapper_and_submapper(self):
        data = bytearray(image(flags7=0x28))
        data[8] = 0x31
        report = inspect_rom(bytes(data))
        self.assertEqual(report["header_claims"]["format"], "NES 2.0")
        self.assertEqual(report["header_claims"]["mapper"], 0x12B)
        self.assertEqual(report["header_claims"]["submapper"], 3)

    def test_nes2_extended_linear_size(self):
        header = bytearray(b"NES\x1a" + bytes(12))
        header[4] = 1
        header[7] = 8
        header[9] = 1
        report = inspect_rom(bytes(header) + bytes(257 * 16384))
        self.assertEqual(report["prg"]["size"], 257 * 16384)

    def test_nes2_exponent_sizes_are_bytes_not_bank_counts(self):
        header = bytearray(b"NES\x1a" + bytes(12))
        header[4] = (14 << 2) | 1  # 2**14 * 3 = 49152 PRG bytes.
        header[5] = 13 << 2        # 2**13 * 1 = 8192 CHR bytes.
        header[7] = 8
        header[9] = 0xFF
        report = inspect_rom(bytes(header) + bytes(49152 + 8192))
        self.assertEqual(report["prg"]["size"], 49152)
        self.assertEqual(report["chr"]["size"], 8192)
        self.assertEqual(report["trailing"]["size"], 0)

    def test_truncation_rejected_for_each_section(self):
        for data in (image()[:-1], image()[:100], image(trainer=b"T" * 512)[:100]):
            with self.subTest(size=len(data)), self.assertRaisesRegex(ValueError, "truncated"):
                inspect_rom(data)

    def test_invalid_containers_rejected(self):
        cases = (b"", bytes(16), image(flags7=4), image(flags7=12))
        for data in cases:
            with self.subTest(header=data[:16]), self.assertRaises(ValueError):
                inspect_rom(data)
        header = bytearray(image())
        header[4] = 0
        with self.assertRaisesRegex(ValueError, "no PRG"):
            inspect_rom(bytes(header))

    def test_dirty_legacy_header_is_flagged_and_not_rewritten(self):
        data = bytearray(image())
        data[11:16] = b"dirty"
        report = inspect_rom(bytes(data))
        self.assertEqual(report["header_claims"]["hex"], bytes(data[:16]).hex())
        self.assertIn("unreliable", report["notes"][0])

    def test_cli_reads_only_and_reports_missing_input(self):
        script = Path(__file__).resolve().parents[1] / "tools" / "identify_rom.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic image.nes"
            data = image()
            path.write_bytes(data)
            result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["file"]["size"], len(data))
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(list(Path(directory).iterdir()), [path])
            missing = subprocess.run([sys.executable, str(script), str(path.with_name("missing.nes"))], capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("ROM inspection failed", missing.stderr)
            self.assertNotIn("Traceback", missing.stderr)


if __name__ == "__main__":
    unittest.main()
