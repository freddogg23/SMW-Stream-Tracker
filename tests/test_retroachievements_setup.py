import importlib.util
import hashlib
import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_retroachievements_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RetroAchievementsSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_retroarch_setup_preserves_other_settings_and_reports_ready(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "retroarch.cfg"
            config_path.write_text(
                'video_driver = "vulkan"\n'
                'cheevos_enable = "false"\n'
                'cheevos_username = "old"\n'
                'cheevos_token = "old-token"\n',
                encoding="utf-8",
            )
            self.tracker.write_retroarch_retroachievements_settings(
                config_path,
                username="MarioPlayer",
                password="secret-password",
                hardcore=True,
            )
            text = config_path.read_text(encoding="utf-8")
            status = self.tracker.retroarch_retroachievements_status(
                config_path
            )

        self.assertIn('video_driver = "vulkan"', text)
        self.assertEqual(text.count("cheevos_enable ="), 1)
        self.assertIn('cheevos_enable = "true"', text)
        self.assertIn('cheevos_username = "MarioPlayer"', text)
        self.assertIn('cheevos_token = ""', text)
        self.assertTrue(status["ready"])
        self.assertTrue(status["hardcore"])
        self.assertEqual(status["username"], "MarioPlayer")
        self.assertNotIn("password", status)

    def test_retroarch_existing_account_can_reuse_token_without_password(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "retroarch.cfg"
            config_path.write_text(
                'cheevos_username = "MarioPlayer"\n'
                'cheevos_token = "saved-token"\n',
                encoding="utf-8",
            )
            self.tracker.write_retroarch_retroachievements_settings(
                config_path,
                username="MarioPlayer",
                hardcore=False,
            )
            text = config_path.read_text(encoding="utf-8")

        self.assertIn('cheevos_token = "saved-token"', text)
        self.assertIn('cheevos_hardcore_mode_enable = "false"', text)

    def test_changing_retroarch_account_requires_password(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "retroarch.cfg"
            config_path.write_text(
                'cheevos_username = "old"\n'
                'cheevos_token = "saved-token"\n',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                self.tracker.write_retroarch_retroachievements_settings(
                    config_path,
                    username="new",
                )

    def test_mister_setup_updates_credentials_and_preserves_other_values(self):
        text = self.tracker.mister_retroachievements_config_text(
            "volume=70\nusername=old\nhardcore=0\n",
            username="LuigiPlayer",
            password="secret",
            hardcore=True,
        )
        self.assertIn("volume=70", text)
        self.assertEqual(text.count("username="), 1)
        self.assertIn("username=LuigiPlayer", text)
        self.assertIn("password=secret", text)
        self.assertIn("hardcore=1", text)

    def test_mister_ini_enables_ra_main_and_preserves_other_sections(self):
        text = self.tracker.mister_retroachievements_ini_text(
            "[MiSTer]\nbootscreen=1\n\n[RA_*]\nmain=Old_Main\nvideo_mode=6\n\n[menu]\nvideo_mode=0\n"
        )
        self.assertIn("[MiSTer]\nbootscreen=1", text)
        self.assertIn("[RA_*]\nmain=MiSTer_RA\nvideo_mode=6", text)
        self.assertIn("[menu]\nvideo_mode=0", text)
        self.assertEqual(text.count("main=MiSTer_RA"), 1)

    def test_snes_hash_candidates_strip_a_copier_header(self):
        body = bytes(range(256)) * 4
        header = b"H" * 512
        with tempfile.TemporaryDirectory() as temporary_directory:
            rom_path = Path(temporary_directory) / "test.smc"
            rom_path.write_bytes(header + body)
            hashes = self.tracker.retroachievements_snes_hash_candidates(
                rom_path
            )
        self.assertEqual(hashes[0], hashlib.md5(body).hexdigest())
        self.assertIn(hashlib.md5(header + body).hexdigest(), hashes)

    def test_hash_library_parser_keeps_only_valid_supported_hashes(self):
        valid_hash = "a" * 32
        parsed = self.tracker.parse_retroachievements_hash_library(
            json.dumps(
                {
                    "Success": True,
                    "MD5List": {
                        valid_hash: 123,
                        "not-a-hash": 456,
                        "b" * 32: 0,
                    },
                }
            )
        )
        self.assertEqual(parsed, {valid_hash: 123})

    def test_ra2snes_asset_selection_prefers_current_platform(self):
        release = {
            "assets": [
                {
                    "name": "RA2Snes-macOS.zip",
                    "browser_download_url": "https://github.com/Factor-64/RA2Snes/releases/download/v1/mac.zip",
                },
                {
                    "name": "RA2Snes-Windows-x64.zip",
                    "browser_download_url": "https://github.com/Factor-64/RA2Snes/releases/download/v1/win.zip",
                },
                {
                    "name": "Source-code.zip",
                    "browser_download_url": "https://github.com/Factor-64/RA2Snes/releases/download/v1/source.zip",
                },
            ]
        }
        name, url = self.tracker.select_ra2snes_release_asset(
            release,
            windows=True,
            macos=False,
        )
        self.assertEqual(name, "RA2Snes-Windows-x64.zip")
        self.assertTrue(url.endswith("win.zip"))

    def test_platform_settings_expose_one_click_setup(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_settings_dialog
        )
        self.assertEqual(source.count('"retroachievements",'), 3)
        self.assertIn("self.open_retroachievements_setup", source)
        dialog_source = inspect.getsource(
            self.tracker.TrackerApp.open_retroachievements_setup
        )
        self.assertIn("write_retroarch_retroachievements_settings", dialog_source)
        self.assertIn("_configure_mister_retroachievements", dialog_source)
        self.assertIn("_install_ra2snes", dialog_source)

    def test_setup_normalizes_every_supported_platform_without_crashing(self):
        self.assertEqual(
            self.tracker.normalize_platform_name("RetroArch"),
            "RetroArch",
        )
        self.assertEqual(
            self.tracker.normalize_platform_name("MiSTer FPGA"),
            "MiSTer",
        )
        self.assertEqual(
            self.tracker.normalize_platform_name("SD2SNES"),
            "FXPAK Pro",
        )
        self.assertEqual(
            self.tracker.normalize_platform_name("unknown"),
            "FXPAK Pro",
        )

    def test_fxpak_launch_reopens_ra2snes_after_setup(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._run_fxpak_game_launch
        )
        self.assertIn("retroachievements_setup_platforms", source)
        self.assertIn("_ensure_qusb2snes_running", source)
        self.assertIn("_start_ra2snes_if_configured", source)

    def test_mister_setup_installs_the_official_ra_components(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_retroachievements_components
        )
        self.assertIn("MISTER_RETROACHIEVEMENTS_DB_URL", source)
        self.assertIn("RetroAchievementsDB_MiSTer", self.tracker.MISTER_RETROACHIEVEMENTS_DB_URL)
        self.assertIn("DOWNLOADER_INI_PATH", source)
        self.assertIn("MiSTer_RA", source)
        self.assertIn("mister_retroachievements_ini_text", source)

    def test_game_library_uses_cached_exact_hash_trophies(self):
        scan_source = inspect.getsource(
            self.tracker.TrackerApp._start_game_library_retroachievements_scan
        )
        library_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        self.assertIn("retroachievements_snes_hash_candidates", scan_source)
        self.assertIn("_cached_retroachievements_snes_hash_library", scan_source)
        self.assertIn("_retroachievements_trophy_photo", library_source)
        self.assertIn("_start_game_library_retroachievements_scan", library_source)
        self.assertIn(": Supports Retro Achievements", library_source)
        self.assertIn("retroachievements_var", library_source)

    def test_downloader_uses_the_same_status_legend_and_title_trophies(self):
        opener_source = inspect.getsource(
            self.tracker.TrackerApp.open_hack_downloader
        )
        preview_source = inspect.getsource(
            self.tracker.TrackerApp._refresh_downloader_preview
        )
        overlay_source = inspect.getsource(
            self.tracker.TrackerApp._render_downloader_title_overlay
        )
        scan_source = inspect.getsource(
            self.tracker.TrackerApp._start_game_library_retroachievements_scan
        )

        self.assertIn(": Supports Retro Achievements", opener_source)
        self.assertIn('"Hall of Fame"', opener_source)
        self.assertIn(
            "Waiting for SMW Central Moderation",
            opener_source,
        )
        self.assertIn("_retroachievements_trophy_photo", opener_source)
        self.assertIn('self.downloader_widgets["preview_build"] = None', opener_source)
        self.assertIn("_retroachievements_scan_revision", preview_source)
        self.assertIn("_downloader_catalog_index", preview_source)
        self.assertIn("_retroachievements_scan_revision", scan_source)
        self.assertIn("_retroachievements_game_id", overlay_source)
        self.assertIn("canonical_game = self.hack_catalog", overlay_source)

    def test_library_special_status_colors_only_overlay_the_title_cell(self):
        overlay_source = inspect.getsource(
            self.tracker.TrackerApp._render_game_title_tree_overlay
        )
        library_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )

        self.assertIn('tree.bbox(iid, "#0")', overlay_source)
        self.assertIn('STREAM_DESK["yellow"]', overlay_source)
        self.assertIn('STREAM_DESK["red"]', overlay_source)
        self.assertIn('text=tr("Hall of Fame")', library_source)
        self.assertIn(
            "Waiting for SMW Central Moderation",
            library_source,
        )

    def test_mister_trophy_games_offer_the_achievement_core(self):
        launch_source = inspect.getsource(
            self.tracker.TrackerApp._launch_catalog_game
        )
        mister_source = inspect.getsource(
            self.tracker.TrackerApp._run_mister_game_launch
        )
        self.assertIn("_retroachievements_game_id", launch_source)
        self.assertIn("messagebox.askyesnocancel", launch_source)
        self.assertIn("_mister_use_retroachievements_core", launch_source)
        self.assertIn("/media/fat/_RA_Cores/Cores/SNES.rbf", mister_source)
        self.assertIn("retroachievements=use_retroachievements_core", mister_source)

    def test_platform_only_settings_save_does_not_rebuild_the_ui(self):
        source = inspect.getsource(self.tracker.TrackerApp._open_settings_dialog)
        self.assertIn("if language_changed:", source)
        self.assertIn("old_language", source)
        appearance_source = inspect.getsource(
            self.tracker.TrackerApp._apply_widget_appearance
        )
        self.assertIn("widget.winfo_exists()", appearance_source)
        self.assertIn("tuple(widget.winfo_children())", appearance_source)


if __name__ == "__main__":
    unittest.main()
