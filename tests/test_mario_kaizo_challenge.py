import importlib.util
import inspect
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import sys
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_mario_kaizo_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MarioKaizoChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self, *, target=500, total_exits=12):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "mario_kaizo_challenge_playlist": [
                {
                    "catalog_key": "first-hack",
                    "title": "First Hack",
                    "total_exits": total_exits,
                    "difficulty": "Kaizo: Intermediate",
                },
                {
                    "catalog_key": "second-hack",
                    "title": "Second Hack",
                    "total_exits": 20,
                    "difficulty": "Kaizo: Expert",
                },
            ],
            "mario_kaizo_challenge_target_levels": target,
            "mario_kaizo_challenge_target_hours": target // 10,
            "mario_kaizo_challenge_completed_levels": 0,
            "mario_kaizo_challenge_current_index": 0,
            "mario_kaizo_challenge_started_at": "",
            "mario_kaizo_challenge_active": True,
            "mario_kaizo_challenge_history": [],
        }
        app.exits_var = SimpleNamespace(get=lambda: "Exits: 12 / 12")
        app.current_hack_record = dict(
            app.config["mario_kaizo_challenge_playlist"][0]
        )
        app._refresh_mario_kaizo_dashboard_queue = mock.Mock()
        app._launch_mario_kaizo_current_hack = mock.Mock()
        app._set_active_game_mode_session = mock.Mock()
        app._show_localized_info = mock.Mock()
        app._close_game_mode_dialog = mock.Mock()
        app._translate_ui_text = lambda text: str(text)
        app.root = None
        return app

    def test_default_config_persists_the_entire_challenge_state(self):
        defaults = self.tracker.DEFAULT_CONFIG
        self.assertEqual(defaults["mario_kaizo_challenge_playlist"], [])
        self.assertEqual(defaults["mario_kaizo_challenge_target_levels"], 500)
        self.assertEqual(defaults["mario_kaizo_challenge_target_hours"], 50)
        self.assertEqual(defaults["mario_kaizo_challenge_completed_levels"], 0)
        self.assertEqual(defaults["mario_kaizo_challenge_current_index"], 0)
        self.assertFalse(defaults["mario_kaizo_challenge_active"])
        self.assertEqual(
            defaults["mario_kaizo_challenge_filters"],
            {
                "search": "",
                "creator": "Any",
                "difficulty": "Any",
                "hack_type": "Any",
            },
        )

    def test_dashboard_shares_the_playlist_and_has_curate_button(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_dashboard
        )
        self.assertIn("self._dashboard_up_next_games(3)", source)
        self.assertIn('text="Curate Playlist"', source)
        self.assertIn("self._open_mario_kaizo_playlist_curator", source)
        self.assertIn('"Hack Completed" if mario_kaizo_active', source)

    def test_skipping_advances_without_awarding_exits(self):
        app = self.make_app(target=500, total_exits=12)
        with mock.patch.object(self.tracker, "save_config") as save:
            app._skip_mario_kaizo_hack()

        self.assertEqual(
            app.config["mario_kaizo_challenge_completed_levels"],
            0,
        )
        self.assertEqual(app.config["mario_kaizo_challenge_current_index"], 1)
        history = app.config["mario_kaizo_challenge_history"]
        self.assertEqual(history[0]["levels"], 0)
        self.assertTrue(history[0]["skipped"])
        save.assert_called_once_with(app.config)
        app._refresh_mario_kaizo_dashboard_queue.assert_called_once_with()
        app._launch_mario_kaizo_current_hack.assert_called_once_with()

    def test_active_challenge_up_next_starts_after_current_hack(self):
        app = self.make_app(target=500, total_exits=12)
        upcoming = app._active_game_mode_up_next_games(3)

        self.assertEqual([game["title"] for game in upcoming], ["Second Hack"])

    def test_challenge_dashboard_controls_match_the_active_mode_actions(self):
        app = self.make_app(target=500, total_exits=12)
        app.active_game_mode_name = "Mario Kaizo Challenge"
        labels = [
            label
            for label, _command, _background, _active_background
            in app._game_mode_dashboard_control_definitions()
        ]

        self.assertEqual(
            labels,
            [
                "Curate Playlist",
                "Hack Completed",
                "Skip Hack",
                "Stop Challenge",
            ],
        )

    def test_completion_credits_hack_levels_and_advances_immediately(self):
        app = self.make_app(target=500, total_exits=12)
        with mock.patch.object(self.tracker, "save_config") as save:
            app._complete_mario_kaizo_hack()

        self.assertEqual(
            app.config["mario_kaizo_challenge_completed_levels"],
            12,
        )
        self.assertEqual(app.config["mario_kaizo_challenge_current_index"], 1)
        self.assertEqual(app.config["mario_kaizo_challenge_history"][0]["levels"], 12)
        self.assertTrue(app.config["mario_kaizo_challenge_active"])
        save.assert_called_once_with(app.config)
        app._refresh_mario_kaizo_dashboard_queue.assert_called_once_with()
        app._launch_mario_kaizo_current_hack.assert_called_once_with()

    def test_reaching_target_finishes_without_launching_another_hack(self):
        app = self.make_app(target=10, total_exits=12)
        with mock.patch.object(self.tracker, "save_config"):
            app._complete_mario_kaizo_hack()

        self.assertFalse(app.config["mario_kaizo_challenge_active"])
        app._launch_mario_kaizo_current_hack.assert_not_called()
        app._set_active_game_mode_session.assert_called_once_with(None)
        app._show_localized_info.assert_called_once()

    def test_dashboard_uses_cumulative_challenge_exits_and_target(self):
        app = self.make_app(target=1000, total_exits=50)
        app.config["mario_kaizo_challenge_completed_levels"] = 325
        app.exits_var = SimpleNamespace(get=lambda: "Exits: 27 / 50")

        self.assertEqual(
            app._active_exit_based_mode_progress(),
            (352, 1000),
        )

    def test_dashboard_does_not_double_count_during_next_hack_handoff(self):
        app = self.make_app(target=1000, total_exits=50)
        app.config["mario_kaizo_challenge_completed_levels"] = 375
        app.config["mario_kaizo_challenge_current_index"] = 1
        app.exits_var = SimpleNamespace(get=lambda: "Exits: 50 / 50")

        self.assertEqual(
            app._active_exit_based_mode_progress(),
            (375, 1000),
        )

    def test_stopping_challenge_restores_default_dashboard_exit_mode(self):
        app = self.make_app(target=1000, total_exits=50)
        with mock.patch.object(self.tracker, "save_config") as save:
            app._stop_mario_kaizo_challenge()

        self.assertFalse(app.config["mario_kaizo_challenge_active"])
        self.assertIsNone(app._active_exit_based_mode_progress())
        save.assert_called_once_with(app.config)
        app._set_active_game_mode_session.assert_called_once_with(None)
        app._refresh_mario_kaizo_dashboard_queue.assert_called_once_with()
        app._close_game_mode_dialog.assert_called_once_with()

    def test_reordering_mid_challenge_keeps_completed_and_current_hacks_anchored(self):
        app = self.make_app(target=500, total_exits=12)
        app.config["mario_kaizo_challenge_current_index"] = 1
        app.config["mario_kaizo_challenge_history"] = [
            {
                "hack": dict(app.config["mario_kaizo_challenge_playlist"][0]),
                "levels": 12,
            }
        ]
        future = {
            "catalog_key": "future-hack",
            "title": "Future Hack",
            "total_exits": 30,
        }
        completed = dict(app.config["mario_kaizo_challenge_playlist"][0])

        with mock.patch.object(self.tracker, "save_config"):
            app._save_mario_kaizo_playlist([future, completed])

        titles = [
            game["title"]
            for game in app.config["mario_kaizo_challenge_playlist"]
        ]
        self.assertEqual(titles, ["First Hack", "Second Hack", "Future Hack"])
        self.assertEqual(app.config["mario_kaizo_challenge_current_index"], 1)

    def test_playlist_exit_total_handles_catalog_values_safely(self):
        total = self.tracker.TrackerApp._mario_kaizo_playlist_exit_total(
            [
                {"title": "One", "total_exits": 12},
                {"title": "Two", "total_exits": "20"},
                {"title": "Unknown", "total_exits": None},
                {"title": "Bad", "total_exits": "not-a-number"},
            ]
        )
        self.assertEqual(total, 32)

    def test_playlist_editor_displays_per_hack_and_live_exit_totals(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_mario_kaizo_playlist_curator
        )
        self.assertIn("available_display_entries", source)
        self.assertIn("playlist_summary_var", source)
        self.assertIn("_mario_kaizo_playlist_exit_total", source)

    def test_start_is_blocked_when_curated_playlist_has_too_few_exits(self):
        app = self.make_app(target=500, total_exits=12)
        app.config["mario_kaizo_challenge_active"] = False

        with mock.patch.object(self.tracker, "save_config") as save:
            app._start_mario_kaizo_challenge(500)

        app._show_localized_info.assert_called_once()
        app._launch_mario_kaizo_current_hack.assert_not_called()
        app._set_active_game_mode_session.assert_not_called()
        save.assert_not_called()

    def test_empty_playlist_builds_filtered_random_queue_when_exits_are_enough(self):
        app = self.make_app(target=500, total_exits=12)
        app.config["mario_kaizo_challenge_playlist"] = []
        app.config["mario_kaizo_challenge_active"] = False
        ready = [
            {
                "catalog_key": "one",
                "title": "Kaizo One",
                "author": "Creator",
                "total_exits": 300,
                "difficulty": "Expert",
                "hack_type": "Standard",
            },
            {
                "catalog_key": "two",
                "title": "Kaizo Two",
                "author": "Creator",
                "total_exits": 250,
                "difficulty": "Expert",
                "hack_type": "Standard",
            },
        ]
        app._game_mode_ready_hacks = mock.Mock(return_value=ready)

        with (
            mock.patch.object(self.tracker, "save_config") as save,
            mock.patch.object(self.tracker.random, "sample", return_value=ready),
        ):
            app._start_mario_kaizo_challenge(
                500,
                search_text="kaizo",
                difficulty_value="Expert",
                type_value="Standard",
            )

        playlist = app.config["mario_kaizo_challenge_playlist"]
        self.assertEqual([game["title"] for game in playlist], ["Kaizo One", "Kaizo Two"])
        self.assertGreaterEqual(app._mario_kaizo_playlist_exit_total(playlist), 500)
        self.assertTrue(app.config["mario_kaizo_challenge_active"])
        save.assert_called_once_with(app.config)
        app._launch_mario_kaizo_current_hack.assert_called_once_with()

    def test_challenge_search_difficulty_and_type_filters_share_ready_pool(self):
        app = self.make_app()
        ready = [
            {
                "title": "Alpha Kaizo",
                "author": "Maker",
                "difficulty": "Expert",
                "hack_type": "Standard, Kaizo",
            },
            {
                "title": "Beta World",
                "author": "Other",
                "difficulty": "Casual",
                "hack_type": "Standard",
            },
        ]
        matches = app._mario_kaizo_filtered_ready_hacks(
            "alpha",
            "Expert",
            "Kaizo",
            ready_hacks=ready,
        )
        self.assertEqual([game["title"] for game in matches], ["Alpha Kaizo"])

        creator_matches = app._mario_kaizo_filtered_ready_hacks(
            "other",
            "Casual",
            "Standard",
            creator_value="Other",
            ready_hacks=ready,
        )
        self.assertEqual(
            [game["title"] for game in creator_matches],
            ["Beta World"],
        )

    def test_redundant_rules_buttons_are_removed_from_game_modes(self):
        builder_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_modes
        )
        page_source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )
        self.assertNotIn('tr("Rules")', builder_source)
        self.assertNotIn('_translate_ui_text("Rules")', page_source)

    def test_challenge_presets_use_large_responsive_selectors(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_mario_kaizo_challenge
        )
        self.assertIn("indicator_size = self._ui_px(26)", source)
        self.assertIn("layout_preset_cards", source)
        self.assertNotIn("tk.Radiobutton", source)

    def test_mario_hat_is_a_real_vector_icon_in_both_renderers(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._draw_stream_desk_icon
        )
        self.assertIn('"mario_hat"', source)
        self.assertGreaterEqual(source.count('key == "mario_hat"'), 2)

    def test_new_challenge_copy_is_translated_in_every_language(self):
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for phrase in (
                "Mario Kaizo Challenge",
                "Curate Playlist",
                "Hack Completed",
                "Start Challenge",
                "Resume Challenge",
                "Stop Challenge",
                "Next Hack",
                "Skip Hack",
                "Finish Mode",
                "500 levels / 50 hours",
                "Playlist Total: {hacks} hacks • {exits} exits",
                "Filtered Pool: {hacks} hacks • {exits} exits",
                "Not Enough Exits",
            ):
                with self.subTest(language=language, phrase=phrase):
                    self.assertIn(phrase, translations)


if __name__ == "__main__":
    unittest.main()
