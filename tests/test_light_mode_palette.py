import ast
from pathlib import Path
import unittest


SOURCE_FILE = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class LightModePaletteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_FILE.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.methods = {
            node.name: ast.get_source_segment(cls.source, node) or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

    def test_stream_desk_has_complete_dark_and_light_palettes(self):
        self.assertIn("STREAM_DESK_DARK = dict(STREAM_DESK)", self.source)
        self.assertIn("STREAM_DESK_LIGHT = {", self.source)
        for key in (
            "window",
            "rail",
            "topbar",
            "surface",
            "surface_alt",
            "surface_deep",
            "selected",
            "border",
            "text",
            "text_strong",
            "muted",
        ):
            self.assertIn(f'"{key}"', self.source)

    def test_selected_palette_is_activated_before_ui_build(self):
        self.assertIn(
            "self._activate_stream_desk_palette(saved_theme)",
            self.source,
        )
        self.assertIn(
            "self._activate_stream_desk_palette(normalized)",
            self.methods["_set_appearance"],
        )

    def test_in_app_pages_use_the_selected_appearance(self):
        source = self.methods["_open_in_app_page"]
        self.assertIn(
            'dark=(self.appearance_var.get() == "dark")',
            source,
        )
        self.assertNotIn("dark=True", source)

    def test_settings_sections_share_the_active_surface_palette(self):
        source = self.methods["_open_settings_dialog"]
        self.assertNotIn('bg="#F9F5FF"', source)
        self.assertNotIn('panel_bg="#F9F5FF"', source)
        self.assertIn('panel_bg=STREAM_DESK["surface"]', source)

    def test_canvas_heavy_pages_rebuild_after_live_theme_switch(self):
        source = self.methods["_set_appearance"]
        for page_key in (
            '"overview"',
            '"game_modes"',
            '"smwcentral"',
            '"language"',
            '"settings"',
        ):
            self.assertIn(page_key, source)

    def test_popup_factory_applies_the_active_palette(self):
        source = self.methods["_create_tracker_dialog"]
        self.assertIn('dialog.configure(bg=STREAM_DESK["window"])', source)
        self.assertIn("self._apply_widget_appearance", source)
        self.assertIn('self.appearance_var.get() == "dark"', source)

    def test_selector_popup_uses_the_shared_dynamic_palette(self):
        source = self.methods["_post_main_hack_selector_popup"]
        self.assertIn("palette = self._library_palette()", source)
        self.assertIn('bg=palette["panel"]', source)
        self.assertIn('selectbackground=palette["selected"]', source)

    def test_all_open_popups_are_rethemed_on_switch(self):
        source = self.methods["_refresh_open_window_appearances"]
        self.assertIn("for dialog in open_windows", source)
        self.assertIn("self._apply_widget_appearance", source)
        self.assertIn("self._refresh_downloader_window_appearance()", source)
        self.assertIn("self._refresh_fxpak_sd_window_appearance()", source)
        self.assertIn("self._refresh_game_library_window_appearance()", source)

    def test_nested_menus_receive_the_active_palette_recursively(self):
        source = self.methods["_style_stream_desk_menu_tree"]
        self.assertIn("self._style_stream_desk_menu_tree", source)
        self.assertIn('activebackground=STREAM_DESK["selected"]', source)
        self.assertIn('selectcolor=STREAM_DESK["green"]', source)

    def test_future_submenus_inherit_the_active_palette(self):
        source = self.methods["_set_appearance"]
        for option in (
            "*Menu.background",
            "*Menu.foreground",
            "*Menu.activeBackground",
            "*Menu.activeForeground",
            "*Menu.disabledForeground",
            "*Menu.selectColor",
        ):
            self.assertIn(f'self.root.option_add("{option}"', source)


if __name__ == "__main__":
    unittest.main()
