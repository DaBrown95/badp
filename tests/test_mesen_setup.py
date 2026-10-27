"""MesenCE archive validation tests use synthetic files only."""
from io import BytesIO
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

from tools.setup_mesen import extract_safe


def package(inner_name: str, symlink: bool = False) -> bytes:
    nested = BytesIO()
    with zipfile.ZipFile(nested, 'w') as archive:
        info = zipfile.ZipInfo(inner_name)
        info.create_system = 3
        info.external_attr = ((stat.S_IFLNK if symlink else stat.S_IFREG) | 0o755) << 16
        archive.writestr(info, b'synthetic')
    outer = BytesIO()
    with zipfile.ZipFile(outer, 'w') as archive:
        archive.writestr('Mesen.app.zip', nested.getvalue())
    return outer.getvalue()


class MesenSetupTests(unittest.TestCase):
    def test_extracts_regular_files_with_executable_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'release.zip'
            archive.write_bytes(package('Mesen.app/Contents/MacOS/Mesen'))
            output = root / 'output'
            output.mkdir()
            extract_safe(archive, output)
            executable = output / 'Mesen.app/Contents/MacOS/Mesen'
            self.assertEqual(executable.read_bytes(), b'synthetic')
            self.assertTrue(executable.stat().st_mode & stat.S_IXUSR)

    def test_rejects_traversal_and_links_before_extracting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, link in (('Mesen.app/../../escape', False),
                               ('Mesen.app/Contents/link', True),
                               ('Mesen.app/./duplicate', False),
                               ('other/file', False)):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'unsafe'):
                    archive = root / 'release.zip'
                    archive.write_bytes(package(name, link))
                    output = root / 'output'
                    output.mkdir(exist_ok=True)
                    extract_safe(archive, output)
                self.assertFalse((root / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
