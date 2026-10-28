"""Generate per-version PRG coverage from current matching-build evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from . import map_assets, map_layout_assets, sprite_assets, text_assets
from .build_rom import (MUTATIONS, PROOF_INPUTS, SYMBOL_CONTROLS, digest, mutate_include, mutate_source,
                        source_regions, verify_control, verify_symbol_control)
from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, load_project, load_target
from .setup import verified_tools


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "us-v1.5"
BEGIN = "<!-- BEGIN GENERATED PROGRESS -->"
END = "<!-- END GENERATED PROGRESS -->"


def percentage(completed: int, total: int) -> str:
    """Round to two decimal places without implying incomplete work is 100%."""
    if total <= 0 or completed < 0 or completed > total:
        raise ValueError("invalid progress numerator or denominator")
    hundredths = (completed * 20000 + total) // (2 * total)
    if completed and hundredths == 0:
        return "<0.01%"
    if completed < total:
        hundredths = min(hundredths, 9999)
    return f"{hundredths // 100}.{hundredths % 100:02d}%"


def verify_primary(root: Path, target: dict) -> dict:
    """Refuse stale, incomplete or uncontrolled evidence instead of crediting it."""
    directory = root / "build" / PRIMARY
    proof = json.loads((directory / "proof.json").read_text())
    if proof.get("debug_sha256") != digest((directory / "bible-adventures.dbg").read_bytes()):
        raise ValueError("build proof debug information is stale")
    source_map_bytes = (root / "config/source-us-v1.5.json").read_bytes()
    source_map = json.loads(source_map_bytes)
    if source_map["target"] != PRIMARY or proof["target"] != PRIMARY or proof["match"] is not True:
        raise ValueError("missing or incorrect v1.5 matching proof")
    source_bytes = (root / source_map["source"]).read_bytes()
    include_bytes = (root / "include/nes.inc").read_bytes()
    link_bytes = (root / source_map["linker_config"]).read_bytes()
    expected_files = {
        "source_sha256": digest(source_bytes),
        "include_sha256": digest(include_bytes),
        "linker_config_sha256": digest(link_bytes),
        "source_map_sha256": digest(source_map_bytes),
        "target_manifest_sha256": digest((root / "config/targets/us-v1.5.json").read_bytes()),
        "catalogue_sha256": digest((root / "config/catalogues/no-intro-nes.json").read_bytes()),
    }
    if any(proof.get(key) != value for key, value in expected_files.items()):
        raise ValueError("build proof is stale for a source, configuration or reference manifest")
    for name, expected in (("source/rom.s", source_bytes), ("source/nes.inc", include_bytes),
                           ("source/link.cfg", link_bytes)):
        if (directory / name).read_bytes() != expected:
            raise ValueError(f"build proof snapshot differs: {name}")
    proof_inputs = {name: digest((root / name).read_bytes()) for name in PROOF_INPUTS}
    if proof.get("verification_input_sha256") != proof_inputs:
        raise ValueError("build proof is stale for its verification tools")
    pin = json.loads((root / "config/cc65-toolchain.json").read_text())
    tools = verified_tools(root)
    if (proof.get("toolchain_revision") != pin["revision"]
            or proof.get("tool_sha256") != {name: digest(path.read_bytes()) for name, path in tools.items()}):
        raise ValueError("build proof is stale for the pinned toolchain")

    reference = (root / target["input_path"]).read_bytes()
    parsed = inspect_rom(reference)
    if any(parsed[part] != target["reference"][part] for part in IDENTITY_PARTS):
        raise ValueError("reference input differs from the pinned target")
    output = (directory / "bible-adventures.nes").read_bytes()
    if (output != reference or digest(output) != target["reference"]["file"]["sha256"]
            or proof.get("output_sha256") != digest(output)
            or proof.get("reference_sha256") != digest(reference)):
        raise ValueError("retained build does not match the reference")
    prg_offset = parsed["prg"]["offset"]
    prg = reference[prg_offset:prg_offset + parsed["prg"]["size"]]
    asset, payload, asset_source, asset_input_hash = map_assets.select(root, prg, digest(reference))
    asset_evidence = proof.get("map_assets", {})
    if (asset_evidence.get("source") != asset_source or asset_evidence.get("input_sha256") != asset_input_hash
            or asset_evidence.get("payload_sha256") != digest(payload)
            or (directory / "inputs" / map_assets.GAP_NAME).read_bytes() != payload
            or (directory / "inputs/map-chunks.json").read_bytes() != map_assets.serialize(asset)):
        raise ValueError("map asset build evidence is stale")
    changed_asset = map_assets.changed_asset(asset)
    changed_json = map_assets.serialize(changed_asset)
    changed_payload = map_assets.encode(changed_asset, prg, digest(reference))
    asset_dir = directory / "controls/map_asset"
    asset_candidate = (asset_dir / "candidate.nes").read_bytes()
    asset_control = asset_evidence.get("control", {})
    if ((asset_dir / "rom.s").read_bytes() != source_bytes
            or (asset_dir / "map-chunks.json").read_bytes() != changed_json
            or (asset_dir / "map-chunks.bin").read_bytes() != changed_payload
            or asset_control.get("asset_sha256") != digest(changed_json)
            or asset_control.get("payload_sha256") != digest(changed_payload)
            or asset_control.get("candidate_sha256") != digest(asset_candidate)
            or asset_control.get("changed_offsets") != map_assets.verify_control(reference, asset_candidate, prg_offset)):
        raise ValueError("map asset source-change control is stale or invalid")
    components = proof.get("component_matches", {})
    if set(components) != set(IDENTITY_PARTS) or any(value is not True for value in components.values()):
        raise ValueError("component comparisons are incomplete")

    regions = source_regions(source_map, parsed["prg"]["offset"])
    if proof.get("source_regions") != regions:
        raise ValueError("source ownership differs from the build proof")
    layouts, layout_spans, layout_source, layout_input_hash = map_layout_assets.select(root, prg, digest(reference))
    layout_gaps = map_layout_assets.gap_payloads(prg, regions, layout_spans)
    layout_evidence = proof.get("layout_assets", {})
    if (layout_evidence.get("source") != layout_source
            or layout_evidence.get("input_sha256") != layout_input_hash
            or layout_evidence.get("gap_sha256") != {name: digest(payload) for name, payload in layout_gaps.items()}
            or (directory / "inputs/map-layouts.json").read_bytes() != map_layout_assets.serialize(layouts)
            or any((directory / "inputs" / name).read_bytes() != payload for name, payload in layout_gaps.items())):
        raise ValueError("map layout build evidence is stale")
    changed_layouts = map_layout_assets.changed_asset(layouts)
    changed_layout_json = map_layout_assets.serialize(changed_layouts)
    changed_layout_spans = map_layout_assets.encode(changed_layouts, prg, digest(reference))
    changed_layout_gaps = map_layout_assets.gap_payloads(prg, regions, changed_layout_spans)
    changed_names = [name for name in layout_gaps if changed_layout_gaps[name] != layout_gaps[name]]
    if not changed_names or set(changed_names) != set(layout_gaps):
        raise ValueError("map layout control does not affect every input gap")
    layout_dir = directory / "controls/layout_asset"
    layout_candidate = (layout_dir / "candidate.nes").read_bytes()
    layout_control = layout_evidence.get("control", {})
    if ((layout_dir / "rom.s").read_bytes() != source_bytes
            or (layout_dir / "map-layouts.json").read_bytes() != changed_layout_json
            or any((layout_dir / "gaps" / name).read_bytes() != changed_layout_gaps[name] for name in changed_names)
            or layout_control.get("asset_sha256") != digest(changed_layout_json)
            or layout_control.get("gap_sha256") != {name: digest(changed_layout_gaps[name]) for name in changed_names}
            or layout_control.get("candidate_sha256") != digest(layout_candidate)
            or layout_control.get("changed_offsets") != map_layout_assets.verify_control(reference, layout_candidate,
                                                                                             prg_offset, layouts)):
        raise ValueError("map layout source-change control is stale or invalid")
    text, text_spans, text_source, text_input_hash = text_assets.select(root, prg, digest(reference))
    text_gaps = map_layout_assets.gap_payloads(prg, regions, text_spans, allow_owned=True)
    if map_assets.GAP_NAME in text_gaps or set(text_gaps) & set(layout_gaps):
        raise ValueError("packed text and map assets share an input gap")
    text_evidence = proof.get("text_assets", {})
    if (text_evidence.get("source") != text_source or text_evidence.get("input_sha256") != text_input_hash
            or text_evidence.get("gap_sha256") != {name: digest(payload) for name, payload in text_gaps.items()}
            or (directory / "inputs/packed-text.json").read_bytes() != text_assets.serialize(text)
            or any((directory / "inputs" / name).read_bytes() != payload for name, payload in text_gaps.items())):
        raise ValueError("packed-text build evidence is stale")
    changed_text = text_assets.changed_asset(text, prg)
    changed_text_json = text_assets.serialize(changed_text)
    changed_text_spans = text_assets.encode(changed_text, prg, digest(reference))
    changed_text_gaps = map_layout_assets.gap_payloads(prg, regions, changed_text_spans, allow_owned=True)
    text_changed_names = [name for name in text_gaps if changed_text_gaps[name] != text_gaps[name]]
    if not text_changed_names or set(text_changed_names) != set(text_gaps):
        raise ValueError("packed-text control does not affect every input gap")
    text_dir = directory / "controls/text_asset"
    text_candidate = (text_dir / "candidate.nes").read_bytes()
    text_control = text_evidence.get("control", {})
    if ((text_dir / "rom.s").read_bytes() != source_bytes
            or (text_dir / "packed-text.json").read_bytes() != changed_text_json
            or any((text_dir / "gaps" / name).read_bytes() != changed_text_gaps[name] for name in text_changed_names)
            or text_control.get("asset_sha256") != digest(changed_text_json)
            or text_control.get("gap_sha256") != {name: digest(changed_text_gaps[name]) for name in text_changed_names}
            or text_control.get("candidate_sha256") != digest(text_candidate)
            or text_control.get("changed_offsets") != text_assets.verify_control(reference, text_candidate, prg_offset,
                                                                                     text_spans, changed_text_spans)):
        raise ValueError("packed-text source-change control is stale or invalid")
    sprites, sprite_spans, sprite_source, sprite_input_hash = sprite_assets.select(root, prg, digest(reference))
    sprite_gaps = map_layout_assets.gap_payloads(prg, regions, sprite_spans)
    if map_assets.GAP_NAME in sprite_gaps or set(sprite_gaps) & (set(layout_gaps) | set(text_gaps)):
        raise ValueError("sprite frames and other assets share an input gap")
    sprite_evidence = proof.get("sprite_assets", {})
    if (sprite_evidence.get("source") != sprite_source or sprite_evidence.get("input_sha256") != sprite_input_hash
            or sprite_evidence.get("gap_sha256") != {name: digest(payload) for name, payload in sprite_gaps.items()}
            or (directory / "inputs/sprite-frames.json").read_bytes() != sprite_assets.serialize(sprites)
            or any((directory / "inputs" / name).read_bytes() != payload for name, payload in sprite_gaps.items())):
        raise ValueError("sprite asset build evidence is stale")
    changed_sprites = sprite_assets.changed_asset(sprites)
    changed_sprite_json = sprite_assets.serialize(changed_sprites)
    changed_sprite_spans = sprite_assets.encode(root, changed_sprites, prg, digest(reference))
    changed_sprite_gaps = map_layout_assets.gap_payloads(prg, regions, changed_sprite_spans)
    sprite_changed_names = [name for name in sprite_gaps if changed_sprite_gaps[name] != sprite_gaps[name]]
    if not sprite_changed_names or set(sprite_changed_names) != set(sprite_gaps):
        raise ValueError("sprite control does not affect every input gap")
    sprite_dir = directory / "controls/sprite_asset"
    sprite_candidate = (sprite_dir / "candidate.nes").read_bytes()
    sprite_control = sprite_evidence.get("control", {})
    if ((sprite_dir / "rom.s").read_bytes() != source_bytes
            or (sprite_dir / "sprite-frames.json").read_bytes() != changed_sprite_json
            or any((sprite_dir / "gaps" / name).read_bytes() != changed_sprite_gaps[name] for name in sprite_changed_names)
            or sprite_control.get("asset_sha256") != digest(changed_sprite_json)
            or sprite_control.get("gap_sha256") != {name: digest(changed_sprite_gaps[name]) for name in sprite_changed_names}
            or sprite_control.get("candidate_sha256") != digest(sprite_candidate)
            or sprite_control.get("changed_offsets") != sprite_assets.verify_control(reference, sprite_candidate,
                                                                                         prg_offset, sprites)):
        raise ValueError("sprite source-change control is stale or invalid")
    code = sum(region["size"] for region in regions if region["kind"] == "code")
    data = sum(region["size"] for region in regions if region["kind"] == "data")
    counts = proof["counts"]
    if (counts["matching_code_bytes"] != code or counts["structured_data_bytes"] != data
            or counts["local_prg_bytes"] != parsed["prg"]["size"] - code - data
            or counts["local_chr_bytes"] != parsed["chr"]["size"]):
        raise ValueError("source and local byte totals differ from the verified layout")

    controls = proof["controls"]
    if len(controls) != len(MUTATIONS) or {c["control"] for c in controls} != set(MUTATIONS):
        raise ValueError("source-change controls are incomplete or duplicated")
    source_text = source_bytes.decode("utf-8")
    for control in controls:
        name = control["control"]
        candidate_source = mutate_source(source_text, name).encode("utf-8")
        control_dir = directory / "controls" / name
        candidate = (control_dir / "candidate.nes").read_bytes()
        if ((control_dir / "rom.s").read_bytes() != candidate_source
                or control["source_sha256"] != digest(candidate_source)
                or control["candidate_sha256"] != digest(candidate)
                or control["affected_regions"] != [r["id"] for r in regions if r["control"] == name]
                or control["changed_offsets"] != verify_control(reference, candidate, regions, name)):
            raise ValueError(f"source-change control is stale or invalid: {name}")
    symbol_controls = proof.get("symbol_controls", [])
    if (len(symbol_controls) != len(SYMBOL_CONTROLS)
            or {control["symbol"] for control in symbol_controls} != set(SYMBOL_CONTROLS)):
        raise ValueError("shared-symbol controls are incomplete or duplicated")
    for control in symbol_controls:
        name = control["symbol"]
        changed_include = mutate_include(include_bytes.decode("utf-8"), name).encode("utf-8")
        folder = directory / "controls" / f"symbol_{name}"
        candidate = (folder / "candidate.nes").read_bytes()
        if ((folder / "rom.s").read_bytes() != source_bytes
                or (folder / "nes.inc").read_bytes() != changed_include
                or control["include_sha256"] != digest(changed_include)
                or control["candidate_sha256"] != digest(candidate)
                or control["changed_offsets"] != verify_symbol_control(reference, candidate, regions, name)):
            raise ValueError(f"shared-symbol control is stale or invalid: {name}")
    return {"code_bytes": code, "data_bytes": data,
            "source_sha256": expected_files["source_sha256"],
            "source_map_sha256": expected_files["source_map_sha256"],
            "toolchain_revision": pin["revision"]}


def progress_data(root: Path) -> dict:
    project = load_project(root)
    if project["primary_target"] != PRIMARY:
        raise ValueError("progress verification currently supports us-v1.5 as the primary target")
    targets = []
    for target_id in project["target_order"]:
        target = load_target(root, target_id)
        prg_size = target["reference"]["prg"]["size"]
        if target_id == PRIMARY:
            verified = verify_primary(root, target)
            status = "In progress"
        else:
            if target["reconstruction_status"] != "unstarted" or (root / "config" / f"source-{target_id}.json").exists():
                raise ValueError(f"{target_id}: add target-specific verified progress support before reporting it")
            verified = {"code_bytes": 0, "data_bytes": 0}
            status = "Not started"
        total = verified["code_bytes"] + verified["data_bytes"]
        revision = target["revision"]
        label = f"{target['region']}, unversioned" if revision == "unversioned" else f"{target['region']} {revision}"
        targets.append({"target": target_id, "version": label, "status": status,
                        "prg_bytes": prg_size, "reconstructed_bytes": total,
                        "percentage": percentage(total, prg_size),
                        "code_bytes": verified["code_bytes"], "structured_data_bytes": verified["data_bytes"],
                        "reference_sha256": target["reference"]["file"]["sha256"],
                        "evidence": verified if target_id == PRIMARY else None})
    return {"schema_version": 1, "metric": "verified reconstructed PRG bytes / total physical PRG bytes",
            "complete_code_inventory": False, "chr_included": False, "targets": targets}


def render_table(data: dict) -> str:
    lines = [BEGIN, "| Version | Reconstructed PRG | Status |", "| --- | ---: | --- |"]
    for row in data["targets"]:
        lines.append(f"| {row['version']} | **{row['percentage']}** "
                     f"({row['reconstructed_bytes']:,} / {row['prg_bytes']:,} bytes) | {row['status']} |")
    return "\n".join([*lines, END])


def update_readme(original: str, table: str) -> str:
    if original.count(BEGIN) != 1 or original.count(END) != 1:
        raise ValueError("README must contain exactly one generated progress block")
    start, end = original.index(BEGIN), original.index(END)
    if end < start:
        raise ValueError("README progress block markers are reversed")
    return original[:start] + table + original[end + len(END):]


def main() -> int:
    try:
        data = progress_data(ROOT)
        readme = ROOT / "README.md"
        updated = update_readme(readme.read_text(), render_table(data))
        progress = ROOT / "assets/progress.json"
        progress.write_text(json.dumps(data, indent=2) + "\n")
        readme.write_text(updated)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f"Progress update failed: {exc}", file=sys.stderr)
        return 1
    print(f"Updated verified PRG progress for {len(data['targets'])} versions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
