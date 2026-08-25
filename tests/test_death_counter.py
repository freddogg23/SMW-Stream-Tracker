import importlib.util
import json
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
        "smw_tracker_death_counter_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DeathCounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self.temporary_directory.name)
        self.original_death_save_file = self.tracker.DEATH_SAVE_FILE
        self.original_level_progress_save_file = (
            self.tracker.LEVEL_PROGRESS_SAVE_FILE
        )
        self.tracker.DEATH_SAVE_FILE = (
            self.temporary_path / "SMWStreamTrackerDeaths.json"
        )
        self.tracker.LEVEL_PROGRESS_SAVE_FILE = (
            self.temporary_path / "SMWStreamTrackerLevelProgress.json"
        )
        self.config = dict(self.tracker.DEFAULT_CONFIG)
        self.config["output_folder"] = str(self.temporary_path / "obs")

    def tearDown(self):
        self.tracker.DEATH_SAVE_FILE = self.original_death_save_file
        self.tracker.LEVEL_PROGRESS_SAVE_FILE = (
            self.original_level_progress_save_file
        )
        self.temporary_directory.cleanup()

    def make_worker(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "samplehack"
        worker.game_started = True
        worker.level_id = 1
        worker.level_waiting_for_start = False
        worker.level_auto_tracking_armed = True
        worker.send_livesplit_command = lambda *_args, **_kwargs: True
        return worker

    def make_state(
        self,
        mode,
        save_slot=0,
        player_state=0x00,
        translevel=1,
        level_number=None,
    ):
        if level_number is None:
            level_number = translevel
        return {
            "mode": mode,
            "level_number": level_number,
            "save_slot": save_slot,
            "player_state": player_state,
            "paused": 0,
            "translevel": translevel,
            "exits": 0,
            "level_end_timer": 0,
            "joypad": 0,
            "joypad_axlr": 0,
        }

    def settle_after_death(self, worker, lives=4):
        for _ in range(3):
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                lives,
            )

    def test_hot_potato_rotation_waits_for_stable_post_death_gameplay(self):
        worker = self.make_worker()
        request_id = "safe-rotation-test"
        worker.request_hot_potato_safe_rotation(request_id)
        worker.process_commands()
        ready_at = (
            worker.hot_potato_rotation_requested_at
            + self.tracker.HOT_POTATO_ROTATION_MIN_RECOVERY_SECONDS
        )

        transition_state = self.make_state(0x0F, player_state=0x00)
        self.assertFalse(
            worker.update_hot_potato_rotation_readiness(
                transition_state,
                ready_at + 1.0,
            )
        )
        self.assertEqual(worker.hot_potato_rotation_safe_samples, 0)

        gameplay_state = self.make_state(
            self.tracker.LEVEL_MODE,
            player_state=0x00,
        )
        for sample in range(
            self.tracker.HOT_POTATO_ROTATION_STABLE_SAMPLES - 1
        ):
            self.assertFalse(
                worker.update_hot_potato_rotation_readiness(
                    gameplay_state,
                    ready_at + 1.1 + sample * 0.1,
                )
            )

        self.assertTrue(
            worker.update_hot_potato_rotation_readiness(
                gameplay_state,
                ready_at + 2.0,
            )
        )
        events = []
        while not worker.event_queue.empty():
            events.append(worker.event_queue.get_nowait())
        self.assertIn(
            {
                "type": "hot_potato_rotation_ready",
                "request_id": request_id,
                "mode": self.tracker.LEVEL_MODE,
            },
            events,
        )
        self.assertEqual(worker.hot_potato_rotation_request_id, "")

    def test_hot_potato_rotation_rejects_an_active_death_latch(self):
        worker = self.make_worker()
        worker.request_hot_potato_safe_rotation("latched-death-test")
        worker.process_commands()
        worker.death_detection_latched = True
        state = self.make_state(
            self.tracker.LEVEL_MODE,
            player_state=0x00,
        )

        self.assertFalse(
            worker.update_hot_potato_rotation_readiness(
                state,
                worker.hot_potato_rotation_requested_at
                + self.tracker.HOT_POTATO_ROTATION_MIN_RECOVERY_SECONDS
                + 10.0,
            )
        )
        self.assertEqual(worker.hot_potato_rotation_safe_samples, 0)

    def test_hot_potato_accepts_stable_title_with_stale_player_state(self):
        worker = self.make_worker()
        worker.request_hot_potato_safe_rotation("safe-title-test")
        worker.process_commands()
        worker.death_detection_latched = True
        state = self.make_state(
            self.tracker.PLAYER_SELECT_MODE,
            player_state=0x09,
        )
        ready_at = (
            worker.hot_potato_rotation_requested_at
            + self.tracker.HOT_POTATO_ROTATION_MIN_RECOVERY_SECONDS
            + 1.0
        )

        for sample in range(
            self.tracker.HOT_POTATO_ROTATION_STABLE_SAMPLES - 1
        ):
            self.assertFalse(
                worker.update_hot_potato_rotation_readiness(
                    state,
                    ready_at + sample * 0.1,
                )
            )
        self.assertTrue(
            worker.update_hot_potato_rotation_readiness(
                state,
                ready_at + 1.0,
            )
        )

    def test_override_updates_level_and_total_deaths_together(self):
        worker = self.make_worker()
        worker.select_save_slot(0)

        worker.override_timers(
            game_seconds=None,
            level_seconds=None,
            level_deaths=7,
            total_deaths=42,
        )
        worker.process_commands()

        self.assertEqual(worker.level_death_count, 7)
        self.assertEqual(worker.death_count, 42)
        self.assertEqual(
            worker.load_saved_deaths()[worker.current_time_key],
            42,
        )
        self.assertEqual(
            (self.temporary_path / "obs" / "level_deaths.txt").read_text(
                encoding="utf-8"
            ),
            "Level Deaths: 7",
        )
        self.assertEqual(
            (self.temporary_path / "obs" / "total_deaths.txt").read_text(
                encoding="utf-8"
            ),
            "Total Deaths: 42",
        )

    def test_live_death_counter_updates_before_obs_file_writes(self):
        worker = self.make_worker()
        worker.level_death_count = 4
        worker.death_count = 19
        calls = []
        worker.send_event = lambda event_type, **payload: calls.append(
            ("event", event_type, payload)
        )
        worker.write_text_file = lambda filename, text: calls.append(
            ("file", filename, text)
        )

        worker.update_death_file()

        self.assertEqual(calls[0][0:2], ("event", "deaths"))
        self.assertEqual(calls[0][2]["level_deaths"], 4)
        self.assertEqual(calls[0][2]["total_deaths"], 19)
        self.assertEqual(
            [call[1] for call in calls[1:]],
            ["level_deaths.txt", "death_counter.txt", "total_deaths.txt"],
        )

    def test_first_observed_death_counts_once_and_writes_obs_file(self):
        worker = self.make_worker()
        worker.select_save_slot(0)

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
            )
        )
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
            )
        )

        self.assertEqual(worker.death_count, 1)
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(
            (self.temporary_path / "obs" / "death_counter.txt").read_text(
                encoding="utf-8"
            ),
            "Level Deaths: 1",
        )
        self.assertEqual(
            (self.temporary_path / "obs" / "level_deaths.txt").read_text(
                encoding="utf-8"
            ),
            "Level Deaths: 1",
        )
        self.assertEqual(
            (self.temporary_path / "obs" / "total_deaths.txt").read_text(
                encoding="utf-8"
            ),
            "Total Deaths: 1",
        )

    def test_each_mario_slot_restores_its_own_death_count(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_player_state = 0x00
        worker.update_death_counter_from_state(
            0x09,
            self.tracker.LEVEL_MODE,
        )
        self.settle_after_death(worker)
        worker.previous_player_state = 0x00
        worker.update_death_counter_from_state(
            0x09,
            self.tracker.LEVEL_MODE,
        )
        self.assertEqual(worker.death_count, 2)
        self.assertEqual(worker.level_death_count, 2)

        worker.select_save_slot(1)
        self.assertEqual(worker.death_count, 0)
        self.assertEqual(worker.level_death_count, 0)
        worker.previous_player_state = 0x00
        worker.update_death_counter_from_state(
            0x09,
            self.tracker.LEVEL_MODE,
        )
        self.assertEqual(worker.death_count, 1)
        self.assertEqual(worker.level_death_count, 1)

        restored_worker = self.make_worker()
        restored_worker.select_save_slot(0)
        self.assertEqual(restored_worker.death_count, 2)
        self.assertEqual(restored_worker.level_death_count, 2)
        restored_worker.select_save_slot(1)
        self.assertEqual(restored_worker.death_count, 1)
        self.assertEqual(restored_worker.level_death_count, 1)
        restored_worker.select_save_slot(2)
        self.assertEqual(restored_worker.death_count, 0)
        self.assertEqual(restored_worker.level_death_count, 0)

        saved = json.loads(
            self.tracker.DEATH_SAVE_FILE.read_text(encoding="utf-8")
        )
        self.assertEqual(saved["samplehack::slot0"], 2)
        self.assertEqual(saved["samplehack::slot1"], 1)

    def test_lives_decrement_catches_a_missed_death_animation(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1

        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_switching_slots_does_not_treat_lives_sync_as_a_death(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )

        worker.select_save_slot(1)
        for lives in (5, 4):
            self.assertFalse(
                worker.update_death_counter_from_state(
                    0x00,
                    self.tracker.LEVEL_MODE,
                    lives,
                )
            )

        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 0)

        # Immediately after the two slot-handoff readings, Mario B's first
        # actual life loss remains available as the fallback for hacks whose
        # death animation is missed.
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                3,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_slot_handoff_never_suppresses_primary_death_signal(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )
        worker.select_save_slot(1)

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_animation_and_lives_change_count_only_once(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_mister_delayed_lives_drop_does_not_double_count_death(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )

        # MiSTer can deliver the animation edge, one clean-looking sample,
        # and the lives decrement in three separate memory snapshots.
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertTrue(worker.death_detection_latched)
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

        # The consumed lives signal allows the next clean sample to rearm,
        # and the next actual death must still be counted normally.
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertFalse(worker.death_detection_latched)
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 2)
        self.assertEqual(worker.death_count, 2)

    def test_lives_change_on_death_to_overworld_is_counted(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.OVERWORLD_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_uncleared_overworld_transition_is_not_inferred_as_a_death(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.level_waiting_for_start = False
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.OVERWORLD_MODE,
                player_state=0x00,
            )
            | {"player_lives": 5},
            delta=0.1,
            now=25.0,
        )

        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 0)

    def test_death_to_overworld_counts_when_same_level_is_reentered(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE)
            | {"player_lives": 5},
            delta=0.1,
            now=25.0,
        )
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 5},
            delta=0.1,
            now=25.1,
        )
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 5},
            delta=0.1,
            now=25.2,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_pipe_and_door_room_changes_are_not_retry_deaths(self):
        for transition_mode, label in ((0x0F, "pipe"), (0x10, "door")):
            with self.subTest(transition=label):
                worker = self.make_worker()
                worker.select_save_slot(0)
                worker.previous_mode = self.tracker.LEVEL_MODE
                worker.previous_player_state = 0x00
                worker.previous_player_lives = 5

                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=28.0,
                )
                worker.update_timers_from_state(
                    self.make_state(
                        transition_mode,
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=28.1,
                )
                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        # RA_SNES can expose the old room for the first
                        # returned gameplay sample.
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=28.2,
                )
                self.assertEqual(worker.death_count, 0)

                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        level_number=0x0106,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=28.3,
                )

                self.assertEqual(worker.level_death_count, 0)
                self.assertEqual(worker.death_count, 0)

    def test_same_room_pipe_and_door_cycles_are_not_retry_deaths(self):
        transition_actions = (
            (0x05, "horizontal pipe"),
            (0x06, "vertical pipe"),
            (0x0D, "door"),
        )
        for player_action, label in transition_actions:
            with self.subTest(transition=label):
                worker = self.make_worker()
                worker.select_save_slot(0)
                worker.previous_mode = self.tracker.LEVEL_MODE
                worker.previous_player_state = 0x00
                worker.previous_player_lives = 5

                # SMW announces the intentional transition through $71 while
                # the player is still in gameplay mode.
                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        player_state=player_action,
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=29.0,
                )
                worker.update_timers_from_state(
                    self.make_state(0x10, level_number=0x0105)
                    | {"player_lives": 5},
                    delta=0.1,
                    now=29.1,
                )

                # A same-room door/pipe makes both the translevel and $010B
                # match the origin, so room identity alone must not count it.
                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=29.2,
                )
                worker.update_timers_from_state(
                    self.make_state(
                        self.tracker.LEVEL_MODE,
                        level_number=0x0105,
                    )
                    | {"player_lives": 5},
                    delta=0.1,
                    now=29.3,
                )

                self.assertFalse(
                    worker.intentional_level_transition_pending
                )
                self.assertEqual(worker.level_death_count, 0)
                self.assertEqual(worker.death_count, 0)

    def test_suspicious_pipe_lives_drop_is_consumed_not_counted_later(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5
        worker.last_level_player_lives = 5
        state = self.make_state(self.tracker.LEVEL_MODE) | {
            "player_lives": 4,
            "pipe_action": 1,
        }
        suspicious = self.tracker.death_sample_is_suspicious(
            state,
            previous_mode=self.tracker.LEVEL_MODE,
            slot_lives_baseline_pending=False,
            intentional_transition_pending=False,
        )
        self.assertTrue(suspicious)
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
                suspicious_transition=suspicious,
            )
        )
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.death_count, 0)

    def test_save_restore_lives_sample_is_rejected(self):
        state = self.make_state(
            self.tracker.LEVEL_MODE,
            player_state=0x00,
        )
        self.assertTrue(
            self.tracker.death_sample_is_suspicious(
                state,
                previous_mode=self.tracker.LEVEL_MODE,
                slot_lives_baseline_pending=True,
                intentional_transition_pending=False,
            )
        )

    def test_instant_retry_loading_cycle_counts_without_life_drop(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(0x10) | {"player_lives": 5},
            delta=0.1,
            now=30.0,
        )
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 5},
            delta=0.1,
            now=30.1,
        )
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 5},
            delta=0.1,
            now=30.2,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_death_to_title_via_loading_mode_counts_once(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(0x10) | {"player_lives": 5},
            delta=0.1,
            now=32.0,
        )
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(self.tracker.PLAYER_SELECT_MODE)
            | {"player_lives": 5},
            delta=0.1,
            now=32.1,
        )
        self.assertEqual(worker.load_saved_deaths()["samplehack::slot0"], 1)

    def test_retry_transition_does_not_double_count_death_memory(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(0x10, player_state=0x09)
            | {"player_lives": 4},
            delta=0.1,
            now=35.0,
        )
        self.assertEqual(worker.death_count, 1)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 4},
            delta=0.1,
            now=35.1,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_completed_level_reload_is_not_counted_as_a_death(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE

        worker.update_timers_from_state(
            self.make_state(0x10) | {
                "level_end_timer": 20,
                "player_lives": 5,
            },
            delta=0.1,
            now=40.0,
        )
        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=1)
            | {"player_lives": 5},
            delta=0.1,
            now=40.1,
        )
        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 0)

    def test_death_memory_counts_during_post_selection_loading(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = None
        worker.level_waiting_for_start = True
        worker.level_prestart_tracking = True
        worker.previous_player_state = 0x00

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                0x0B,
                5,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_overworld_fallback_does_not_double_count_a_normal_signal(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.level_waiting_for_start = False
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.OVERWORLD_MODE,
                player_state=0x09,
            )
            | {"player_lives": 4},
            delta=0.1,
            now=30.0,
        )

        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_death_counter_does_not_depend_on_game_timer_started(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.game_started = False
        worker.previous_player_state = 0x00

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_death_detection_rearms_after_respawn(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )
        worker.update_death_counter_from_state(
            0x09,
            self.tracker.LEVEL_MODE,
            4,
        )
        self.settle_after_death(worker, lives=4)

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                3,
            )
        )
        self.assertEqual(worker.level_death_count, 2)
        self.assertEqual(worker.death_count, 2)

    def test_lives_only_deaths_rearm_after_one_recovery_sample(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.update_death_counter_from_state(
            0x00,
            self.tracker.LEVEL_MODE,
            5,
        )

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                4,
            )
        )
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                3,
            )
        )
        self.assertEqual(worker.level_death_count, 2)
        self.assertEqual(worker.death_count, 2)

    def test_startup_guard_arms_from_clean_loading_memory(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.death_startup_guard_active = True
        worker.previous_mode = self.tracker.PLAYER_SELECT_MODE

        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                0x0B,
                5,
            )
        )
        self.assertFalse(worker.death_startup_guard_active)
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertEqual(worker.death_count, 1)

    def test_startup_guard_accepts_confirmed_gameplay_death_edge(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.death_startup_guard_active = True
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.previous_player_lives = 5

        self.assertTrue(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertFalse(worker.death_startup_guard_active)
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_startup_guard_rejects_unconfirmed_stale_death_state(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.death_startup_guard_active = True
        worker.previous_mode = self.tracker.PLAYER_SELECT_MODE
        worker.previous_player_state = None

        self.assertFalse(
            worker.update_death_counter_from_state(
                0x09,
                self.tracker.LEVEL_MODE,
                5,
            )
        )
        self.assertTrue(worker.death_startup_guard_active)
        self.assertEqual(worker.death_count, 0)

    def test_leaving_and_reselecting_the_same_slot_restores_deaths(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.death_count = 4
        worker.level_death_count = 2
        worker.save_current_death_count()
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.run_reached_gameplay = True

        worker.update_timers_from_state(
            self.make_state(self.tracker.PLAYER_SELECT_MODE),
            delta=0.1,
            now=10.0,
        )
        self.assertEqual(worker.death_count, 0)
        self.assertEqual(worker.level_death_count, 0)
        self.assertIsNone(worker.current_time_key)

        worker.update_timers_from_state(
            self.make_state(self.tracker.OVERWORLD_MODE),
            delta=0.1,
            now=10.1,
        )
        self.assertEqual(worker.death_count, 4)
        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.current_time_key, "samplehack::slot0")

    def test_reopening_started_slot_directly_into_level_rearms_deaths(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.game_elapsed = 45.0
        worker.death_count = 4
        worker.level_death_count = 2
        worker.save_current_game_time()
        worker.save_current_death_count()
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.run_reached_gameplay = True

        worker.update_timers_from_state(
            self.make_state(self.tracker.PLAYER_SELECT_MODE),
            delta=0.1,
            now=50.0,
        )

        self.assertFalse(worker.game_started)
        self.assertIsNone(worker.current_time_key)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                player_state=0x09,
                translevel=1,
            ),
            delta=0.1,
            now=50.1,
        )

        self.assertTrue(worker.level_auto_tracking_armed)
        self.assertEqual(worker.current_time_key, "samplehack::slot0")
        self.assertEqual(worker.level_id, 1)
        self.assertEqual(worker.level_death_count, 2)
        self.assertEqual(worker.death_count, 4)

        # The first readable sample can retain a stale death state from file
        # loading. A normal gameplay sample arms detection; the next genuine
        # transition must still count immediately.
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                player_state=0x00,
                translevel=1,
            ),
            delta=0.1,
            now=50.2,
        )
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                player_state=0x09,
                translevel=1,
            ),
            delta=0.1,
            now=50.3,
        )

        self.assertEqual(worker.level_death_count, 3)
        self.assertEqual(worker.death_count, 5)

    def test_new_level_resets_level_deaths_but_keeps_total(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_id = 1
        worker.level_waiting_for_start = False
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.previous_player_state = 0x00
        worker.level_death_count = 3
        worker.death_count = 8

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, translevel=2),
            delta=0.1,
            now=20.0,
        )

        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 8)
        self.assertEqual(worker.level_id, 2)

    def test_no_retry_death_survives_an_intermediate_game_mode(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.previous_mode = self.tracker.LEVEL_MODE
        worker.level_id = 1
        worker.level_waiting_for_start = False

        # Establish the last clean in-level lives value.
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.LEVEL_MODE,
                5,
            )
        )

        # Older/no-retry hacks can pass through an unrecognized transition
        # after decrementing lives.  The rolling previous value becomes 4,
        # but this sample is not itself a valid death context.
        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                0x0D,
                4,
            )
        )
        self.assertEqual(worker.death_count, 0)

        # By the time the overworld appears, $71 no longer says death and the
        # immediate lives comparison is also flat.  The retained clean-level
        # baseline must still record exactly one death.
        self.assertTrue(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.OVERWORLD_MODE,
                4,
            )
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

        self.assertFalse(
            worker.update_death_counter_from_state(
                0x00,
                self.tracker.OVERWORLD_MODE,
                4,
            )
        )
        self.assertEqual(worker.death_count, 1)

    def test_level_and_total_resets_are_independent(self):
        worker = self.make_worker()
        worker.select_save_slot(0)
        worker.level_death_count = 4
        worker.death_count = 12
        worker.save_current_death_count()

        self.assertTrue(worker.clear_level_death_count())
        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 12)

        worker.level_death_count = 2
        self.assertTrue(worker.clear_saved_death_count())
        self.assertEqual(worker.level_death_count, 2)
        self.assertEqual(worker.death_count, 0)


if __name__ == "__main__":
    unittest.main()
