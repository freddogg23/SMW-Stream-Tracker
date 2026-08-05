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
        "smw_tracker_streamer_warning_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StreamerPrivacyWarningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_warning_can_be_suppressed_per_scope(self):
        app = self.tracker.TrackerApp.__new__(
            self.tracker.TrackerApp
        )
        app.config = {
            "streamer_privacy_warning_disabled_scopes": [
                "downloads_files"
            ]
        }

        self.assertTrue(
            app._streamer_privacy_warning_is_suppressed(
                "downloads_files"
            )
        )
        self.assertFalse(
            app._streamer_privacy_warning_is_suppressed(
                "settings_files"
            )
        )

    def test_warning_can_be_suppressed_everywhere(self):
        app = self.tracker.TrackerApp.__new__(
            self.tracker.TrackerApp
        )
        app.config = {
            "streamer_privacy_warning_disabled_everywhere": True
        }

        self.assertTrue(
            app._streamer_privacy_warning_is_suppressed(
                "settings_files"
            )
        )
        self.assertTrue(
            app._streamer_privacy_warning_is_suppressed(
                "downloads_files"
            )
        )


if __name__ == "__main__":
    unittest.main()
