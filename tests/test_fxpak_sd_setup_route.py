import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_fxpak_sd_setup_route_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DummyVariable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DummyRoot:
    def after_idle(self, callback):
        callback()
        return "after-id"


class FxpakSdSetupRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.root = DummyRoot()
        app.config = {
            "rom_builder_sd_folder": "",
            "rom_builder_copy_to_sd": False,
        }
        app.downloader_widgets = {
            "copy_to_sd_var": DummyVariable(True),
            "sd_folder_var": DummyVariable(""),
        }
        app._pending_fxpak_sd_setup_return = False
        app._pending_settings_action_flash = None
        return app

    def test_setup_finds_an_existing_all_hacks_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            card_root = Path(temporary_directory) / "FXPAK"
            hacks_folder = card_root / "All_Hacks"
            hacks_folder.mkdir(parents=True)
            app = self.make_app()
            app._mounted_fxpak_sd_volume_roots = lambda: [card_root]

            with mock.patch.object(
                self.tracker.filedialog,
                "askdirectory",
            ) as askdirectory:
                selected = app._setup_fxpak_sd_folder(parent=None)

            self.assertEqual(selected, hacks_folder)
            askdirectory.assert_not_called()

    def test_setup_creates_all_hacks_on_the_only_mounted_card(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            card_root = Path(temporary_directory) / "FXPAK"
            card_root.mkdir()
            app = self.make_app()
            app._mounted_fxpak_sd_volume_roots = lambda: [card_root]

            selected = app._setup_fxpak_sd_folder(parent=None)

            self.assertEqual(selected, card_root / "All_Hacks")
            self.assertTrue(selected.is_dir())

    def test_missing_folder_routes_checkbox_to_file_locations(self):
        app = self.make_app()
        opened_sections = []
        app._open_settings_dialog = opened_sections.append

        with mock.patch.object(self.tracker, "save_config"):
            app._on_downloader_fxpak_sd_toggle()

        self.assertFalse(app.downloader_widgets["copy_to_sd_var"].get())
        self.assertTrue(app._pending_fxpak_sd_setup_return)
        self.assertEqual(
            app._pending_settings_action_flash,
            ("File Locations", "Setup FXPAK Folder"),
        )
        self.assertEqual(opened_sections, ["File Locations"])

    def test_ready_folder_keeps_checkbox_selected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            app = self.make_app()
            app.config["rom_builder_sd_folder"] = temporary_directory
            opened_sections = []
            app._open_settings_dialog = opened_sections.append

            app._on_downloader_fxpak_sd_toggle()

            self.assertTrue(app.downloader_widgets["copy_to_sd_var"].get())
            self.assertEqual(
                app.downloader_widgets["sd_folder_var"].get(),
                temporary_directory,
            )
            self.assertEqual(opened_sections, [])


if __name__ == "__main__":
    unittest.main()
