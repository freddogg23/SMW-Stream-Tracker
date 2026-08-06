import importlib.util
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_replay_deaths_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReplayAndTrackerDeathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        )
        self.database_path = (
            Path(self.temporary_directory.name) / "tracker.db"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_completion_saves_and_exports_total_deaths(self):
        database = self.tracker.TrackerDatabase(self.database_path)
        result = database.complete_hack(
            {
                "title": "Death Test World",
                "author": "Tester",
                "total_exits": 1,
                "difficulty": "Casual",
                "hack_type": "Standard",
                "is_custom": True,
            },
            completed_exits=1,
            total_exits=1,
            playtime_seconds=90,
            rating=4.5,
            notes="",
            total_deaths=37,
        )

        self.assertEqual(result["total_deaths"], 37)
        row = database.list_tracked()[0]
        self.assertEqual(row["total_deaths"], 37)
        self.assertEqual(row["death_count_legacy"], 0)
        fieldnames, export_rows = database._tracker_export_data()
        self.assertIn("Total Deaths", fieldnames)
        self.assertEqual(export_rows[0]["Total Deaths"], 37)

    def test_existing_completed_rows_receive_legacy_marker(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.executescript(
                """
                CREATE TABLE catalog_hacks (
                    catalog_key TEXT PRIMARY KEY,
                    smwc_id TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL,
                    normalized_title TEXT NOT NULL,
                    author TEXT NOT NULL DEFAULT 'Unknown',
                    total_exits INTEGER NOT NULL DEFAULT 0,
                    difficulty TEXT NOT NULL DEFAULT 'Unknown',
                    hack_type TEXT NOT NULL DEFAULT 'Unknown',
                    added_date TEXT NOT NULL DEFAULT '',
                    smwc_rating REAL,
                    page_url TEXT NOT NULL DEFAULT '',
                    download_url TEXT NOT NULL DEFAULT '',
                    is_custom INTEGER NOT NULL DEFAULT 0,
                    rom_path TEXT NOT NULL DEFAULT '',
                    local_rom_path TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE tracked_hacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    catalog_key TEXT NOT NULL UNIQUE,
                    display_order INTEGER,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL DEFAULT 'Unknown',
                    total_exits INTEGER NOT NULL DEFAULT 0,
                    difficulty TEXT NOT NULL DEFAULT 'Unknown',
                    hack_type TEXT NOT NULL DEFAULT 'Unknown',
                    smwc_rating REAL,
                    date_started TEXT NOT NULL DEFAULT '',
                    date_completed TEXT NOT NULL DEFAULT '',
                    completed_exits INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'Planned',
                    personal_rating REAL,
                    playtime_seconds INTEGER NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO catalog_hacks (
                    catalog_key, title, normalized_title, total_exits
                ) VALUES ('TITLE:old hack', 'Old Hack', 'old hack', 1);
                INSERT INTO tracked_hacks (
                    catalog_key, title, total_exits, completed_exits, status
                ) VALUES ('TITLE:old hack', 'Old Hack', 1, 1, 'Completed');
                """
            )

        database = self.tracker.TrackerDatabase(self.database_path)
        database.initialize()
        row = database.list_tracked()[0]
        self.assertIsNone(row["total_deaths"])
        self.assertEqual(row["death_count_legacy"], 1)
        _fieldnames, export_rows = database._tracker_export_data()
        self.assertEqual(export_rows[0]["Total Deaths"], "*")

    def test_tracker_total_deaths_can_be_edited_and_are_preserved(self):
        database = self.tracker.TrackerDatabase(self.database_path)
        result = database.complete_hack(
            {
                "title": "Editable Death World",
                "author": "Tester",
                "total_exits": 1,
                "difficulty": "Advanced",
                "hack_type": "Kaizo",
                "is_custom": True,
            },
            completed_exits=1,
            total_exits=1,
            playtime_seconds=120,
            rating=4.0,
            notes="",
            total_deaths=12,
        )

        database.save_tracked(
            result["id"],
            1,
            "Completed",
            4.0,
            120,
            "2026-08-05",
            "2026-08-05",
            "ordinary edit preserves deaths",
        )
        self.assertEqual(
            database.list_tracked()[0]["total_deaths"],
            12,
        )

        database.save_tracked(
            result["id"],
            1,
            "Completed",
            4.0,
            120,
            "2026-08-05",
            "2026-08-05",
            "manual historical total",
            total_deaths=48,
        )
        edited = database.list_tracked()[0]
        self.assertEqual(edited["total_deaths"], 48)
        self.assertEqual(edited["death_count_legacy"], 0)

    def test_replay_resolves_saved_hack_to_current_catalog_record(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.last_launched_hack = {
            "catalog_key": "SMWC:123",
            "title": "Saved Copy",
        }
        live_record = {
            "catalog_key": "SMWC:123",
            "title": "Current Catalog Title",
            "download_url": "https://example.invalid/patch.zip",
        }
        app.hack_catalog = [live_record]

        self.assertIs(app._resolved_replay_hack(), live_record)

    def test_recent_replay_history_keeps_five_newest_without_duplicates(self):
        history = [
            {"catalog_key": f"SMWC:{number}", "title": f"Hack {number}"}
            for number in range(1, 6)
        ]

        updated = self.tracker.TrackerApp._updated_recent_hack_history(
            history,
            {"catalog_key": "SMWC:3", "title": "Hack 3 Updated"},
        )

        self.assertEqual(
            [game["catalog_key"] for game in updated],
            ["SMWC:3", "SMWC:1", "SMWC:2", "SMWC:4", "SMWC:5"],
        )
        self.assertEqual(updated[0]["title"], "Hack 3 Updated")

    def test_replay_resolves_selected_recent_hack(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        selected_snapshot = {
            "catalog_key": "SMWC:456",
            "title": "Selected Recent Hack",
        }
        live_record = {
            "catalog_key": "SMWC:456",
            "title": "Selected Recent Hack - Live",
        }
        app.hack_catalog = [live_record]

        self.assertIs(
            app._resolved_replay_hack(selected_snapshot),
            live_record,
        )


if __name__ == "__main__":
    unittest.main()
