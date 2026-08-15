import ast
from pathlib import Path
import re
import unittest


SOURCE_FILE = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class InAppNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_FILE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def assert_uses_page_host(self, method_name):
        method = self.methods[method_name]
        calls = {
            node.func.attr
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_open_in_app_page", calls, method_name)

    def test_requested_destinations_use_the_main_window_page_host(self):
        for method_name in (
            "_open_settings_dialog",
            "open_stats_overview",
            "open_my_tracker",
            "open_hack_downloader",
            "open_game_library",
            "open_fxpak_sd_card_browser",
            "open_diagnostics",
            "open_setup_health_check",
            "open_readme_dialog",
            "open_obs_settings_dialog",
        ):
            with self.subTest(method=method_name):
                self.assert_uses_page_host(method_name)

    def test_overview_and_tracker_do_not_duplicate_cross_navigation_buttons(self):
        for method_name, removed_caption in (
            ("open_stats_overview", "Open My Tracker"),
            ("open_my_tracker", "Overview"),
        ):
            constants = {
                node.value
                for node in ast.walk(self.methods[method_name])
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)
            }
            with self.subTest(method=method_name):
                self.assertNotIn(removed_caption, constants)

    def test_tracker_bottom_actions_use_one_equal_grid(self):
        method = self.methods["open_my_tracker"]
        source = ast.get_source_segment(
            self.source,
            method,
        )
        self.assertIn('uniform="tracker_bottom_actions"', source)
        self.assertIn("weight=1", source)
        for caption in (
            "Spreadsheet Settings",
            "Google Sheets Settings",
            "Open SMW Central",
            "Launch Game",
        ):
            with self.subTest(caption=caption):
                self.assertIn(f'"{caption}"', source)
        self.assertNotIn('text="Edit Selected"', source)

        action_assignment = next(
            node
            for node in ast.walk(method)
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "tracker_bottom_actions"
        )
        self.assertIsInstance(action_assignment.value, ast.Tuple)
        self.assertEqual(len(action_assignment.value.elts), 4)

    def test_tracker_has_adjacent_add_and_remove_circles(self):
        method = self.methods["open_my_tracker"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('uniform="tracker_filter_controls"', source)
        self.assertIn("minsize=self._ui_px(300)", source)
        self.assertIn("Image.Resampling.LANCZOS", source)
        self.assertIn("ImageTk.PhotoImage", source)
        self.assertIn("supersample = 6", source)
        circle_calls = [
            node
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "make_tracker_circle_action"
        ]
        controls = {
            (
                node.args[0].value,
                node.args[3].attr,
            )
            for node in circle_calls
            if len(node.args) >= 4
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[3], ast.Attribute)
        }
        self.assertIn(("+", "_add_tracker_record"), controls)
        self.assertIn(("−", "_remove_tracker_record"), controls)

    def test_page_host_has_a_home_action(self):
        method = self.methods["_open_in_app_page"]
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        attributes = {
            node.attr
            for node in ast.walk(method)
            if isinstance(node, ast.Attribute)
        }
        self.assertIn("Home", constants)
        self.assertIn("request_close", attributes)

    def test_page_host_only_uses_defined_theme_colors(self):
        method = self.methods["_open_in_app_page"]
        referenced_theme_colors = {
            node.slice.value
            for node in ast.walk(method)
            if isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "THEME"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        }
        theme_assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "THEME"
                for target in node.targets
            )
        )
        defined_theme_colors = {
            key.value
            for key in theme_assignment.value.keys
            if isinstance(key, ast.Constant)
        }
        self.assertLessEqual(
            referenced_theme_colors,
            defined_theme_colors,
        )

    def test_callback_errors_copy_a_redacted_report_without_diagnostics(self):
        method = self.methods["_report_tk_callback_exception"]
        source = ast.get_source_segment(self.source, method)
        attributes = {
            node.attr
            for node in ast.walk(method)
            if isinstance(node, ast.Attribute)
        }
        self.assertIn("_redact_diagnostic_text", attributes)
        self.assertIn("clipboard_append", attributes)
        self.assertIn("_show_localized_info", attributes)
        self.assertNotIn("showerror", attributes)
        self.assertNotIn("master=dialog", source)
        self.assertIn("except Exception", source)

    def test_closed_tracker_tables_are_never_refreshed(self):
        refresh_source = ast.get_source_segment(
            self.source,
            self.methods["_refresh_my_tracker"],
        )
        import_source = ast.get_source_segment(
            self.source,
            self.methods["import_existing_spreadsheet"],
        )
        close_source = ast.get_source_segment(
            self.source,
            self.methods["_close_in_app_page"],
        )
        self.assertIn("_tracker_list_ui_is_alive", refresh_source)
        self.assertIn("_tracker_list_ui_is_alive", import_source)
        self.assertIn("_dispose_tracker_list_ui", close_source)

    def test_stats_backup_commands_are_grouped_into_submenus(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["_build_menu_bar"],
        )
        self.assertIn('label="Database Tools"', source)
        self.assertIn('label="Automatic Backups"', source)
        self.assertIn("database_tools_menu", source)
        self.assertIn("automatic_backups_menu", source)

    def test_shutdown_creates_a_new_exit_recovery_backup(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["shutdown"],
        )
        self.assertIn('self._create_recovery_backup("exit")', source)
        self.assertIn("shutdown_in_progress", source)

    def test_related_catalog_and_downloader_actions_are_on_their_pages(self):
        method = self.methods["open_hack_downloader"]
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertIn("Refresh Moderated Hacks from SMW Central", constants)
        self.assertIn("Add Unmoderated Hack", constants)

    def test_downloader_footer_is_reserved_before_the_expandable_table(self):
        method = self.methods["open_hack_downloader"]
        assignments = {
            target.id: node
            for node in ast.walk(method)
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id in {
                "footer_panel",
                "list_frame",
                "progress_panel",
                "button_panel",
            }
        }
        self.assertLess(
            assignments["footer_panel"].lineno,
            assignments["list_frame"].lineno,
        )

        footer_pack = next(
            node
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "footer_panel"
            and node.func.attr == "pack"
        )
        footer_pack_options = {
            keyword.arg: keyword.value
            for keyword in footer_pack.keywords
        }
        self.assertEqual(footer_pack_options["side"].value, "bottom")
        self.assertEqual(footer_pack_options["fill"].value, "x")

        for panel_name in ("progress_panel", "button_panel"):
            panel_call = assignments[panel_name].value
            self.assertIsInstance(panel_call, ast.Call)
            self.assertIsInstance(panel_call.args[0], ast.Name)
            self.assertEqual(panel_call.args[0].id, "footer_panel")

    def test_fxpak_menu_opens_the_library_without_a_home_submenu(self):
        method = self.methods["_build_menu_bar"]
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertIn("FXPAK Pro…", constants)
        self.assertNotIn("FXPAK Pro Home…", constants)

        compatibility_route = self.methods["open_fxpak_pro_page"]
        called_attributes = {
            node.func.attr
            for node in ast.walk(compatibility_route)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("open_fxpak_sd_card_browser", called_attributes)
        self.assertNotIn("_open_in_app_page", called_attributes)

        loaded_names = {
            node.id
            for node in ast.walk(method)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        self.assertNotIn(
            "fxpak_downloads_menu",
            loaded_names,
            "The removed FXPAK submenu must not leave a startup reference.",
        )

    def test_feedback_menu_launches_the_embedded_form_directly(self):
        method = self.methods["open_feedback_dialog"]
        called_names = {
            node.func.id
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        }
        called_attributes = {
            node.func.attr
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_feedback_webview_command", called_names)
        self.assertIn("Popen", called_attributes)
        self.assertNotIn("_open_in_app_page", called_attributes)

    def test_fullscreen_forms_use_centered_bounded_panels(self):
        for method_name in (
            "_open_settings_dialog",
            "open_setup_health_check",
            "open_obs_settings_dialog",
        ):
            method = self.methods[method_name]
            calls = {
                node.func.attr
                for node in ast.walk(method)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
            }
            with self.subTest(method=method_name):
                self.assertIn("_create_centered_page_panel", calls)

    def test_readme_toc_entries_map_to_their_section_headings(self):
        helper = self.methods["_readme_toc_targets"]
        namespace = {"re": re}
        exec(
            compile(
                ast.Module(body=[helper], type_ignores=[]),
                str(SOURCE_FILE),
                "exec",
            ),
            namespace,
        )
        sample = (
            "TABLE OF CONTENTS\n"
            "1. First section\n"
            "2. Second section\n"
            "3. Third section\n\n"
            "1. FIRST SECTION\nBody\n\n"
            "2. SECOND SECTION\nBody\n\n"
            "3. THIRD SECTION\nBody\n"
        )
        self.assertEqual(
            namespace["_readme_toc_targets"](sample),
            [(2, 6), (3, 9), (4, 12)],
        )

        for readme_path in sorted(
            (SOURCE_FILE.parent / "docs").glob("README.*.txt")
        ):
            with self.subTest(readme=readme_path.name):
                links = namespace["_readme_toc_targets"](
                    readme_path.read_text(
                        encoding="utf-8-sig",
                        errors="replace",
                    )
                )
                self.assertGreaterEqual(len(links), 10)
                self.assertTrue(
                    all(target_line > toc_line for toc_line, target_line in links)
                )

    def test_packaged_startup_check_constructs_the_complete_ui(self):
        source = SOURCE_FILE.read_text(encoding="utf-8")
        self.assertIn(
            "TrackerApp(probe_root, startup_check=True)",
            source,
        )
        self.assertIn(
            "if not self.startup_check:\n            self._configure_tray()",
            source,
        )


if __name__ == "__main__":
    unittest.main()
