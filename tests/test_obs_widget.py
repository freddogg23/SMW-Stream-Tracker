import importlib.util
import inspect
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_obs_widget_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ObsWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_widget_state_contains_live_tracker_values(self):
        state = self.tracker.build_obs_widget_state(
            hack="A Plumber For All Seasons",
            creator="By: Maddy Thorson",
            exits_text="Exits: 7 / 12",
            level_deaths="3",
            total_deaths="41",
            game_timer="1:23:45",
            level_timer="02:17",
            connected=True,
            achievements={
                "status": "ready",
                "game_id": 123,
                "game_title": "Super Mario World",
                "hardcore": True,
                "unlocked": 8,
                "total": 10,
                "recent": [
                    {
                        "id": 7,
                        "title": "Cape Escape",
                        "description": "Finish with the cape.",
                        "points": 5,
                        "badge_name": "12345",
                        "unlocked": True,
                    }
                ],
            },
            radio={
                "ready": True,
                "playing": True,
                "title": "Dancing Mad",
                "subtitle": "Nobuo Uematsu, ported by musicalman",
                "elapsed": "1:15",
                "duration": "4:00",
                "progress": 0.3125,
                "can_skip": True,
            },
        )
        self.assertEqual(state["hack"], "A Plumber For All Seasons")
        self.assertEqual(state["creator"], "Maddy Thorson")
        self.assertEqual(state["exits"]["completed"], 7)
        self.assertEqual(state["exits"]["total"], 12)
        self.assertEqual(state["deaths"], {"level": 3, "total": 41})
        self.assertEqual(state["timers"]["game"], "1:23:45")
        self.assertTrue(state["connected"])
        self.assertEqual(
            state["achievements"]["recent"][0]["badge_url"],
            "https://retroachievements.org/Badge/12345.png",
        )
        self.assertNotIn("web_api_key", json.dumps(state).casefold())
        self.assertEqual(state["radio"]["title"], "Dancing Mad")
        self.assertEqual(state["radio"]["elapsed_seconds"], 75.0)
        self.assertEqual(state["radio"]["duration_seconds"], 240.0)
        self.assertTrue(state["radio"]["playing"])

    def test_widget_exit_denominator_uses_authoritative_values(self):
        state = self.tracker.build_obs_widget_state(
            exits_text="Custom exit wording without a slash",
            exits_completed=7,
            exits_total="12.0",
        )

        self.assertEqual(
            state["exits"],
            {"completed": 7, "total": 12, "label": "7 / 12"},
        )

    def test_widget_server_serves_dock_assets_and_pushes_websocket_state(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            assets = Path(temporary_directory)
            (assets / "index.html").write_text("<h1>Widget</h1>", encoding="utf-8")
            (assets / "widget.css").write_text("body{}", encoding="utf-8")
            (assets / "widget.js").write_text("void 0;", encoding="utf-8")
            (assets / "radio.html").write_text(
                "<h1>Radio Widget</h1>", encoding="utf-8"
            )
            (assets / "radio.css").write_text("body{}", encoding="utf-8")
            (assets / "radio.js").write_text("void 0;", encoding="utf-8")
            expected = self.tracker.build_obs_widget_state(hack="Test Hack")
            received_commands = []

            def handle_command(document):
                received_commands.append(document)
                server.publish_websocket_event(
                    {
                        "event": "command_result",
                        "request_id": document.get("request_id", ""),
                        "ok": True,
                        "message": "Command received.",
                    }
                )

            server = self.tracker.ObsWidgetHTTPServer(
                (self.tracker.OBS_WIDGET_HOST, 0),
                lambda: expected,
                assets,
                handle_command,
                "unit-test-token",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            port = int(server.server_address[1])
            client = None
            try:
                with urlopen(
                    f"http://127.0.0.1:{port}/obs-widget/",
                    timeout=3,
                ) as response:
                    self.assertIn(b"Widget", response.read())
                with urlopen(
                    f"http://127.0.0.1:{port}/obs-radio/",
                    timeout=3,
                ) as response:
                    self.assertIn(b"Radio Widget", response.read())
                with self.assertRaises(
                    self.tracker.websocket.WebSocketBadStatusException
                ):
                    blocked_client = self.tracker.websocket.create_connection(
                        f"ws://127.0.0.1:{port}/obs-widget/socket",
                        timeout=3,
                        http_proxy_host=None,
                        http_proxy_port=None,
                    )
                    blocked_client.close()
                client = self.tracker.websocket.create_connection(
                    (
                        f"ws://127.0.0.1:{port}/obs-widget/socket"
                        "?token=unit-test-token"
                    ),
                    timeout=3,
                    http_proxy_host=None,
                    http_proxy_port=None,
                )
                initial = json.loads(client.recv())
                self.assertEqual(initial["hack"], "Test Hack")
                server.publish_websocket_state(
                    self.tracker.build_obs_widget_state(
                        hack="Pushed Directly",
                        exits_text="Exits: 9 / 10",
                    )
                )
                pushed = json.loads(client.recv())
                self.assertEqual(pushed["hack"], "Pushed Directly")
                self.assertEqual(pushed["exits"]["completed"], 9)
                client.send(
                    json.dumps(
                        {
                            "command": "play_random_hack",
                            "request_id": "request-7",
                            "filters": {"difficulty": "Expert"},
                        }
                    )
                )
                response = json.loads(client.recv())
                self.assertEqual(response["event"], "command_result")
                self.assertEqual(response["request_id"], "request-7")
                self.assertEqual(
                    received_commands[0]["command"],
                    "play_random_hack",
                )
                self.assertEqual(
                    received_commands[0]["filters"]["difficulty"],
                    "Expert",
                )
            finally:
                if client is not None:
                    client.close()
                server.stop_websockets()
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_widget_has_all_selectable_fields_and_direct_websocket(self):
        html = (PROJECT_ROOT / "obs_widget" / "index.html").read_text(
            encoding="utf-8"
        )
        script = (PROJECT_ROOT / "obs_widget" / "widget.js").read_text(
            encoding="utf-8"
        )
        for field in self.tracker.OBS_WIDGET_FIELDS:
            self.assertIn(f'data-field="{field}"', html)
        self.assertIn('id="searchControlToggle"', html)
        self.assertIn('id="randomControlToggle"', html)
        self.assertIn('data-random-filter="rating"', html)
        self.assertIn('data-random-filter="difficulty"', html)
        self.assertIn('data-random-filter="type"', html)
        self.assertIn('data-random-filter="released"', html)
        self.assertIn('data-random-filter="hall_of_fame"', html)
        self.assertIn('id="hackSearchButton"', html)
        self.assertIn('id="playRandomButton"', html)
        self.assertIn("localStorage.setItem", script)
        self.assertIn("new WebSocket", script)
        self.assertIn("/obs-widget/socket", script)
        self.assertIn('sendCommand("search_hacks"', script)
        self.assertIn('sendCommand("play_hack"', script)
        self.assertIn('sendCommand("play_random_hack"', script)
        self.assertIn("URLSearchParams", script)
        self.assertNotIn("fetch(", script)
        self.assertNotIn("setInterval", script)
        self.assertNotIn("transparent", script.casefold())

    def test_widget_is_available_from_obs_settings_and_stops_on_shutdown(self):
        settings_source = inspect.getsource(
            self.tracker.TrackerApp._open_settings_dialog
        )
        shutdown_source = inspect.getsource(self.tracker.TrackerApp.shutdown)
        setup_source = inspect.getsource(
            self.tracker.TrackerApp.open_obs_widget_setup
        )
        self.assertIn('"Open OBS Widget & Radio Setup..."', settings_source)
        self.assertIn("self.open_obs_widget_setup", settings_source)
        self.assertIn("self._stop_obs_widget_server()", shutdown_source)
        self.assertIn("Custom Browser Dock URL", setup_source)
        self.assertIn("connected directly", setup_source)
        self.assertIn("SMW Central Radio Browser Source URL", setup_source)
        self.assertIn("1000 × 260", setup_source)

    def test_radio_browser_source_uses_live_websocket_state(self):
        html = (PROJECT_ROOT / "obs_widget" / "radio.html").read_text(
            encoding="utf-8"
        )
        script = (PROJECT_ROOT / "obs_widget" / "radio.js").read_text(
            encoding="utf-8"
        )
        stylesheet = (PROJECT_ROOT / "obs_widget" / "radio.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("SMW Central Radio", html)
        self.assertIn('id="progressFill"', html)
        self.assertIn('class="equalizer"', html)
        self.assertIn("new WebSocket", script)
        self.assertIn("document.radio", script)
        self.assertIn('sendCommand("radio_start")', script)
        self.assertNotIn("fetch(", script)
        self.assertIn("background: transparent", stylesheet)
        self.assertIn("spin-record", stylesheet)

    def test_widget_commands_use_existing_library_filters_and_launch_path(self):
        handler_source = inspect.getsource(
            self.tracker.TrackerApp._handle_obs_widget_command
        )
        candidate_source = inspect.getsource(
            self.tracker.TrackerApp._obs_widget_random_candidates
        )
        queue_source = inspect.getsource(
            self.tracker.TrackerApp._queue_obs_widget_command
        )
        self.assertIn('command == "search_hacks"', handler_source)
        self.assertIn('command == "play_hack"', handler_source)
        self.assertIn('command == "play_random_hack"', handler_source)
        self.assertIn('"radio_start"', handler_source)
        self.assertIn('"radio_next"', handler_source)
        self.assertIn("self._launch_catalog_game(game)", handler_source)
        self.assertIn("self._game_matches_library_filters", candidate_source)
        self.assertIn("self._catalog_game_has_downloaded_rom", candidate_source)
        self.assertIn("self.root.after", queue_source)

    def test_widget_assets_are_in_windows_and_source_packages(self):
        spec_text = (PROJECT_ROOT / "SMWStreamTracker.spec").read_text(
            encoding="utf-8"
        )
        build_text = (PROJECT_ROOT / "release" / "build_release.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("('obs_widget', 'obs_widget')", spec_text)
        self.assertIn("'obs_widget'", build_text)


if __name__ == "__main__":
    unittest.main()
