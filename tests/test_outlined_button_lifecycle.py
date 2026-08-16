import importlib.util
from pathlib import Path
import sys
import types
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_outlined_button_lifecycle_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OutlinedButtonLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_redraw_stops_when_button_is_already_destroyed(self):
        button = types.SimpleNamespace(
            winfo_exists=lambda: False,
            _redraw_existing=lambda _event=None: self.fail(
                "A destroyed button must not be redrawn"
            ),
        )

        self.tracker.OutlinedButton._redraw(button)

    def test_redraw_ignores_destroy_race_after_existence_check(self):
        button = types.SimpleNamespace()
        button.winfo_exists = lambda: True
        button.delete = lambda _tag: (_ for _ in ()).throw(
            self.tracker.tk.TclError(
                'invalid command name ".!toplevel.!outlinedbutton"'
            )
        )
        button._redraw_existing = types.MethodType(
            self.tracker.OutlinedButton._redraw_existing,
            button,
        )

        self.tracker.OutlinedButton._redraw(button)


if __name__ == "__main__":
    unittest.main()
