import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_streamerbot_websocket_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeStreamerBotSocket:
    def __init__(self, *, authentication=None):
        self.authentication = authentication
        self.sent = []
        self.first_receive = True
        self.closed = False

    def send(self, payload):
        self.sent.append(json.loads(payload))

    def recv(self):
        if self.first_receive:
            self.first_receive = False
            hello = {
                "request": "Hello",
                "info": {"name": "Streamer.bot", "version": "1.0.0"},
            }
            if self.authentication is not None:
                hello["authentication"] = dict(self.authentication)
            return json.dumps(hello)
        request = self.sent[-1]
        response = {"id": request["id"], "status": "ok"}
        if request["request"] == "GetActions":
            response["actions"] = [
                {
                    "id": "disabled-action",
                    "name": "Disabled Action",
                    "group": "Tracker",
                    "enabled": False,
                },
                {
                    "id": "death-action",
                    "name": "Death Alert",
                    "group": "Tracker",
                    "enabled": True,
                },
            ]
        return json.dumps(response)

    def close(self):
        self.closed = True


class StreamerBotWebSocketIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_default_settings_are_local_and_disabled(self):
        config = self.tracker.DEFAULT_CONFIG
        self.assertFalse(config["streamerbot_enabled"])
        self.assertFalse(config["streamerbot_controls_enabled"])
        self.assertEqual(config["streamerbot_control_actions"], {})
        self.assertEqual(config["streamerbot_host"], "127.0.0.1")
        self.assertEqual(config["streamerbot_port"], 8080)
        self.assertEqual(config["streamerbot_endpoint"], "/")
        self.assertEqual(
            self.tracker.streamerbot_websocket_url(
                "127.0.0.1",
                "8080",
                "/",
            ),
            "ws://127.0.0.1:8080/",
        )

    def test_authentication_value_matches_documented_challenge_response(self):
        password = "test password"
        salt = "salt-value"
        challenge = "challenge-value"
        secret = base64.b64encode(
            hashlib.sha256((password + salt).encode("utf-8")).digest()
        ).decode("ascii")
        expected = base64.b64encode(
            hashlib.sha256((secret + challenge).encode("utf-8")).digest()
        ).decode("ascii")
        self.assertEqual(
            self.tracker.streamerbot_authentication_value(
                password,
                salt,
                challenge,
            ),
            expected,
        )

    def test_connection_loads_actions_and_runs_selected_action(self):
        fake_socket = FakeStreamerBotSocket()
        with patch.object(
            self.tracker.websocket,
            "create_connection",
            return_value=fake_socket,
        ) as create_connection:
            connection = self.tracker.StreamerBotConnection()
            info = connection.connect()
            actions = connection.get_actions()
            response = connection.do_action(
                actions[0],
                {"eventName": "death_added", "gameDeaths": 7},
            )
            connection.close()

        self.assertEqual(info["version"], "1.0.0")
        self.assertEqual([action["id"] for action in actions], ["death-action"])
        self.assertEqual(response["status"], "ok")
        create_connection.assert_called_once_with(
            "ws://127.0.0.1:8080/",
            timeout=4.0,
            enable_multithread=True,
        )
        do_action = fake_socket.sent[-1]
        self.assertEqual(do_action["request"], "DoAction")
        self.assertEqual(do_action["action"]["id"], "death-action")
        self.assertEqual(do_action["args"]["gameDeaths"], 7)
        self.assertTrue(fake_socket.closed)

    def test_connection_subscribes_to_raw_action_events(self):
        fake_socket = FakeStreamerBotSocket()
        with patch.object(
            self.tracker.websocket,
            "create_connection",
            return_value=fake_socket,
        ):
            connection = self.tracker.StreamerBotConnection()
            connection.connect()
            response = connection.subscribe_action_events()
            connection.close()

        self.assertEqual(response["status"], "ok")
        subscribe = fake_socket.sent[-1]
        self.assertEqual(subscribe["request"], "Subscribe")
        self.assertEqual(subscribe["events"], {"raw": ["Action"]})

    def test_password_challenge_is_answered_before_requests(self):
        authentication = {"salt": "salt", "challenge": "challenge"}
        fake_socket = FakeStreamerBotSocket(authentication=authentication)
        with patch.object(
            self.tracker.websocket,
            "create_connection",
            return_value=fake_socket,
        ):
            connection = self.tracker.StreamerBotConnection(password="secret")
            connection.connect()
            connection.close()

        authenticate = fake_socket.sent[0]
        self.assertEqual(authenticate["request"], "Authenticate")
        self.assertEqual(
            authenticate["authentication"],
            self.tracker.streamerbot_authentication_value(
                "secret",
                "salt",
                "challenge",
            ),
        )

    def test_settings_page_precedes_obs_and_uses_reference_icons(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        sidebar_start = source.index("settings_sidebar_section_names = (")
        sidebar_end = source.index("settings_section_icons = {", sidebar_start)
        sidebar = source[sidebar_start:sidebar_end]
        self.assertLess(
            sidebar.index('"Streamer.bot"'),
            sidebar.index('"OBS"'),
        )
        self.assertIn('"Streamer.bot": "streamerbot"', source)
        self.assertIn('"Platform": "super_nintendo_console"', source)
        self.assertIn('"File Locations": "windows_file"', source)
        self.assertIn('"Storage": "nvme"', source)
        self.assertIn('"OBS": "obs"', source)
        self.assertIn('"Timers": "stopwatch"', source)
        self.assertIn('"Help": "open_book"', source)
        self.assertIn('"About & Updates": "bell"', source)
        self.assertIn('brand_cyan = "#27DCE5"', source)
        self.assertIn('brand_purple = "#9A4DE3"', source)
        self.assertIn('text="Test & Load Actions"', source)
        self.assertIn('connection.get_actions()', source)
        self.assertIn(
            "def build_streamerbot_settings_page() -> None:\n"
            "            tr = self._translate_ui_text",
            source,
        )
        self.assertIn('text=tr("Tracker Controls")', source)
        self.assertIn(
            'text=tr("Allow Streamer.bot to control the tracker")',
            source,
        )
        self.assertIn("class StreamerBotControlListener", source)

    def test_confirmed_tracker_events_are_available_for_mapping(self):
        labels = dict(self.tracker.STREAMERBOT_EVENT_DEFINITIONS)
        for event_name in (
            "game_started",
            "death_added",
            "exit_collected",
            "level_completed",
            "achievement_unlocked",
            "game_timer_started",
            "game_timer_finished",
            "hack_completed",
        ):
            with self.subTest(event=event_name):
                self.assertIn(event_name, labels)

    def test_only_mapped_raw_actions_become_tracker_controls(self):
        mappings = {
            "toggle_game_timer": {
                "id": "timer-action",
                "name": "Toggle Timer",
            }
        }
        document = {
            "event": {"source": "Raw", "type": "Action"},
            "data": {
                "id": "action-run-instance",
                "actionId": "timer-action",
                "name": "Toggle Timer",
                "arguments": {"source": "chat"},
            },
        }
        self.assertEqual(
            self.tracker.streamerbot_control_from_action_event(
                document,
                mappings,
            ),
            ("toggle_game_timer", {"source": "chat"}),
        )
        document["data"]["actionId"] = "not-approved"
        document["data"]["name"] = "Not Approved"
        self.assertIsNone(
            self.tracker.streamerbot_control_from_action_event(
                document,
                mappings,
            )
        )

    def test_tracker_generated_actions_cannot_loop_back_as_controls(self):
        document = {
            "event": {"source": "Raw", "type": "Action"},
            "data": {
                "id": "action-run-instance",
                "actionId": "same-action",
                "name": "Toggle Timer",
                "arguments": {
                    "appName": self.tracker.APP_NAME,
                    "eventName": "death_added",
                },
            },
        }
        self.assertIsNone(
            self.tracker.streamerbot_control_from_action_event(
                document,
                {
                    "toggle_game_timer": {
                        "id": "same-action",
                        "name": "Toggle Timer",
                    }
                },
            )
        )

    def test_approved_control_runs_on_tracker_command_handler(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": True,
        }
        app.toggle_game_timer = MagicMock()
        app.finish_game_timer = MagicMock()
        app.complete_in_spreadsheet = MagicMock()
        app.open_game_library = MagicMock()
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command("toggle_game_timer", {})

        app.toggle_game_timer.assert_called_once_with()
        app._set_streamerbot_control_status.assert_called_once()

    def test_search_control_accepts_chat_command_raw_input(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": True,
        }
        result = {"id": "hack-1", "title": "Grand Poo World 2"}
        game = {"id": "hack-1", "title": "Grand Poo World 2"}
        app._obs_widget_search_results = MagicMock(return_value=[result])
        app._obs_widget_game_by_id = MagicMock(return_value=game)
        app._launch_catalog_game = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command(
            "search_and_play_hack",
            {"rawInput": "Grand Poo World 2"},
        )

        app._obs_widget_search_results.assert_called_once_with(
            "Grand Poo World 2",
            limit=30,
        )
        app._launch_catalog_game.assert_called_once_with(game)


if __name__ == "__main__":
    unittest.main()
