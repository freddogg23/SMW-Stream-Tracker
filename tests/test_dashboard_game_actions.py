import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"


class DashboardGameActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_FILE.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

    def method_source(self, name):
        return ast.get_source_segment(self.source, self.methods[name])

    def test_up_next_and_recently_played_use_separate_sources(self):
        up_next = self.method_source("_dashboard_up_next_games")
        recently_played = self.method_source(
            "_dashboard_recently_played_games"
        )
        self.assertIn('== "Planned"', up_next)
        self.assertIn("_active_game_mode_up_next_games", up_next)
        self.assertIn("self.recent_launched_hacks", recently_played)
        self.assertNotIn("self.recent_launched_hacks", up_next)

    def test_game_rows_offer_start_or_library_details(self):
        action = self.method_source("_open_dashboard_game_action")
        dialog = self.method_source("_show_stream_desk_message_dialog")
        library = self.method_source("_open_game_library_for_game")
        self.assertIn('response_type="askgameaction"', action)
        self.assertIn('choice == "start"', action)
        self.assertIn('choice == "details"', action)
        self.assertIn('("Game Details", "details", False)', dialog)
        self.assertIn('("Start Game", "start", True)', dialog)
        self.assertIn('widgets.get("select_game")', library)

    def test_current_game_title_opens_the_library_selection(self):
        dashboard = self.method_source("_build_stream_desk_dashboard")
        current_game = self.method_source("_open_current_game_in_library")
        self.assertIn("self._open_current_game_in_library", dashboard)
        self.assertIn("self.current_hack_record", current_game)

    def test_current_run_actions_finish_timer_before_completing_hack(self):
        dashboard = self.method_source("_build_stream_desk_dashboard")
        add_position = dashboard.index('text="Add to My Tracker"')
        finish_position = dashboard.index('text="Finish Game Timer"')
        complete_position = dashboard.index('else "Complete Hack"')

        self.assertLess(add_position, finish_position)
        self.assertLess(finish_position, complete_position)
        self.assertIn("command=self.finish_game_timer", dashboard)
        self.assertNotIn('text="Game Modes"', dashboard)
        self.assertIn("run_action_buttons[2]", dashboard)
        self.assertIn('uniform="dashboard_run_actions"', dashboard)

    def test_mister_login_uses_the_stream_desk_card_treatment(self):
        login = self.method_source("_prompt_mister_password")
        self.assertIn('STREAM_DESK["surface_deep"]', login)
        self.assertIn('STREAM_DESK["border_strong"]', login)
        self.assertIn('text="SSH"', login)
        self.assertIn('"Show Passwords"', login)

    def test_about_has_one_combined_thank_you_with_linked_testers(self):
        about_text = self.method_source("_localized_about_text")
        about_dialog = self.method_source("open_about_dialog")
        self.assertIn("A HUGE thank you to Jole_12, PixelPadlock", about_text)
        self.assertEqual(about_text.count("A HUGE thank you"), 1)
        for name, url in (
            ("Jole_12", "https://www.twitch.tv/jole_12"),
            ("PixelPadlock", "https://www.twitch.tv/pixelpadlock"),
        ):
            self.assertIn(name, about_text)
            self.assertIn(name, about_dialog)
            self.assertIn(url, about_dialog)
        self.assertIn("about_text_widget.tag_bind", about_dialog)

    def test_installers_own_finish_actions_without_native_run_entries(self):
        installer = (ROOT / "installer" / "SMWStreamTrackerInstaller.iss").read_text(
            encoding="utf-8"
        )
        updater = (ROOT / "installer" / "SMWStreamTrackerUpdater.iss").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("\n[Run]\n", installer)
        self.assertNotIn("\n[Run]\n", updater)
        self.assertIn("RunSelectedFinishOptions", installer)
        self.assertIn("CurPageID = wpFinished", installer)
        self.assertIn("CurPageID = wpFinished", updater)
        self.assertIn("LaunchUpdatedAppSelected", updater)


if __name__ == "__main__":
    unittest.main()
