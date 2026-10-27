"""Install the pinned macOS ARM64 MesenCE release into ignored local storage."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = b'{}\n'


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def spec(root: Path = ROOT) -> dict:
    pin = json.loads((root / 'config/mesence-toolchain.json').read_text())
    if pin.get('schema_version') != 1 or pin.get('platform') != 'darwin-arm64':
        raise ValueError('unsupported MesenCE toolchain pin')
    return pin


def executable_dir(root: Path, pin: dict) -> Path:
    return root / 'toolchains' / pin['install_dir'] / 'Mesen.app' / 'Contents' / 'MacOS'


def verify_emulator(root: Path = ROOT, require_core: bool = True) -> Path:
    pin = spec(root)
    directory = executable_dir(root, pin)
    exe = directory / 'Mesen'
    if digest_file(exe) != pin['executable_sha256']:
        raise ValueError('MesenCE executable differs from the pinned release')
    if (directory / 'settings.json').read_bytes() != SETTINGS:
        raise ValueError('MesenCE portable settings differ from the required empty settings')
    for name, key in (('MesenCore.dylib', 'core_sha256'), ('MesenNesDB.txt', 'database_sha256')):
        path = directory / name
        if not path.exists() and not require_core:
            continue
        if digest_file(path) != pin[key]:
            raise ValueError(f'MesenCE dependency differs from the pinned release: {name}')
    return exe


def extract_safe(archive: Path, destination: Path) -> None:
    """Extract the expected nested application ZIP without links or traversal."""
    with zipfile.ZipFile(archive) as outer:
        infos = outer.infolist()
        if len(infos) != 1 or infos[0].filename != 'Mesen.app.zip' or infos[0].file_size > 100_000_000:
            raise ValueError('unexpected MesenCE outer archive layout')
        if stat.S_ISLNK(infos[0].external_attr >> 16):
            raise ValueError('unsafe outer archive link')
        with tempfile.NamedTemporaryFile(dir=destination, suffix='.zip') as nested:
            with outer.open(infos[0]) as source:
                shutil.copyfileobj(source, nested)
            nested.flush()
            with zipfile.ZipFile(nested.name) as inner:
                members = inner.infolist()
                if sum(item.file_size for item in members) > 500_000_000:
                    raise ValueError('MesenCE archive is unexpectedly large')
                seen: set[str] = set()
                for item in members:
                    name = PurePosixPath(item.filename)
                    mode = item.external_attr >> 16
                    kind = stat.S_IFMT(mode)
                    canonical = str(name)
                    if (name.is_absolute() or not name.parts or name.parts[0] != 'Mesen.app'
                            or '..' in name.parts or '\\' in item.filename
                            or canonical != item.filename.rstrip('/') or canonical in seen
                            or kind not in (0, stat.S_IFREG, stat.S_IFDIR)
                            or (item.is_dir() and kind == stat.S_IFREG)
                            or (not item.is_dir() and kind == stat.S_IFDIR)):
                        raise ValueError(f'unsafe MesenCE archive member: {item.filename}')
                    seen.add(canonical)
                for item in members:
                    path = destination.joinpath(*PurePosixPath(item.filename).parts)
                    if item.is_dir():
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with inner.open(item) as source, path.open('wb') as output:
                            shutil.copyfileobj(source, output)
                        mode = item.external_attr >> 16
                        path.chmod((mode & 0o755) if mode else 0o644)


def main() -> int:
    try:
        pin = spec()
        if sys.platform != 'darwin' or platform.machine() != 'arm64':
            raise ValueError('the pinned MesenCE runtime currently supports macOS Apple silicon only')
        root = ROOT / 'toolchains'
        destination = root / pin['install_dir']
        if destination.exists():
            verify_emulator(require_core=False)
            print('Pinned MesenCE is already installed locally.')
            return 0
        downloads = root / 'downloads'
        downloads.mkdir(parents=True, exist_ok=True)
        archive = downloads / pin['archive_name']
        if not archive.exists():
            print(f"Downloading {pin['archive_url']}", flush=True)
            with tempfile.NamedTemporaryFile(dir=downloads, delete=False) as tmp:
                name = Path(tmp.name)
                try:
                    with urllib.request.urlopen(pin['archive_url'], timeout=120) as response:
                        shutil.copyfileobj(response, tmp)
                except BaseException:
                    name.unlink(missing_ok=True)
                    raise
            if digest_file(name) != pin['archive_sha256']:
                name.unlink(missing_ok=True)
                raise ValueError('downloaded MesenCE archive SHA-256 does not match the pin')
            os.replace(name, archive)
        if digest_file(archive) != pin['archive_sha256']:
            raise ValueError('cached MesenCE archive SHA-256 does not match the pin')
        with tempfile.TemporaryDirectory(prefix='mesence-setup-', dir=root) as tmp:
            stage = Path(tmp) / 'install'
            stage.mkdir()
            extract_safe(archive, stage)
            directory = stage / 'Mesen.app' / 'Contents' / 'MacOS'
            if digest_file(directory / 'Mesen') != pin['executable_sha256']:
                raise ValueError('MesenCE executable SHA-256 does not match the pin')
            # An empty settings file selects the documented portable folder and
            # avoids creating or changing the user's global Mesen configuration.
            (directory / 'settings.json').write_bytes(SETTINGS)
            stage.rename(destination)
        verify_emulator(require_core=False)
        print('Installed pinned MesenCE in the local toolchains directory.')
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'MesenCE setup failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
