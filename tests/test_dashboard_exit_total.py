import importlib.util
import json
from pathlib import Path
import queue
import sys
import time
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_dashboard_exit_total_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DashboardExitTotalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_worker(self):
        events = queue.Queue()
        worker = self.tracker.TrackerWorker(
            dict(self.tracker.DEFAULT_CONFIG),
            events,
        )
        worker.update_title_files = lambda *_args, **_kwargs: None
        worker.log = lambda *_args, **_kwargs: None
        return worker, events

    def test_catalog_launch_command_carries_known_game_and_rom_path(self):
        worker, _events = self.make_worker()
        game = {
            "title": "Example Hack",
            "author": "Creator",
            "total_exits": 12,
        }

        worker.notify_catalog_launch(
            game,
            "/media/fat/games/SNES/Example Hack.sfc",
        )

        command = worker.command_queue.get_nowait()
        self.assertTrue(command.startswith("catalog_launch:"))
        payload = json.loads(command.split(":", 1)[1])
        self.assertEqual(payload["game"]["total_exits"], 12)
        self.assertEqual(
            payload["rom_path"],
            "/media/fat/games/SNES/Example Hack.sfc",
        )

        worker.command_queue.put(command)
        worker.reset_all_timers_for_new_rom = lambda: None
        worker.process_commands()
        self.assertEqual(
            worker.pending_catalog_launch_game["title"],
            "Example Hack",
        )
        self.assertEqual(
            worker.pending_catalog_launch_path,
            "/media/fat/games/SNES/Example Hack.sfc",
        )
        self.assertGreater(worker.pending_catalog_launch_at, 0.0)

    def test_matching_launch_path_keeps_dashboard_exit_denominator(self):
        worker, events = self.make_worker()
        worker.database = {}
        worker.previous_rom_path = "Example Hack.sfc"
        worker.pending_catalog_launch_game = {
            "title": "Example Hack",
            "author": "Creator",
            "total_exits": "12",
            "catalog_key": "SMWC:123",
        }
        worker.pending_catalog_launch_path = (
            "/media/fat/games/SNES/Example Hack.sfc"
        )
        worker.pending_catalog_launch_at = time.monotonic()

        worker.refresh_current_hack_metadata()

        self.assertTrue(worker.current_matched)
        self.assertEqual(worker.current_total, 12)
        game_event = events.get_nowait()
        self.assertEqual(game_event["type"], "game")
        self.assertEqual(game_event["total"], 12)
        self.assertEqual(game_event["title"], "Example Hack")

    def test_different_rom_does_not_reuse_pending_exit_total(self):
        worker, _events = self.make_worker()
        worker.pending_catalog_launch_game = {
            "title": "Expected Hack",
            "author": "Creator",
            "total_exits": 12,
        }
        worker.pending_catalog_launch_path = (
            "/media/fat/games/SNES/Expected Hack.sfc"
        )
        worker.pending_catalog_launch_at = time.monotonic()

        self.assertIsNone(
            worker.pending_catalog_hack_for_rom("Different Hack.sfc")
        )
        self.assertEqual(
            worker.pending_catalog_launch_game["title"],
            "Expected Hack",
        )

    def test_same_rom_reconnect_keeps_completed_exit_denominator(self):
        worker, _events = self.make_worker()
        worker.previous_rom_path = "Completed Hack.sfc"
        worker.current_hack_title = "Completed Hack"
        worker.current_hack_record = {
            "title": "Completed Hack",
            "author": "Creator",
            "total_exits": 12,
        }
        worker.current_total = 12
        worker.current_matched = True
        worker.displayed_exit_count = 12
        written_exits = []

        class Connection:
            def close(self):
                return None

        worker.start_qusb2snes_if_needed = lambda: None
        worker.connect_to_fxpak = lambda: (Connection(), "MiSTer")
        worker.process_commands = lambda *_args: None
        worker.get_loaded_rom_path = lambda *_args: "Completed Hack.sfc"
        worker.read_game_state = lambda *_args: {
            "mode": self.tracker.LEVEL_MODE,
            "level_number": 0x0105,
            "save_slot": 0,
            "player_state": 0,
            "player_lives": 5,
            "translevel": 3,
            "exits": 12,
        }
        worker.update_timers_from_state = (
            lambda *_args, **_kwargs: worker.stop_event.set()
        )
        worker.update_exit_file = (
            lambda completed, total: written_exits.append((completed, total))
        )
        worker.save_current_level_progress = lambda: None
        worker.save_current_game_time = lambda: None
        worker.save_current_death_count = lambda: None

        worker._run_connection({})

        self.assertTrue(worker.current_matched)
        self.assertEqual(worker.current_total, 12)
        self.assertIn((12, 12), written_exits)


if __name__ == "__main__":
    unittest.main()
