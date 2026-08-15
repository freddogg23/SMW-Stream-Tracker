import importlib.util
import inspect
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_platform_menu_visibility_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PlatformSpecificMenuVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_each_platform_has_only_its_setup_menu_options(self):
        expected = {
            "FXPAK Pro": ("qusb2snes",),
            "RetroArch": ("sni", "retroarch"),
            "MiSTer": ("mister",),
        }
        for platform_name, option_names in expected.items():
            with self.subTest(platform=platform_name):
                self.assertEqual(
                    self.tracker.platform_setup_menu_options(platform_name),
                    option_names,
                )

    def test_unknown_platform_safely_uses_fxpak_menu(self):
        self.assertEqual(
            self.tracker.platform_setup_menu_options("unknown"),
            ("qusb2snes",),
        )

    def test_downloads_menu_hides_fxpak_browser_on_other_platforms(self):
        source = inspect.getsource(self.tracker.TrackerApp._build_menu_bar)
        self.assertIn("platform_setup_menu_options", source)
        self.assertIn('if selected_platform == "FXPAK Pro"', source)
        self.assertIn('"FXPAK Pro…"', source)
        self.assertIn("self.connection_option_menu_names", source)

    def test_platform_selection_rebuilds_only_the_menu_bar(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._on_platform_selected
        )
        self.assertIn(
            "self.root.after_idle(self._rebuild_platform_specific_menus)",
            source,
        )
        rebuild_source = inspect.getsource(
            self.tracker.TrackerApp._rebuild_platform_specific_menus
        )
        self.assertIn("self._build_menu_bar()", rebuild_source)
        self.assertNotIn("self._build_ui", rebuild_source)

    def test_settings_page_hides_inactive_platform_fields(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_settings_dialog
        )
        self.assertIn('if selected_platform == "RetroArch"', source)
        self.assertIn('elif selected_platform == "FXPAK Pro"', source)
        self.assertIn(
            'if selected_platform in {"FXPAK Pro", "RetroArch"}',
            source,
        )

    def test_fxpak_usb_downloader_controls_are_platform_gated(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_hack_downloader
        )
        self.assertIn('if selected_platform == "FXPAK Pro"', source)
        self.assertIn("Upload new ROMs through FXPAK Pro USB:", source)

    def test_platform_settings_notes_are_translated(self):
        notes = (
            "FXPAK Pro uses QUsb2Snes for live memory tracking. "
            "The workbook remains optional after import.",
            "RetroArch uses SNI for live memory tracking and also needs "
            "Network Commands enabled. The workbook remains optional "
            "after import.",
            "MiSTer uses its local network connection for live memory "
            "tracking. The workbook remains optional after import.",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            for note in notes:
                with self.subTest(language=language, note=note[:12]):
                    self.assertIn(note, self.tracker.UI_TRANSLATIONS[language])


if __name__ == "__main__":
    unittest.main()
