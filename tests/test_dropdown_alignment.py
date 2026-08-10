import ast
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

    def test_searchable_hack_popup_uses_the_app_yellow_scrollbar(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        popup_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_post_main_hack_selector_popup"
        )
        called_names = {
            node.func.id
            for node in ast.walk(popup_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        }
        called_attributes = {
            (node.func.value.id, node.func.attr)
            for node in ast.walk(popup_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
        }

        self.assertIn("YellowCanvasScrollbar", called_names)
        self.assertNotIn(("tk", "Scrollbar"), called_attributes)

    def test_catalog_and_downloader_dropdown_arrows_use_blue_style(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for method_name in (
            "_refresh_downloader_window_appearance",
            "open_hack_downloader",
        ):
            method = next(
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                and node.name == method_name
            )
            method_source = ast.get_source_segment(source, method)
            self.assertIn(
                'background=THEME["blue"]',
                method_source,
            )
            self.assertNotIn(
                'background=THEME["yellow"] if dark_mode',
                method_source,
            )

    def test_catalog_and_downloader_give_type_column_more_room(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "open_hack_downloader"
        )
        method_source = ast.get_source_segment(source, method)

        self.assertIn('else "Hack Title"', method_source)
        self.assertIn('{"title": "Hack Title"}', method_source)
        self.assertIn('width=(260 if catalog_view_only', method_source)
        self.assertIn('minwidth=(240 if catalog_view_only', method_source)
        self.assertIn('heading_width("type", 240)', method_source)


if __name__ == "__main__":
    unittest.main()
