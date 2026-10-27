"""Target selection and reference rejection using synthetic ROMs only."""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.identify_rom import inspect_rom
from tools.project import IDENTITY_PARTS, audit_target, audit_targets, load_target, main


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("config/targets", "config/catalogues", "baseroms"):
            (self.root / directory).mkdir(parents=True)
        self.write_json("config/project.json", {
            "primary_target": "new", "target_order": ["new", "old"],
        })
        entries = []
        for target_id, fill in (("new", 1), ("old", 2)):
            data = b"NES\x1a" + bytes([1, 0]) + bytes(10) + bytes([fill]) * 16384
            path = f"baseroms/Synthetic {target_id}.nes"
            (self.root / path).write_bytes(data)
            report = inspect_rom(data)
            self.write_json(f"config/targets/{target_id}.json", {
                "id": target_id, "input_path": path,
                "reference": {part: report[part] for part in IDENTITY_PARTS},
            })
            entries.append({
                "target": target_id,
                "file_size": report["file"]["size"],
                "file_sha1": report["file"]["sha1"],
                "payload_size": report["prg_chr"]["size"],
                "payload_sha1": report["prg_chr"]["sha1"],
            })
        self.write_json("config/catalogues/no-intro-nes.json", {"entries": entries})

    def write_json(self, path, value):
        (self.root / path).write_text(json.dumps(value))

    def test_default_primary_and_explicit_other_target(self):
        for args, expected in ((["audit"], "new"), (["audit", "--target", "old"], "old")):
            output = io.StringIO()
            with self.subTest(args=args), patch("tools.project.ROOT", self.root), \
                    patch.dict(os.environ, {"BADP_TARGET": "", "BADP_ROM": ""}), \
                    patch.object(sys, "argv", ["project", *args]), redirect_stdout(output):
                self.assertEqual(main(), 0)
            result = json.loads(output.getvalue())
            self.assertTrue(result["ok"])
            self.assertEqual(result["results"][0]["target"], expected)

    def test_changed_payload_is_rejected_without_updating_reference(self):
        manifest = self.root / "config/targets/new.json"
        before = manifest.read_bytes()
        path = self.root / "baseroms/Synthetic new.nes"
        data = bytearray(path.read_bytes())
        data[100] ^= 1
        path.write_bytes(data)
        result = audit_target(self.root, "new")
        self.assertFalse(result["ok"])
        self.assertEqual(set(result["mismatches"]), {"file", "prg", "prg_chr"})
        self.assertEqual(manifest.read_bytes(), before)

    def test_changed_header_is_rejected_even_with_identical_payload(self):
        path = self.root / "baseroms/Synthetic new.nes"
        data = bytearray(path.read_bytes())
        data[6] ^= 1
        path.write_bytes(data)
        result = audit_target(self.root, "new")
        self.assertFalse(result["ok"])
        self.assertEqual(set(result["mismatches"]), {"file", "header_claims"})

    def test_wrong_version_is_rejected_despite_matching_layout(self):
        result = audit_target(self.root, "new", "baseroms/Synthetic old.nes")
        self.assertFalse(result["ok"])
        self.assertIn("prg", result["mismatches"])

    def test_all_audit_continues_after_missing_input_and_fails(self):
        (self.root / "baseroms/Synthetic new.nes").unlink()
        result = audit_targets(self.root, ["new", "old"])
        self.assertFalse(result["ok"])
        self.assertFalse(result["results"][0]["ok"])
        self.assertTrue(result["results"][1]["ok"])
        with self.assertRaisesRegex(ValueError, "no targets"):
            audit_targets(self.root, [])

    def test_manifest_must_agree_with_pinned_catalogue(self):
        target = load_target(self.root, "new")
        target["reference"]["prg_chr"]["sha1"] = "0" * 40
        self.write_json("config/targets/new.json", target)
        result = audit_target(self.root, "new")
        self.assertFalse(result["ok"])
        self.assertIn("disagrees with catalogue", result["error"])

    def test_unknown_target_is_rejected(self):
        result = audit_target(self.root, "unknown")
        self.assertFalse(result["ok"])
        self.assertIn("unknown target", result["error"])

    def test_all_cli_cannot_silently_use_single_target_or_file_override(self):
        for env in ({"BADP_TARGET": "old", "BADP_ROM": ""},
                    {"BADP_TARGET": "", "BADP_ROM": "example.nes"}):
            with self.subTest(env=env), patch.dict(os.environ, env), \
                    patch.object(sys, "argv", ["project", "audit", "--all"]), \
                    redirect_stdout(io.StringIO()), patch("sys.stderr", io.StringIO()), \
                    self.assertRaises(SystemExit) as raised:
                main()
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
