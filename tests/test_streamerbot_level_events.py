import base64
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
        "smw_tracker_streamerbot_events_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def decode_field(value):
    return base64.b64decode(value).decode("utf-8")


class StreamerBotLevelEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.output_folder = Path(self.temporary_directory.name)
        config = dict(self.tracker.DEFAULT_CONFIG)
        config["output_folder"] = str(self.output_folder)
        self.worker = self.tracker.TrackerWorker(config, queue.Queue())
        self.worker.current_hack_title = "Emoji Hack 🐸|Test"
        self.worker.current_rom_key = "sample-rom"
        self.worker.current_time_key = "sample-rom::slot0"
        self.worker.level_id = 7
        self.worker.level_waiting_for_start = False
        self.worker.level_death_count = 0
        self.worker.death_count = 0

    def tearDown(self):
        self.temporary_directory.cleanup()

    def read_events(self):
        path = self.output_folder / "streamerbot_level_events.txt"
        return [line.split("|") for line in path.read_text(
            encoding="utf-8"
        ).splitlines()]

    def test_level_event_protocol_preserves_unicode_and_delimiters(self):
        self.worker.start_streamerbot_level_session(7)

        events = self.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0:4], [
            "SMWTRACKER", "1", events[0][2], "start"
        ])
        self.assertEqual(decode_field(events[0][5]), "Emoji Hack 🐸|Test")
        self.assertEqual(events[0][6], "7")
        self.assertEqual(events[0][7], "0")
        self.assertEqual(events[0][9], "en")

    def test_death_clear_and_cancel_are_distinct_file_tail_events(self):
        self.worker.start_streamerbot_level_session(7)
        self.worker.level_death_count = 3
        self.worker.append_streamerbot_level_event("death")
        self.worker.send_level_completion_event("overworld")

        events = self.read_events()
        self.assertEqual([event[3] for event in events], [
            "start", "death", "clear"
        ])
        self.assertEqual([event[7] for event in events], ["0", "3", "3"])
        self.assertEqual(self.worker.streamerbot_level_session_id, "")

        self.worker.start_streamerbot_level_session(8)
        self.worker.cancel_streamerbot_level_session("ROM changed")
        events = self.read_events()
        self.assertEqual([event[3] for event in events][-2:], [
            "start", "cancel"
        ])
        self.assertEqual(decode_field(events[-1][8]), "ROM changed")

    def test_blank_output_folder_disables_file_without_writing_to_cwd(self):
        self.worker.config["output_folder"] = ""
        self.worker.start_streamerbot_level_session(7)
        self.assertFalse(
            (self.output_folder / "streamerbot_level_events.txt").exists()
        )


if __name__ == "__main__":
    unittest.main()
