"""Progress accounting and stale-proof rejection with synthetic data only."""

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_build import synthetic_map
from tools.build_rom import MUTATIONS, PROOF_INPUTS, digest, mutate_source, source_regions
from tools.identify_rom import inspect_rom
from tools.progress import BEGIN, END, main, percentage, progress_data, render_table, update_readme, verify_primary
from tools.project import IDENTITY_PARTS


class PercentageTests(unittest.TestCase):
    def test_byte_denominator_and_rounding(self):
        self.assertEqual(percentage(165, 65536), "0.25%")
        self.assertEqual(percentage(0, 65536), "0.00%")
        self.assertEqual(percentage(1, 65536), "<0.01%")
        self.assertEqual(percentage(999999, 1000000), "99.99%")
        self.assertEqual(percentage(100, 100), "100.00%")
        for numerator, denominator in ((-1, 2), (1, 0), (3, 2)):
            with self.subTest(numerator=numerator, denominator=denominator), self.assertRaises(ValueError):
                percentage(numerator, denominator)

    def test_table_and_marker_replacement_are_unambiguous(self):
        data = {"targets": [{"version": "USA v1.5", "percentage": "0.25%", "status": "In progress",
                             "reconstructed_bytes": 165, "prg_bytes": 65536}]}
        table = render_table(data)
        self.assertIn("**0.25%** (165 / 65,536 bytes)", table)
        self.assertEqual(update_readme(f"before\n{BEGIN}\nold\n{END}\nafter", table),
                         f"before\n{table}\nafter")
        for text in ("no markers", f"{BEGIN}{BEGIN}{END}", f"{END}{BEGIN}"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                update_readme(text, table)

    def test_failed_validation_does_not_overwrite_existing_tracker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            (root / "README.md").write_text("original readme")
            (root / "assets/progress.json").write_text("original progress")
            with patch("tools.progress.ROOT", root), \
                    patch("tools.progress.progress_data", side_effect=ValueError("stale")), \
                    redirect_stderr(io.StringIO()):
                self.assertEqual(main(), 1)
            self.assertEqual((root / "README.md").read_text(), "original readme")
            self.assertEqual((root / "assets/progress.json").read_text(), "original progress")

    def test_unstarted_versions_have_zero_credit_and_new_work_fails_closed(self):
        project = {"primary_target": "us-v1.5", "target_order": ["us-v1.5", "us-v1.4"]}
        def target(target_id):
            revision = target_id.removeprefix("us-")
            return {"revision": revision, "region": "USA", "reconstruction_status": "unstarted",
                    "reference": {"prg": {"size": 65536}, "file": {"sha256": target_id}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("tools.progress.load_project", return_value=project), \
                    patch("tools.progress.load_target", side_effect=lambda _, name: target(name)), \
                    patch("tools.progress.verify_primary", return_value={"code_bytes": 121, "data_bytes": 44}):
                rows = progress_data(root)["targets"]
                self.assertEqual((rows[0]["percentage"], rows[0]["status"]), ("0.25%", "In progress"))
                self.assertEqual((rows[1]["percentage"], rows[1]["status"]), ("0.00%", "Not started"))
                (root / "config").mkdir()
                (root / "config/source-us-v1.4.json").write_text("{}")
                with self.assertRaisesRegex(ValueError, "target-specific verified progress support"):
                    progress_data(root)


class ProofFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proof_dir = self.root / "build/us-v1.5"
        self.proof_dir.mkdir(parents=True)

        def write(path, data):
            path = self.root / path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        self.write = write
        source = "".join(f"{old} ; {marker}\n" for marker, old, _ in MUTATIONS.values()).encode()
        include = b"synthetic include\n"
        link = b"synthetic linker config\n"
        source_map = {**synthetic_map(), "target": "us-v1.5", "source": "src/rom.s",
                      "linker_config": "config/link.cfg"}
        source_map_bytes = json.dumps(source_map).encode()
        write("src/rom.s", source)
        write("include/nes.inc", include)
        write("config/link.cfg", link)
        write("config/source-us-v1.5.json", source_map_bytes)
        write("config/targets/us-v1.5.json", b"synthetic target manifest")
        write("config/catalogues/no-intro-nes.json", b"synthetic catalogue")
        for path in PROOF_INPUTS:
            write(path, b"synthetic verifier")
        write("config/cc65-toolchain.json", json.dumps({"revision": "synthetic"}).encode())
        self.tools = {name: self.root / "fake-tools" / name for name in ("ca65", "ld65")}
        for name in self.tools:
            write(f"fake-tools/{name}", name.encode())

        reference = b"NES\x1a" + bytes([4, 8]) + bytes(10) + bytes(131072)
        write("baseroms/synthetic.nes", reference)
        parsed = inspect_rom(reference)
        self.target = {"input_path": "baseroms/synthetic.nes",
                       "reference": {key: parsed[key] for key in IDENTITY_PARTS}}
        regions = source_regions(source_map, parsed["prg"]["offset"])
        for path, data in (("source/rom.s", source), ("source/nes.inc", include), ("source/link.cfg", link),
                           ("bible-adventures.nes", reference), ("bible-adventures.dbg", b"synthetic debug")):
            (self.proof_dir / path).parent.mkdir(parents=True, exist_ok=True)
            (self.proof_dir / path).write_bytes(data)
        controls = []
        for name in MUTATIONS:
            selected = [r for r in regions if r["control"] == name]
            candidate = bytearray(reference)
            changed = sorted(r["file_offset"] for r in selected)
            for offset in changed:
                candidate[offset] = 1
            candidate = bytes(candidate)
            candidate_source = mutate_source(source.decode(), name).encode()
            folder = self.proof_dir / "controls" / name
            folder.mkdir(parents=True)
            (folder / "rom.s").write_bytes(candidate_source)
            (folder / "candidate.nes").write_bytes(candidate)
            controls.append({"control": name, "changed_offsets": changed,
                             "affected_regions": [r["id"] for r in selected],
                             "source_sha256": digest(candidate_source), "candidate_sha256": digest(candidate)})
        code = sum(r["size"] for r in regions if r["kind"] == "code")
        data = sum(r["size"] for r in regions if r["kind"] == "data")
        self.proof = {
            "target": "us-v1.5", "match": True, "source_sha256": digest(source),
            "debug_sha256": digest(b"synthetic debug"),
            "include_sha256": digest(include), "linker_config_sha256": digest(link),
            "source_map_sha256": digest(source_map_bytes),
            "target_manifest_sha256": digest(b"synthetic target manifest"),
            "catalogue_sha256": digest(b"synthetic catalogue"),
            "verification_input_sha256": {p: digest((self.root / p).read_bytes()) for p in PROOF_INPUTS},
            "toolchain_revision": "synthetic", "tool_sha256": {n: digest(p.read_bytes()) for n, p in self.tools.items()},
            "output_sha256": digest(reference), "reference_sha256": digest(reference),
            "component_matches": {p: True for p in IDENTITY_PARTS}, "source_regions": regions,
            "counts": {"matching_code_bytes": code, "structured_data_bytes": data,
                       "local_prg_bytes": 65536 - code - data, "local_chr_bytes": 65536},
            "controls": controls,
        }
        self.save_proof()

    def save_proof(self):
        (self.proof_dir / "proof.json").write_text(json.dumps(self.proof))

    def verify(self):
        with patch("tools.progress.verified_tools", return_value=self.tools):
            return verify_primary(self.root, self.target)

    def test_valid_synthetic_proof_and_stale_source(self):
        result = self.verify()
        self.assertGreater(result["code_bytes"], 0)
        self.write("src/rom.s", b"changed source")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.verify()

    def test_changed_debug_information_is_rejected(self):
        (self.proof_dir / "bible-adventures.dbg").write_bytes(b"changed debug")
        with self.assertRaisesRegex(ValueError, "debug information is stale"):
            self.verify()

    def test_modified_control_or_missing_control_is_rejected(self):
        (self.proof_dir / "controls/reset/candidate.nes").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "control"):
            self.verify()
        self.proof["controls"].pop()
        self.save_proof()
        with self.assertRaisesRegex(ValueError, "controls are incomplete"):
            self.verify()

    def test_changed_verifier_or_retained_output_is_rejected(self):
        self.write("tools/build_rom.py", b"changed verifier")
        with self.assertRaisesRegex(ValueError, "verification tools"):
            self.verify()
        self.write("tools/build_rom.py", b"synthetic verifier")
        (self.proof_dir / "bible-adventures.nes").write_bytes(b"changed output")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
