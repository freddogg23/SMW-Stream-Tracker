import importlib.util
import json
from pathlib import Path
import sys
import unittest

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)
PLUGIN_ROOT = (
    PROJECT_ROOT
    / "streamdeck"
    / "com.freddogg23.smwstreamtracker.sdPlugin"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_streamdeck_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeTrackerApp:
    def __init__(self):
        self.smwcentral_spc_command_path = Path("command.json")
        self.smwcentral_spc_native_state = {
            "elapsed": "0:30",
            "duration": "2:00",
            "looping": False,
            "volume": 80,
        }
        self.sent_commands = []
        self.events = []
        self.opened_radio = False
        self.closed_radio = False

    @staticmethod
    def _obs_widget_request_id(document):
        return str(document.get("request_id", ""))

    def _send_smwcentral_spc_command(self, action, value=None):
        self.sent_commands.append((action, value))

    def _publish_obs_widget_event(self, document):
        self.events.append(document)

    def _open_smwcentral_radio(self):
        self.opened_radio = True

    def _stop_smwcentral_webview_process(self):
        self.closed_radio = True


class StreamDeckPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_manifest_is_windows_only_and_exposes_spc_controls(self):
        manifest = json.loads(
            (PLUGIN_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["SDKVersion"], 2)
        self.assertEqual(manifest["Nodejs"]["Version"], "20")
        self.assertEqual(
            manifest["OS"],
            [{"Platform": "windows", "MinimumVersion": "10"}],
        )
        self.assertEqual(manifest["Icon"], "imgs/plugin-icon")
        action_names = {action["Name"] for action in manifest["Actions"]}
        self.assertEqual(
            action_names,
            {
                "Start SMW Central Radio",
                "Close SMW Central Radio",
                "Play / Pause",
                "Replay Track",
                "Next Track",
                "Toggle Looping",
                "Seek Back 10 Seconds",
                "Seek Forward 10 Seconds",
                "Volume Down",
                "Volume Up",
            },
        )
        action_ids = [action["UUID"] for action in manifest["Actions"]]
        self.assertEqual(len(action_ids), len(set(action_ids)))
        self.assertNotIn("mac", json.dumps(manifest).casefold())

    def test_plugin_uses_local_token_and_live_player_state(self):
        script = (PLUGIN_ROOT / "bin" / "plugin.js").read_text(
            encoding="utf-8"
        )
        self.assertIn("SMWStreamTrackerConfig.json", script)
        self.assertIn("obs_widget_access_token", script)
        self.assertIn("127.0.0.1", script)
        self.assertIn("/obs-widget/socket", script)
        self.assertIn('command: "radio_toggle"', script)
        self.assertIn('command: "radio_start"', script)
        self.assertIn('command: "radio_close"', script)
        self.assertIn('command: "radio_loop"', script)
        self.assertIn('command: "radio_seek"', script)
        self.assertIn('command: "radio_volume"', script)
        self.assertIn("latestRadioState.playing", script)
        self.assertIn("latestRadioState.looping", script)
        self.assertNotIn("wss://", script)

    def test_radio_state_includes_streamdeck_feedback(self):
        state = self.tracker.obs_radio_widget_state(
            {
                "ready": True,
                "playing": True,
                "title": "Test Track",
                "elapsed": "0:20",
                "duration": "1:40",
                "can_loop": True,
                "looping": True,
                "volume": 125,
            }
        )
        self.assertTrue(state["playing"])
        self.assertTrue(state["can_loop"])
        self.assertTrue(state["looping"])
        self.assertEqual(state["volume"], 125.0)

    def test_tracker_translates_streamdeck_loop_seek_and_volume(self):
        app = FakeTrackerApp()
        handler = self.tracker.TrackerApp._handle_obs_widget_command

        handler(app, {"command": "radio_loop", "request_id": "loop"})
        handler(
            app,
            {
                "command": "radio_seek",
                "request_id": "seek",
                "delta_seconds": 10,
            },
        )
        handler(
            app,
            {
                "command": "radio_volume",
                "request_id": "volume",
                "delta": 10,
            },
        )

        self.assertEqual(app.sent_commands[0], ("loop", True))
        self.assertEqual(app.sent_commands[1][0], "seek")
        self.assertAlmostEqual(app.sent_commands[1][1], 40 / 120)
        self.assertEqual(app.sent_commands[2], ("volume", 90.0))
        self.assertTrue(all(event["ok"] for event in app.events))

    def test_tracker_starts_and_closes_radio_from_streamdeck(self):
        app = FakeTrackerApp()
        handler = self.tracker.TrackerApp._handle_obs_widget_command

        handler(app, {"command": "radio_start", "request_id": "start"})
        handler(app, {"command": "radio_close", "request_id": "close"})

        self.assertTrue(app.opened_radio)
        self.assertTrue(app.closed_radio)
        self.assertEqual(
            [event["message"] for event in app.events],
            [
                "SMW Central Radio is starting.",
                "SMW Central Radio is closed.",
            ],
        )
        self.assertTrue(all(event["ok"] for event in app.events))

    def test_windows_release_bundles_plugin_installer(self):
        spec_text = (PROJECT_ROOT / "SMWStreamTracker.spec").read_text(
            encoding="utf-8"
        )
        build_text = (
            PROJECT_ROOT / "release" / "build_release.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("SMWStreamTracker-SPC-Controls.streamDeckPlugin", spec_text)
        self.assertIn("package_streamdeck_plugin.ps1", build_text)
        self.assertIn("'streamdeck'", build_text)

        workflow_text = (
            PROJECT_ROOT
            / ".github"
            / "workflows"
            / "publish-windows-release.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('node-version: "24"', workflow_text)
        self.assertIn('"@elgato/cli@1.9.0"', workflow_text)

    def test_elgato_settings_page_owns_the_one_click_installer(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        sidebar_start = source.index("settings_sidebar_section_names = (")
        sidebar_end = source.index(")", sidebar_start)
        sidebar = source[sidebar_start:sidebar_end]
        self.assertLess(sidebar.index('"Elgato"'), sidebar.index('"OBS"'))
        self.assertIn(
            'settings_section_builders["Elgato"] = '
            "build_elgato_settings_page",
            source,
        )
        self.assertIn("Install / Update Stream Deck Plugin", source)
        self.assertIn("Included SPC Player Controls", source)

        music_start = source.index("def _open_music_identifier_page")
        music_end = source.index("\n    def ", music_start + 10)
        music_page = source[music_start:music_end]
        self.assertNotIn("Install Stream Deck Controls", music_page)

    def test_elgato_sidebar_asset_has_real_transparency(self):
        icon_path = PROJECT_ROOT / "app_assets" / "elgato_logo.png"
        self.assertTrue(icon_path.is_file())
        with Image.open(icon_path) as icon_source:
            icon = icon_source.convert("RGBA")
        alpha = icon.getchannel("A")
        self.assertEqual(alpha.getextrema(), (0, 255))
        self.assertGreater(
            sum(1 for alpha_value in alpha.getdata() if alpha_value == 0),
            icon.width * icon.height // 4,
        )


if __name__ == "__main__":
    unittest.main()
