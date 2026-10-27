"""Read-only target selection and audits against reviewed reference identities."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .identify_rom import inspect_rom


ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PARTS = ("file", "header_claims", "trainer", "prg", "chr", "prg_chr", "trailing")


def load_project(root: Path) -> dict:
    project = json.loads((root / "config/project.json").read_text())
    order = project["target_order"]
    if not order or len(order) != len(set(order)) or project["primary_target"] not in order:
        raise ValueError("project needs unique targets and a primary target in its target order")
    return project


def load_target(root: Path, target_id: str) -> dict:
    if target_id not in load_project(root)["target_order"]:
        raise ValueError(f"unknown target: {target_id}")
    target = json.loads((root / "config/targets" / f"{target_id}.json").read_text())
    if target["id"] != target_id:
        raise ValueError(f"target manifest id disagrees with its filename: {target_id}")
    # Corroboration is pinned separately from the locally measured SHA-256 values.
    catalogue = json.loads((root / "config/catalogues/no-intro-nes.json").read_text())
    entries = [entry for entry in catalogue["entries"] if entry["target"] == target_id]
    if len(entries) != 1:
        raise ValueError(f"expected one catalogue entry for {target_id}")
    entry = entries[0]
    for part, prefix in (("file", "file"), ("prg_chr", "payload")):
        for field in ("size", "sha1"):
            if target["reference"][part][field] != entry[f"{prefix}_{field}"]:
                raise ValueError(f"{target_id}: reference {part}.{field} disagrees with catalogue")
    return target


def input_path(root: Path, target: dict, override: str | None) -> Path:
    return root / (override or target["input_path"])


def audit_target(root: Path, target_id: str, override: str | None = None) -> dict:
    try:
        target = load_target(root, target_id)
        actual = inspect_rom(input_path(root, target, override).read_bytes())
        mismatches = [part for part in IDENTITY_PARTS if actual[part] != target["reference"][part]]
        return {"target": target_id, "ok": not mismatches, "mismatches": mismatches}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"target": target_id, "ok": False, "error": str(exc)}


def audit_targets(root: Path, target_ids: list[str], override: str | None = None) -> dict:
    if not target_ids:
        raise ValueError("no targets selected")
    results = [audit_target(root, target_id, override) for target_id in target_ids]
    return {"ok": all(result["ok"] for result in results), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("identify", "audit", "targets"))
    parser.add_argument("--target", default=os.environ.get("BADP_TARGET") or None)
    parser.add_argument("--rom", default=os.environ.get("BADP_ROM") or None)
    parser.add_argument("--all", action="store_true", help="audit all configured targets")
    args = parser.parse_args()
    if args.all and (args.command != "audit" or args.rom or args.target):
        parser.error("--all is for audit without TARGET/ROM overrides")
    try:
        project = load_project(ROOT)
        target_id = args.target or project["primary_target"]
        if args.command == "targets":
            result = project
        elif args.command == "identify":
            if args.rom:
                # Arbitrary inspection must still work for a new, unregistered ROM.
                result = inspect_rom((ROOT / args.rom).read_bytes())
            else:
                target = load_target(ROOT, target_id)
                result = {"target": target_id, **inspect_rom(input_path(ROOT, target, None).read_bytes())}
        else:
            selected = project["target_order"] if args.all else [target_id]
            result = audit_targets(ROOT, selected, args.rom)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Project command failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
