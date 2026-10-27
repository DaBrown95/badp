"""Generate per-version PRG coverage from current matching-build evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from .build_rom import MUTATIONS, PROOF_INPUTS, digest, mutate_source, source_regions, verify_control
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
    components = proof.get("component_matches", {})
    if set(components) != set(IDENTITY_PARTS) or any(value is not True for value in components.values()):
        raise ValueError("component comparisons are incomplete")

    regions = source_regions(source_map, parsed["prg"]["offset"])
    if proof.get("source_regions") != regions:
        raise ValueError("source ownership differs from the build proof")
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
