import ast
from pathlib import Path
import unittest


SOURCE_FILE = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class StatsOverviewLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_FILE.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "open_stats_overview"
        )
        cls.stream_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_build_stream_desk_overview"
        )

    def _panel_parent(self, panel_name):
        assignment = next(
            node
            for node in ast.walk(self.method)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "create_section_panel"
            and any(
                isinstance(target, ast.Tuple)
                and any(
                    isinstance(item, ast.Name)
                    and item.id == panel_name
                    for item in target.elts
                )
                for target in node.targets
            )
        )
        return assignment.value.args[0].id

    def _grid_position(self, widget_name):
        call = next(
            node
            for node in ast.walk(self.method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "grid"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == widget_name
        )
        values = {
            keyword.arg: keyword.value.value
            for keyword in call.keywords
            if keyword.arg in {"row", "column"}
            and isinstance(keyword.value, ast.Constant)
        }
        return values["row"], values["column"]

    def test_overview_panels_use_the_requested_two_by_two_layout(self):
        self.assertEqual(self._panel_parent("bar_outer"), "content")
        self.assertEqual(self._grid_position("bar_outer"), (0, 0))

        self.assertEqual(self._panel_parent("difficulty_outer"), "content")
        self.assertEqual(self._grid_position("difficulty_outer"), (0, 1))

        self.assertEqual(self._panel_parent("pie_outer"), "content")
        self.assertEqual(self._grid_position("pie_outer"), (1, 0))

        self.assertEqual(self._grid_position("side_panel"), (1, 1))
        self.assertEqual(self._panel_parent("recent_outer"), "side_panel")

    def test_progress_table_height_matches_its_actual_rows(self):
        tree_assignment = next(
            node
            for node in ast.walk(self.method)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "difficulty_tree"
                for target in node.targets
            )
        )
        height = next(
            keyword.value
            for keyword in tree_assignment.value.keywords
            if keyword.arg == "height"
        )
        self.assertIsInstance(height, ast.Call)
        self.assertIsInstance(height.func, ast.Name)
        self.assertEqual(height.func.id, "max")
        self.assertEqual(height.args[0].value, 1)
        self.assertIsInstance(height.args[1], ast.Call)
        self.assertEqual(height.args[1].func.id, "len")
        self.assertEqual(height.args[1].args[0].id, "difficulty_rows")

    def test_overview_charts_expand_with_their_available_panels(self):
        method_source = ast.get_source_segment(self.source, self.method)
        self.assertIn("int(height * 0.76)", method_source)
        self.assertIn("self._ui_px(320)", method_source)
        self.assertIn("int(width * 0.055)", method_source)
        self.assertIn("int(width * 0.18)", method_source)
        self.assertIn("self._ui_px(42)", method_source)
        self.assertNotIn("self._ui_px(290)", method_source)

    def test_stream_desk_overview_restores_the_smooth_status_donut(self):
        method_source = ast.get_source_segment(self.source, self.stream_method)
        self.assertIn("def draw_status_donut", method_source)
        self.assertIn('tr("Completed")', method_source)
        self.assertIn('tr("In Progress")', method_source)
        self.assertIn('tr("Planned")', method_source)
        self.assertIn("Image.LANCZOS", method_source)
        self.assertIn('"pie_canvas": pie_canvas', method_source)

    def test_stream_desk_overview_reflows_for_the_available_width(self):
        method_source = ast.get_source_segment(self.source, self.stream_method)
        self.assertIn("def reflow_overview", method_source)
        self.assertIn("def queue_overview_layout", method_source)
        self.assertNotIn(
            'body.bind("<Configure>", queue_overview_layout',
            method_source,
        )
        self.assertIn(
            'body_canvas.bind("<Configure>", queue_overview_layout',
            method_source,
        )
        self.assertIn("dialog.add_prepaint_callback", method_source)
        self.assertIn('panel_mode = "wide"', method_source)
        self.assertIn('panel_mode = "medium"', method_source)
        self.assertIn('panel_mode = "stacked"', method_source)
        self.assertIn("metric_columns = 4", method_source)
        self.assertIn("else 2", method_source)
        self.assertIn("def resize_overview_body", method_source)
        self.assertIn('dialog.bind("<MouseWheel>", scroll_overview', method_source)
        self.assertIn('"body_scrollbar": body_scrollbar', method_source)
        self.assertIn("available_height", method_source)
        self.assertIn('vertical_mode = (', method_source)
        self.assertIn("overview_body_geometry", method_source)
        self.assertIn("natural_height > visible_height + self._ui_px(10)", method_source)
        self.assertIn("natural_height > visible_height - self._ui_px(10)", method_source)
        self.assertNotIn("height=0,", method_source)
        self.assertNotIn("body.update_idletasks()", method_source)
        self.assertIn('"running": False', method_source)
        self.assertIn("72,", method_source)
        self.assertIn("body_scrollbar.grid_remove()", method_source)
        self.assertIn("body_canvas.yview_moveto(0.0)", method_source)

    def test_stream_desk_overview_uses_larger_readable_type(self):
        method_source = ast.get_source_segment(self.source, self.stream_method)
        self.assertIn('font=("Segoe UI", 30, "bold")', method_source)
        self.assertIn("value_font_size=24", method_source)
        self.assertIn("title_font_size=17", method_source)


if __name__ == "__main__":
    unittest.main()
