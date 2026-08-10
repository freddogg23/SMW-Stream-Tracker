import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_fxpak_safe_upload_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FxpakSafeUploadNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_safe_title_removes_emoji_but_keeps_readable_title(self):
        safe_title = self.tracker.rom_builder_fxpak_safe_title(
            "✨ Pokémon Adventure 🎮",
            "12345",
        )

        self.assertEqual(safe_title, "Pokémon Adventure")
        self.assertTrue(safe_title.isprintable())
        self.assertNotIn("✨", safe_title)
        self.assertNotIn("🎮", safe_title)

    def test_emoji_only_title_uses_stable_catalog_fallback(self):
        self.assertEqual(
            self.tracker.rom_builder_fxpak_safe_title("🎮✨", "9876"),
            "SMWC 9876",
        )

    def test_sd_copy_uses_safe_name_without_renaming_local_rom(self):
        game = {
            "title": "🌟 Amazing Hack 🎮",
            "smwc_id": "42",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            local_rom = root / "🌟 Amazing Hack 🎮.sfc"
            sd_root = root / "All_Hacks"
            local_rom.write_bytes(b"test-rom")
            sd_root.mkdir()

            destination, status = self.tracker.rom_builder_copy_rom_to_sd(
                local_rom,
                sd_root,
                game,
            )

            self.assertEqual(status, "copied")
            self.assertEqual(
                destination.relative_to(sd_root),
                Path("A") / "Amazing Hack.sfc",
            )
            self.assertEqual(destination.read_bytes(), b"test-rom")
            self.assertTrue(local_rom.exists())

    def test_download_usb_path_uses_fxpak_safe_path_builder(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        worker = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_filtered_hack_download_worker"
        )
        called_names = {
            node.func.id
            for node in ast.walk(worker)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        }

        self.assertIn("rom_builder_fxpak_relative_rom_path", called_names)

    def test_usb_destination_error_uses_blue_app_popup(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        expected = '''self._show_localized_info(
                    "Hack Downloader",
                    (
                        "The FXPAK Pro USB destination is not ready. "'''

        self.assertIn(expected, source)

    def test_download_completion_saves_usb_mapping_without_worker_helper(self):
        class DummyWidget:
            def configure(self, **_values):
                return None

        class DummyVariable:
            def __init__(self):
                self.value = ""

            def set(self, value):
                self.value = value

        class DummyDatabase:
            def update_catalog_rom_path(self, *_args, **_kwargs):
                return None

            def save_rom_mapping(self, *_args, **_kwargs):
                return None

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.downloader_widgets = {
            "download_button": DummyWidget(),
            "cancel_button": DummyWidget(),
            "status_var": DummyVariable(),
        }
        app.config = {"fxpak_rom_mappings": {}}
        app.hack_catalog = [{"smwc_id": "123", "title": "Test Hack"}]
        app.stats_db = DummyDatabase()
        app.worker = None
        app.status_var = DummyVariable()
        app._translate_ui_text = lambda text: text
        app._refresh_downloader_preview = lambda **_values: None
        # Intentionally omit fxpak_path_map to reproduce the packaged-build
        # failure that occurred when the first USB mapping was completed.
        with mock.patch.object(self.tracker, "save_config"):
            app._finish_filtered_hack_download(
                [
                    {
                        "status": "ok",
                        "smwc_id": "123",
                        "fxpak_path": "/All_Hacks/T/Test Hack.sfc",
                    }
                ],
                {},
                True,
                "",
                Path("C:/TestLibrary"),
                None,
                "/All_Hacks",
            )

        self.assertEqual(
            app.fxpak_path_map["smwc:123"],
            "/All_Hacks/T/Test Hack.sfc",
        )
        self.assertEqual(
            app.config["fxpak_rom_mappings"]["smwc:123"],
            "/All_Hacks/T/Test Hack.sfc",
        )

    def test_saved_safe_filename_alias_displays_original_catalog_title(self):
        worker = self.tracker.TrackerWorker.__new__(
            self.tracker.TrackerWorker
        )
        game = {
            "catalog_key": "SMWC:9876",
            "mapping_key": "SMWC:9876",
            "smwc_id": "9876",
            "title": "🎮✨",
            "author": "Creator",
            "total_exits": 5,
        }
        worker.config = {}
        worker.fxpak_path_map = {}
        worker.hack_catalog = [dict(game)]
        worker.database = {}

        worker.register_fxpak_mapping(
            game,
            "/All_Hacks/S/SMWC 9876.sfc",
        )
        matched, _method = worker.find_hack(
            "SMWC 9876",
            worker.database,
        )

        self.assertIsNotNone(matched)
        self.assertEqual(matched["title"], "🎮✨")


if __name__ == "__main__":
    unittest.main()
