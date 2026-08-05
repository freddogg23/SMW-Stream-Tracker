import importlib.util
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACKER_SOURCE = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_stream_tracker_test_module",
        TRACKER_SOURCE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RomBuilderZipHandlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_damaged_readme_does_not_reject_valid_patch(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            archive_path = root / "broken-readme.zip"
            downloaded_path = root / "downloaded.zip"
            extract_directory = root / "patches"
            patch_data = b"BPS1-valid-test-patch"

            with zipfile.ZipFile(
                archive_path,
                "w",
                compression=zipfile.ZIP_STORED,
            ) as archive:
                archive.writestr("game.bps", patch_data)
                archive.writestr("readme.txt", b"documentation")

            with zipfile.ZipFile(archive_path, "r") as archive:
                readme_offset = archive.getinfo(
                    "readme.txt"
                ).header_offset

            archive_bytes = bytearray(archive_path.read_bytes())
            archive_bytes[readme_offset : readme_offset + 4] = b"BORK"
            archive_path.write_bytes(archive_bytes)

            with zipfile.ZipFile(archive_path, "r") as archive:
                self.assertEqual(archive.testzip(), "readme.txt")

            self.tracker.rom_builder_validate_patch_archive(
                archive_path
            )
            self.tracker.rom_builder_download_file(
                archive_path.as_uri(),
                downloaded_path,
                threading.Event(),
                retries=1,
            )
            patches = self.tracker.rom_builder_extract_patches(
                downloaded_path,
                extract_directory,
            )

            self.assertEqual(len(patches), 1)
            self.assertEqual(patches[0].name, "game.bps")
            self.assertEqual(patches[0].read_bytes(), patch_data)


if __name__ == "__main__":
    unittest.main()
