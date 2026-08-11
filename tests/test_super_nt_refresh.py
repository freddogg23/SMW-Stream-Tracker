import ast
import importlib.util
import json
from pathlib import Path
import queue
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_super_nt_refresh_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeWebSocket:
    def __init__(self, info):
        self.info = info

    def recv(self):
        return json.dumps({"Results": self.info})


class SuperNtRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def method_source(self, name):
        return ast.get_source_segment(
            self.source,
            self.methods[name],
        )

    def make_worker(self, output_folder):
        worker = self.tracker.TrackerWorker(
            {"output_folder": str(output_folder)},
            queue.Queue(),
        )
        worker.save_current_level_progress = lambda: None
        worker.save_current_game_time = lambda: None
        worker.save_current_death_count = lambda: None
        return worker

    def test_attached_fxpak_receives_info_then_reset(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            worker = self.make_worker(temporary_directory)
            requests = []
            worker.send_request = (
                lambda _ws, opcode, operands=None: requests.append(
                    (opcode, operands)
                )
            )
            worker._reset_attached_console(
                FakeWebSocket(
                    [
                        "1.11.0",
                        "SD2SNES",
                        "/All_Hacks/test.sfc",
                        "FEAT_CMD_UNLOCK",
                    ]
                )
            )
            self.assertEqual(
                requests,
                [("Info", None), ("Reset", None)],
            )

    def test_no_control_flag_prevents_unsupported_reset(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            worker = self.make_worker(temporary_directory)
            requests = []
            worker.send_request = (
                lambda _ws, opcode, operands=None: requests.append(opcode)
            )
            with self.assertRaisesRegex(
                RuntimeError,
                "does not allow remote reset",
            ):
                worker._reset_attached_console(
                    FakeWebSocket(
                        ["1.0", "Virtual Device", "NO_CONTROL_CMD"]
                    )
                )
            self.assertEqual(requests, ["Info"])

    def test_refresh_command_resets_then_stops_for_reconnection(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            worker = self.make_worker(temporary_directory)
            requests = []
            worker.send_request = (
                lambda _ws, opcode, operands=None: requests.append(opcode)
            )
            worker.request_console_refresh()
            worker.process_commands(
                FakeWebSocket(
                    ["1.11.0", "SD2SNES", "/All_Hacks/test.sfc"]
                )
            )
            self.assertTrue(worker.stop_event.is_set())
            self.assertEqual(requests, ["Info", "Reset"])
            events = []
            while not worker.event_queue.empty():
                events.append(worker.event_queue.get_nowait())
            reset_events = [
                event
                for event in events
                if event.get("type") == "console_reset"
            ]
            self.assertEqual(len(reset_events), 1)
            self.assertTrue(reset_events[0]["success"])

    def test_main_refresh_resets_only_connected_fxpak(self):
        source = self.method_source("refresh_tracker")
        self.assertIn(
            'self.platform_var.get().strip() == "FXPAK Pro"',
            source,
        )
        self.assertIn("self.connection_is_connected", source)
        self.assertIn("worker.request_console_refresh()", source)
        self.assertIn("pending_worker.stop()", source)

    def test_refresh_messages_are_translated_in_every_language(self):
        texts = (
            "Restarting the running FXPAK Pro game and connection…",
            (
                "The running FXPAK Pro game was reset. Reconnecting the "
                "tracker…"
            ),
            (
                "The FXPAK Pro does not allow remote reset. The tracker "
                "connection will still restart."
            ),
            (
                "Could not reset the running FXPAK Pro game: {error}. The "
                "tracker connection will still restart."
            ),
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in texts:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)


if __name__ == "__main__":
    unittest.main()
