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

    def test_add_circle_opens_the_manual_tracker_form(self):
        source = self.method_source("open_my_tracker")
        self.assertIn("make_tracker_circle_action", source)
        self.assertIn("self._add_tracker_record", source)

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

    def test_removing_a_tracker_row_compacts_hack_numbers(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            added_records = [
                database.add_to_tracker(
                    {
                        "title": title,
                        "author": "Test Creator",
                        "total_exits": 1,
                    }
                )
                for title in (
                    "First Test Hack",
                    "Second Test Hack",
                    "Third Test Hack",
                )
            ]

            database.remove_tracked(int(added_records[1]["id"]))

            remaining = database.list_tracked()
            self.assertEqual(
                [row["title"] for row in remaining],
                ["First Test Hack", "Third Test Hack"],
            )
            self.assertEqual(
                [row["display_order"] for row in remaining],
                [1, 2],
            )

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
        source = self.method_source("_confirm_tracker_remove_selection")
        self.assertIn("self._ask_localized_yes_no(", source)
        self.assertNotIn("messagebox.askyesno(", source)

    def test_remove_circle_opens_bulk_checkbox_mode(self):
        toggle_source = self.method_source("_remove_tracker_record")
        mode_source = self.method_source("_set_tracker_remove_mode")
        event_source = self.method_source("_select_tracker_overlay_event")
        render_source = self.method_source("_render_tracker_cell_overlays")
        confirm_source = self.method_source(
            "_confirm_tracker_remove_selection"
        )
        self.assertIn("self._set_tracker_remove_mode(", toggle_source)
        self.assertIn('remove_bar.pack(', mode_source)
        self.assertIn('"remove_checkbox_boxes"', event_source)
        self.assertIn('column == "#0"', render_source)
        self.assertIn("row_canvas.create_line(", render_source)
        self.assertIn("for record in selected_records:", confirm_source)
        self.assertIn("self.stats_db.remove_tracked", confirm_source)

    def test_remove_confirmation_is_translated_in_every_language(self):
        texts = (
            "Remove from My Tracker",
            "Select the hacks you want to remove, then choose Remove Selected.",
            "{count} hack(s) selected",
            "Remove Selected",
            "Cancel Selection",
            "Remove {count} selected hack(s) from My Tracker?",
            "This removes personal progress, ratings, playtime, and notes for the selected hacks. The games stay in the catalog and game library.",
            "Removed {count} hack(s) from My Tracker.",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in texts:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)
                    self.assertNotEqual(translations[text], text)


if __name__ == "__main__":
    unittest.main()
