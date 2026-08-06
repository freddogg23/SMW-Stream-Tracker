import importlib.util
from pathlib import Path
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
