import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
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
        self.assertEqual(config["streamerbot_song_scene_name"], "SNES Scene")
        self.assertFalse(config["streamerbot_song_reward_enabled"])
        self.assertFalse(
            config["streamerbot_song_reward_actions_installed"]
        )
        self.assertEqual(config["streamerbot_song_reply_action"], {})
        self.assertEqual(
            config["streamerbot_song_reward_name"],
            "What Song Is Playing?",
        )
        self.assertEqual(config["streamerbot_song_reward_cost"], 1)
        self.assertEqual(config["streamerbot_song_reward_cooldown"], 30)
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

    def test_connection_subscribes_to_direct_song_reward_events(self):
        fake_socket = FakeStreamerBotSocket()
        with patch.object(
            self.tracker.websocket,
            "create_connection",
            return_value=fake_socket,
        ):
            connection = self.tracker.StreamerBotConnection()
            connection.connect()
            connection.subscribe_tracker_events(
                include_actions=False,
                include_song_reward=True,
            )
            connection.send_message("The song is Test", platform="twitch")
            connection.close()

        subscribe = fake_socket.sent[-2]
        self.assertEqual(
            subscribe["events"],
            {
                "twitch": ["RewardRedemption"],
                "obs": ["SceneChanged"],
            },
        )
        send_message = fake_socket.sent[-1]
        self.assertEqual(send_message["request"], "SendMessage")
        self.assertEqual(send_message["platform"], "twitch")
        self.assertEqual(send_message["message"], "The song is Test")

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
        self.assertIn(
            '"https://streamer.bot/api/releases/streamer.bot/latest/download"',
            source,
        )
        self.assertIn('else "✦  Install Streamer.bot"', source)
        self.assertIn(
            "self._download_dependency_file(\n"
            "                    STREAMERBOT_LATEST_DOWNLOAD_URL",
            source,
        )
        self.assertIn(
            'Path(local_app_data) / "Programs" / "Streamer.bot"',
            source,
        )
        self.assertIn("shutil.copytree(\n", source)
        streamerbot_page = source[
            source.index("def build_streamerbot_settings_page() -> None:"):
            source.index("def platform_px(value: float) -> int:")
        ]
        self.assertNotIn(
            "visibility Action enables the reward",
            streamerbot_page,
        )
        self.assertNotIn("Search & Play reads query", streamerbot_page)
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
        self.assertEqual(
            labels["song_identified"],
            "Song Identified for Chat",
        )
        self.assertEqual(
            dict(self.tracker.STREAMERBOT_CONTROL_DEFINITIONS)[
                "identify_current_song"
            ],
            "Post Current Level Song to Chat",
        )

    def test_song_scene_is_read_only_from_explicit_streamerbot_arguments(self):
        self.assertEqual(
            self.tracker.streamerbot_scene_from_arguments(
                {"sceneName": "SNES Scene"}
            ),
            "SNES Scene",
        )
        self.assertEqual(
            self.tracker.streamerbot_scene_from_arguments(
                {"obs": {"currentScene": "SNES Scene"}}
            ),
            "SNES Scene",
        )
        self.assertEqual(
            self.tracker.streamerbot_scene_from_arguments(
                {"sceneName": "BRB"}
            ),
            "BRB",
        )
        self.assertEqual(
            self.tracker.streamerbot_scene_from_arguments(
                {"rewardName": "What song is this?"}
            ),
            "",
        )

    def test_direct_reward_and_obs_scene_events_are_normalized(self):
        scene_document = {
            "event": {"source": "Obs", "type": "SceneChanged"},
            "data": {"sceneName": "Gameplay"},
        }
        self.assertEqual(
            self.tracker.streamerbot_scene_from_event(scene_document),
            "Gameplay",
        )
        reward_document = {
            "event": {"source": "Twitch", "type": "RewardRedemption"},
            "data": {
                "reward": {"id": "reward-1", "title": "What Song?"},
                "user": {"name": "Viewer", "login": "viewer"},
                "redemptionId": "redeem-1",
            },
        }
        reward = self.tracker.streamerbot_song_reward_from_event(
            reward_document
        )
        self.assertEqual(reward["rewardName"], "What Song?")
        self.assertEqual(reward["userName"], "Viewer")
        self.assertTrue(reward["directChatReply"])

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

    def test_song_control_only_posts_on_explicit_snes_scene(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": True,
            "streamerbot_event_actions": {
                "song_identified": {
                    "id": "song-chat-action",
                    "name": "Song Identified for Chat",
                }
            },
        }
        current_song = {
            "title": "Stickerbrush Symphony",
            "smwcentral_url": "https://www.smwcentral.net/?p=section&a=details&id=1",
        }
        app._current_level_song_result = MagicMock(return_value=current_song)
        app._dispatch_streamerbot_song_response = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command(
            "identify_current_song",
            {"sceneName": "BRB", "userName": "Viewer"},
        )
        app._handle_streamerbot_control_command(
            "identify_current_song",
            {"userName": "Viewer"},
        )

        app._current_level_song_result.assert_not_called()
        app._dispatch_streamerbot_song_response.assert_not_called()

        app._handle_streamerbot_control_command(
            "identify_current_song",
            {"sceneName": "SNES Scene", "userName": "Viewer"},
        )

        app._current_level_song_result.assert_called_once_with()
        app._dispatch_streamerbot_song_response.assert_called_once_with(
            {"sceneName": "SNES Scene", "userName": "Viewer"},
            result=current_song,
        )

    def test_song_control_uses_user_configured_scene_for_direct_reward(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": False,
            "streamerbot_song_reward_enabled": True,
            "streamerbot_song_scene_name": "Gameplay",
        }
        app._current_level_song_result = MagicMock(
            return_value={
                "title": "Stale song from the previous level",
                "smwcentral_url": "https://www.smwcentral.net/?p=section&a=details&id=1",
            }
        )
        app._start_streamerbot_live_song_lookup = MagicMock(return_value=True)
        app._dispatch_streamerbot_song_response = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command(
            "identify_current_song",
            {
                "sceneName": "Gameplay",
                "userName": "Viewer",
                "directChatReply": True,
            },
        )

        app._current_level_song_result.assert_not_called()
        app._start_streamerbot_live_song_lookup.assert_called_once_with(
            {
                "sceneName": "Gameplay",
                "userName": "Viewer",
                "directChatReply": True,
            }
        )
        app._dispatch_streamerbot_song_response.assert_not_called()

    def test_uncached_direct_song_reward_starts_live_identification(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": False,
            "streamerbot_song_reward_enabled": True,
            "streamerbot_song_scene_name": "SNES Scene",
        }
        request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "directChatReply": True,
        }
        app._current_level_song_result = MagicMock(return_value={})
        app._start_streamerbot_live_song_lookup = MagicMock(return_value=True)
        app._dispatch_streamerbot_song_response = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command(
            "identify_current_song",
            request,
        )

        app._start_streamerbot_live_song_lookup.assert_called_once_with(request)
        app._dispatch_streamerbot_song_response.assert_not_called()

    def test_music_context_uses_live_room_and_music_register(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.current_hack_record = {}
        app.worker = MagicMock(
            current_rom_key="pitofrta",
            current_time_key="",
            previous_rom_path="",
            current_translevel=0x99,
            level_id=0x12,
            last_gameplay_level_number=0x1F4,
            current_music_track=0x2A,
        )

        context_key = app._current_tracker_music_context_key()

        self.assertEqual(
            context_key,
            "pitofrta|translevel:153|room:500|music:42",
        )

    def test_music_context_changes_when_same_level_loads_another_song(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.current_hack_record = {}
        app.worker = MagicMock(
            current_rom_key="pitofrta",
            current_time_key="",
            previous_rom_path="",
            current_translevel=0x99,
            level_id=0x99,
            last_gameplay_level_number=0x1F4,
            current_music_track=0x2A,
        )
        first_context = app._current_tracker_music_context_key()
        app.worker.current_music_track = 0x35

        second_context = app._current_tracker_music_context_key()

        self.assertNotEqual(first_context, second_context)
        self.assertTrue(second_context.endswith("|music:53"))

    def test_music_context_changes_for_a_new_live_level_session(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.current_hack_record = {}
        app.worker = MagicMock(
            current_rom_key="pitofrta",
            current_time_key="",
            previous_rom_path="",
            current_translevel=0x99,
            level_id=0x99,
            last_gameplay_level_number=0x1F4,
            current_music_track=0x2A,
            streamerbot_level_session_id="first-session",
        )
        first_context = app._current_tracker_music_context_key()
        app.worker.streamerbot_level_session_id = "second-session"

        second_context = app._current_tracker_music_context_key()

        self.assertNotEqual(first_context, second_context)
        self.assertTrue(first_context.endswith("|session:first-session"))
        self.assertTrue(second_context.endswith("|session:second-session"))

    def test_direct_song_reward_posts_live_session_cache_immediately(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_controls_enabled": False,
            "streamerbot_song_reward_enabled": True,
            "streamerbot_song_scene_name": "SNES Scene",
        }
        request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "directChatReply": True,
        }
        current_song = {
            "title": "Stickerbrush Symphony",
            "smwcentral_url": "https://www.smwcentral.net/?id=1",
        }
        app._current_tracker_music_context_key = MagicMock(
            return_value=(
                "pitofrta|translevel:153|room:500|music:42|session:live-1"
            )
        )
        app._current_level_song_result = MagicMock(return_value=current_song)
        app._start_streamerbot_live_song_lookup = MagicMock(return_value=True)
        app._dispatch_streamerbot_song_response = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        app._handle_streamerbot_control_command(
            "identify_current_song",
            request,
        )

        app._dispatch_streamerbot_song_response.assert_called_once_with(
            request,
            result=current_song,
        )
        app._start_streamerbot_live_song_lookup.assert_not_called()

    def test_level_start_schedules_background_song_prefetch(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_song_reward_enabled": True,
        }
        app.root = MagicMock()
        app.root.after.return_value = "prefetch-1"
        app.music_identifier_prefetch_after_id = None
        app.music_identifier_prefetch_session_id = ""

        scheduled = app._schedule_streamerbot_song_prefetch("level-session")

        self.assertTrue(scheduled)
        self.assertEqual(
            app.music_identifier_prefetch_session_id,
            "level-session",
        )
        app.root.after.assert_called_once_with(
            1200,
            app._prefetch_streamerbot_current_level_song,
        )

    def test_background_prefetch_starts_identifier_for_current_session(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_song_reward_enabled": True,
        }
        app.music_identifier_prefetch_after_id = "prefetch-1"
        app.music_identifier_prefetch_session_id = "level-session"
        app.music_identifier_streamerbot_request = None
        app.music_identifier_thread = None
        app.music_identifier_sources = {"Game Audio": {"token": "game"}}
        app.root = MagicMock()
        app.root.after.return_value = "monitor-1"
        app.music_identifier_source_var = MagicMock()
        app.music_identifier_source_var.get.return_value = "Game Audio"
        app._current_tracker_music_context_key = MagicMock(
            return_value=(
                "rom|translevel:1|room:2|music:3|session:level-session"
            )
        )
        app._current_level_song_result = MagicMock(return_value={})
        app._start_music_identifier = MagicMock(return_value=True)
        app._set_streamerbot_control_status = MagicMock()

        started = app._prefetch_streamerbot_current_level_song()

        self.assertTrue(started)
        app._start_music_identifier.assert_called_once_with()
        self.assertIn(
            "reply immediately",
            app._set_streamerbot_control_status.call_args.args[0],
        )

    def test_fresh_background_song_cache_avoids_another_audio_capture(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "streamerbot_enabled": True,
            "streamerbot_song_reward_enabled": True,
        }
        app.root = MagicMock()
        app.root.after.return_value = "monitor-2"
        app.music_identifier_prefetch_after_id = "prefetch-1"
        app.music_identifier_prefetch_session_id = "level-session"
        app._current_tracker_music_context_key = MagicMock(
            return_value=(
                "rom|translevel:1|room:2|music:3|session:level-session"
            )
        )
        app._current_level_song_result = MagicMock(
            return_value={
                "title": "A Song",
                "_recognized_at_epoch": time.time(),
            }
        )
        app._start_music_identifier = MagicMock(return_value=True)

        cached = app._prefetch_streamerbot_current_level_song()

        self.assertTrue(cached)
        app._start_music_identifier.assert_not_called()
        app.root.after.assert_called_once_with(
            self.tracker.MUSIC_IDENTIFIER_BACKGROUND_MONITOR_MS,
            app._prefetch_streamerbot_current_level_song,
        )

    def test_song_match_can_be_saved_to_redemption_memory_context(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {}
        app.music_identifier_context_results = {}
        app._current_tracker_music_context_key = MagicMock(
            return_value="new-room|translevel:2|room:20|music:8"
        )
        result = {
            "title": "Stickerbrush Symphony",
            "smwcentral_url": "https://www.smwcentral.net/?id=1",
        }
        requested_context = "old-room|translevel:1|room:10|music:7"

        with patch.object(self.tracker, "save_config"):
            saved = app._remember_current_level_song(
                result,
                context_key=requested_context,
            )

        self.assertEqual(saved["_tracker_context_key"], requested_context)
        self.assertIn(requested_context, app.music_identifier_context_results)
        self.assertNotIn(
            "new-room|translevel:2|room:20|music:8",
            app.music_identifier_context_results,
        )

    def test_confirmed_song_persists_without_the_level_session_token(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {}
        app.music_identifier_confirmed_level_songs = {}
        app._current_tracker_music_context_key = MagicMock(return_value="")
        context = (
            "sha256:abc|translevel:2|room:20|music:8|session:live-123"
        )
        result = {
            "title": "Stickerbrush Symphony",
            "smwcentral_url": "https://www.smwcentral.net/?id=1",
            "_tracker_context_key": context,
        }

        with patch.object(self.tracker, "save_config") as save:
            confirmed = app._remember_confirmed_level_song(result)

        stable = "sha256:abc|translevel:2|room:20|music:8"
        self.assertTrue(confirmed["_confirmed_by_user"])
        self.assertIn(stable, app.music_identifier_confirmed_level_songs)
        self.assertIn(
            stable,
            app.config["music_identifier_confirmed_level_songs"],
        )
        save.assert_called_once_with(app.config)

    def test_new_level_session_reuses_a_confirmed_rom_level_song(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        stable = "sha256:abc|translevel:2|room:20|music:8"
        live = stable + "|session:new-session"
        app._current_tracker_music_context_key = MagicMock(return_value=live)
        app.music_identifier_context_results = {}
        app.music_identifier_last_result = {}
        app.music_identifier_confirmed_level_songs = {
            stable: {
                "title": "Stickerbrush Symphony",
                "smwcentral_url": "https://www.smwcentral.net/?id=1",
                "_confirmed_by_user": True,
            }
        }

        result = app._current_level_song_result()

        self.assertEqual(result["title"], "Stickerbrush Symphony")
        self.assertTrue(result["_from_confirmed_level_memory"])
        self.assertEqual(result["_tracker_context_key"], live)
        self.assertIn(live, app.music_identifier_context_results)

    def test_music_context_prefers_the_local_rom_sha256(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.music_identifier_rom_hash_cache = {}
        with tempfile.TemporaryDirectory() as temp_folder:
            rom_path = Path(temp_folder) / "Example.sfc"
            rom_path.write_bytes(b"SNES ROM CONTENT")
            expected = self.tracker.file_sha256(rom_path)
            app.current_hack_record = {"local_rom_path": str(rom_path)}
            app.worker = MagicMock(
                current_rom_key="example",
                current_time_key="",
                previous_rom_path=str(rom_path),
                current_translevel=2,
                level_id=2,
                last_gameplay_level_number=20,
                current_music_track=8,
                streamerbot_level_session_id="live",
            )

            context = app._current_tracker_music_context_key()

        self.assertTrue(context.startswith(f"sha256:{expected}|"))
        self.assertTrue(context.endswith("|session:live"))

    def test_live_song_lookup_uses_memory_context_and_audio_identifier(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "directChatReply": True,
        }
        app.music_identifier_streamerbot_request = None
        app.music_identifier_thread = None
        app.music_identifier_sources = {}
        app.music_identifier_source_var = MagicMock()
        app.music_identifier_source_var.get.return_value = ""
        app._current_tracker_music_context_key = MagicMock(
            return_value="rom-key|translevel:42"
        )
        app._refresh_music_identifier_sources = MagicMock()
        app._start_music_identifier = MagicMock(return_value=True)
        app._dispatch_streamerbot_song_response = MagicMock()
        app._set_streamerbot_control_status = MagicMock()

        started = app._start_streamerbot_live_song_lookup(request)

        self.assertTrue(started)
        self.assertEqual(
            app.music_identifier_streamerbot_request["_trackerMusicContextKey"],
            "rom-key|translevel:42",
        )
        app._refresh_music_identifier_sources.assert_called_once_with()
        app._start_music_identifier.assert_called_once_with()
        app._dispatch_streamerbot_song_response.assert_not_called()
        self.assertIn(
            "listening to live game audio",
            app._set_streamerbot_control_status.call_args.args[0],
        )

    def test_live_song_lookup_joins_an_identifier_already_running(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "directChatReply": True,
        }
        app.music_identifier_streamerbot_request = None
        app.music_identifier_thread = MagicMock()
        app.music_identifier_thread.is_alive.return_value = True
        app._current_tracker_music_context_key = MagicMock(
            return_value="rom-key|translevel:42"
        )
        app._refresh_music_identifier_sources = MagicMock()
        app._start_music_identifier = MagicMock()
        app._dispatch_streamerbot_song_response = MagicMock()
        app._set_streamerbot_control_status = MagicMock()

        started = app._start_streamerbot_live_song_lookup(request)

        self.assertTrue(started)
        self.assertEqual(
            app.music_identifier_streamerbot_request["userName"],
            "Viewer",
        )
        app._refresh_music_identifier_sources.assert_not_called()
        app._start_music_identifier.assert_not_called()
        app._dispatch_streamerbot_song_response.assert_not_called()

    def test_live_song_lookup_queues_behind_previous_level_prefetch(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "directChatReply": True,
        }
        app.music_identifier_streamerbot_request = None
        app.music_identifier_queued_streamerbot_request = None
        app.music_identifier_lookup_context_key = (
            "rom|translevel:1|session:old-level"
        )
        app.music_identifier_thread = MagicMock()
        app.music_identifier_thread.is_alive.return_value = True
        app._current_tracker_music_context_key = MagicMock(
            return_value="rom|translevel:2|session:new-level"
        )
        app._refresh_music_identifier_sources = MagicMock()
        app._start_music_identifier = MagicMock()
        app._dispatch_streamerbot_song_response = MagicMock()
        app._set_streamerbot_control_status = MagicMock()

        started = app._start_streamerbot_live_song_lookup(request)

        self.assertTrue(started)
        self.assertIsNone(app.music_identifier_streamerbot_request)
        self.assertEqual(
            app.music_identifier_queued_streamerbot_request[
                "_trackerMusicContextKey"
            ],
            "rom|translevel:2|session:new-level",
        )
        app._start_music_identifier.assert_not_called()
        app._dispatch_streamerbot_song_response.assert_not_called()

    def test_song_result_exposes_title_link_and_ready_chat_message(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {}
        app.music_identifier_streamerbot_request = {
            "sceneName": "SNES Scene",
            "userName": "Viewer",
            "rewardName": "What Song Is Playing?",
        }
        app._dispatch_streamerbot_event = MagicMock(return_value=True)

        dispatched = app._complete_streamerbot_song_request(
            result={
                "title": "Stickerbrush Symphony",
                "artist": "David Wise, ported by Example",
                "smwcentral_url": "https://www.smwcentral.net/?p=section&a=details&id=1",
                "track_url": "https://files.smwcentral.net/music/example.zip",
                "confidence_value": 88.0,
            }
        )

        self.assertTrue(dispatched)
        app._dispatch_streamerbot_event.assert_called_once()
        event_name, arguments = app._dispatch_streamerbot_event.call_args.args
        self.assertEqual(event_name, "song_identified")
        self.assertTrue(arguments["songFound"])
        self.assertEqual(arguments["songTitle"], "Stickerbrush Symphony")
        self.assertIn("Stickerbrush Symphony", arguments["chatMessage"])
        self.assertIn("smwcentral.net", arguments["chatMessage"])
        self.assertEqual(arguments["sceneName"], "SNES Scene")
        self.assertEqual(arguments["requiredScene"], "SNES Scene")
        self.assertIsNone(app.music_identifier_streamerbot_request)

    def test_song_reward_setup_status_describes_current_level_data(self):
        status = self.tracker.streamerbot_song_reward_setup_status(
            True,
            "What Song Is Playing?",
            "SNES Scene",
            250,
            45,
        )

        self.assertIn("REWARD + ACTIONS INSTALLED", status)
        self.assertIn("shows the reward only on that scene", status)
        self.assertIn("250 points", status)
        self.assertIn("45-second cooldown", status)
        self.assertIn("SNES Scene", status)
        self.assertIn("live game audio", status)
        self.assertNotIn("LISTENER", status)

    def test_song_reward_settings_validate_cost_and_cooldown(self):
        settings = self.tracker.normalize_streamerbot_song_reward_settings(
            "What Song Is Playing?",
            "SNES Scene",
            "500",
            "60",
        )

        self.assertEqual(settings["cost"], 500)
        self.assertEqual(settings["cooldown"], 60)
        with self.assertRaisesRegex(ValueError, "Reward cost"):
            self.tracker.normalize_streamerbot_song_reward_settings(
                "What Song Is Playing?",
                "SNES Scene",
                "0",
                "60",
            )
        with self.assertRaisesRegex(ValueError, "Global cooldown"):
            self.tracker.normalize_streamerbot_song_reward_settings(
                "What Song Is Playing?",
                "SNES Scene",
                "500",
                "-1",
            )

    def test_one_click_reward_setup_passes_cost_and_cooldown_to_helper(self):
        completed = MagicMock(
            returncode=0,
            stdout=(
                '{"ok":true,"status":"updated","message":"ready",'
                '"created":false,"updated":true,'
                '"actionsInstalled":true,'
                '"visibilityActionId":"visibility-1",'
                '"replyActionId":"reply-1"}\n'
            ),
            stderr="",
        )
        with patch.object(
            self.tracker.shutil,
            "which",
            return_value=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        ), patch.object(
            self.tracker.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = self.tracker.install_streamerbot_song_reward(
                "What Song Is Playing?",
                "SNES Scene",
                750,
                90,
            )

        self.assertTrue(result["ok"])
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-Cost") + 1], "750")
        self.assertEqual(command[command.index("-Cooldown") + 1], "90")
        self.assertEqual(command[command.index("-SceneName") + 1], "SNES Scene")

    def test_reward_setup_helper_installs_visible_actions_and_scene_rule(self):
        helper = (
            PROJECT_ROOT / "tools" / "streamerbot_reward_setup.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "SMW Stream Tracker - Current Level Song Reward",
            helper,
        )
        self.assertIn(
            "SMW Stream Tracker - Song Reward Scene Visibility",
            helper,
        )
        self.assertIn(
            "SMW Stream Tracker - Post Current Level Song to Chat",
            helper,
        )
        self.assertIn("type = 112", helper)
        self.assertIn("type = 14004", helper)
        self.assertIn("type = 10", helper)
        self.assertIn("text = '%chatMessage%'", helper)
        self.assertIn("fallback = $true", helper)
        self.assertIn("-ReplyActionId $replyActionId", helper)
        self.assertIn("input = '%currentScene%'", helper)
        self.assertIn("state = 0", helper)
        self.assertIn("state = 1", helper)
        self.assertIn(".smw-stream-tracker-backup", helper)

    def test_reward_setup_navigation_supports_streamerbot_1_0_cards(self):
        helper = (
            PROJECT_ROOT / "tools" / "streamerbot_reward_setup.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn("function Open-NamedNavigationTarget", helper)
        self.assertIn("ControlType]::Text", helper)
        self.assertIn("Click-Element -Element $target", helper)
        self.assertIn("function Scroll-ElementIntoView", helper)
        self.assertIn("ScrollItemPattern", helper)
        self.assertIn("$pattern.ScrollIntoView()", helper)
        self.assertLess(
            helper.index("Click-Element -Element $target"),
            helper.index("return (Invoke-Element $target)"),
        )
        self.assertIn("-Name 'Platforms'", helper)
        self.assertIn("-Name 'Twitch'", helper)
        self.assertIn("-Name 'Channel Point Rewards'", helper)

    def test_reward_setup_reuses_existing_reward_without_twitch_navigation(self):
        helper = (
            PROJECT_ROOT / "tools" / "streamerbot_reward_setup.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn("$savedRewardAction", helper)
        self.assertIn("$installedRewardId", helper)
        self.assertIn("$repairMissingReplyAction", helper)
        self.assertIn(
            "$preflightActionNames -contains $rewardActionName",
            helper,
        )
        self.assertIn(
            "$preflightActionNames -contains $visibilityActionName",
            helper,
        )
        self.assertIn(
            "$preflightActionNames -notcontains $replyActionName",
            helper,
        )
        self.assertLess(
            helper.index("$hasExistingSongReward ="),
            helper.index("if (-not $hasExistingSongReward)"),
        )
        navigation_block = helper.split(
            "if (-not $hasExistingSongReward)",
            1,
        )[1]
        self.assertIn("-Name 'Platforms'", navigation_block)
        self.assertIn("-Name 'Twitch'", navigation_block)

    def test_reward_setup_expands_collapsed_reward_groups(self):
        helper = (
            PROJECT_ROOT / "tools" / "streamerbot_reward_setup.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn("function Expand-RewardGroups", helper)
        self.assertIn("ExpandCollapsePattern", helper)
        self.assertIn("$visibleItems.Count -eq 0", helper)
        self.assertIn("Expand-RewardGroups -Grid $Grid", helper)
        self.assertIn("$item.Current.IsOffscreen", helper)
        self.assertIn("-Name 'Edit'", helper)
        self.assertIn("[System.IO.Path]::GetDirectoryName", helper)

    def test_direct_song_reward_uses_installed_reply_action_not_send_message(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {}
        app._dispatch_streamerbot_event = MagicMock(return_value=True)
        app._queue_streamerbot_status = MagicMock()
        app._send_streamerbot_chat_message_async = MagicMock(return_value=True)

        dispatched = app._dispatch_streamerbot_song_response(
            {
                "directChatReply": True,
                "userName": "Viewer",
                "rewardName": "What Song Is Playing?",
                "sceneName": "SNES Scene",
            },
            result={
                "title": "Stickerbrush Symphony",
                "artist": "David Wise",
                "smwcentral_url": (
                    "https://www.smwcentral.net/?p=section&a=details&id=1"
                ),
            },
        )

        self.assertTrue(dispatched)
        app._send_streamerbot_chat_message_async.assert_not_called()
        app._dispatch_streamerbot_event.assert_called_once()
        event_name, arguments = app._dispatch_streamerbot_event.call_args.args
        self.assertEqual(event_name, "song_identified")
        self.assertIn("Stickerbrush Symphony", arguments["chatMessage"])
        self.assertIn("smwcentral.net", arguments["chatMessage"])


if __name__ == "__main__":
    unittest.main()
