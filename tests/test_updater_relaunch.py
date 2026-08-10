import importlib.util
import os
from pathlib import Path
import sys
import tempfile
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

    def test_updater_checks_tk_before_launch_and_has_runtime_fallback(self):
        updater_script = (
            MODULE_PATH.parent
            / "installer"
            / "SMWStreamTrackerUpdater.iss"
        ).read_text(encoding="utf-8")

        self.assertIn("--startup-check", updater_script)
        self.assertIn("UpdatedAppPassedStartupCheck", updater_script)
        self.assertIn("dist\\runtime\\tcl\\*", updater_script)
        self.assertIn("dist\\runtime\\tk\\*", updater_script)
        self.assertIn("CopyFile(PreviousExecutable, AppExecutable, False)", updater_script)

        release_script = (
            MODULE_PATH.parent / "release" / "build_release.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("Stage-TclTkRuntime", release_script)
        self.assertIn("Confirm-AppStartup", release_script)
        self.assertIn("--startup-check", release_script)
        self.assertIn("Test-BuildPython", release_script)
        self.assertIn("working Tcl/Tk runtime", release_script)
        self.assertIn("__smw_tcl_log|tcl-init-log", release_script)
        self.assertIn("WaitForExit(30000)", release_script)
        self.assertIn("Stop-Process -Id $process.Id -Force", release_script)

        build_spec = (MODULE_PATH.parent / "SMWStreamTracker.spec").read_text(
            encoding="utf-8"
        )
        self.assertIn("SMWStreamTrackerLauncher.py", build_spec)
        self.assertIn("import tkinter as tk", build_spec)
        self.assertIn("_tk_build_probe = tk.Tk()", build_spec)
        self.assertIn("cannot be packaged with this Python runtime", build_spec)
        self.assertIn("hookspath=[]", build_spec)
        self.assertIn(
            "runtime_hooks=['release_tools\\\\pyi_rth_tcl_find_executable.py']",
            build_spec,
        )

    def test_installed_runtime_is_preferred_when_complete(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            app_directory = Path(temporary_directory)
            executable = app_directory / "SMWStreamTracker.exe"
            executable.touch()
            tcl_directory = app_directory / "runtime" / "tcl"
            tk_directory = app_directory / "runtime" / "tk"
            tcl_directory.mkdir(parents=True)
            tk_directory.mkdir(parents=True)
            (tcl_directory / "init.tcl").write_text("# Tcl", encoding="utf-8")
            (tk_directory / "tk.tcl").write_text("# Tk", encoding="utf-8")

            with mock.patch.object(
                self.tracker.sys,
                "frozen",
                True,
                create=True,
            ), mock.patch.object(
                self.tracker.sys,
                "executable",
                str(executable),
            ), mock.patch.dict(
                self.tracker.os.environ,
                {},
                clear=False,
            ):
                configured = self.tracker._configure_installed_tcl_tk_runtime()
                self.assertTrue(configured)
                self.assertEqual(
                    self.tracker.os.environ["TCL_LIBRARY"],
                    str(tcl_directory),
                )
                self.assertEqual(
                    self.tracker.os.environ["TK_LIBRARY"],
                    str(tk_directory),
                )


if __name__ == "__main__":
    unittest.main()
