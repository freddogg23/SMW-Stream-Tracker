import importlib.util
import gc
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_fxpak_sd_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeListWebSocket:
    def __init__(self, listings):
        self.listings = listings
        self.last_request = {}

    def send(self, payload):
        self.last_request = json.loads(payload)

    def recv(self):
        folder = self.last_request["Operands"][0]
        return json.dumps({"Results": self.listings.get(folder, [])})


class FxpakSdCardBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_recursive_scan_keeps_only_rom_files(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.fxpak_sd_cancel_event = threading.Event()
        websocket = FakeListWebSocket(
            {
                "/All_Hacks": [
                    "0", "Advanced", "1", "Root Hack.sfc", "1", "readme.txt"
                ],
                "/All_Hacks/Advanced": [
                    "1", "Nested Hack.smc", "1", "cover.png"
                ],
            }
        )

        records = app._scan_fxpak_sd_roms(websocket, "/All_Hacks")

        self.assertEqual(
            {record["path"] for record in records},
            {
                "/All_Hacks/Root Hack.sfc",
                "/All_Hacks/Advanced/Nested Hack.smc",
            },
        )
        self.assertEqual(
            {record["format"] for record in records},
            {"SFC", "SMC"},
        )

    def test_title_letters_ignore_leading_articles(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)

        self.assertEqual(app._alphabet_segment("The Dog"), "D")
        self.assertEqual(app._alphabet_segment("A Great Adventure"), "G")
        self.assertEqual(app._alphabet_segment("An Untitled Hack"), "U")
        self.assertEqual(
            app._title_without_leading_article("The Dog"),
            "Dog",
        )

    def test_library_letter_filter_uses_second_word(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        game = {
            "title": "The Dog",
            "author": "Creator",
            "smwc_id": "123",
            "rating": 4.5,
            "difficulty": "Advanced",
            "hack_type": "Kaizo",
        }

        self.assertTrue(
            app._game_matches_library_filters(
                game,
                "",
                "Any",
                "Any",
                "Any",
                "D",
            )
        )
        self.assertFalse(
            app._game_matches_library_filters(
                game,
                "",
                "Any",
                "Any",
                "Any",
                "T",
            )
        )

    def test_info_parser_detects_current_rom_paths(self):
        paths = self.tracker.TrackerApp._fxpak_info_rom_paths(
            {
                "Results": [
                    "FXPAK Pro",
                    "All_Hacks/Kaizo/Current Game.sfc",
                    "NO_CONTROL_CMD",
                ]
            }
        )

        self.assertEqual(
            paths,
            {"/all_hacks/kaizo/current game.sfc"},
        )

    def test_deleted_remote_path_clears_only_its_mapping(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            database.initialize()
            with database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO catalog_hacks (
                        catalog_key, title, normalized_title, rom_path
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        "TITLE:test hack",
                        "Test Hack",
                        "test hack",
                        "/All_Hacks/Test Hack.sfc",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO rom_mappings (
                        map_key, catalog_key, title, rom_path
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        "title:test hack",
                        "TITLE:test hack",
                        "Test Hack",
                        "All_Hacks\\Test Hack.sfc",
                    ),
                )

            database.clear_remote_rom_paths(
                ["/All_Hacks/Test Hack.sfc"]
            )

            with database.connect() as connection:
                catalog_path = connection.execute(
                    "SELECT rom_path FROM catalog_hacks"
                ).fetchone()["rom_path"]
                mapping_count = connection.execute(
                    "SELECT COUNT(*) AS count FROM rom_mappings"
                ).fetchone()["count"]
            self.assertEqual(catalog_path, "")
            self.assertEqual(mapping_count, 0)
            del connection
            gc.collect()


if __name__ == "__main__":
    unittest.main()
