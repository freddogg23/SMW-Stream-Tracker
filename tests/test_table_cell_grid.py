import ast
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class TableCellGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    @staticmethod
    def _is_treeview_constructor(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ttk"
            and node.func.attr == "Treeview"
        )

    @staticmethod
    def _is_grid_install(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_install_treeview_cell_grid"
        )

    def test_every_treeview_installs_the_shared_cell_grid(self):
        constructors = [
            node
            for node in ast.walk(self.tree)
            if self._is_treeview_constructor(node)
        ]
        installers = [
            node
            for node in ast.walk(self.tree)
            if self._is_grid_install(node)
        ]

        self.assertEqual(len(constructors), 8)
        self.assertEqual(len(installers), len(constructors))

        for method in (
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
        ):
            method_constructors = sum(
                self._is_treeview_constructor(node)
                for node in ast.walk(method)
            )
            if not method_constructors:
                continue
            method_installers = sum(
                self._is_grid_install(node)
                for node in ast.walk(method)
            )
            self.assertEqual(
                method_installers,
                method_constructors,
                method.name,
            )

    def test_grid_draws_both_directions_and_tracks_scrolling(self):
        method = next(
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_render_treeview_cell_grid"
        )
        method_source = ast.get_source_segment(self.source, method)
        installer = next(
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_install_treeview_cell_grid"
        )
        installer_source = ast.get_source_segment(self.source, installer)

        self.assertIn("identify_row", method_source)
        self.assertIn("tree.bbox", method_source)
        self.assertIn("_smw_cell_grid_vertical_lines", method_source)
        self.assertIn("_smw_cell_grid_horizontal_lines", method_source)
        self.assertIn('tree.cget("yscrollcommand")', installer_source)
        self.assertIn('tree.cget("xscrollcommand")', installer_source)
        self.assertIn("preserve_scroll_command", installer_source)
        self.assertIn("34 if vertical_scroll else 0", installer_source)
        self.assertIn('tree.column("#0", "width")', method_source)
        self.assertIn("first_column_edge", method_source)

    def test_colored_cell_overlays_use_the_same_grid_color(self):
        self.assertNotIn('outline=palette["border"]', self.source)
        grid_color_uses = (
            self.source.count("outline=self._table_grid_line_color()")
            + self.source.count("border_color=self._table_grid_line_color()")
        )
        self.assertGreaterEqual(grid_color_uses, 8)

    def test_grid_uses_light_blue_colors_in_both_themes(self):
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
            and target.id in {
                "TABLE_GRID_LINE_DARK",
                "TABLE_GRID_LINE_LIGHT",
                "TABLE_GRID_BORDER_WIDTH",
            }
        }
        self.assertEqual(assignments["TABLE_GRID_LINE_DARK"], "#4B7CA3")
        self.assertEqual(assignments["TABLE_GRID_LINE_LIGHT"], "#86C5EB")
        self.assertEqual(assignments["TABLE_GRID_BORDER_WIDTH"], 1)


if __name__ == "__main__":
    unittest.main()
