import importlib.util
from pathlib import Path
import queue
import sys
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_level_overworld_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LevelTimerOverworldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_death_save_file = self.tracker.DEATH_SAVE_FILE
        self.tracker.DEATH_SAVE_FILE = (
            Path(self.temporary_directory.name)
            / "SMWStreamTrackerDeaths.json"
        )
        self.config = dict(self.tracker.DEFAULT_CONFIG)
        self.config["output_folder"] = str(
            Path(self.temporary_directory.name) / "obs"
        )
        self.config["overworld_idle_seconds"] = 30

    def tearDown(self):
        self.tracker.DEATH_SAVE_FILE = self.original_death_save_file
        self.temporary_directory.cleanup()

    def make_worker(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "samplehack"
        worker.current_time_key = "samplehack::slot0"
        worker.active_save_slot = 0
        worker.game_started = True
        worker.level_id = 1
        worker.level_elapsed = 10.0
        worker.level_finished = False
        worker.level_waiting_for_start = False
        worker.level_livesplit_running = True
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_exit_count = 0
        worker.displayed_exit_count = 0
        worker.previous_player_state = 0
        worker.commands = []
        worker.send_livesplit_command = (
            lambda timer, command: worker.commands.append(
                (timer, command)
            )
        )
        return worker

    def make_state(
        self,
        mode,
        *,
        translevel=1,
        level_end_timer=0,
        exits=0,
        player_state=0,
        player_lives=5,
    ):
        return {
            "mode": mode,
            "save_slot": 0,
            "player_state": player_state,
            "player_lives": player_lives,
            "paused": 0,
            "translevel": translevel,
            "exits": exits,
            "level_end_timer": level_end_timer,
            "joypad": 0,
            "joypad_axlr": 0,
        }

    def test_intro_cutscene_does_not_start_timer_or_count_deaths(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "introhack"
        worker.current_time_key = "introhack::slot0"
        worker.active_save_slot = 0
        worker.game_started = True
        worker.previous_mode = self.tracker.PLAYER_SELECT_MODE
        worker.commands = []
        worker.send_livesplit_command = (
            lambda timer, command: worker.commands.append(
                (timer, command)
            )
        )

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=0,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=10.0,
        )

        self.assertIsNone(worker.level_id)
        self.assertEqual(worker.level_elapsed, 0.0)
        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 0)
        self.assertNotIn(("level", "starttimer"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.25,
            now=10.25,
        )
        self.assertTrue(worker.level_auto_tracking_armed)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=2,
            ),
            delta=0.25,
            now=10.5,
        )

        self.assertEqual(worker.level_id, 2)
        self.assertEqual(worker.level_elapsed, 0.25)
        self.assertIn(("level", "starttimer"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=2,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=10.75,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_death_on_first_playable_level_sample_is_counted(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "fastdeathhack"
        worker.current_time_key = "fastdeathhack::slot0"
        worker.active_save_slot = 0
        worker.game_started = True
        worker.previous_mode = self.tracker.OVERWORLD_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5
        worker.level_auto_tracking_armed = True
        worker.commands = []
        worker.send_livesplit_command = (
            lambda timer, command: worker.commands.append(
                (timer, command)
            )
        )

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=2,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=20.0,
        )

        self.assertEqual(worker.level_id, 2)
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)
        self.assertIn(("level", "starttimer"), worker.commands)

    def test_reconnecting_to_started_slot_rearms_level_and_deaths(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "resumedhack"
        worker.previous_mode = None
        worker.commands = []
        worker.send_livesplit_command = (
            lambda timer, command: worker.commands.append(
                (timer, command)
            )
        )

        def select_existing_slot(slot):
            worker.active_save_slot = slot
            worker.current_time_key = f"resumedhack::slot{slot}"
            worker.death_count = 6

        worker.select_save_slot = select_existing_slot
        worker.get_saved_game_time_for_slot = lambda _slot: 125.0

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=4,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=40.0,
        )

        self.assertTrue(worker.level_auto_tracking_armed)
        self.assertEqual(worker.level_id, 4)
        self.assertFalse(worker.level_waiting_for_start)
        self.assertIn(("level", "starttimer"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=4,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=40.25,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 7)

    def test_castle_destruction_does_not_finish_game_timer(self):
        worker = self.make_worker()
        worker.game_elapsed = 20.0

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=300.0,
        )

        self.assertFalse(worker.game_finished)
        self.assertFalse(worker.timers_paused)
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertNotIn(("game", "pause"), worker.commands)

    def test_death_overworld_uses_grace_then_resumes_same_level(self):
        worker = self.make_worker()

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.5,
            now=100.0,
        )
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertTrue(worker.level_livesplit_running)
        self.assertNotIn(("level", "pause"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.5,
            now=110.0,
        )
        self.assertEqual(worker.level_elapsed, 11.0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.5,
            now=131.0,
        )
        self.assertEqual(worker.level_elapsed, 11.0)
        self.assertTrue(worker.level_livesplit_overworld_paused)
        self.assertIn(("level", "pause"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=132.0,
        )
        self.assertEqual(worker.level_elapsed, 11.5)
        self.assertFalse(worker.level_livesplit_overworld_paused)
        self.assertIn(("level", "resume"), worker.commands)

    def test_clear_stops_resets_on_overworld_and_starts_next_level(self):
        worker = self.make_worker()

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=1,
            ),
            delta=0.2,
            now=200.0,
        )
        self.assertTrue(worker.level_finished)
        self.assertEqual(worker.level_elapsed, 10.0)
        self.assertIn(("level", "pause"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.2,
            now=200.2,
        )
        self.assertIsNone(worker.level_id)
        self.assertEqual(worker.level_elapsed, 0.0)
        self.assertTrue(worker.level_waiting_for_start)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=2,
            ),
            delta=0.2,
            now=200.4,
        )
        self.assertEqual(worker.level_id, 2)
        self.assertEqual(worker.level_elapsed, 0.2)
        self.assertFalse(worker.level_waiting_for_start)
        self.assertIn(("level", "starttimer"), worker.commands)


if __name__ == "__main__":
    unittest.main()
