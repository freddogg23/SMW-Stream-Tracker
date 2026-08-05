import importlib.util
from pathlib import Path
import types
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_dropdown_alignment_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTcl:
    def __init__(self, tracker):
        self.tracker = tracker
        self.values = ("All", "Date Added (Newest)")
        self.inserted = []
        self.calls = []

    def call(self, *args):
        self.calls.append(args)
        if args[1:] == ("configure", "-justify", "center"):
            raise self.tracker.tk.TclError("unsupported option")
        if args[0] == ".filters" and args[1:] == ("cget", "-values"):
            return self.values
        if args[0] == ".filters" and args[1:] == ("cget", "-width"):
            return "22"
        if args[0] == ".filters" and args[1:] == ("current",):
            return "1"
        if args[1] == "insert":
            self.inserted.append(args[-1])
        return ""

    @staticmethod
    def splitlist(value):
        return tuple(value)


class DropdownAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_popup_rows_are_centered_without_changing_filter_values(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        fake_tcl = FakeTcl(self.tracker)
        app.root = types.SimpleNamespace(tk=fake_tcl)
        event = types.SimpleNamespace(
            widget=".filters.popdown.f.l",
        )

        app._center_dropdown_list_items(event)

        self.assertEqual(
            fake_tcl.values,
            ("All", "Date Added (Newest)"),
        )
        self.assertEqual(
            fake_tcl.inserted,
            [
                "All".center(22),
                "Date Added (Newest)".center(22),
            ],
        )
        self.assertIn(
            (
                ".filters.popdown.f.l",
                "selection",
                "set",
                1,
            ),
            fake_tcl.calls,
        )

    def test_searchable_hack_popup_centers_display_only_text(self):
        class FixedWidthFont:
            @staticmethod
            def measure(value):
                return len(value) * 10

        values = ["A", "Four"]
        display_values = (
            self.tracker.TrackerApp._center_listbox_display_values(
                values,
                FixedWidthFont(),
                100,
            )
        )

        self.assertEqual(values, ["A", "Four"])
        self.assertEqual(display_values, ["    A", "   Four"])


if __name__ == "__main__":
    unittest.main()
