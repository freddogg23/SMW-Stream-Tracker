import importlib.util
from pathlib import Path
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
        "smw_tracker_guided_connection_gate_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DummyVariable:
    def __init__(self, value):
        self.value = str(value)

    def get(self):
        return self.value


class DummyRoot:
    def after(self, _delay, callback):
        callback()
        return "after-id"


class GuidedSetupConnectionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self, folder, choice):
        sni_path = folder / "sni.exe"
        qusb_path = folder / "QUsb2Snes.exe"
        retroarch_path = folder / "retroarch.exe"
        core_path = folder / "bsnes_mercury_performance_libretro.dll"
        for path in (sni_path, qusb_path, retroarch_path, core_path):
            path.touch()

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app._guided_setup_stage = "connection"
        app._guided_setup_software_choice = choice
        app._guided_setup_software_selected = set()
        app._guided_setup_software_completed = set()
        app.config = {
            "sni_path": str(sni_path),
            "qusb2snes_path": str(qusb_path),
            "retroarch_executable_path": str(retroarch_path),
            "retroarch_core_path": str(core_path),
        }
        app.sni_path_var = DummyVariable(sni_path)
        app.qusb_path_var = DummyVariable(qusb_path)
        app.root = DummyRoot()
        app._guided_setup_post_downloads_menu = lambda: None
        app.flash_refreshes = 0
        app._guided_setup_refresh_connection_flash = (
            lambda: setattr(
                app,
                "flash_refreshes",
                app.flash_refreshes + 1,
            )
        )
        app.advanced_stages = []
        app._guided_setup_set_stage = app.advanced_stages.append
        return app

    def test_sni_and_retroarch_must_both_finish_before_advancing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            for first, second in (
                ("sni", "retroarch"),
                ("retroarch", "sni"),
            ):
                with self.subTest(first=first):
                    app = self.make_app(folder, "sni_retroarch")
                    app._guided_optional_software_completed(first)
                    self.assertEqual(app.advanced_stages, [])
                    self.assertEqual(
                        app._guided_setup_software_completed,
                        {first},
                    )
                    self.assertEqual(app.flash_refreshes, 1)

                    app._guided_optional_software_completed(second)
                    self.assertEqual(app.advanced_stages, ["catalog"])
                    self.assertEqual(
                        app._guided_setup_software_completed,
                        {"sni", "retroarch"},
                    )

    def test_sni_selection_leaves_only_retroarch_highlighted(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        downloads_menu = object()
        connection_menu = object()
        app.downloads_menu = downloads_menu
        app.connection_setup_menu = connection_menu
        app.connection_setup_menu_index = 5
        app.connection_option_menu_indexes = (10, 11, 12)
        app._guided_setup_software_choice = "sni_retroarch"
        app._guided_setup_software_selected = {"sni"}
        app._guided_setup_software_completed = set()

        self.assertEqual(
            app._guided_setup_target_menu_entries("connection"),
            ((downloads_menu, 5), (connection_menu, 12)),
        )

    def test_retroarch_selection_leaves_only_sni_highlighted(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        downloads_menu = object()
        connection_menu = object()
        app.downloads_menu = downloads_menu
        app.connection_setup_menu = connection_menu
        app.connection_setup_menu_index = 5
        app.connection_option_menu_indexes = (10, 11, 12)
        app._guided_setup_software_choice = "sni_retroarch"
        app._guided_setup_software_selected = {"retroarch"}
        app._guided_setup_software_completed = set()

        self.assertEqual(
            app._guided_setup_target_menu_entries("connection"),
            ((downloads_menu, 5), (connection_menu, 10)),
        )

    def test_qusb2snes_alone_can_advance(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            app = self.make_app(
                Path(temporary_directory),
                "qusb2snes",
            )
            app._guided_optional_software_completed("qusb2snes")
            self.assertEqual(app.advanced_stages, ["catalog"])
            self.assertEqual(
                app._guided_setup_software_completed,
                {"qusb2snes"},
            )


if __name__ == "__main__":
    unittest.main()
