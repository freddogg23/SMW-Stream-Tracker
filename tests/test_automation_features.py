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
        "smw_tracker_automation_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AutomationFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_reconciliation_modes_adjust_confirmation_strength(self):
        responsive, responsive_initial = (
            self.tracker.live_state_confirmation_samples(
                {"statistics_reconciliation_mode": "Responsive"}
            )
        )
        balanced, balanced_initial = (
            self.tracker.live_state_confirmation_samples(
                {"statistics_reconciliation_mode": "Balanced"}
            )
        )
        conservative, conservative_initial = (
            self.tracker.live_state_confirmation_samples(
                {"statistics_reconciliation_mode": "Conservative"}
            )
        )
        self.assertLess(responsive["exits"], balanced["exits"])
        self.assertGreater(conservative["exits"], balanced["exits"])
        self.assertLess(responsive_initial, balanced_initial)
        self.assertGreater(conservative_initial, balanced_initial)

    def test_completion_detection_finishes_only_once(self):
        events = queue.Queue()
        worker = self.tracker.TrackerWorker(
            {
                "automatic_completion_detection": True,
                "completion_detection_always_ask": False,
            },
            events,
        )
        worker.game_started = True
        worker.game_finished = False
        worker.current_hack_title = "Test Hack"
        worker.send_livesplit_command = lambda *_args, **_kwargs: None
        worker.save_current_game_time = lambda: None
        worker.update_timer_files = lambda: None
        worker.log = lambda *_args, **_kwargs: None

        self.assertFalse(worker.check_for_automatic_completion(9, 10))
        self.assertTrue(worker.check_for_automatic_completion(10, 10))
        self.assertFalse(worker.check_for_automatic_completion(10, 10))
        self.assertTrue(worker.game_finished)
        self.assertTrue(worker.game_manual_paused)
        self.assertEqual(events.get_nowait()["type"], "completion_detected")

    def test_completion_detection_can_require_confirmation(self):
        events = queue.Queue()
        worker = self.tracker.TrackerWorker(
            {
                "automatic_completion_detection": True,
                "completion_detection_always_ask": True,
            },
            events,
        )
        worker.game_started = True
        worker.current_hack_title = "Test Hack"
        worker.log = lambda *_args, **_kwargs: None

        self.assertFalse(
            worker.check_for_automatic_completion(
                9,
                10,
                completion_state=True,
            )
        )
        self.assertFalse(
            worker.check_for_automatic_completion(
                10,
                10,
                completion_state=False,
            )
        )
        self.assertTrue(
            worker.check_for_automatic_completion(
                10,
                10,
                completion_state=True,
            )
        )
        self.assertFalse(worker.game_finished)
        event = events.get_nowait()
        self.assertTrue(event["requires_confirmation"])

    def test_adaptive_sample_rate_backs_off_and_recovers(self):
        slow = self.tracker.adaptive_tracking_sample_interval(0.10, 0.20)
        recovered = self.tracker.adaptive_tracking_sample_interval(slow, 0.01)
        self.assertGreater(slow, 0.10)
        self.assertLess(recovered, slow)
        self.assertGreaterEqual(
            recovered,
            self.tracker.TRACKING_SAMPLE_INTERVAL_MIN,
        )
        self.assertLessEqual(
            slow,
            self.tracker.TRACKING_SAMPLE_INTERVAL_MAX,
        )

    def test_named_mister_profiles_migrate_without_passwords(self):
        profiles, active = self.tracker.normalized_mister_profiles(
            {
                "mister_host": "192.168.50.145",
                "mister_ssh_user": "root",
                "mister_ssh_port": 22,
                "mister_password": "must-not-copy",
            }
        )
        self.assertEqual(active, "MiSTer")
        self.assertEqual(profiles[0]["host"], "192.168.50.145")
        self.assertNotIn("password", profiles[0])

    def test_online_mister_profile_prefers_active_then_fails_over(self):
        config = {
            "active_mister_profile": "Living Room",
            "mister_profiles": [
                {
                    "name": "Living Room",
                    "host": "192.168.50.116",
                    "port": 22,
                },
                {
                    "name": "Office",
                    "host": "192.168.50.145",
                    "port": 22,
                },
            ],
        }
        selected = self.tracker.online_mister_profile(
            config,
            lambda host, port: host == "192.168.50.145" and port == 23074,
        )
        self.assertEqual(selected["name"], "Office")
        self.assertTrue(
            self.tracker.apply_mister_profile_to_config(config, selected)
        )
        self.assertEqual(config["active_mister_profile"], "Office")
        self.assertEqual(config["mister_host"], "192.168.50.145")

    def test_recommended_streamerbot_actions_match_prefixed_names(self):
        events, controls = self.tracker.recommended_streamerbot_action_mappings(
            [
                {"id": "event-1", "name": "SMW Tracker - Death Added"},
                {"id": "control-1", "name": "Tracker Play Random Hack"},
            ]
        )
        self.assertEqual(events["death_added"]["id"], "event-1")
        self.assertEqual(controls["play_random_hack"]["id"], "control-1")

    def test_library_maintenance_repairs_metadata_without_deleting_roms(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            rom = Path(folder) / "Game (U) [!].sfc"
            rom.write_bytes(b"rom")
            records = [
                {"id": "same", "title": "Game (U) [!]", "local_rom_path": str(rom)},
                {"id": "same", "title": "Duplicate", "local_rom_path": str(rom)},
            ]
            maintained, report = self.tracker.maintain_non_smw_rom_library(
                records
            )
            self.assertEqual(len(maintained), 1)
            self.assertEqual(maintained[0]["title"], "Game")
            self.assertEqual(report["duplicates_removed"], 1)
            self.assertTrue(rom.is_file())

    def test_tracker_automation_is_on_platform_not_timers(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            'automation_card = tk.Frame(\n            platform_form,',
            source,
        )
        self.assertNotIn(
            'automation_card = tk.Frame(\n            body,',
            source,
        )

    def test_platform_setup_only_sizes_the_selected_platform_page(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "for setup_name, setup_page in platform_setup_pages.items():",
            source,
        )
        self.assertIn("setup_page.grid_remove()", source)
        self.assertIn("setup_page.grid()", source)
        self.assertNotIn(
            "self.root.winfo_width() >= self._ui_px(1180)",
            source,
        )

    def test_retroarch_platform_setup_uses_compact_two_column_layout(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn("retroarch_fields = tk.Frame(", source)
        self.assertIn('uniform="retroarch_fields"', source)
        self.assertIn("retroarch_left_row = add_platform_setup_path(", source)
        self.assertIn("retroarch_right_row = add_platform_service_choice(", source)
        self.assertIn(
            "action_columns = min(3, len(selected_actions))",
            source,
        )


if __name__ == "__main__":
    unittest.main()
