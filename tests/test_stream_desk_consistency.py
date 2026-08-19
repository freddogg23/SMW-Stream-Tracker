import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
INSTALLER_PATH = ROOT / "installer" / "SMWStreamTrackerInstaller.iss"
UPDATER_PATH = ROOT / "installer" / "SMWStreamTrackerUpdater.iss"


class StreamDeskConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.methods = {
            node.name: ast.get_source_segment(cls.source, node) or ""
            for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def test_tracker_dialog_factory_applies_shared_chrome(self):
        source = self.methods["_create_tracker_dialog"]
        self.assertIn("STREAM_DESK", source)
        self.assertIn("_set_windows_titlebar_theme", source)
        self.assertIn("_apply_widget_appearance", source)
        self.assertIn("_localize_widget_tree", source)

    def test_raw_toplevel_creation_is_limited_to_factory_and_selector_popup(self):
        callers = set()
        for method_name, source in self.methods.items():
            if "tk.Toplevel(" in source:
                callers.add(method_name)
        self.assertEqual(
            callers,
            {"_create_tracker_dialog", "_post_main_hack_selector_popup"},
        )

        selector = self.methods["_post_main_hack_selector_popup"]
        self.assertIn('palette["border_strong"]', selector)
        self.assertIn('palette["selected"]', selector)

    def test_every_messagebox_type_routes_through_tracker_ui(self):
        source = self.methods["_install_localized_messageboxes"]
        self.assertIn("_show_localized_info", source)
        self.assertIn("_ask_localized_yes_no", source)
        self.assertIn("_show_stream_desk_message_dialog", source)
        for name in (
            "showinfo",
            "showwarning",
            "showerror",
            "askquestion",
            "askokcancel",
            "askyesno",
            "askyesnocancel",
            "askretrycancel",
        ):
            self.assertIn(name, self.source)

    def test_livesplit_obs_guide_uses_stream_desk_and_yellow_scrollbar(self):
        source = self.methods["open_livesplit_obs_setup_guide"]
        self.assertIn('dialog._uses_stream_desk_palette = True', source)
        self.assertIn('palette["entry"]', source)
        self.assertIn('STREAM_DESK["yellow"]', source)
        self.assertIn("YellowCanvasScrollbar", source)
        self.assertIn('footer.pack(side="bottom", fill="x")', source)
        self.assertIn('uniform="livesplit_actions"', source)
        self.assertNotIn('bg=THEME["blue"]', source)

    def test_updates_and_utility_pages_use_the_shared_stream_desk_header(self):
        for method_name in (
            "_show_update_dialog",
            "open_readme_dialog",
            "open_setup_health_check",
            "open_diagnostics",
            "open_obs_settings_dialog",
            "open_smwcentral_home",
        ):
            with self.subTest(method_name=method_name):
                self.assertIn(
                    "_create_stream_desk_page_header",
                    self.methods[method_name],
                )
        update_source = self.methods["_show_update_dialog"]
        self.assertIn('actions.pack(side="bottom", fill="x")', update_source)
        self.assertIn("YellowCanvasScrollbar", update_source)
        diagnostics_source = self.methods["open_diagnostics"]
        self.assertIn('actions.pack(side="bottom", fill="x")', diagnostics_source)
        self.assertIn("YellowCanvasScrollbar", diagnostics_source)
        obs_source = self.methods["open_obs_settings_dialog"]
        self.assertIn('dialog._uses_stream_desk_palette = True', obs_source)
        self.assertIn('actions.pack(side="bottom", fill="x")', obs_source)
        self.assertIn("YellowCanvasScrollbar", obs_source)
        self.assertNotIn('THEME["purple"]', obs_source)

    def test_dashboard_current_run_stats_are_centered(self):
        source = self.methods["_build_stream_desk_dashboard"]
        self.assertEqual(source.count('anchor="center"'), 5)

    def test_global_menu_and_scrollbar_defaults_use_shared_palette(self):
        source = self.methods["_build_ui"]
        self.assertIn('option_add("*Menu.background"', source)
        self.assertIn('"#FFD43B"', source)
        self.assertIn('"#FFE66D"', source)

    def test_every_checkbox_uses_the_large_mario_checkbox(self):
        self.assertIn("class MarioCheckbutton(tk.Checkbutton):", self.source)
        self.assertIn("BASE_INDICATOR_SIZE = 24", self.source)
        self.assertIn('CHECKED_FILL = "#2FAF73"', self.source)
        app_body = self.source.split(
            "class MarioCheckbutton(tk.Checkbutton):",
            1,
        )[1]
        self.assertNotIn("tk.Checkbutton(", app_body)
        self.assertGreaterEqual(app_body.count("MarioCheckbutton("), 10)

    def test_tracker_add_remove_controls_use_green_and_soft_red(self):
        source = self.methods["open_my_tracker"]
        self.assertIn('STREAM_DESK["green"]', source)
        self.assertIn('STREAM_DESK["green_dark"]', source)
        self.assertIn('"#D86B72"', source)
        self.assertIn('"#BE5961"', source)

    def test_message_dialog_reserves_button_footer_before_expanding_card(self):
        source = self.methods["_show_stream_desk_message_dialog"]
        self.assertIn('side="bottom"', source)
        self.assertIn("before=card", source)
        self.assertLess(source.index("actions.pack("), source.index("action_group ="))

    def test_catalog_refresh_progress_popup_uses_stream_desk_theme(self):
        source = self.methods["refresh_smwcentral_catalog"]
        self.assertIn('text="SMW CENTRAL"', source)
        self.assertIn('STREAM_DESK["surface_deep"]', source)
        self.assertIn('STREAM_DESK["yellow"]', source)
        self.assertIn('"CatalogRefresh.Horizontal.TProgressbar"', source)
        self.assertNotIn('THEME["orange"]', source)

    def test_downloader_selection_uses_smooth_checkbox_artwork(self):
        opener = self.methods["open_hack_downloader"]
        self.assertIn('"selection_checkbox_images"', opener)
        self.assertIn("MarioCheckbutton._build_indicator", opener)
        for method_name in (
            "_toggle_downloader_row_selection",
            "_update_downloader_select_heading",
            "_toggle_downloader_select_all",
        ):
            source = self.methods[method_name]
            self.assertNotIn("☐", source)
            self.assertNotIn("☑", source)

    def test_downloader_checkboxes_are_centered_in_select_cells(self):
        source = self.methods["_render_downloader_selection_overlay"]
        self.assertIn('tree.bbox(iid, "#0")', source)
        self.assertIn("column_width / 2", source)
        self.assertIn("row_y + (row_height / 2)", source)
        self.assertIn('anchor="center"', source)

    def test_installer_and_updater_share_dark_banner_theme(self):
        for path in (INSTALLER_PATH, UPDATER_PATH):
            source = path.read_text(encoding="utf-8")
            self.assertIn("WizardStyle=modern dark", source)
            self.assertIn("WizardBackColor=#0D1216", source)
            self.assertIn("smw_installer_banner.png", source)
            self.assertIn("#F2F6F8", source)
            self.assertIn("#9AA7B0", source)


if __name__ == "__main__":
    unittest.main()
