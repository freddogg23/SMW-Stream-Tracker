import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_updater_relaunch_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UpdaterRelaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_updater_starts_with_fresh_pyinstaller_environment(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.shutdown = mock.Mock()
        updater = Path("SMWStreamTracker_Update_1.0.3.exe")

        inherited_environment = {
            "PATH": os.environ.get("PATH", ""),
            "_PYI_APPLICATION_HOME_DIR": r"C:\Temp\_MEIold",
            "_PYI_ARCHIVE_FILE": r"C:\Old\SMWStreamTracker.exe",
        }
        with mock.patch.dict(
            self.tracker.os.environ,
            inherited_environment,
            clear=True,
        ), mock.patch.object(
            self.tracker.subprocess,
            "Popen",
        ) as popen:
            app._launch_update_package(updater)

        arguments, keywords = popen.call_args
        self.assertEqual(arguments[0], [str(updater), "/SP-"])
        child_environment = keywords["env"]
        self.assertEqual(
            child_environment["PYINSTALLER_RESET_ENVIRONMENT"],
            "1",
        )
        self.assertNotIn("_PYI_APPLICATION_HOME_DIR", child_environment)
        self.assertNotIn("_PYI_ARCHIVE_FILE", child_environment)
        self.assertIn("PATH", child_environment)
        app.shutdown.assert_called_once_with()

    def test_updater_package_resets_environment_before_final_launch(self):
        updater_script = (
            MODULE_PATH.parent
            / "installer"
            / "SMWStreamTrackerUpdater.iss"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "SetEnvironmentVariable('PYINSTALLER_RESET_ENVIRONMENT', '1')",
            updater_script,
        )
        self.assertIn("function InitializeSetup(): Boolean;", updater_script)


if __name__ == "__main__":
    unittest.main()
