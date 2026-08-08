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
        self.original_level_progress_save_file = (
            self.tracker.LEVEL_PROGRESS_SAVE_FILE
        )
        self.tracker.DEATH_SAVE_FILE = (
            Path(self.temporary_directory.name)
            / "SMWStreamTrackerDeaths.json"
        )
        self.tracker.LEVEL_PROGRESS_SAVE_FILE = (
            Path(self.temporary_directory.name)
            / "SMWStreamTrackerLevelProgress.json"
        )
        self.config = dict(self.tracker.DEFAULT_CONFIG)
        self.config["output_folder"] = str(
            Path(self.temporary_directory.name) / "obs"
        )
        self.config["overworld_idle_seconds"] = 30

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
        save_slot=0,
        paused=0,
        sprite_lock=0,
        level_flags=0,
    ):
        return {
            "mode": mode,
            "save_slot": save_slot,
            "player_state": player_state,
            "player_lives": player_lives,
            "paused": paused,
            "sprite_lock": sprite_lock,
            "translevel": translevel,
            "level_flags": level_flags,
            "exits": exits,
            "level_end_timer": level_end_timer,
            "joypad": 0,
            "joypad_pressed": 0,
            "joypad_axlr": 0,
            "joypad_axlr_pressed": 0,
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

    def test_new_rom_starts_all_tracking_from_post_select_loading_mode(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "newgamehack"
        worker.previous_mode = None
        worker.commands = []
        worker.send_livesplit_command = (
            lambda timer, command: worker.commands.append(
                (timer, command)
            )
        )

        def restore_selected_slot(slot):
            worker.select_save_slot(slot)
            return 0.0

        worker.get_saved_game_time_for_slot = restore_selected_slot

        # 0B is the first loading mode after Mario A/B/C selection. Older
        # logic missed the run when the ROM was first detected here rather
        # than on the exact 0A -> 0B transition.
        worker.update_timers_from_state(
            self.make_state(
                0x0B,
                save_slot=0xFF,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=60.0,
        )

        self.assertTrue(worker.game_started)
        self.assertTrue(worker.level_auto_tracking_armed)
        self.assertTrue(worker.level_prestart_tracking)
        self.assertIsNone(worker.active_save_slot)
        self.assertGreater(worker.game_elapsed, 0.0)
        self.assertGreater(worker.level_elapsed, 0.0)
        self.assertIn(("level", "starttimer"), worker.commands)

        # A stale death byte during loading must not add an automatic death.
        # The timer is already running, and death counting arms only after a
        # normal playable sample establishes a clean baseline.
        # The slot byte can also become valid on this sample. Keep the time
        # accumulated since confirmation and attach it to that Mario file.
        loading_elapsed = worker.game_elapsed
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                save_slot=1,
                translevel=3,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=60.25,
        )

        self.assertEqual(worker.level_id, 3)
        self.assertEqual(worker.active_save_slot, 1)
        self.assertGreater(worker.game_elapsed, loading_elapsed)
        self.assertGreater(worker.level_elapsed, 0.0)
        self.assertEqual(worker.level_death_count, 0)
        self.assertEqual(worker.death_count, 0)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=3,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=60.5,
        )
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                translevel=3,
                player_state=0x09,
                player_lives=4,
            ),
            delta=0.25,
            now=60.75,
        )
        self.assertEqual(worker.level_death_count, 1)
        self.assertEqual(worker.death_count, 1)

    def test_file_selection_carries_slot_into_loading_and_starts_timers(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "slotcarryhack"
        worker.send_livesplit_command = lambda *_args, **_kwargs: True

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.PLAYER_SELECT_MODE,
                save_slot=2,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.10,
            now=75.0,
        )
        worker.update_timers_from_state(
            self.make_state(
                0x0B,
                save_slot=0xFF,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=75.25,
        )

        self.assertEqual(worker.active_save_slot, 2)
        self.assertTrue(worker.game_started)
        self.assertTrue(worker.level_prestart_tracking)
        self.assertGreater(worker.game_elapsed, 0.0)
        self.assertGreater(worker.level_elapsed, 0.0)

    def test_timers_start_only_after_leaving_title_screen(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "immediatefileconfirm"
        worker.send_livesplit_command = lambda *_args, **_kwargs: True

        state = self.make_state(
            self.tracker.PLAYER_SELECT_MODE,
            save_slot=1,
            player_state=0x00,
            player_lives=5,
        )
        state["joypad_axlr"] = 0x80  # A confirms Mario B.

        worker.update_timers_from_state(
            state,
            delta=0.10,
            now=90.0,
        )

        self.assertFalse(worker.game_started)
        self.assertFalse(worker.level_prestart_tracking)
        self.assertEqual(worker.game_elapsed, 0.0)
        self.assertEqual(worker.level_elapsed, 0.0)

        # Releasing the button while the title/file-select group is still
        # visible must not start either timer.
        state["joypad_axlr"] = 0
        worker.update_timers_from_state(
            state,
            delta=0.10,
            now=90.1,
        )
        self.assertFalse(worker.game_started)

        # Both timers start on the first sample after the title group ends.
        worker.update_timers_from_state(
            self.make_state(
                0x0B,
                save_slot=0xFF,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=90.35,
        )
        self.assertTrue(worker.game_started)
        self.assertTrue(worker.level_prestart_tracking)
        self.assertTrue(worker.level_livesplit_running)
        self.assertEqual(worker.active_save_slot, 1)
        # This clean post-title memory sample also establishes the death
        # baseline, so a real first death is eligible immediately.
        self.assertFalse(worker.death_startup_guard_active)
        self.assertGreater(worker.game_elapsed, 0.0)
        self.assertGreater(worker.level_elapsed, 0.0)

    def test_file_highlight_without_confirm_does_not_start_timers(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "highlightonly"
        worker.send_livesplit_command = lambda *_args, **_kwargs: True

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.PLAYER_SELECT_MODE,
                save_slot=2,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.10,
            now=91.0,
        )

        self.assertFalse(worker.game_started)
        self.assertFalse(worker.level_prestart_tracking)

    def test_file_confirm_runs_through_title_mode_opening_cutscene(self):
        worker = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        worker.current_rom_key = "openingcutscene"
        worker.send_livesplit_command = lambda *_args, **_kwargs: True

        state = self.make_state(
            self.tracker.PLAYER_SELECT_MODE,
            save_slot=0,
            player_state=0x00,
            player_lives=5,
        )
        state["joypad_axlr_pressed"] = 0x80
        worker.update_timers_from_state(
            state,
            delta=0.10,
            now=100.0,
        )

        self.assertFalse(worker.game_started)
        self.assertTrue(worker.startup_sequence_active)
        self.assertEqual(worker.game_elapsed, 0.0)
        self.assertEqual(worker.level_elapsed, 0.0)

        # Opening scenes in some hacks remain in another title-like mode.
        # Neither timer starts until the title group is actually left.
        worker.update_timers_from_state(
            self.make_state(
                0x08,
                save_slot=0,
                sprite_lock=1,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=100.25,
        )

        self.assertFalse(worker.game_started)
        self.assertTrue(worker.startup_sequence_active)
        self.assertEqual(worker.game_elapsed, 0.0)
        self.assertEqual(worker.level_elapsed, 0.0)

        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                save_slot=0,
                translevel=3,
                sprite_lock=0,
                player_state=0x00,
                player_lives=5,
            ),
            delta=0.25,
            now=100.50,
        )

        self.assertFalse(worker.startup_sequence_active)
        self.assertTrue(worker.run_reached_gameplay)
        self.assertTrue(worker.game_started)
        self.assertGreater(worker.game_elapsed, 0.0)
        self.assertGreater(worker.level_elapsed, 0.0)

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

    def test_timer_grace_applies_outside_overworld_too(self):
        worker = self.make_worker()
        worker.game_elapsed = 20.0

        # A non-overworld interruption/cutscene receives the same grace.
        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=300.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=331.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertIn(("game", "pause"), worker.commands)
        self.assertIn(("level", "pause"), worker.commands)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=332.0,
        )
        self.assertEqual(worker.game_elapsed, 21.0)
        self.assertEqual(worker.level_elapsed, 11.0)
        self.assertIn(("game", "resume"), worker.commands)
        self.assertIn(("level", "resume"), worker.commands)

    def test_retroarch_losing_focus_pauses_both_timers_immediately(self):
        worker = self.make_worker()
        worker.config["selected_platform"] = "RetroArch"
        worker.game_elapsed = 20.0
        focus = {"active": False}
        worker.retroarch_has_focus = lambda: focus["active"]
        worker.retroarch_runloop_is_paused = lambda now: False

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=350.0,
        )

        self.assertTrue(worker.retroarch_focus_paused)
        self.assertEqual(worker.game_elapsed, 20.0)
        self.assertEqual(worker.level_elapsed, 10.0)
        self.assertIn(("game", "pause"), worker.commands)
        self.assertIn(("level", "pause"), worker.commands)

        focus["active"] = True
        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=350.5,
        )

        self.assertFalse(worker.retroarch_focus_paused)
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertIn(("game", "resume"), worker.commands)
        self.assertIn(("level", "resume"), worker.commands)

    def test_configured_grace_stops_both_elapsed_timers(self):
        worker = self.make_worker()
        worker.config["timer_grace_seconds"] = 2
        worker.game_elapsed = 20.0

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=400.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=402.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertTrue(worker.game_livesplit_overworld_paused)
        self.assertTrue(worker.level_livesplit_overworld_paused)
        self.assertIn(("game", "pause"), worker.commands)
        self.assertIn(("level", "pause"), worker.commands)

    def test_stale_startup_transition_cannot_bypass_level_grace(self):
        worker = self.make_worker()
        worker.config["timer_grace_seconds"] = 2
        worker.game_elapsed = 20.0
        # Modified hacks can leave their file-start/cutscene transition flag
        # active longer than expected. It must not override the shared grace.
        worker.startup_sequence_active = True

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=410.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)

        worker.update_timers_from_state(
            self.make_state(0x1A),
            delta=0.5,
            now=412.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertTrue(worker.game_livesplit_overworld_paused)
        self.assertTrue(worker.level_livesplit_overworld_paused)

    def test_standard_in_game_pause_uses_configured_grace(self):
        worker = self.make_worker()
        worker.config["timer_grace_seconds"] = 2
        worker.game_elapsed = 20.0

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, paused=1),
            delta=0.5,
            now=500.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, paused=1),
            delta=0.5,
            now=502.0,
        )
        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertTrue(worker.game_livesplit_overworld_paused)
        self.assertTrue(worker.level_livesplit_overworld_paused)

    def test_sprite_locked_interruption_uses_configured_grace(self):
        worker = self.make_worker()
        worker.config["timer_grace_seconds"] = 2
        worker.game_elapsed = 20.0

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, sprite_lock=1),
            delta=0.5,
            now=510.0,
        )
        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE, sprite_lock=1),
            delta=0.5,
            now=512.0,
        )

        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertIn(("game", "pause"), worker.commands)
        self.assertIn(("level", "pause"), worker.commands)

    def test_retroarch_pause_status_uses_configured_grace(self):
        worker = self.make_worker()
        worker.config["selected_platform"] = "RetroArch"
        worker.config["timer_grace_seconds"] = 2
        worker.game_elapsed = 20.0
        worker.retroarch_has_focus = lambda: True
        worker.retroarch_runloop_is_paused = lambda now: True

        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=520.0,
        )
        worker.update_timers_from_state(
            self.make_state(self.tracker.LEVEL_MODE),
            delta=0.5,
            now=522.0,
        )

        self.assertEqual(worker.game_elapsed, 20.5)
        self.assertEqual(worker.level_elapsed, 10.5)
        self.assertTrue(worker.game_livesplit_overworld_paused)
        self.assertTrue(worker.level_livesplit_overworld_paused)

    def test_goal_updates_immediately_then_confirms_without_duplicate(self):
        worker = self.make_worker()
        worker.previous_exit_count = 5
        worker.displayed_exit_count = 5

        # The goal-tape/orb frame immediately displays the expected new exit,
        # before SMW updates its authoritative counter on a later frame.
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=1,
                exits=5,
            ),
            delta=0.2,
            now=450.0,
        )
        self.assertEqual(worker.displayed_exit_count, 6)
        self.assertTrue(worker.provisional_goal_exit)

        # The provisional display is held through the goal sequence.
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=2,
                exits=5,
            ),
            delta=0.2,
            now=450.2,
        )
        self.assertEqual(worker.displayed_exit_count, 6)

        # SMW's real increment confirms the display and records this normal
        # route so replaying it cannot show another +1.
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=3,
                exits=6,
            ),
            delta=0.2,
            now=450.4,
        )
        self.assertEqual(worker.displayed_exit_count, 6)
        self.assertFalse(worker.provisional_goal_exit)

        # Replaying and clearing the same route leaves SMW's real counter at
        # six, so the tracker must also remain at six without a false flash.
        worker.level_finished = False
        worker.level_livesplit_running = True
        worker.previous_exit_count = 6
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=1,
                exits=6,
            ),
            delta=0.2,
            now=451.0,
        )
        self.assertEqual(worker.displayed_exit_count, 6)
        self.assertFalse(worker.provisional_goal_exit)

        # A secret route on the same translevel is tracked independently and
        # still receives its own immediate display.
        worker.level_finished = False
        secret_state = self.make_state(
            self.tracker.LEVEL_MODE,
            level_end_timer=1,
            exits=6,
        )
        secret_state["secret_goal_flag"] = 1
        worker.update_timers_from_state(
            secret_state,
            delta=0.2,
            now=452.0,
        )
        self.assertEqual(worker.displayed_exit_count, 7)
        self.assertTrue(worker.provisional_goal_exit)

    def test_previously_beaten_level_never_flashes_an_extra_exit(self):
        worker = self.make_worker()
        worker.previous_exit_count = 6
        worker.displayed_exit_count = 6

        # This worker has never personally observed the route, but SMW's
        # per-level save flag says it was beaten in an earlier session.
        worker.update_timers_from_state(
            self.make_state(
                self.tracker.LEVEL_MODE,
                level_end_timer=1,
                exits=6,
                level_flags=0x80,
            ),
            delta=0.2,
            now=453.0,
        )

        self.assertEqual(worker.displayed_exit_count, 6)
        self.assertFalse(worker.provisional_goal_exit)

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

    def test_reentering_level_restores_its_timer_and_deaths(self):
        worker = self.make_worker()
        worker.level_elapsed = 42.5
        worker.level_death_count = 6
        worker.save_current_level_progress()

        worker.start_fresh_level_tracking(2)
        worker.level_elapsed = 8.0
        worker.level_death_count = 1
        worker.save_current_level_progress()

        worker.start_fresh_level_tracking(1)

        self.assertEqual(worker.level_elapsed, 42.5)
        self.assertEqual(worker.level_death_count, 6)
        self.assertIn(
            ("level", "setgametime 0:00:42.500"),
            worker.commands,
        )

    def test_level_progress_is_separate_for_each_mario_slot(self):
        worker = self.make_worker()
        worker.level_elapsed = 25.0
        worker.level_death_count = 3
        worker.save_current_level_progress()

        worker.select_save_slot(1)
        self.assertEqual(worker.level_elapsed, 0.0)
        self.assertEqual(worker.level_death_count, 0)
        worker.level_elapsed = 9.0
        worker.level_death_count = 2
        worker.save_current_level_progress()

        worker.select_save_slot(0)
        self.assertEqual(worker.level_elapsed, 25.0)
        self.assertEqual(worker.level_death_count, 3)
        worker.select_save_slot(1)
        self.assertEqual(worker.level_elapsed, 9.0)
        self.assertEqual(worker.level_death_count, 2)

    def test_level_progress_restores_after_worker_restart(self):
        worker = self.make_worker()
        worker.level_elapsed = 91.25
        worker.level_death_count = 11
        worker.save_current_level_progress()

        restored = self.tracker.TrackerWorker(
            dict(self.config),
            queue.Queue(),
        )
        restored.current_rom_key = "samplehack"
        restored.current_time_key = "samplehack::slot0"
        restored.active_save_slot = 0
        restored.commands = []
        restored.send_livesplit_command = (
            lambda timer, command: restored.commands.append(
                (timer, command)
            )
        )
        restored.start_fresh_level_tracking(1)

        self.assertEqual(restored.level_elapsed, 91.25)
        self.assertEqual(restored.level_death_count, 11)

    def test_manual_level_resets_are_saved_independently(self):
        worker = self.make_worker()
        worker.level_elapsed = 32.0
        worker.level_death_count = 4
        worker.save_current_level_progress()

        self.assertTrue(worker.clear_level_death_count())
        self.assertEqual(worker.get_saved_level_progress(1), (32.0, 0))

        worker.level_elapsed = 0.0
        worker.save_current_level_progress()
        self.assertEqual(worker.get_saved_level_progress(1), (0.0, 0))

    def test_corrupt_level_progress_file_is_ignored(self):
        self.tracker.LEVEL_PROGRESS_SAVE_FILE.write_text(
            "not json",
            encoding="utf-8",
        )
        worker = self.make_worker()
        worker.start_fresh_level_tracking(1)
        self.assertEqual(worker.level_elapsed, 0.0)
        self.assertEqual(worker.level_death_count, 0)


if __name__ == "__main__":
    unittest.main()
