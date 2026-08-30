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
            "MiSTer": ("sni", "mister"),
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

    def test_setup_menu_is_removed_and_platform_routes_remain(self):
        source = inspect.getsource(self.tracker.TrackerApp._build_menu_bar)
        next_step_source = inspect.getsource(
            self.tracker.TrackerApp._open_next_connection_setup_step
        )
        self.assertIn('self._open_settings_dialog("Platform")', next_step_source)
        self.assertNotIn('create_menu_button(\n                "Setup"', source)
        self.assertNotIn('("Setup", downloads_menu)', source)
        self.assertNotIn('"FXPAK Pro…"', source)
        self.assertIn("self.downloads_menu = None", source)
        self.assertIn("self.connection_option_menu_names = ()", source)

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

    def test_platform_launch_preferences_are_persistent_config_values(self):
        expected_defaults = {
            "auto_connect_on_startup": True,
            "return_to_dashboard_after_launch": True,
            "confirm_before_replacing_game": False,
            "save_tracker_data_automatically": True,
        }
        for key, expected in expected_defaults.items():
            with self.subTest(key=key):
                self.assertIn(key, self.tracker.DEFAULT_CONFIG)
                self.assertEqual(self.tracker.DEFAULT_CONFIG[key], expected)

    def test_settings_page_shows_only_the_selected_platform_setup(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_settings_dialog
        )
        self.assertIn("for platform_name in PLATFORM_OPTIONS", source)
        self.assertIn("platform_setup_pages[platform_name]", source)
        self.assertIn("for setup_name, setup_page in platform_setup_pages.items()", source)
        self.assertIn("setup_page.tkraise()", source)
        self.assertIn("setup_page.grid_remove()", source)
        self.assertIn("connection_service_codes_for(platform_name)", source)
        self.assertIn("platform_logo_label.configure(image=selected_logo)", source)

    def test_fxpak_downloader_uses_only_the_mounted_sd_copy_control(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_hack_downloader
        )
        self.assertIn('if selected_platform == "FXPAK Pro"', source)
        self.assertIn('"send_fxpak_sd_button"', source)
        self.assertIn('self.downloader_widgets["fxpak_sd_option"]', source)
        self.assertIn("columnspan=2", source)
        self.assertIn("copy_to_sd_var.set(False)", source)
        self.assertNotIn("Copy through FXPAK Pro USB", source)
        self.assertNotIn("Upload new ROMs through FXPAK Pro USB", source)

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
