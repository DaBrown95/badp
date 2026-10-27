"""Assemble the v1.5 scaffold, compare it, and retain source-change controls."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools


ROOT = Path(__file__).resolve().parents[1]
TARGET = "us-v1.5"

# Each mutation changes a meaningful instruction or structured data value.
# The marker must occur exactly once in the maintained source, even when its
# macro expands into two banks. Controls are built from isolated source copies.
MUTATIONS = {
    "boot": ("CONTROL_BOOT", "sei", "cli"),
    "wait": ("CONTROL_WAIT", "lda PPUSTATUS", "ldx PPUSTATUS"),
    "switch": ("CONTROL_SWITCH", "sta BankValues,y", "sta BankValues,x"),
    "table": ("CONTROL_TABLE", "$0C |", "$08 |"),
    "nmi": ("CONTROL_NMI", "ldy NmiSavedIndex", "ldx NmiSavedIndex"),
    "reset": ("CONTROL_RESET", "#$FF", "#$FE"),
    "vectors": ("CONTROL_VECTORS", "NmiHandler, ResetEntry, IrqHandler",
                "ResetEntry, ResetEntry, IrqHandler"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_regions(config: dict, prg_offset: int) -> list[dict]:
    """Validate each physical ownership span and calculate its file offset."""
    bank_size, cpu_base, count = config["bank_size"], config["cpu_base"], config["bank_count"]
    if (bank_size, cpu_base, count) != (0x8000, 0x8000, 2):
        raise ValueError("unexpected v1.5 physical bank layout")
    output = []
    for entry in config["regions"]:
        bank, cpu, size = entry["bank"], int(entry["cpu"], 0), entry["size"]
        if (bank not in range(count) or size <= 0 or cpu < cpu_base
                or cpu + size > cpu_base + bank_size or entry["kind"] not in ("code", "data")
                or entry["control"] not in MUTATIONS):
            raise ValueError(f"invalid source region: {entry}")
        output.append({**entry, "file_offset": prg_offset + bank * bank_size + cpu - cpu_base})
    if len({entry["id"] for entry in output}) != len(output):
        raise ValueError("duplicate source region id")
    if {entry["control"] for entry in output} != set(MUTATIONS):
        raise ValueError("each source-change control must own at least one region")
    for bank in range(count):
        end = cpu_base
        for entry in sorted((r for r in output if r["bank"] == bank), key=lambda r: int(r["cpu"], 0)):
            start = int(entry["cpu"], 0)
            if start < end:
                raise ValueError(f"overlapping source regions in bank {bank}")
            end = start + entry["size"]
    return output


def extract_gaps(prg: bytes, chr_data: bytes, regions: list[dict], inputs: Path) -> list[dict]:
    """Extract only the complement of claimed source spans into ignored files."""
    if len(prg) != 0x10000 or len(chr_data) != 0x10000:
        raise ValueError("unexpected v1.5 PRG/CHR sizes")
    inputs.mkdir(parents=True)
    gaps = []
    for bank in range(2):
        start = 0x8000
        spans = sorted((r for r in regions if r["bank"] == bank), key=lambda r: int(r["cpu"], 0))
        for region in [*spans, {"cpu": "0x10000", "size": 0}]:
            end = int(region["cpu"], 0)
            if end > start:
                name = f"bank{bank}_{start:04x}_{end:04x}.bin"
                offset = bank * 0x8000 + start - 0x8000
                payload = prg[offset:offset + end - start]
                (inputs / name).write_bytes(payload)
                gaps.append({"name": name, "bank": bank, "cpu_start": f"0x{start:04x}",
                             "size": len(payload), "sha256": digest(payload)})
            start = end + region["size"]
    (inputs / "chr.bin").write_bytes(chr_data)
    return gaps


def mutate_source(source: str, control: str) -> str:
    marker, old, new = MUTATIONS[control]
    lines = source.splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if marker in line]
    if len(indexes) != 1 or lines[indexes[0]].count(old) != 1:
        raise ValueError(f"control {control}: expected one marked, mutable source line")
    lines[indexes[0]] = lines[indexes[0]].replace(old, new, 1)
    return "".join(lines)


def verify_control(reference: bytes, candidate: bytes, regions: list[dict], control: str) -> list[int]:
    if len(candidate) != len(reference):
        raise ValueError(f"control {control}: output size changed")
    changed = {index for index, (a, b) in enumerate(zip(reference, candidate)) if a != b}
    selected = [entry for entry in regions if entry["control"] == control]
    allowed = set()
    for entry in selected:
        offsets = set(range(entry["file_offset"], entry["file_offset"] + entry["size"]))
        if not changed.intersection(offsets):
            raise ValueError(f"control {control}: no change in {entry['id']}")
        allowed.update(offsets)
    if not changed or changed - allowed:
        raise ValueError(f"control {control}: no difference or differences outside its source regions")
    return sorted(changed)


def assemble(work: Path, tools: dict[str, Path], source: Path, prefix: Path) -> Path:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        str(tools["ca65"]), "-g", "-I", "source", "--bin-include-dir", "inputs",
        "-l", str(prefix.with_suffix(".lst")), "-o", str(prefix.with_suffix(".o")), str(source),
    ], cwd=work, check=True)
    result = prefix.with_suffix(".nes")
    subprocess.run([
        str(tools["ld65"]), "-C", "source/link.cfg", "-m", str(prefix.with_suffix(".map")),
        "--dbgfile", str(prefix.with_suffix(".dbg")), "-o", str(result), str(prefix.with_suffix(".o")),
    ], cwd=work, check=True)
    return work / result


def build() -> dict:
    if os.environ.get("BADP_TARGET") not in (None, "", TARGET):
        raise ValueError("only us-v1.5 has a ROM build; select TARGET=us-v1.5")
    tool_paths = verified_tools()
    target = load_target(ROOT, TARGET)
    input_path = ROOT / (os.environ.get("BADP_ROM") or target["input_path"])
    reference = input_path.read_bytes()
    parsed = inspect_rom(reference)
    mismatch = [part for part in IDENTITY_PARTS if parsed[part] != target["reference"][part]]
    if mismatch:
        raise ValueError(f"reference input does not match {TARGET}: {', '.join(mismatch)}")
    source_map = (ROOT / "config/source-us-v1.5.json").read_bytes()
    config = json.loads(source_map)
    if config["target"] != TARGET:
        raise ValueError("source map target differs from build target")
    regions = source_regions(config, parsed["prg"]["offset"])
    source = (ROOT / config["source"]).read_text()
    include = (ROOT / "include/nes.inc").read_bytes()
    linker = (ROOT / config["linker_config"]).read_bytes()
    prg = reference[parsed["prg"]["offset"]:parsed["prg"]["offset"] + parsed["prg"]["size"]]
    chr_data = reference[parsed["chr"]["offset"]:parsed["chr"]["offset"] + parsed["chr"]["size"]]
    base = ROOT / "build"
    base.mkdir(exist_ok=True)
    final = base / TARGET
    if final.is_symlink():
        raise ValueError("refusing to replace a symlinked build directory")
    with tempfile.TemporaryDirectory(prefix=f".{TARGET}-", dir=base) as temporary:
        temp = Path(temporary)
        work = temp / "proof"
        (work / "source").mkdir(parents=True)
        (work / "source/rom.s").write_text(source)
        (work / "source/nes.inc").write_bytes(include)
        (work / "source/link.cfg").write_bytes(linker)
        gaps = extract_gaps(prg, chr_data, regions, work / "inputs")
        output_path = assemble(work, tool_paths, Path("source/rom.s"), Path("bible-adventures"))
        output = output_path.read_bytes()
        if output != reference:
            first = next((i for i, (a, b) in enumerate(zip(output, reference)) if a != b), None)
            raise ValueError(f"assembled ROM differs from reference (first byte {first}; "
                             f"sizes {len(output)} / {len(reference)})")
        output_parts = inspect_rom(output)
        component_matches = {part: output_parts[part] == parsed[part] for part in IDENTITY_PARTS}
        if not all(component_matches.values()):
            raise ValueError("assembled ROM components differ from the reference")
        controls = []
        for control in MUTATIONS:
            changed_source = mutate_source(source, control)
            control_dir = work / "controls" / control
            control_dir.mkdir(parents=True)
            (control_dir / "rom.s").write_text(changed_source)
            control_rom = assemble(work, tool_paths, Path("controls") / control / "rom.s",
                                   Path("controls") / control / "candidate")
            candidate = control_rom.read_bytes()
            changed = verify_control(reference, candidate, regions, control)
            controls.append({"control": control, "changed_offsets": changed,
                             "affected_regions": [r["id"] for r in regions if r["control"] == control],
                             "source_sha256": digest(changed_source.encode()),
                             "candidate_sha256": digest(candidate)})
        counts = {kind: sum(r["size"] for r in regions if r["kind"] == kind)
                  for kind in ("code", "data")}
        pin = json.loads((ROOT / "config/cc65-toolchain.json").read_text())
        proof = {
            "schema_version": 1, "target": TARGET, "match": True,
            "reference_sha256": parsed["file"]["sha256"], "output_sha256": digest(output),
            "component_matches": component_matches,
            "toolchain_revision": pin["revision"], "source_sha256": digest(source.encode()),
            "include_sha256": digest(include), "linker_config_sha256": digest(linker),
            "source_map_sha256": digest(source_map),
            "target_manifest_sha256": digest((ROOT / "config/targets/us-v1.5.json").read_bytes()),
            "catalogue_sha256": digest((ROOT / "config/catalogues/no-intro-nes.json").read_bytes()),
            "tool_sha256": {name: digest(path.read_bytes()) for name, path in tool_paths.items()},
            "source_regions": regions, "local_prg_gaps": gaps,
            "counts": {"matching_code_bytes": counts["code"], "structured_data_bytes": counts["data"],
                       "local_prg_bytes": sum(g["size"] for g in gaps),
                       "local_chr_bytes": len(chr_data), "container_header_bytes": 16},
            "controls": controls,
        }
        (work / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
        previous = temp / "previous"
        if final.exists():
            final.rename(previous)
        try:
            work.rename(final)
        except OSError:
            if previous.exists():
                previous.rename(final)
            raise
    return proof


def main() -> int:
    try:
        proof = build()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"ROM build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"target": TARGET, "match": proof["match"],
                      "output": f"build/{TARGET}/bible-adventures.nes",
                      "proof": f"build/{TARGET}/proof.json",
                      "counts": proof["counts"], "controls_passed": len(proof["controls"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
