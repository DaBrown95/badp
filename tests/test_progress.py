"""Progress accounting and stale-proof rejection with synthetic data only."""

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_build import synthetic_map
from test_map_assets import synthetic_prg
from test_menu_assets import synthetic_menu_prg
from test_palette_assets import synthetic_palettes
from test_ppu_assets import synthetic_ppu_assets
from tools import chr_assets, map_assets, map_layout_assets, menu_assets, palette_assets, ppu_assets, packed_text, sprite_assets, text_assets
from tools.build_rom import (MUTATIONS, PROOF_INPUTS, SYMBOL_CONTROLS, digest, mutate_include,
                             mutate_source, source_regions)
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
        include = ("synthetic include\n" + "".join(
            f"{name} = ${address:04X}\n" for name, (address, _) in SYMBOL_CONTROLS.items())).encode()
        link = b"synthetic linker config\n"
        source_map = {**synthetic_map(), "target": "us-v1.5", "source": "src/rom.s",
                      "linker_config": "config/link.cfg"}
        # Synthetic source-owned text destination headers split the local
        # message payloads into distinct gaps, matching the project geometry.
        synthetic_bank = synthetic_prg()[map_assets.BANK_SIZE:]
        for index in range(packed_text.RECORD_COUNT):
            pos = packed_text.TABLE_OFFSET + index * 2
            cpu = int.from_bytes(synthetic_bank[pos:pos + 2], "little")
            source_map["regions"].append({"id": f"synthetic-text-header-{index}", "bank": 1,
                                          "cpu": hex(cpu), "size": 2, "kind": "data", "control": "reset"})
        # Separate synthetic menu input from packed-text gaps without copying game data.
        source_map["regions"].append({"id": "synthetic-menu-separator", "bank": 1, "cpu": "0xf300",
                                      "size": 2, "kind": "data", "control": "reset"})
        for cpu, size in ((0xe000, 3), (0xe013, 3), (0xe036, 2)):
            source_map["regions"].append({"id": f"synthetic-palette-{cpu:x}", "bank": 0,
                                          "cpu": hex(cpu), "size": size, "kind": "data", "control": "reset"})
        for bank in (0, 1):
            for cpu, size in ((0xf800, 3), (0xf805, 3), (0xf80a, 1), (0xf80b, 2)):
                source_map["regions"].append({"id": f"synthetic-ppu-{bank}-{cpu:x}", "bank": bank,
                                              "cpu": hex(cpu), "size": size, "kind": "data", "control": "reset"})
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
        write(str(sprite_assets.MANIFEST), json.dumps({"schema_version": 1, "target": "us-v1.5",
              "source": "synthetic frames", "bank": 0, "cpu_addresses": ["0xf000", "0xf010"]}).encode())
        self.tools = {name: self.root / "fake-tools" / name for name in ("ca65", "ld65")}
        for name in self.tools:
            write(f"fake-tools/{name}", name.encode())

        preliminary_regions = source_regions(source_map, 16)
        code_regions = [r for r in preliminary_regions if r["kind"] == "code" and r["bank"] == 0]
        prg = bytearray(synthetic_ppu_assets(self.root, synthetic_palettes(self.root, synthetic_menu_prg(synthetic_prg()))))
        prg[0x7000:0x7004] = bytes([0x05, 0x11, 0x42, 0x37])
        prg[0x7010:0x7014] = bytes([0x06, 0x11, 0x43, 0x38])
        symbol_offsets = {}
        cursor = 0
        for name, (address, count) in SYMBOL_CONTROLS.items():
            selected = code_regions[cursor:cursor + count]
            if len(selected) != count:
                raise ValueError("not enough synthetic code regions")
            offsets = [r["file_offset"] for r in selected]
            for offset in offsets:
                prg[offset - 16:offset - 14] = address.to_bytes(2, "little")
            symbol_offsets[name] = offsets
            cursor += count
        prg = bytes(prg)
        reference = b"NES\x1a" + bytes([4, 8]) + bytes(10) + prg + bytes(65536)
        write("baseroms/synthetic.nes", reference)
        parsed = inspect_rom(reference)
        self.target = {"input_path": "baseroms/synthetic.nes",
                       "reference": {key: parsed[key] for key in IDENTITY_PARTS}}
        regions = source_regions(source_map, parsed["prg"]["offset"])
        for path, data in (("source/rom.s", source), ("source/nes.inc", include), ("source/link.cfg", link),
                           ("bible-adventures.nes", reference), ("bible-adventures.dbg", b"synthetic debug")):
            (self.proof_dir / path).parent.mkdir(parents=True, exist_ok=True)
            (self.proof_dir / path).write_bytes(data)
        asset, asset_payload, asset_source, asset_hash = map_assets.select(
            self.root, prg, digest(reference))
        inputs = self.proof_dir / "inputs"
        inputs.mkdir()
        (inputs / map_assets.GAP_NAME).write_bytes(asset_payload)
        (inputs / "map-chunks.json").write_bytes(map_assets.serialize(asset))
        changed_asset = map_assets.changed_asset(asset)
        changed_json = map_assets.serialize(changed_asset)
        changed_payload = map_assets.encode(changed_asset, prg, digest(reference))
        changed_reference = bytearray(reference)
        changed_reference[16 + map_assets.BANK_SIZE] ^= 1
        asset_candidate = bytes(changed_reference)
        asset_dir = self.proof_dir / "controls/map_asset"
        asset_dir.mkdir(parents=True)
        (asset_dir / "rom.s").write_bytes(source)
        (asset_dir / "map-chunks.json").write_bytes(changed_json)
        (asset_dir / "map-chunks.bin").write_bytes(changed_payload)
        (asset_dir / "candidate.nes").write_bytes(asset_candidate)
        asset_evidence = {"source": asset_source, "input_sha256": asset_hash,
                          "payload_sha256": digest(asset_payload),
                          "control": {"asset_sha256": digest(changed_json),
                                      "payload_sha256": digest(changed_payload),
                                      "candidate_sha256": digest(asset_candidate),
                                      "changed_offsets": [16 + map_assets.BANK_SIZE]}}
        layouts, spans, layout_source, layout_hash = map_layout_assets.select(self.root, prg, digest(reference))
        layout_gaps = map_layout_assets.gap_payloads(prg, regions, spans)
        (inputs / "map-layouts.json").write_bytes(map_layout_assets.serialize(layouts))
        for name, payload in layout_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_layouts = map_layout_assets.changed_asset(layouts)
        changed_layout_json = map_layout_assets.serialize(changed_layouts)
        changed_spans = map_layout_assets.encode(changed_layouts, prg, digest(reference))
        changed_gaps = map_layout_assets.gap_payloads(prg, regions, changed_spans)
        changed_names = [name for name in layout_gaps if layout_gaps[name] != changed_gaps[name]]
        if not changed_names or set(changed_names) != set(layout_gaps):
            raise ValueError("invalid synthetic layout control")
        changed_reference = bytearray(reference)
        changed_offsets = sorted(16 + item['bank'] * map_layout_assets.BANK_SIZE + int(item['cpu'], 0) - 0x8000 + 2
                                 for item in layouts['layouts'])
        for changed_offset in changed_offsets:
            changed_reference[changed_offset] ^= 1
        layout_candidate = bytes(changed_reference)
        layout_dir = self.proof_dir / "controls/layout_asset"
        layout_dir.mkdir(parents=True)
        (layout_dir / "rom.s").write_bytes(source)
        (layout_dir / "map-layouts.json").write_bytes(changed_layout_json)
        (layout_dir / "gaps").mkdir()
        for name in changed_names:
            (layout_dir / "gaps" / name).write_bytes(changed_gaps[name])
        (layout_dir / "candidate.nes").write_bytes(layout_candidate)
        layout_evidence = {"source": layout_source, "input_sha256": layout_hash,
                           "gap_sha256": {name: digest(payload) for name, payload in layout_gaps.items()},
                           "control": {"asset_sha256": digest(changed_layout_json),
                                       "gap_sha256": {name: digest(changed_gaps[name]) for name in changed_names},
                                       "candidate_sha256": digest(layout_candidate), "changed_offsets": changed_offsets}}
        text, text_spans, text_source, text_hash = text_assets.select(self.root, prg, digest(reference))
        text_gaps = map_layout_assets.gap_payloads(prg, regions, text_spans)
        if set(text_gaps) & set(layout_gaps):
            raise ValueError("synthetic text and layout gaps unexpectedly overlap")
        (inputs / "packed-text.json").write_bytes(text_assets.serialize(text))
        for name, payload in text_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_text = text_assets.changed_asset(text, prg)
        changed_text_json = text_assets.serialize(changed_text)
        changed_text_spans = text_assets.encode(changed_text, prg, digest(reference))
        changed_text_gaps = map_layout_assets.gap_payloads(prg, regions, changed_text_spans)
        text_names = [name for name in text_gaps if text_gaps[name] != changed_text_gaps[name]]
        if not text_names or set(text_names) != set(text_gaps):
            raise ValueError("invalid synthetic packed-text control")
        candidate_data = bytearray(reference)
        for bank, offset, payload in changed_text_spans:
            start = 16 + bank * map_assets.BANK_SIZE + offset
            candidate_data[start:start + len(payload)] = payload
        text_candidate = bytes(candidate_data)
        text_offsets = text_assets.verify_control(reference, text_candidate, 16, text_spans, changed_text_spans)
        text_dir = self.proof_dir / "controls/text_asset"
        text_dir.mkdir(parents=True)
        (text_dir / "rom.s").write_bytes(source)
        (text_dir / "packed-text.json").write_bytes(changed_text_json)
        (text_dir / "gaps").mkdir()
        for name in text_names:
            (text_dir / "gaps" / name).write_bytes(changed_text_gaps[name])
        (text_dir / "candidate.nes").write_bytes(text_candidate)
        text_evidence = {"source": text_source, "input_sha256": text_hash,
                         "gap_sha256": {name: digest(payload) for name, payload in text_gaps.items()},
                         "control": {"asset_sha256": digest(changed_text_json),
                                     "gap_sha256": {name: digest(changed_text_gaps[name]) for name in text_names},
                                     "candidate_sha256": digest(text_candidate), "changed_offsets": text_offsets}}
        sprites, sprite_spans, sprite_source, sprite_hash = sprite_assets.select(self.root, prg, digest(reference))
        sprite_gaps = map_layout_assets.gap_payloads(prg, regions, sprite_spans)
        if set(sprite_gaps) & (set(layout_gaps) | set(text_gaps)):
            raise ValueError("synthetic sprite and other assets unexpectedly overlap")
        (inputs / "sprite-frames.json").write_bytes(sprite_assets.serialize(sprites))
        for name, payload in sprite_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_sprites = sprite_assets.changed_asset(sprites)
        changed_sprite_json = sprite_assets.serialize(changed_sprites)
        changed_sprite_spans = sprite_assets.encode(self.root, changed_sprites, prg, digest(reference))
        changed_sprite_gaps = map_layout_assets.gap_payloads(prg, regions, changed_sprite_spans)
        sprite_names = [name for name in sprite_gaps if sprite_gaps[name] != changed_sprite_gaps[name]]
        candidate_data = bytearray(reference)
        for bank, offset, payload in changed_sprite_spans:
            start = 16 + bank * map_assets.BANK_SIZE + offset
            candidate_data[start:start + len(payload)] = payload
        sprite_candidate = bytes(candidate_data)
        sprite_offsets = sprite_assets.verify_control(reference, sprite_candidate, 16, sprites)
        sprite_dir = self.proof_dir / "controls/sprite_asset"
        sprite_dir.mkdir(parents=True)
        (sprite_dir / "rom.s").write_bytes(source)
        (sprite_dir / "sprite-frames.json").write_bytes(changed_sprite_json)
        (sprite_dir / "gaps").mkdir()
        for name in sprite_names:
            (sprite_dir / "gaps" / name).write_bytes(changed_sprite_gaps[name])
        (sprite_dir / "candidate.nes").write_bytes(sprite_candidate)
        sprite_evidence = {"source": sprite_source, "input_sha256": sprite_hash,
                           "gap_sha256": {name: digest(payload) for name, payload in sprite_gaps.items()},
                           "control": {"asset_sha256": digest(changed_sprite_json),
                                       "gap_sha256": {name: digest(changed_sprite_gaps[name]) for name in sprite_names},
                                       "candidate_sha256": digest(sprite_candidate), "changed_offsets": sprite_offsets}}
        menu, menu_spans, menu_source, menu_hash = menu_assets.select(self.root, prg, digest(reference))
        menu_gaps = map_layout_assets.gap_payloads(prg, regions, menu_spans)
        if set(menu_gaps) & (set(layout_gaps) | set(text_gaps) | set(sprite_gaps)):
            raise ValueError("synthetic menu and other assets unexpectedly overlap")
        (inputs / "menu-tiles.json").write_bytes(menu_assets.serialize(menu))
        for name, payload in menu_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_menu = menu_assets.changed_asset(menu)
        changed_menu_json = menu_assets.serialize(changed_menu)
        changed_menu_spans = menu_assets.encode(changed_menu, prg, digest(reference))
        changed_menu_gaps = map_layout_assets.gap_payloads(prg, regions, changed_menu_spans)
        menu_names = [name for name in menu_gaps if menu_gaps[name] != changed_menu_gaps[name]]
        candidate_data = bytearray(reference)
        for bank, offset, payload in changed_menu_spans:
            start = 16 + bank * map_assets.BANK_SIZE + offset
            candidate_data[start:start + len(payload)] = payload
        menu_candidate = bytes(candidate_data)
        menu_offsets = menu_assets.verify_control(reference, menu_candidate, 16, menu)
        menu_dir = self.proof_dir / "controls/menu_asset"
        menu_dir.mkdir(parents=True)
        (menu_dir / "rom.s").write_bytes(source)
        (menu_dir / "menu-tiles.json").write_bytes(changed_menu_json)
        (menu_dir / "gaps").mkdir()
        for name in menu_names:
            (menu_dir / "gaps" / name).write_bytes(changed_menu_gaps[name])
        (menu_dir / "candidate.nes").write_bytes(menu_candidate)
        menu_evidence = {"source": menu_source, "input_sha256": menu_hash,
                         "gap_sha256": {name: digest(payload) for name, payload in menu_gaps.items()},
                         "control": {"asset_sha256": digest(changed_menu_json),
                                     "gap_sha256": {name: digest(changed_menu_gaps[name]) for name in menu_names},
                                     "candidate_sha256": digest(menu_candidate), "changed_offsets": menu_offsets}}
        palette, palette_spans, palette_source, palette_hash = palette_assets.select(self.root, prg, digest(reference))
        palette_gaps = map_layout_assets.gap_payloads(prg, regions, palette_spans)
        if set(palette_gaps) & (set(layout_gaps) | set(text_gaps) | set(sprite_gaps)):
            raise ValueError("synthetic palette and other assets unexpectedly overlap")
        (inputs / "palettes.json").write_bytes(palette_assets.serialize(palette))
        for name, payload in palette_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_palette = palette_assets.changed_asset(palette)
        changed_palette_json = palette_assets.serialize(changed_palette)
        changed_palette_spans = palette_assets.encode(self.root, changed_palette, prg, digest(reference))
        changed_palette_gaps = map_layout_assets.gap_payloads(prg, regions, changed_palette_spans)
        palette_names = [name for name in palette_gaps if palette_gaps[name] != changed_palette_gaps[name]]
        candidate_data = bytearray(reference)
        for bank, offset, payload in changed_palette_spans:
            start = 16 + bank * map_assets.BANK_SIZE + offset
            candidate_data[start:start + len(payload)] = payload
        palette_candidate = bytes(candidate_data)
        palette_offsets = palette_assets.verify_control(reference, palette_candidate, 16, palette)
        palette_dir = self.proof_dir / "controls/palette_asset"
        palette_dir.mkdir(parents=True)
        (palette_dir / "rom.s").write_bytes(source)
        (palette_dir / "palettes.json").write_bytes(changed_palette_json)
        (palette_dir / "gaps").mkdir()
        for name in palette_names:
            (palette_dir / "gaps" / name).write_bytes(changed_palette_gaps[name])
        (palette_dir / "candidate.nes").write_bytes(palette_candidate)
        palette_evidence = {"source": palette_source, "input_sha256": palette_hash,
                         "gap_sha256": {name: digest(payload) for name, payload in palette_gaps.items()},
                         "control": {"asset_sha256": digest(changed_palette_json),
                                     "gap_sha256": {name: digest(changed_palette_gaps[name]) for name in palette_names},
                                     "candidate_sha256": digest(palette_candidate), "changed_offsets": palette_offsets}}
        ppu, ppu_spans, ppu_source, ppu_hash = ppu_assets.select(self.root, prg, digest(reference))
        ppu_gaps = map_layout_assets.gap_payloads(prg, regions, ppu_spans)
        if set(ppu_gaps) & (set(layout_gaps) | set(text_gaps) | set(sprite_gaps) | set(menu_gaps) | set(palette_gaps)):
            raise ValueError("synthetic ppu and other assets unexpectedly overlap")
        (inputs / "ppu-tiles.json").write_bytes(ppu_assets.serialize(ppu))
        for name, payload in ppu_gaps.items():
            (inputs / name).write_bytes(payload)
        changed_ppu = ppu_assets.changed_asset(ppu)
        changed_ppu_json = ppu_assets.serialize(changed_ppu)
        changed_ppu_spans = ppu_assets.encode(self.root, changed_ppu, prg, digest(reference))
        changed_ppu_gaps = map_layout_assets.gap_payloads(prg, regions, changed_ppu_spans)
        ppu_names = [name for name in ppu_gaps if ppu_gaps[name] != changed_ppu_gaps[name]]
        candidate_data = bytearray(reference)
        for bank, offset, payload in changed_ppu_spans:
            start = 16 + bank * map_assets.BANK_SIZE + offset
            candidate_data[start:start + len(payload)] = payload
        ppu_candidate = bytes(candidate_data)
        ppu_offsets = ppu_assets.verify_control(reference, ppu_candidate, 16, ppu)
        ppu_dir = self.proof_dir / "controls/ppu_asset"
        ppu_dir.mkdir(parents=True)
        (ppu_dir / "rom.s").write_bytes(source)
        (ppu_dir / "ppu-tiles.json").write_bytes(changed_ppu_json)
        (ppu_dir / "gaps").mkdir()
        for name in ppu_names:
            (ppu_dir / "gaps" / name).write_bytes(changed_ppu_gaps[name])
        (ppu_dir / "candidate.nes").write_bytes(ppu_candidate)
        ppu_evidence = {"source": ppu_source, "input_sha256": ppu_hash,
                         "gap_sha256": {name: digest(payload) for name, payload in ppu_gaps.items()},
                         "control": {"asset_sha256": digest(changed_ppu_json),
                                     "gap_sha256": {name: digest(changed_ppu_gaps[name]) for name in ppu_names},
                                     "candidate_sha256": digest(ppu_candidate), "changed_offsets": ppu_offsets}}
        chr_offset = parsed["chr"]["offset"]
        reference_chr = reference[chr_offset:chr_offset + parsed["chr"]["size"]]
        chr_asset, chr_payload, chr_source, chr_hash = chr_assets.select(self.root, reference_chr, digest(reference))
        (inputs / "chr.bin").write_bytes(chr_payload)
        (inputs / "chr-tiles.json").write_bytes(chr_assets.serialize(chr_asset))
        changed_chr = chr_assets.changed_asset(chr_asset)
        changed_chr_json = chr_assets.serialize(changed_chr)
        changed_chr_payload = chr_assets.encode(changed_chr, digest(reference))
        chr_candidate = reference[:chr_offset] + changed_chr_payload
        chr_offsets = chr_assets.verify_control(reference, chr_candidate, chr_offset)
        chr_dir = self.proof_dir / "controls/chr_asset"
        chr_dir.mkdir(parents=True)
        (chr_dir / "rom.s").write_bytes(source)
        (chr_dir / "chr-tiles.json").write_bytes(changed_chr_json)
        (chr_dir / "chr.bin").write_bytes(changed_chr_payload)
        (chr_dir / "candidate.nes").write_bytes(chr_candidate)
        chr_evidence = {"source": chr_source, "input_sha256": chr_hash,
                        "payload_sha256": digest(chr_payload),
                        "control": {"asset_sha256": digest(changed_chr_json),
                                    "payload_sha256": digest(changed_chr_payload),
                                    "candidate_sha256": digest(chr_candidate), "changed_offsets": chr_offsets}}
        controls = []
        for name in MUTATIONS:
            selected = [r for r in regions if r["control"] == name]
            candidate = bytearray(reference)
            changed = sorted(r["file_offset"] for r in selected)
            for offset in changed:
                candidate[offset] ^= 1
            candidate = bytes(candidate)
            candidate_source = mutate_source(source.decode(), name).encode()
            folder = self.proof_dir / "controls" / name
            folder.mkdir(parents=True)
            (folder / "rom.s").write_bytes(candidate_source)
            (folder / "candidate.nes").write_bytes(candidate)
            controls.append({"control": name, "changed_offsets": changed,
                             "affected_regions": [r["id"] for r in selected],
                             "source_sha256": digest(candidate_source), "candidate_sha256": digest(candidate)})
        symbol_controls = []
        for name, (address, _) in SYMBOL_CONTROLS.items():
            folder = self.proof_dir / "controls" / f"symbol_{name}"
            folder.mkdir(parents=True)
            changed_include = mutate_include(include.decode(), name).encode()
            candidate = bytearray(reference)
            for offset in symbol_offsets[name]:
                candidate[offset] = (address ^ 1) & 255
            candidate = bytes(candidate)
            (folder / "rom.s").write_bytes(source)
            (folder / "nes.inc").write_bytes(changed_include)
            (folder / "candidate.nes").write_bytes(candidate)
            symbol_controls.append({"symbol": name, "include_sha256": digest(changed_include),
                                    "candidate_sha256": digest(candidate), "changed_offsets": symbol_offsets[name]})
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
            "map_assets": asset_evidence, "layout_assets": layout_evidence, "text_assets": text_evidence,
            "sprite_assets": sprite_evidence, "menu_assets": menu_evidence, "palette_assets": palette_evidence, "ppu_assets": ppu_evidence, "chr_assets": chr_evidence,
            "counts": {"matching_code_bytes": code, "structured_data_bytes": data,
                       "local_prg_bytes": 65536 - code - data, "local_chr_bytes": 65536},
            "controls": controls, "symbol_controls": symbol_controls,
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

    def test_changed_or_missing_shared_symbol_control_is_rejected(self):
        (self.proof_dir / "controls/symbol_MapTileY/nes.inc").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "shared-symbol control"):
            self.verify()
        self.proof["symbol_controls"].pop()
        self.save_proof()
        with self.assertRaisesRegex(ValueError, "controls are incomplete"):
            self.verify()

    def test_changed_chr_asset_or_control_is_rejected(self):
        path = self.root / chr_assets.ASSET_PATH
        path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/chr-tiles.json").read_bytes()
        asset = json.loads(raw)
        path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "CHR asset build evidence is stale"):
            self.verify()
        self.proof["chr_assets"]["source"] = "local"
        self.proof["chr_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        path.write_bytes(chr_assets.serialize(chr_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "CHR asset build evidence is stale"):
            self.verify()
        path.unlink()
        self.proof["chr_assets"]["source"] = "reference"
        self.proof["chr_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        (self.proof_dir / "controls/chr_asset/chr.bin").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "CHR asset control"):
            self.verify()

    def test_changed_menu_asset_or_control_is_rejected(self):
        asset_path = self.root / menu_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/menu-tiles.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "menu asset build evidence is stale"):
            self.verify()
        self.proof["menu_assets"]["source"] = "local"
        self.proof["menu_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(menu_assets.serialize(menu_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "menu asset build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["menu_assets"]["source"] = "reference"
        self.proof["menu_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        name = next(iter(self.proof["menu_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/menu_asset/gaps" / name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "menu source-change control"):
            self.verify()

    def test_changed_palette_asset_or_control_is_rejected(self):
        asset_path = self.root / palette_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/palettes.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "palette asset build evidence is stale"):
            self.verify()
        self.proof["palette_assets"]["source"] = "local"
        self.proof["palette_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(palette_assets.serialize(palette_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "palette asset build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["palette_assets"]["source"] = "reference"
        self.proof["palette_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        name = next(iter(self.proof["palette_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/palette_asset/gaps" / name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "palette source-change control"):
            self.verify()

    def test_changed_ppu_asset_or_control_is_rejected(self):
        asset_path = self.root / ppu_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/ppu-tiles.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "ppu asset build evidence is stale"):
            self.verify()
        self.proof["ppu_assets"]["source"] = "local"
        self.proof["ppu_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(ppu_assets.serialize(ppu_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "ppu asset build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["ppu_assets"]["source"] = "reference"
        self.proof["ppu_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        name = next(iter(self.proof["ppu_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/ppu_asset/gaps" / name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "ppu source-change control"):
            self.verify()

    def test_changed_sprite_asset_or_control_is_rejected(self):
        asset_path = self.root / sprite_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/sprite-frames.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "sprite asset build evidence is stale"):
            self.verify()
        self.proof["sprite_assets"]["source"] = "local"
        self.proof["sprite_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(sprite_assets.serialize(sprite_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "sprite asset build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["sprite_assets"]["source"] = "reference"
        self.proof["sprite_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        name = next(iter(self.proof["sprite_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/sprite_asset/gaps" / name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "sprite source-change control"):
            self.verify()

    def test_changed_text_asset_or_control_is_rejected(self):
        asset_path = self.root / text_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/packed-text.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "packed-text build evidence is stale"):
            self.verify()
        self.proof["text_assets"]["source"] = "local"
        self.proof["text_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        prg = self.target["reference"]["prg"]
        reference = (self.root / self.target["input_path"]).read_bytes()
        payload = reference[prg["offset"]:prg["offset"] + prg["size"]]
        asset_path.write_bytes(text_assets.serialize(text_assets.changed_asset(asset, payload)))
        with self.assertRaisesRegex(ValueError, "packed-text build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["text_assets"]["source"] = "reference"
        self.proof["text_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        name = next(iter(self.proof["text_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/text_asset/gaps" / name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "packed-text source-change control"):
            self.verify()

    def test_changed_layout_asset_or_control_is_rejected(self):
        asset_path = self.root / map_layout_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        raw = (self.proof_dir / "inputs/map-layouts.json").read_bytes()
        asset = json.loads(raw)
        asset_path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "map layout build evidence is stale"):
            self.verify()
        self.proof["layout_assets"]["source"] = "local"
        self.proof["layout_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(map_layout_assets.serialize(map_layout_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "map layout build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["layout_assets"]["source"] = "reference"
        self.proof["layout_assets"]["input_sha256"] = digest(raw)
        self.save_proof()
        gap_name = next(iter(self.proof["layout_assets"]["control"]["gap_sha256"]))
        (self.proof_dir / "controls/layout_asset/gaps" / gap_name).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "map layout source-change control"):
            self.verify()

    def test_changed_map_asset_or_control_is_rejected(self):
        asset_path = self.root / map_assets.ASSET_PATH
        asset_path.parent.mkdir(parents=True)
        asset = map_assets.capture(synthetic_prg(), self.target["reference"]["file"]["sha256"])
        asset_bytes = map_assets.serialize(asset)
        asset_path.write_bytes(asset_bytes)
        with self.assertRaisesRegex(ValueError, "map asset build evidence is stale"):
            self.verify()
        self.proof["map_assets"]["source"] = "local"
        self.proof["map_assets"]["input_sha256"] = digest(asset_bytes)
        self.save_proof()
        self.verify()
        asset_path.write_bytes(map_assets.serialize(map_assets.changed_asset(asset)))
        with self.assertRaisesRegex(ValueError, "map asset build evidence is stale"):
            self.verify()
        asset_path.unlink()
        self.proof["map_assets"]["source"] = "reference"
        self.proof["map_assets"]["input_sha256"] = digest(asset_bytes)
        self.save_proof()
        (self.proof_dir / "controls/map_asset/map-chunks.bin").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "map asset source-change control"):
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
