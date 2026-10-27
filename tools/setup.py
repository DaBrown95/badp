"""Build the pinned cc65 tools locally from a checksum-verified source release."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec(root: Path = ROOT) -> dict:
    return json.loads((root / "config/cc65-toolchain.json").read_text())


def verified_tools(root: Path = ROOT) -> dict[str, Path]:
    pin = spec(root)
    directory = root / "toolchains" / pin["archive_root"]
    receipt = json.loads((directory / "badp-receipt.json").read_text())
    if receipt["revision"] != pin["revision"] or receipt["archive_sha256"] != pin["archive_sha256"]:
        raise ValueError("local toolchain receipt disagrees with the pinned cc65 source")
    tools = {}
    for name in pin["programs"]:
        path = directory / "bin" / name
        if sha256(path) != receipt["program_sha256"][name]:
            raise ValueError(f"local {name} differs from its setup receipt")
        tools[name] = path
    return tools


def unpack_verified(archive: Path, destination: Path, archive_root: str) -> None:
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        for member in members:
            name = PurePosixPath(member.name)
            if (name.is_absolute() or not name.parts or name.parts[0] != archive_root
                    or ".." in name.parts or not (member.isfile() or member.isdir())):
                raise ValueError(f"unsafe archive member: {member.name}")
        source.extractall(destination, members=members)


def main() -> int:
    pin = spec()
    root = ROOT / "toolchains"
    archive = root / "downloads" / pin["archive_name"]
    destination = root / pin["archive_root"]
    try:
        if destination.exists():
            verified_tools()
            print(f"Pinned {pin['name']} {pin['release']} is already installed locally.")
            return 0
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            print(f"Downloading {pin['archive_url']}", flush=True)
            with tempfile.NamedTemporaryFile(dir=archive.parent, delete=False) as tmp:
                download = Path(tmp.name)
                try:
                    with urllib.request.urlopen(pin["archive_url"], timeout=60) as response:
                        shutil.copyfileobj(response, tmp)
                except BaseException:
                    download.unlink(missing_ok=True)
                    raise
            if sha256(download) != pin["archive_sha256"]:
                download.unlink(missing_ok=True)
                raise ValueError("downloaded cc65 archive SHA-256 does not match the pin")
            os.replace(download, archive)
        if sha256(archive) != pin["archive_sha256"]:
            raise ValueError(f"cached cc65 archive SHA-256 does not match the pin: {archive}")
        with tempfile.TemporaryDirectory(prefix="cc65-setup-", dir=root) as temporary:
            unpack_verified(archive, Path(temporary), pin["archive_root"])
            source = Path(temporary) / pin["archive_root"]
            command = ["make", "-j4", f"BUILD_ID={pin['build_id']}", *pin["programs"]]
            subprocess.run(command, cwd=source / "src", check=True)
            programs = {name: sha256(source / "bin" / name) for name in pin["programs"]}
            receipt = {"revision": pin["revision"], "archive_sha256": pin["archive_sha256"],
                       "program_sha256": programs}
            (source / "badp-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
            source.rename(destination)
        verified_tools()
        print(f"Built {pin['name']} {pin['release']} in the local toolchains directory.")
        return 0
    except (OSError, ValueError, KeyError, tarfile.TarError, subprocess.CalledProcessError) as exc:
        print(f"Toolchain setup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
