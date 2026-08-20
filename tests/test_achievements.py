import importlib.util
import inspect
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock
from urllib.error import HTTPError, URLError


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_achievements_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def game_progress_payload():
    return {
        "ID": 123,
        "Title": "Test Achievement World",
        "ConsoleID": 3,
        "NumAchievements": 3,
        "Achievements": {
            "9": {
                "ID": 9,
                "Title": "First Badge",
                "Description": "Clear the first stage.",
                "Points": 5,
                "BadgeName": "108302",
                "DisplayOrder": 1,
                "DateEarned": "2026-08-18 10:00:00",
                "DateEarnedHardcore": "2026-08-18 10:00:00",
            },
            "10": {
                "ID": 10,
                "Title": "Softcore Badge",
                "Description": "Clear the second stage.",
                "Points": 10,
                "BadgeName": "108303",
                "DisplayOrder": 2,
                "DateEarned": "2026-08-18 11:00:00",
            },
            "11": {
                "ID": 11,
                "Title": "Final Badge",
                "Description": "Finish the game.",
                "Points": 25,
                "BadgeName": "108304",
                "DisplayOrder": 3,
            },
        },
    }


class AchievementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_real_game_badges_and_hardcore_progress_are_normalized(self):
        hardcore = self.tracker.normalize_retroachievements_game_progress(
            game_progress_payload(),
            hardcore=True,
        )
        softcore = self.tracker.normalize_retroachievements_game_progress(
            game_progress_payload(),
            hardcore=False,
        )

        self.assertEqual(hardcore["source"], "RetroAchievements")
        self.assertEqual(hardcore["game_id"], 123)
        self.assertEqual(hardcore["unlocked"], 1)
        self.assertEqual(softcore["unlocked"], 2)
        self.assertEqual(hardcore["next"]["id"], 10)
        self.assertEqual(hardcore["recent"][0]["title"], "First Badge")
        self.assertEqual(
            hardcore["items"][0]["badge_url"],
            "https://retroachievements.org/Badge/108302.png",
        )

    def test_overview_uses_latest_snes_game_and_recent_ra_unlocks(self):
        calls = []

        def api_get(endpoint, parameters, *, web_api_key):
            calls.append((endpoint, dict(parameters), web_api_key))
            if endpoint == "API_GetUserRecentlyPlayedGames.php":
                return [
                    {"GameID": 5, "ConsoleID": 1, "Title": "Not SNES"},
                    {"GameID": 123, "ConsoleID": 3, "Title": "Test World"},
                    {"GameID": 124, "ConsoleID": 3, "Title": "Another World"},
                ]
            if endpoint == "API_GetGameInfoAndUserProgress.php":
                return game_progress_payload()
            if endpoint == "API_GetUserRecentAchievements.php":
                return [
                    {
                        "AchievementID": 12,
                        "Title": "Another Recent Badge",
                        "Description": "Clear another SNES game stage.",
                        "BadgeName": "108305",
                        "GameID": 124,
                        "GameTitle": "Another SNES World",
                        "Date": "2026-08-18 10:00:00",
                        "HardcoreMode": 1,
                    }
                ]
            raise AssertionError(endpoint)

        summary = self.tracker.fetch_retroachievements_overview(
            "PlayerOne",
            "api-key",
            hardcore=True,
            api_get=api_get,
        )

        self.assertEqual(summary["game_id"], 123)
        self.assertEqual(summary["recent"][0]["badge_name"], "108305")
        self.assertEqual(summary["recent"][0]["detail"], "Another SNES World")
        self.assertEqual(
            [call[0] for call in calls],
            [
                "API_GetUserRecentlyPlayedGames.php",
                "API_GetGameInfoAndUserProgress.php",
                "API_GetUserRecentAchievements.php",
            ],
        )
        self.assertTrue(all(call[2] == "api-key" for call in calls))

    def test_achievement_obs_file_contains_only_ra_progress(self):
        class Variable:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

        summary = self.tracker.normalize_retroachievements_game_progress(
            game_progress_payload(),
            hardcore=True,
        )
        with tempfile.TemporaryDirectory() as folder:
            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.config = {
                "output_folder": folder,
                "retroachievements_username": "PlayerOne",
                "retroachievements_web_api_key": "api-key",
            }
            app.output_folder_var = Variable(folder)

            self.assertTrue(app._export_achievements_to_obs(summary))
            output = Path(folder, "achievements.txt")
            text = output.read_text(encoding="utf-8")
            self.assertIn("RetroAchievements: Test Achievement World", text)
            self.assertIn("1/3 unlocked (hardcore)", text)
            self.assertIn("Latest: First Badge", text)
            self.assertNotIn("Adventure Begins", text)
            self.assertFalse(Path(folder, "achievements.txt.tmp").exists())

    def test_missing_api_credentials_never_create_tracker_milestones(self):
        summary = self.tracker.empty_retroachievements_summary(
            "setup_required",
            "Add your RetroAchievements username and Web API key in Setup.",
        )
        text = self.tracker.format_achievement_obs_text(summary)
        self.assertIn("RetroAchievements", text)
        self.assertIn("Web API key", text)
        self.assertNotIn("unlocked", text)

    def test_new_ui_fetches_real_ra_data_for_both_achievement_surfaces(self):
        overview_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_overview
        )
        library_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        setup_source = inspect.getsource(
            self.tracker.TrackerApp.open_retroachievements_setup
        )
        self.assertIn("render_retroachievements_overview", overview_source)
        self.assertIn("_retroachievements_badge_photo", overview_source)
        self.assertIn("update_selected_achievements", library_source)
        self.assertIn("_retroachievements_game_id", library_source)
        self.assertIn("_start_retroachievements_progress_refresh", library_source)
        self.assertIn("RetroAchievements Web API Key", setup_source)
        self.assertNotIn("One-Hour Run", library_source)

    def test_setup_continues_when_ra_display_check_has_dns_outage(self):
        def unavailable_api(*_args, **_kwargs):
            raise URLError(OSError(11001, "getaddrinfo failed"))

        warning = self.tracker.verify_retroachievements_display_credentials(
            "PlayerOne",
            "api-key",
            api_get=unavailable_api,
        )

        self.assertIn("Platform setup continued", warning)
        self.assertIn("badges and progress", warning)

    def test_setup_rejects_invalid_ra_api_credentials_with_clear_message(self):
        def rejected_api(*_args, **_kwargs):
            raise HTTPError(
                "https://retroachievements.org/API/test",
                401,
                "Unauthorized",
                {},
                None,
            )

        with self.assertRaisesRegex(ValueError, "Get Web API Key"):
            self.tracker.verify_retroachievements_display_credentials(
                "PlayerOne",
                "expired-key",
                api_get=rejected_api,
            )

    def test_setup_dns_error_is_sanitized_for_mister(self):
        message = self.tracker.retroachievements_setup_error_text(
            OSError(11001, "getaddrinfo failed"),
            "MiSTer",
        )

        self.assertIn("Settings > Platform", message)
        self.assertNotIn("11001", message)
        self.assertNotIn("getaddrinfo", message)

    def test_new_setup_form_scrolls_without_hiding_footer(self):
        setup_source = inspect.getsource(
            self.tracker.TrackerApp.open_retroachievements_setup
        )

        self.assertIn("setup_scroll_canvas", setup_source)
        self.assertIn("setup_scrollbar", setup_source)
        self.assertIn("resize_setup_body", setup_source)
        self.assertLess(
            setup_source.index("footer.pack"),
            setup_source.index("setup_body_host.pack"),
        )

    def test_partial_library_cache_is_replaced_by_complete_scan(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        self.assertIn("self.stats_db.load_catalog()", source)
        self.assertIn("def refresh_ready_games_from_disk", source)
        self.assertIn("probe_direct_paths=True", source)
        self.assertIn('name="GameLibraryCompleteScan"', source)

    def test_incomplete_live_catalog_forces_full_repair(self):
        initial_games = [
            {"smwc_id": str(index), "title": f"Game {index}"}
            for index in range(1, 3)
        ]
        repaired_games = [
            {"smwc_id": str(index), "title": f"Game {index}"}
            for index in range(1, 5)
        ]

        class Database:
            def __init__(self):
                self.games = list(initial_games)
                self.saved_metadata = {}

            def load_catalog(self):
                return list(self.games)

            @staticmethod
            def metadata():
                return {
                    "Official Hack Count": "4",
                    "SMWC Feature Metadata Complete": "1",
                }

            def refresh_from_smwcentral(self, games, _refreshed_at, version):
                self.games = list(games)
                return {
                    "fetched": len(games),
                    "new": 2,
                    "updated": 0,
                    "official": len(games),
                    "version": version,
                }

            @staticmethod
            def remove_repository_catalog_ids(_ids):
                return {"deleted": 0, "preserved": 0}

            def set_metadata(self, key, value):
                self.saved_metadata[key] = value

        captured = {}

        def fetch(_cancel_event, _progress_callback, known_ids):
            captured["known_ids"] = known_ids
            return {
                "games": repaired_games,
                "complete": True,
                "pages_read": 2,
                "total_pages": 2,
                "incremental": False,
            }

        database = Database()
        with mock.patch.object(
            self.tracker,
            "fetch_smwcentral_catalog",
            side_effect=fetch,
        ):
            result = self.tracker.refresh_catalog_from_smwcentral_site(
                database,
                threading.Event(),
            )

        self.assertEqual(captured["known_ids"], set())
        self.assertEqual(result["official"], 4)
        self.assertEqual(database.saved_metadata["Official Hack Count"], 4)


if __name__ == "__main__":
    unittest.main()
