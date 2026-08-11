import importlib
from types import SimpleNamespace
import unittest
from unittest import mock


class FakeTrackerApp:
    def _configure_tray(self):
        raise AssertionError("The normal tray path should be replaced on macOS")

    def hide_to_tray(self):
        raise AssertionError("The normal hide-to-tray path should be replaced on macOS")


class MacOSTraySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.launcher = importlib.import_module("SMWStreamTrackerLauncher")

    def test_macos_disables_tray_backend_and_threaded_appkit_loop(self):
        tracker = SimpleNamespace(
            TrackerApp=type("MacTrackerApp", (FakeTrackerApp,), {}),
            pystray=object(),
        )
        self.launcher.configure_platform_runtime(tracker, "darwin")

        app = tracker.TrackerApp()
        app.tray_icon = object()
        app._configure_tray()

        self.assertIsNone(tracker.pystray)
        self.assertIsNone(app.tray_icon)

    def test_macos_close_button_quits_instead_of_hiding(self):
        tracker = SimpleNamespace(
            TrackerApp=type("MacTrackerApp", (FakeTrackerApp,), {}),
            pystray=object(),
        )
        self.launcher.configure_platform_runtime(tracker, "darwin")

        app = tracker.TrackerApp()
        app.shutdown = mock.Mock()
        app.hide_to_tray()

        app.shutdown.assert_called_once_with()

    def test_windows_keeps_existing_tray_behavior(self):
        tracker_app = type("WindowsTrackerApp", (FakeTrackerApp,), {})
        original_configure = tracker_app._configure_tray
        original_close = tracker_app.hide_to_tray
        tracker = SimpleNamespace(TrackerApp=tracker_app, pystray=object())

        self.launcher.configure_platform_runtime(tracker, "win32")

        self.assertIs(tracker.TrackerApp._configure_tray, original_configure)
        self.assertIs(tracker.TrackerApp.hide_to_tray, original_close)
        self.assertIsNotNone(tracker.pystray)


if __name__ == "__main__":
    unittest.main()
