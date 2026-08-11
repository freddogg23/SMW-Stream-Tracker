import importlib.util
from pathlib import Path
import queue
import sys
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_connection_service_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ConnectionServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_automatic_prefers_sni_and_keeps_qusb_fallback(self):
        config = {
            "sni_path": "C:/Tools/SNI/sni.exe",
            "qusb2snes_path": "C:/Tools/QUsb2Snes/QUsb2Snes.exe",
            "connection_service_preference": "Automatic",
        }
        self.assertEqual(
            self.tracker.connection_service_candidates(config),
            [
                ("SNI", "C:/Tools/SNI/sni.exe"),
                (
                    "QUsb2Snes",
                    "C:/Tools/QUsb2Snes/QUsb2Snes.exe",
                ),
            ],
        )

    def test_qusb_preference_reverses_fallback_order(self):
        config = {
            "sni_path": "C:/Tools/SNI/sni.exe",
            "qusb2snes_path": "C:/Tools/QUsb2Snes/QUsb2Snes.exe",
            "connection_service_preference": "QUsb2Snes",
        }
        self.assertEqual(
            self.tracker.connection_service_candidates(config)[0][0],
            "QUsb2Snes",
        )
        self.assertEqual(
            self.tracker.preferred_connection_service_path(config),
            "C:/Tools/QUsb2Snes/QUsb2Snes.exe",
        )

    def test_legacy_path_does_not_duplicate_a_configured_service(self):
        config = {
            "sni_path": "C:/Tools/SNI/sni.exe",
            "qusb2snes_path": "",
            "platform_interface_path": "C:/Tools/SNI/sni.exe",
            "connection_service_preference": "SNI",
        }
        self.assertEqual(
            self.tracker.connection_service_candidates(config),
            [("SNI", "C:/Tools/SNI/sni.exe")],
        )

    def test_hack_selector_prompt_uses_active_language(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        prompt = app._main_hack_selector_prompt_text()
        self.assertEqual(prompt, "Hack suchen oder auswählen...")
        self.assertTrue(app._is_main_hack_selector_prompt(prompt))

    def test_retroarch_reconnect_error_uses_active_language(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        error = app._translate_ui_text(
            "RetroArch Network Commands are not responding. In "
            "RetroArch, enable Settings > Network > Network Commands "
            "on port 55355, launch a game, and try Refresh."
        )

        self.assertIn("RetroArch-Netzwerkbefehle", error)
        self.assertNotIn("are not responding", error)

    def test_remote_host_loss_is_treated_as_transient(self):
        self.assertTrue(
            self.tracker.is_transient_connection_error(
                "Connection to remote host was lost."
            )
        )

    def test_configuration_error_is_not_treated_as_transient(self):
        self.assertFalse(
            self.tracker.is_transient_connection_error(
                "RetroArch Network Commands are not responding."
            )
        )

    def test_recent_live_sample_hides_brief_retroarch_disconnect(self):
        self.assertFalse(
            self.tracker.connection_loss_needs_user_attention(
                "Connection to remote host was lost.",
                last_successful_sample_at=100.0,
                now=106.0,
            )
        )

    def test_stale_live_sample_surfaces_retroarch_disconnect(self):
        self.assertTrue(
            self.tracker.connection_loss_needs_user_attention(
                "Connection to remote host was lost.",
                last_successful_sample_at=100.0,
                now=116.0,
            )
        )

    def test_game_state_uses_small_wram_windows_including_death_memory(self):
        worker = self.tracker.TrackerWorker(
            dict(self.tracker.DEFAULT_CONFIG),
            queue.Queue(),
        )
        snapshot = bytearray(self.tracker.LIVE_STATE_SIZE)
        expected = {
            self.tracker.GAME_MODE_ADDRESS: 0x14,
            self.tracker.SAVE_SLOT_ADDRESS: 0x02,
            self.tracker.PLAYER_STATE_ADDRESS: 0x09,
            self.tracker.PLAYER_LIVES_ADDRESS: 0x04,
            self.tracker.PAUSE_FLAG_ADDRESS: 0x01,
            self.tracker.TRANSLEVEL_ADDRESS: 0x2A,
            self.tracker.EXIT_COUNTER_ADDRESS: 0x11,
            self.tracker.LEVEL_END_TIMER_ADDRESS: 0x20,
            self.tracker.JOYPAD_HELD_ADDRESS: 0x10,
            self.tracker.JOYPAD_AXLR_ADDRESS: 0x20,
        }
        base = int(self.tracker.LIVE_STATE_BASE_ADDRESS, 16)
        for address, value in expected.items():
            snapshot[int(address, 16) - base] = value

        calls = []

        def read_snapshot_chunk(_ws, address, size):
            offset = int(address, 16) - base
            calls.append((address, size))
            return bytes(snapshot[offset : offset + size])

        worker.read_memory = read_snapshot_chunk
        state = worker.read_game_state(object())

        self.assertEqual(calls, list(self.tracker.LIVE_STATE_WINDOWS))
        self.assertEqual(state["mode"], 0x14)
        self.assertEqual(state["save_slot"], 0x02)
        self.assertEqual(state["player_state"], 0x09)
        self.assertEqual(state["player_lives"], 0x04)
        self.assertEqual(state["translevel"], 0x2A)
        self.assertEqual(state["exits"], 0x11)

    def test_retroarch_game_name_is_used_before_bridge_info(self):
        config = dict(self.tracker.DEFAULT_CONFIG)
        config["selected_platform"] = "RetroArch"
        worker = self.tracker.TrackerWorker(config, queue.Queue())
        worker.get_retroarch_game_name = (
            lambda timeout=0.18: "Quickie World 2.sfc"
        )
        worker.send_request = lambda *_args, **_kwargs: self.fail(
            "RetroArch title should be resolved before bridge Info"
        )

        self.assertEqual(
            worker.get_loaded_rom_path(object()),
            "Quickie World 2.sfc",
        )

    def test_running_retroarch_is_ready_without_strict_saved_paths(self):
        class Value:
            def get(self):
                return "RetroArch"

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.platform_var = Value()
        app.connection_is_connected = False
        app.config = {
            "retroarch_executable_path": "",
            "retroarch_core_path": "",
            "output_folder": "",
            "platform_rom_library_folder": "",
        }
        app._test_tcp_port = lambda host, port: False
        app._retroarch_status = lambda timeout=0.5: "GET_STATUS PLAYING"
        retroarch_result = next(
            result
            for result in app._health_check_results()
            if result[1] == "RetroArch"
        )
        self.assertEqual(retroarch_result[0], "Ready")

    def test_livesplit_commands_are_skipped_when_server_is_not_running(self):
        worker = self.tracker.TrackerWorker(
            dict(self.tracker.DEFAULT_CONFIG),
            queue.Queue(),
        )
        with (
            mock.patch.object(
                self.tracker,
                "livesplit_server_is_running",
                return_value=False,
            ) as running_check,
            mock.patch.object(
                self.tracker.socket,
                "create_connection",
            ) as create_connection,
        ):
            self.assertFalse(
                worker.send_livesplit_command("game", "starttimer")
            )
            self.assertFalse(
                worker.send_livesplit_command("game", "pause")
            )

        running_check.assert_called_once()
        create_connection.assert_not_called()

    @unittest.skipUnless(
        sys.platform.startswith("win"),
        "Classic LiveSplit health checks apply only to Windows.",
    )
    def test_health_check_lists_livesplit_as_optional_when_not_running(self):
        class Value:
            def get(self):
                return "FXPAK Pro"

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.platform_var = Value()
        app.connection_is_connected = False
        app.config = dict(self.tracker.DEFAULT_CONFIG)
        app._test_tcp_port = lambda host, port: False
        app._retroarch_status = lambda timeout=0.5: None
        with mock.patch.object(
            self.tracker,
            "livesplit_server_is_running",
            return_value=False,
        ):
            livesplit_result = next(
                result
                for result in app._health_check_results()
                if result[1] == "LiveSplit timer servers"
            )

        self.assertEqual(livesplit_result[0], "Optional")
        self.assertIn("commands are disabled", livesplit_result[2])
        self.assertIn("OBS text files continue", livesplit_result[2])


if __name__ == "__main__":
    unittest.main()
