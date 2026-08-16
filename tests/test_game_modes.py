import importlib.util
import inspect
from pathlib import Path
import sys
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_game_modes_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GameModesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_game_modes_offers_all_requested_modes(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        expected_modes = {
            "Play Random Hack": "self._play_random_main_hack",
            "Hack Draft": "self._open_hack_draft",
            "Difficulty Ladder": "self._open_difficulty_ladder",
            "Creator Spotlight": "self._open_creator_spotlight",
            "Time Capsule": "self._open_time_capsule",
            "Hall of Fame Tour": "self._open_hall_of_fame_tour",
        }
        for label, command in expected_modes.items():
            with self.subTest(label=label):
                self.assertIn(label, source)
                self.assertIn(command, source)
        self.assertNotIn("Hack Gauntlet", source)
        self.assertNotIn("_open_hack_gauntlet_maker", source)

    def test_game_mode_menu_updates_description_on_hover(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        self.assertIn('"<Enter>"', source)
        self.assertIn('"<Leave>"', source)
        self.assertIn("description_var.set", source)

    def test_game_mode_launch_returns_to_the_dashboard(self):
        launch_source = inspect.getsource(
            self.tracker.TrackerApp._launch_game_mode_hack
        )
        random_source = inspect.getsource(
            self.tracker.TrackerApp._launch_filtered_random_main_hack
        )
        return_source = inspect.getsource(
            self.tracker.TrackerApp._return_game_modes_to_dashboard
        )
        self.assertIn("_return_game_modes_to_dashboard", launch_source)
        self.assertIn("_return_game_modes_to_dashboard", random_source)
        self.assertIn('page.page_key == "game_modes"', return_source)
        self.assertIn("page.request_close()", return_source)

    def test_new_game_mode_text_is_translated_in_every_language(self):
        phrases = (
            "Hack Draft",
            "Difficulty Ladder",
            "Creator Spotlight",
            "Time Capsule",
            "Hall of Fame Tour",
            "Ready-to-Play Hack",
            "Launch Selected Hack",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for phrase in phrases:
                with self.subTest(language=language, phrase=phrase):
                    self.assertIn(phrase, translations)
                    self.assertTrue(translations[phrase].strip())

    def test_duplicate_draft_labels_remain_selectable(self):
        games = [
            {"title": "Same Hack", "author": "Creator"},
            {"title": "Same Hack", "author": "Creator"},
        ]

        labels, mapped = (
            self.tracker.TrackerApp._game_mode_unique_labels(games)
        )

        self.assertEqual(len(labels), 2)
        self.assertEqual(len(mapped), 2)
        self.assertNotEqual(labels[0], labels[1])

    def test_catalog_launch_has_no_gauntlet_callback(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._finish_catalog_game_launch
        )

        self.assertNotIn("_finish_hack_gauntlet_launch", source)

    def test_gauntlet_is_not_part_of_default_configuration(self):
        self.assertNotIn(
            "hack_gauntlet_settings",
            self.tracker.DEFAULT_CONFIG,
        )


if __name__ == "__main__":
    unittest.main()
