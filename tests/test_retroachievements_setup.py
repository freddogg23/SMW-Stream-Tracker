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
            "volume=70\nusername=old\nhardcore=0\npopup_position=left\n"
            "show_leaderboards_updates=1\nshow_leaderboards_submission=0\n",
            username="LuigiPlayer",
            password="secret",
            hardcore=True,
        )
        self.assertIn("volume=70", text)
        self.assertEqual(text.count("username="), 1)
        self.assertIn("username=LuigiPlayer", text)
        self.assertIn("password=secret", text)
        self.assertIn("hardcore=1", text)
        self.assertEqual(text.count("popup_position="), 1)
        self.assertIn("popup_position=center", text)
        self.assertIn("multiline_desc=0", text)
        self.assertEqual(text.count("show_leaderboards_updates="), 1)
        self.assertIn("show_leaderboards_updates=0", text)
        self.assertEqual(text.count("show_leaderboards_submission="), 1)
        self.assertIn("show_leaderboards_submission=1", text)

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

    def test_achievement_hash_parser_excludes_games_without_sets(self):
        supported_hash = "a" * 32
        empty_set_hash = "b" * 32
        parsed = (
            self.tracker.parse_retroachievements_achievement_hash_library(
                [
                    {
                        "ID": 123,
                        "NumAchievements": 20,
                        "Hashes": [supported_hash],
                    },
                    {
                        "ID": 456,
                        "NumAchievements": 0,
                        "Hashes": [empty_set_hash],
                    },
                ]
            )
        )
        self.assertEqual(parsed, {supported_hash: 123})

    def test_achievement_hash_fetch_requests_filtered_games_and_hashes(self):
        requests = []

        def fake_api_get(endpoint, parameters, **kwargs):
            requests.append((endpoint, parameters, kwargs))
            return [
                {
                    "ID": 321,
                    "NumAchievements": 10,
                    "Hashes": ["c" * 32],
                }
            ]

        original = self.tracker.retroachievements_api_get
        self.tracker.retroachievements_api_get = fake_api_get
        try:
            hashes = (
                self.tracker.fetch_retroachievements_snes_achievement_hash_library(
                    "secret"
                )
            )
        finally:
            self.tracker.retroachievements_api_get = original

        self.assertEqual(hashes, {"c" * 32: 321})
        self.assertEqual(requests[0][0], "API_GetGameList.php")
        self.assertEqual(requests[0][1]["f"], 1)
        self.assertEqual(requests[0][1]["h"], 1)

    def test_cached_identification_without_achievements_is_removed(self):
        body = bytes(range(256)) * 4
        with tempfile.TemporaryDirectory() as temporary_directory:
            rom_path = Path(temporary_directory) / "empty-set.sfc"
            rom_path.write_bytes(body)
            stat_result = rom_path.stat()
            supported_hash = "d" * 32
            game_id, refreshed = (
                self.tracker.resolve_retroachievements_snes_rom(
                    rom_path,
                    {supported_hash: 123},
                    {
                        "size": stat_result.st_size,
                        "mtime_ns": stat_result.st_mtime_ns,
                        "game_id": 456,
                        "hash_revision": "old",
                    },
                    hash_revision="new",
                    supported_game_ids=frozenset({123}),
                )
            )

        self.assertEqual(game_id, 0)
        self.assertEqual(refreshed["game_id"], 0)

    def test_hash_library_revision_is_stable_and_detects_changes(self):
        first = self.tracker.retroachievements_hash_library_revision(
            {"a" * 32: 123, "b" * 32: 456}
        )
        reordered = self.tracker.retroachievements_hash_library_revision(
            {"b" * 32: 456, "a" * 32: 123}
        )
        changed = self.tracker.retroachievements_hash_library_revision(
            {"a" * 32: 123, "b" * 32: 789}
        )
        self.assertEqual(first, reordered)
        self.assertNotEqual(first, changed)

    def test_cached_no_match_is_rechecked_when_hash_library_changes(self):
        body = bytes(range(256)) * 4
        with tempfile.TemporaryDirectory() as temporary_directory:
            rom_path = Path(temporary_directory) / "newly-supported.sfc"
            rom_path.write_bytes(body)
            stat_result = rom_path.stat()
            old_library = {"a" * 32: 1}
            new_library = {hashlib.md5(body).hexdigest(): 9876}
            cached_entry = {
                "size": stat_result.st_size,
                "mtime_ns": stat_result.st_mtime_ns,
                "game_id": 0,
                "hash_revision": (
                    self.tracker.retroachievements_hash_library_revision(
                        old_library
                    )
                ),
            }

            game_id, refreshed = (
                self.tracker.resolve_retroachievements_snes_rom(
                    rom_path,
                    new_library,
                    cached_entry,
                    hash_revision=(
                        self.tracker.retroachievements_hash_library_revision(
                            new_library
                        )
                    ),
                )
            )

        self.assertEqual(game_id, 9876)
        self.assertEqual(refreshed["game_id"], 9876)
        self.assertIn(hashlib.md5(body).hexdigest(), refreshed["digests"])

    def test_cached_digests_pick_up_support_without_rereading_rom(self):
        digest = "c" * 32
        cached_entry = {
            "size": 1024,
            "mtime_ns": 22,
            "game_id": 0,
            "digests": [digest],
            "hash_revision": "old",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            rom_path = Path(temporary_directory) / "cached.sfc"
            rom_path.write_bytes(b"x" * 1024)
            current_stat = rom_path.stat()
            cached_entry["mtime_ns"] = current_stat.st_mtime_ns
            game_id, refreshed = (
                self.tracker.resolve_retroachievements_snes_rom(
                    rom_path,
                    {digest: 2468},
                    cached_entry,
                    hash_revision="new",
                )
            )

        self.assertEqual(game_id, 2468)
        self.assertEqual(refreshed["digests"], [digest])

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
        self.assertIn("_configure_mister_snes_live_tracking", source)

    def test_game_library_uses_cached_exact_hash_trophies(self):
        scan_source = inspect.getsource(
            self.tracker.TrackerApp._start_game_library_retroachievements_scan
        )
        resolver_source = inspect.getsource(
            self.tracker.resolve_retroachievements_snes_rom
        )
        library_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        self.assertIn("resolve_retroachievements_snes_rom", scan_source)
        self.assertIn("retroachievements_snes_hash_candidates", resolver_source)
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

        self.assertIn("tree.bbox(iid, title_column)", overlay_source)
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
        self.assertIn("_configure_mister_snes_live_tracking", mister_source)

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
