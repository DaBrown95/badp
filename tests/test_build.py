"""Source ownership, control rejection and archive safety using synthetic data."""

import io
import tarfile
import tempfile
from pathlib import Path
import unittest

from tools.build_rom import (MUTATIONS, extract_gaps, mutate_source, retire_control_intermediates,
                             source_regions, validate_mutations, verify_control)
from tools.setup import unpack_verified


def synthetic_map():
    regions = []
    for index, control in enumerate(MUTATIONS):
        regions.append({"id": control, "bank": 0, "cpu": hex(0x8000 + index * 4),
                        "size": 2, "kind": "data" if control in ("table", "vectors") else "code",
                        "control": control})
    regions.append({"id": "second-reset", "bank": 1, "cpu": "0xffe9", "size": 2,
                    "kind": "code", "control": "reset"})
    return {"bank_size": 0x8000, "cpu_base": 0x8000, "bank_count": 2, "regions": regions}


class SourceOwnershipTests(unittest.TestCase):
    def test_gaps_and_owned_regions_cover_each_physical_prg_byte_once(self):
        regions = source_regions(synthetic_map(), 16)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gaps = extract_gaps(bytes(0x10000), bytes(0x10000), regions, root / "inputs")
            self.assertEqual(sum(item["size"] for item in gaps) + sum(r["size"] for r in regions), 0x10000)
            self.assertEqual((root / "inputs/chr.bin").stat().st_size, 0x10000)
            self.assertEqual(regions[-1]["file_offset"], 16 + 0x8000 + 0x7fe9)

    def test_overlapping_regions_and_uncontrolled_map_are_rejected(self):
        config = synthetic_map()
        config["regions"][1]["cpu"] = "0x8001"
        with self.assertRaisesRegex(ValueError, "overlapping"):
            source_regions(config, 16)
        config = synthetic_map()
        config["regions"] = [r for r in config["regions"] if r["control"] != "vectors"]
        with self.assertRaisesRegex(ValueError, "each source-change control"):
            source_regions(config, 16)

    def test_control_requires_a_change_in_both_banks_and_nowhere_else(self):
        regions = source_regions(synthetic_map(), 16)
        first = next(r for r in regions if r["id"] == "reset")["file_offset"]
        second = next(r for r in regions if r["id"] == "second-reset")["file_offset"]
        reference = bytes(131088)
        changed = bytearray(reference)
        changed[first] = changed[second] = 1
        self.assertEqual(verify_control(reference, bytes(changed), regions, "reset"), [first, second])
        changed[second] = 0
        with self.assertRaisesRegex(ValueError, "second-reset"):
            verify_control(reference, bytes(changed), regions, "reset")
        changed[second] = changed[0] = 1
        with self.assertRaisesRegex(ValueError, "outside"):
            verify_control(reference, bytes(changed), regions, "reset")
        with self.assertRaisesRegex(ValueError, "size changed"):
            verify_control(reference, bytes(changed[:-1]), regions, "reset")

    def test_mutation_requires_exactly_one_unambiguous_marker(self):
        line = "    sei ; CONTROL_BOOT\n"
        self.assertIn("cli", mutate_source(line, "boot"))
        unrelated = "    sei ; CONTROL_BOOT_EXTRA\n"
        self.assertEqual(mutate_source(line + unrelated, "boot"), "    cli ; CONTROL_BOOT\n" + unrelated)
        for invalid in ("sei\n", line * 2, "    cli ; CONTROL_BOOT\n"):
            with self.subTest(source=invalid), self.assertRaisesRegex(ValueError, "one marked"):
                mutate_source(invalid, "boot")

    def test_preflight_rejects_a_later_invalid_control(self):
        source = "    sei ; CONTROL_BOOT\n"
        validate_mutations(source, ["boot"])
        with self.assertRaisesRegex(ValueError, "control wait"):
            validate_mutations(source, ["boot", "wait"])

    def test_retiring_control_intermediates_preserves_proof_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("candidate.o", "candidate.lst", "candidate.map", "candidate.dbg",
                         "candidate.nes", "rom.s", "unrelated.txt"):
                (root / name).write_text("synthetic")
            retire_control_intermediates(root)
            self.assertEqual({p.name for p in root.iterdir()},
                             {"candidate.nes", "rom.s", "unrelated.txt"})
            with self.assertRaises(FileNotFoundError):
                retire_control_intermediates(root)


class ArchiveSafetyTests(unittest.TestCase):
    def test_rejects_paths_outside_root_and_links(self):
        for name, kind in (("cc65-2.19/../../escape", tarfile.REGTYPE),
                           ("cc65-2.19/link", tarfile.SYMTYPE)):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = root / "synthetic.tar.gz"
                with tarfile.open(archive, "w:gz") as output:
                    item = tarfile.TarInfo(name)
                    item.type = kind
                    item.linkname = "/tmp/elsewhere" if kind == tarfile.SYMTYPE else ""
                    output.addfile(item, io.BytesIO(b""))
                with self.assertRaisesRegex(ValueError, "unsafe archive member"):
                    unpack_verified(archive, root / "out", "cc65-2.19")
                self.assertFalse((root / "escape").exists())


if __name__ == "__main__":
    unittest.main()
