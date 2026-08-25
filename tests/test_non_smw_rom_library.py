import importlib.util
from pathlib import Path
import queue
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
        "smw_tracker_non_smw_library_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NonSmwRomLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_import_copies_and_deduplicates_snes_rom(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            source = root / "A_Generic-Game.sfc"
            source.write_bytes(b"generic-snes-rom")
            records = []

            record, created = self.tracker.import_non_smw_rom(
                source,
                records,
                root / "Managed",
            )
            duplicate, duplicate_created = self.tracker.import_non_smw_rom(
                source,
                records,
                root / "Managed",
            )

            self.assertTrue(created)
            self.assertFalse(duplicate_created)
            self.assertEqual(record["id"], duplicate["id"])
            self.assertEqual(len(records), 1)
            self.assertTrue(Path(record["local_rom_path"]).is_file())
            self.assertTrue(record["_non_smw_rom"])
            self.assertEqual(record["hack_type"], "Non-SMW ROM")

    def test_import_rejects_non_snes_extension(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            source = Path(folder) / "not-a-rom.zip"
            source.write_bytes(b"not a ROM")
            with self.assertRaisesRegex(ValueError, r"\.sfc or \.smc"):
                self.tracker.import_non_smw_rom(
                    source,
                    [],
                    Path(folder) / "Managed",
                )

    def test_folder_scan_finds_supported_roms_recursively(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            nested = root / "Nested"
            nested.mkdir()
            (root / "First Game.sfc").write_bytes(b"first")
            (nested / "Second Game.SMC").write_bytes(b"second")
            (nested / "Ignore.zip").write_bytes(b"ignore")

            paths = self.tracker.find_snes_rom_files(root)

            self.assertEqual(
                [path.name for path in paths],
                ["First Game.sfc", "Second Game.SMC"],
            )

    def test_clean_display_name_removes_dump_region_and_archive_date_tags(self):
        self.assertEqual(
            self.tracker.clean_snes_rom_display_name(
                "7th Saga, The (U) [!] (2021 06 23 13 12 25 UTC).sfc"
            ),
            "7th Saga, The",
        )
        self.assertEqual(
            self.tracker.clean_snes_rom_display_name(
                "ActRaiser_(USA)_[!].smc"
            ),
            "ActRaiser",
        )

    def test_library_round_trip_restores_runtime_launch_fields(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            library_file = Path(folder) / "library.json"
            records = [
                {
                    "id": "abc",
                    "title": "Generic Game",
                    "filename": "generic.sfc",
                    "local_rom_path": str(Path(folder) / "generic.sfc"),
                    "file_size": 1024,
                    "added_at": "2026-08-24T00:00:00+00:00",
                    "last_played": "",
                    "_non_smw_rom": True,
                    "_retroachievements_game_id": 1234,
                }
            ]
            self.tracker.save_non_smw_rom_library(records, library_file)
            loaded = self.tracker.load_non_smw_rom_library(library_file)

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["title"], "Generic Game")
            self.assertEqual(
                loaded[0]["rom_path"],
                loaded[0]["local_rom_path"],
            )
            self.assertEqual(loaded[0]["author"], "")
            self.assertEqual(loaded[0]["total_exits"], 0)
            self.assertTrue(loaded[0]["_non_smw_rom"])
            self.assertEqual(loaded[0]["_retroachievements_game_id"], 1234)

    def test_loaded_rom_is_recognized_after_tracker_restart(self):
        records = [
            {
                "id": "abc",
                "title": "Generic Game",
                "filename": "generic.sfc",
                "local_rom_path": r"C:\ROMs\generic.sfc",
                "_non_smw_rom": True,
            }
        ]

        local_match = self.tracker.find_non_smw_rom_record(
            r"C:\ROMs\generic.sfc",
            records,
        )
        device_match = self.tracker.find_non_smw_rom_record(
            "/media/fat/games/SNES/Non-SMW/generic.sfc",
            records,
        )

        self.assertEqual(local_match["title"], "Generic Game")
        self.assertEqual(device_match["title"], "Generic Game")

    def test_generic_timers_advance_without_game_memory(self):
        worker = self.tracker.TrackerWorker({}, queue.Queue())
        worker.generic_game_active = True
        worker.game_started = True
        worker.game_finished = False
        worker.game_manual_paused = False
        worker.level_id = 0
        worker.level_finished = False
        worker.level_manual_paused = False
        worker.level_livesplit_running = True
        worker.timers_paused = False

        worker.update_generic_game_timers(1.25)

        self.assertEqual(worker.game_elapsed, 1.25)
        self.assertEqual(worker.level_elapsed, 1.25)

    def test_game_library_contains_non_smw_tab_and_generic_memory_guard(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('library_tabs.add(non_smw_library_tab', source)
        self.assertIn('text=tr("SNES ROMs")', source)
        self.assertIn('command=self._import_snes_roms_from_downloader', source)
        self.assertIn('text=self._translate_ui_text("Import ROM Folder")', source)
        self.assertIn('select_folder=True', source)
        self.assertIn('filenames = find_snes_rom_files(Path(selected_folder))', source)
        self.assertNotIn('("Stored in", path_var)', source)
        self.assertIn('text=tr("Select all visible ROMs")', source)
        self.assertIn('("Delete Selected", remove_selected', source)
        self.assertIn('self._start_game_library_retroachievements_scan(', source)
        self.assertIn(
            'rom_tree.heading("name", text=tr("Game / ROM name"), anchor="center")',
            source,
        )
        self.assertIn('title_column="name"', source)
        self.assertIn('trophy_photo=trophy_photo', source)
        self.assertIn('achievement_badge_strip = tk.Frame(', source)
        self.assertIn('_non_smw_ra_summary_badge_photos', source)
        self.assertIn('uniform="non_smw_ra_game_badges"', source)
        self.assertIn('def scroll_achievement_list(event) -> str:', source)
        self.assertIn(
            'bind_achievement_wheel_tree(achievement_list_content)',
            source,
        )
        self.assertIn(
            'ready_tree.heading("creator", text=tr("Created By"), anchor="center")',
            source,
        )
        self.assertIn('max(0, column_width - 1)', source)
        self.assertIn('if rom_path and self.generic_game_active:', source)
        self.assertIn('self.update_generic_game_timers(delta)', source)
        self.assertIn('elif rom_path:\n                    raw_state = self.read_game_state', source)


if __name__ == "__main__":
    unittest.main()
