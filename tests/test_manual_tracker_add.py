import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_manual_add_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ManualTrackerAddTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def method_source(self, name):
        return ast.get_source_segment(
            self.source,
            self.methods[name],
        )

    def test_add_button_opens_the_manual_tracker_form(self):
        source = self.method_source("open_my_tracker")
        self.assertIn("command=self._add_tracker_record", source)

    def test_manual_form_uses_blue_app_style_and_refreshes_tracker(self):
        source = self.method_source("_add_tracker_record")
        for expected in (
            'bg=THEME["blue"]',
            "self.stats_db.add_to_tracker(",
            "self.stats_db.save_tracked(",
            "self._reload_database_catalog()",
            "self._refresh_my_tracker()",
            "tracker_tree.selection_set(tracker_iid)",
            "self._show_localized_info(",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, source)

    def test_manual_database_record_keeps_all_tracker_details(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            result = database.add_to_tracker(
                {
                    "title": "Manual Tracker Test",
                    "author": "Test Creator",
                    "total_exits": 12,
                    "difficulty": "Expert",
                    "hack_type": "Kaizo",
                    "rating": 4.75,
                },
                completed_exits=3,
                playtime_seconds=3723,
            )
            database.save_tracked(
                int(result["id"]),
                3,
                "In Progress",
                4.5,
                3723,
                "2026-08-11",
                "",
                "Added from the blue form.",
                total_deaths=27,
            )

            record = database.get_tracked(int(result["id"]))
            self.assertIsNotNone(record)
            self.assertEqual(record["title"], "Manual Tracker Test")
            self.assertEqual(record["author"], "Test Creator")
            self.assertEqual(record["total_exits"], 12)
            self.assertEqual(record["completed_exits"], 3)
            self.assertEqual(record["difficulty"], "Expert")
            self.assertEqual(record["hack_type"], "Kaizo")
            self.assertEqual(record["status"], "In Progress")
            self.assertEqual(record["total_deaths"], 27)
            self.assertEqual(record["personal_rating"], 4.5)
            self.assertEqual(record["smwc_rating"], 4.75)
            self.assertEqual(record["playtime_seconds"], 3723)
            self.assertEqual(record["notes"], "Added from the blue form.")

    def test_manual_form_text_is_translated_in_every_language(self):
        texts = (
            "Add Hack to Tracker",
            "Hack Details",
            "Tracker Details",
            "ROM Hack Title:",
            "Created By:",
            "Total exits:",
            "Completed exits:",
            "Difficulty:",
            "Type:",
            "SMWC ID (optional):",
            "Status:",
            "Total deaths:",
            "My rating (1–5):",
            "Playtime:",
            "Date started:",
            "Date completed:",
            "SMWCentral Rating:",
            "Notes:",
            "ROM Hack Title is required.",
            "Check exits, deaths, dates, ratings, and playtime.",
            "Added to My Tracker",
            'Added "{title}" to My Tracker.',
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in texts:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)
                    if language == "au":
                        self.assertNotEqual(translations[text], text)

    def test_remove_confirmation_uses_the_blue_app_dialog(self):
        source = self.method_source("_remove_tracker_record")
        self.assertIn("self._ask_localized_yes_no(", source)
        self.assertNotIn("messagebox.askyesno(", source)

    def test_remove_confirmation_is_translated_in_every_language(self):
        texts = (
            "Remove from My Tracker",
            'Remove "{title}" from My Tracker?',
            (
                "This removes personal progress, rating, playtime, and notes. "
                "The game stays in the catalog and game library."
            ),
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in texts:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)
                    self.assertNotEqual(translations[text], text)


if __name__ == "__main__":
    unittest.main()
