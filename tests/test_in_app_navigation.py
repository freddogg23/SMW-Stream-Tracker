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
            "_open_smwcentral_page",
            "_open_language_page",
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

    def test_page_host_finishes_responsive_work_before_first_paint(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["_open_in_app_page"],
        )
        self.assertIn("paint_cover", source)
        self.assertIn("page.run_prepaint_callbacks()", source)
        self.assertIn("queue_finish_completed_page", source)
        self.assertIn("paint_cover.destroy()", source)
        self.assertNotIn("self.main_ui_scale = 1.0", source)

    def test_translation_results_are_cached_for_repeated_page_labels(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["_translate_ui_text"],
        )
        self.assertIn("_ui_translation_cache", source)
        self.assertIn("cache_key = (language, source_text)", source)
        self.assertIn("cached_translation", source)

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
        self.assertIn("ROM BUILDER", constants)
        self.assertIn("download_patch_selected_button", constants)
        self.assertIn("Moderated hacks", constants)
        self.assertIn("Only missing ROMs", constants)
        source = ast.get_source_segment(self.source, method)
        self.assertIn('else ("title", "difficulty", "patch")', source)
        self.assertIn("self._toggle_downloader_row_selection", source)
        self.assertIn("self._start_selected_downloader_hacks", source)
        self.assertIn('"difficulty_overlay": None', source)

    def test_downloader_shows_all_matching_hacks_by_default(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["open_hack_downloader"],
        )
        self.assertIn(
            "only_missing_var = tk.BooleanVar(value=False)",
            source,
        )
        reset_source = ast.get_source_segment(
            self.source,
            self.methods["_reset_downloader_filters"],
        )
        self.assertIn('(\"only_missing_var\", False)', reset_source)

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

    def test_downloader_keeps_choices_in_header_and_catalog_actions_at_bottom(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["open_hack_downloader"],
        )
        header_start = source.index("header_options = tk.Frame")
        download_button = source.index(
            "primary_download_button = self._make_action_button",
            header_start,
        )
        list_start = source.index("list_frame = tk.Frame")
        for caption in (
            "Moderated hacks",
            "Waiting hacks",
            "Skip mapped games",
            "Only missing ROMs",
        ):
            with self.subTest(caption=caption):
                caption_position = source.index(f'"{caption}"', header_start)
                self.assertLess(caption_position, download_button)
        self.assertIn('"send_fxpak_sd_button"', source[header_start:download_button])
        self.assertNotIn("Copy through FXPAK Pro USB", source)
        self.assertNotIn("Upload new ROMs through FXPAK Pro USB", source)
        self.assertIn("locations_button.pack_forget()", source)
        self.assertIn("option.grid_remove()", source)

        maintenance_start = source.index(
            "catalog_maintenance_panel = tk.Frame",
            list_start,
        )
        self.assertGreater(maintenance_start, list_start)
        for caption in (
            "Refresh Moderated Hacks from SMW Central",
            "Refresh Waiting Hacks from SMW Central",
            "Add Unmoderated Hack",
        ):
            with self.subTest(caption=caption):
                self.assertIn(f'text="{caption}"', source[maintenance_start:])

    def test_fxpak_compatibility_route_opens_the_library_without_a_setup_menu(self):
        method = self.methods["_build_menu_bar"]
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertNotIn("FXPAK Pro…", constants)
        self.assertNotIn("FXPAK Pro Home…", constants)
        self.assertNotIn("Setup", constants)

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

        obs_source = ast.get_source_segment(
            self.source,
            self.methods["open_obs_settings_dialog"],
        )
        self.assertIn("YellowCanvasScrollbar", obs_source)
        self.assertIn("max_panel_width", obs_source)
        self.assertIn("horizontal_pad", obs_source)

    def test_settings_sidebar_uses_the_compact_menu_sections(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        for section_name in (
            "Platform",
            "File Locations",
            "Storage",
            "Streamer.bot",
            "OBS",
            "Timers",
            "About & Updates",
            "Help",
        ):
            with self.subTest(section=section_name):
                self.assertIn(section_name, constants)
        self.assertIn("settings_panels[section_name]", source)
        self.assertIn('settings_panels["Platform"]', source)
        self.assertIn('settings_panels["Timers"]', source)
        self.assertIn('build_action_settings_page(\n            "OBS"', source)
        self.assertIn('section.bind(\n                "<Button-1>"', source)
        self.assertIn(
            "show_settings_section(initial_settings_section)",
            source,
        )
        sidebar_source = source[
            source.index("settings_sidebar_section_names = (") :
            source.index("settings_section_icons = {")
        ]
        self.assertNotIn('"Language"', sidebar_source)
        self.assertNotIn('"SMW Central"', sidebar_source)
        self.assertGreater(
            sidebar_source.index('"About & Updates"'),
            sidebar_source.index('"Help"'),
        )
        self.assertNotIn('text="SETTINGS"', source)
        self.assertNotIn(
            '("General", "Connections", "Files & folders", "Timers", "Language")',
            source,
        )
        self.assertIn('"Platform": "super_nintendo_console"', source)
        self.assertIn('"Storage": "nvme"', source)
        self.assertIn('"File Locations": "windows_file"', source)
        self.assertIn('"Streamer.bot": "streamerbot"', source)
        self.assertIn('"OBS": "obs"', source)
        self.assertIn('"Timers": "stopwatch"', source)
        self.assertIn('"About & Updates": "bell"', source)
        self.assertIn('"Help": "open_book"', source)
        self.assertNotIn("self._bind_pointer_tooltip(section_row, section_name)", source)
        self.assertNotIn("self._bind_pointer_tooltip(section, section_name)", source)
        self.assertNotIn("self._bind_pointer_tooltip(section_icon, section_name)", source)
        self.assertNotIn("self._bind_pointer_tooltip(update_badge, section_name)", source)
        self.assertNotIn('settings_panels["Language"]', source)
        self.assertNotIn('settings_panels["SMW Central"]', source)
        self.assertIn('build_action_settings_page(\n            "Storage"', source)
        self.assertLess(
            sidebar_source.index('"Streamer.bot"'),
            sidebar_source.index('"OBS"'),
        )
        self.assertNotIn('build_action_settings_page(\n            "Stats"', source)
        self.assertNotIn('("Overview…", self.open_stats_overview)', source)
        self.assertNotIn('("My Tracker…", self.open_my_tracker)', source)

    def test_file_locations_settings_owns_every_downloader_destination(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('settings_panels["File Locations"]', source)
        self.assertIn('settings_section_bodies["File Locations"]', source)
        for caption in (
            "Clean SMW Base ROM",
            "ROM Game-Library Folder",
            "Mounted SD Copy Folder",
            "FXPAK Pro USB Copy Folder",
            "Choose Base ROM…",
            "Choose ROM Library…",
            "Setup FXPAK Folder",
            "Set FXPAK Folder…",
        ):
            with self.subTest(caption=caption):
                self.assertIn(f'"{caption}"', source)
        for config_key in (
            "rom_builder_base_rom_path",
            "rom_builder_library_folder",
            "rom_builder_sd_folder",
            "rom_builder_usb_folder",
        ):
            with self.subTest(config=config_key):
                self.assertIn(f'"{config_key}"', source)
        self.assertIn("file_location_cards", source)
        self.assertIn("apply_settings_responsive_layout", source)

    def test_platform_settings_panel_matches_launch_preferences_reference(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        for caption in (
            "Platform & Launch Behavior",
            "Active Platform",
            "Console Core",
            "Local ROM Library",
            "Automatically Connect\\nWhen the App Starts",
            "Return to the Dashboard\\nAfter Launching",
            "Confirm Before Replacing\\nthe Current Game",
            "Save Tracker Data\\nAutomatically",
            "QUsb2Snes Application",
            "SNI Application",
            "RetroArch Application",
            "RetroArch Core",
        ):
            with self.subTest(caption=caption):
                self.assertIn(caption, source)
        self.assertIn('platform_box.bind("<<ComboboxSelected>>"', source)
        self.assertIn('"super_nintendo_console"', source)
        self.assertIn("apply_settings_responsive_layout", source)
        self.assertIn("capture_settings_font_baselines", source)
        self.assertIn('tier = "wide"', source)
        self.assertIn('tier = "standard"', source)
        self.assertIn('tier = "compact"', source)
        self.assertIn("font_multiplier = 0.97", source)
        self.assertIn("font_multiplier = 0.94", source)
        self.assertIn("font_multiplier = 0.86", source)
        self.assertNotIn("font_multiplier = 1.30", source)
        self.assertIn("nav_width = 240", source)
        self.assertIn("nav_width = 210", source)
        self.assertIn("nav_width = 168", source)
        self.assertIn("platform_density = 0.97", source)
        self.assertIn("natural_height > visible_height + 2", source)
        self.assertIn("settings_content_scrollbar.grid_remove()", source)
        self.assertIn(
            "for section_name, section_body in settings_section_bodies.items()",
            source,
        )
        self.assertIn("location_card.configure(", source)
        self.assertIn("title_bar.configure(", source)
        self.assertIn("platform_option_widgets", source)
        self.assertIn("platform_setup_pages", source)
        self.assertIn("platform_icon_photos", source)
        self.assertIn("settings_action_groups", source)
        self.assertIn("settings_content_scrollbar", source)
        self.assertIn("sync_settings_content_width", source)
        self.assertIn("scroll_settings_content", source)
        self.assertIn("self.root.winfo_width()", source)
        self.assertIn('"auto_connect_on_startup": bool(', source)
        self.assertIn('"return_to_dashboard_after_launch": bool(', source)
        self.assertIn('"confirm_before_replacing_game": bool(', source)
        self.assertIn('"save_tracker_data_automatically": bool(', source)
        self.assertNotIn('text="Minimize to Tray"', source)

    def test_stream_desk_icon_renderer_includes_platform_controller(self):
        method = self.methods["_draw_stream_desk_icon"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('key == "super_nintendo_console"', source)
        self.assertIn('key == "super_famicom_controller"', source)
        self.assertIn('key in {"windows_file", "file_locations"}', source)
        self.assertIn('key in {"nvme", "storage"}', source)
        self.assertIn('{"controller", "platform"}', source)
        self.assertIn('key == "obs"', source)
        self.assertIn('"obs_logo.png"', source)
        self.assertIn('self._obs_logo_source_image', source)
        self.assertIn('{"timer", "stopwatch"}', source)
        self.assertIn('{"language", "translate"}', source)
        self.assertIn('{"updates", "bell"}', source)
        self.assertIn('{"help", "open_book", "book"}', source)
        self.assertIn('{"smw_central", "smwcentral", "storefront"}', source)
        self.assertIn('"smwcentral_logo.png"', source)
        self.assertIn("round(44 * unit)", source)
        self.assertNotIn("smwc_letters", source)
        self.assertIn("Image.Resampling.NEAREST", source)
        self.assertIn("splinesteps=24", source)

    def test_settings_responsive_redraw_preserves_each_section_icon(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn(
            "settings_section_icons.get(item_name, item_name)",
            source,
        )
        responsive_start = source.index(
            "def apply_settings_responsive_layout()"
        )
        responsive_end = source.index(
            "def scroll_settings_content",
            responsive_start,
        )
        responsive_source = source[responsive_start:responsive_end]
        self.assertNotIn(
            'self._draw_stream_desk_icon(\n                        icon_canvas,\n                        "controller"',
            responsive_source,
        )

    def test_connection_indicator_uses_three_colors_and_opens_settings(self):
        helper_source = ast.get_source_segment(
            self.source,
            self.methods["_set_connection_display"],
        )
        for state_name, theme_color in (
            ('"connected"', 'THEME["good"]'),
            ('"partial"', 'THEME["warning"]'),
            ('"disconnected"', 'THEME["bad"]'),
        ):
            with self.subTest(state=state_name):
                self.assertIn(state_name, helper_source)
                self.assertIn(theme_color, helper_source)
        for stream_color in (
            'STREAM_DESK["green"]',
            'STREAM_DESK["yellow"]',
            'STREAM_DESK["red"]',
        ):
            self.assertIn(stream_color, helper_source)
        build_source = ast.get_source_segment(
            self.source,
            self.methods["_build_ui"],
        )
        self.assertIn(
            'lambda _event: self._open_settings_dialog()',
            build_source,
        )
        menu_source = ast.get_source_segment(
            self.source,
            self.methods["_build_menu_bar"],
        )
        self.assertIn("self.stream_ready_dot", menu_source)
        self.assertIn("self._set_connection_display", menu_source)
        self.assertIn(
            'lambda _event: self._open_settings_dialog()',
            menu_source,
        )
        event_source = ast.get_source_segment(
            self.source,
            self.methods["process_events"],
        )
        self.assertIn('event.get("partial")', event_source)
        self.assertIn('"Partially Connected"', event_source)

    def test_restore_is_under_help_and_tray_command_is_removed(self):
        source = ast.get_source_segment(
            self.source,
            self.methods["_build_menu_bar"],
        )
        self.assertNotIn('"Minimize to Tray"', source)
        self.assertEqual(source.count('"Restore Previous App Version..."'), 1)
        restore_position = source.index('"Restore Previous App Version..."')
        help_position = source.index("self.help_menu_button")
        self.assertGreater(restore_position, help_position)

    def test_each_settings_section_contains_its_existing_menu_actions(self):
        method = self.methods["_open_settings_dialog"]
        constants = {
            node.value
            for node in ast.walk(method)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        expected_actions = (
            "Restore Previous App Version...",
            "Import / Refresh from Spreadsheet…",
            "Back Up Database…",
            "Edit OBS Text Settings...",
            "Read Me / Setup Guide...",
            "Setup & Health Check...",
            "Updates",
            "About...",
        )
        for action_name in expected_actions:
            with self.subTest(action=action_name):
                self.assertIn(action_name, constants)
        self.assertNotIn("View Complete Catalog…", constants)
        self.assertNotIn("Download & Patch Missing Hacks…", constants)

    def test_game_library_owns_the_missing_hacks_action(self):
        method = self.methods["_build_stream_desk_game_library"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('tr("Download & Patch Missing Hacks")', source)
        self.assertIn("self.open_hack_downloader", source)

    def test_missing_hacks_page_can_refresh_the_moderated_catalog(self):
        method = self.methods["open_hack_downloader"]
        source = ast.get_source_segment(self.source, method)
        catalog_branch = source.index("if catalog_view_only:")
        downloader_branch = source.index("else:", catalog_branch)
        downloader_source = source[downloader_branch:]
        self.assertIn(
            'text="Refresh Moderated Hacks from SMW Central"',
            downloader_source,
        )
        self.assertIn(
            "command=self.refresh_smwcentral_catalog",
            downloader_source,
        )

    def test_app_language_has_a_dedicated_main_sidebar_page(self):
        method = self.methods["_open_language_page"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('_open_in_app_page("language", "Language")', source)
        self.assertIn('text=self._translate_ui_text("App Language")', source)
        self.assertIn("button_grid = tk.Frame", source)
        self.assertIn("language_buttons:", source)
        self.assertIn("def select_language", source)
        self.assertIn("APP_LANGUAGE_LABELS.items()", source)
        self.assertIn("self._set_app_language", source)
        self.assertIn("self.root.after_idle(self._open_language_page)", source)
        self.assertNotIn("ttk.Combobox", source)
        self.assertIn("image=self._language_flag_icon(language_code)", source)

        settings_source = ast.get_source_segment(
            self.source,
            self.methods["_open_settings_dialog"],
        )
        self.assertNotIn('settings_panels["Language"]', settings_source)

        labels_assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "APP_LANGUAGE_LABELS"
                for target in node.targets
            )
        )
        flags_assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "APP_LANGUAGE_FLAGS"
                for target in node.targets
            )
        )
        self.assertEqual(
            ast.literal_eval(labels_assignment.value),
            {
                "en": "English",
                "es": "Español",
                "fr": "Français",
                "de": "Deutsch",
                "pt-BR": "Português (Brasil)",
            },
        )
        self.assertEqual(
            ast.literal_eval(flags_assignment.value),
            {
                "en": "US",
                "es": "ES",
                "fr": "FR",
                "de": "DE",
                "pt-BR": "BR",
            },
        )

    def test_platform_settings_no_longer_contains_appearance_selector(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        platform_preferences = source[
            source.index("platform_form = tk.Frame") :
            source.index("def refresh_platform_preview")
        ]
        self.assertNotIn('text="Appearance"', platform_preferences)
        self.assertNotIn('text="Stream Desk"', platform_preferences)
        self.assertNotIn("local_appearance", source)

    def test_updates_actions_are_separate_from_help(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        updates_start = source.index(
            'build_action_settings_page(\n            "About & Updates"'
        )
        help_start = source.index(
            'build_action_settings_page(\n            "Help"',
            updates_start,
        )
        updates_source = source[updates_start:help_start]
        self.assertIn('("Updates", self.check_for_updates)', updates_source)
        self.assertIn('"About..."', updates_source)
        self.assertIn('"Restore Previous App Version..."', updates_source)
        help_source = source[help_start:]
        self.assertNotIn('"About..."', help_source)
        self.assertNotIn('"Restore Previous App Version..."', help_source)

    def test_smwcentral_is_a_standalone_theme_aware_main_sidebar_page(self):
        method = self.methods["_open_smwcentral_page"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('_open_in_app_page("smwcentral", "SMW Central")', source)
        self.assertIn('palette = self._library_palette()', source)
        self.assertIn('panel_bg=palette["panel"]', source)
        self.assertIn('bg=palette["panel"]', source)
        self.assertIn('"SMW Central Updates"', source)
        self.assertIn('"SMW Central Radio"', source)
        self.assertIn('"Log In to SMW Central..."', source)
        self.assertNotIn('"Refresh Moderated Hacks from SMW Central…"', source)
        self.assertNotIn('"SMW Central Catalog"', source)
        self.assertNotIn("settings_nav", source)
        self.assertNotIn("Save Settings", source)

        route_source = ast.get_source_segment(
            self.source,
            self.methods["_open_navigation_section"],
        )
        self.assertIn('"smwcentral": self._open_smwcentral_page', route_source)
        self.assertIn('"language": self._open_language_page', route_source)

    def test_settings_tools_return_to_the_same_settings_section(self):
        settings_source = ast.get_source_segment(
            self.source,
            self.methods["_open_settings_dialog"],
        )
        close_source = ast.get_source_segment(
            self.source,
            self.methods["_close_in_app_page"],
        )
        navigation_source = ast.get_source_segment(
            self.source,
            self.methods["_open_navigation_section"],
        )
        self.assertIn("opened_page._return_to_settings_section = selected_section", settings_source)
        self.assertNotIn("dialog.destroy()\n            action()", settings_source)
        self.assertIn("return_to_settings_section", close_source)
        self.assertIn("self._open_settings_dialog(", close_source)
        self.assertIn("active_page._return_to_settings_section = None", navigation_source)

    def test_top_bar_uses_a_persistent_light_dark_toggle_not_a_menu_button(self):
        menu_source = ast.get_source_segment(
            self.source,
            self.methods["_build_menu_bar"],
        )
        self.assertNotIn('text="☰  Menu"', menu_source)
        self.assertNotIn("self.stream_tools_button =", menu_source)
        self.assertIn("self.stream_theme_toggle = tk.Canvas", menu_source)
        self.assertIn("toggle_stream_theme", menu_source)
        self.assertIn(
            '"light" if self.appearance_var.get() == "dark" else "dark"',
            menu_source,
        )
        appearance_source = ast.get_source_segment(
            self.source,
            self.methods["_set_appearance"],
        )
        self.assertIn(
            'normalized = str(mode or "dark").strip().casefold()',
            appearance_source,
        )
        self.assertIn('if normalized not in {"light", "dark"}', appearance_source)

    def test_workbook_import_is_a_storage_action_not_a_setup_path(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        storage_start = source.index('build_action_settings_page(\n            "Storage"')
        storage_end = source.index(
            'build_action_settings_page(\n            "OBS"',
            storage_start,
        )
        storage_source = source[storage_start:storage_end]
        self.assertIn('"Import / Refresh from Spreadsheet…"', storage_source)
        self.assertIn("self._reload_selected_spreadsheet", storage_source)
        self.assertNotIn('"Import workbook"', source)

    def test_obs_and_timer_settings_are_split_into_purpose_built_pages(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        self.assertIn('build_action_settings_page(\n            "OBS"', source)
        self.assertIn('self._setup_guide_text("obs_title")', source)
        self.assertIn("self.open_guided_obs_text_setup", source)
        self.assertIn('"choose_obs_folder_button"', source)
        self.assertIn('"Edit OBS Text Settings..."', source)
        self.assertIn('"Open OBS Text Folder"', source)
        self.assertIn('settings_panels["Timers"]', source)
        for caption in (
            "Timer & LiveSplit Settings",
            "AutoStop:",
            "Game LiveSplit port:",
            "Level LiveSplit port:",
            "LiveSplit Timers Setup...",
        ):
            with self.subTest(caption=caption):
                self.assertIn(f'"{caption}"', source)
        self.assertIn(
            "Timers keep running for this many seconds whenever gameplay",
            source,
        )
        self.assertNotIn('"OBS text folder"', source)

    def test_settings_action_pages_use_active_stream_desk_text_colors(self):
        method = self.methods["_open_settings_dialog"]
        source = ast.get_source_segment(self.source, method)
        action_page_start = source.index("def build_action_settings_page(")
        file_locations_start = source.index(
            "file_locations_body = self._create_centered_page_panel",
            action_page_start,
        )
        action_page_source = source[action_page_start:file_locations_start]

        self.assertIn('fg=STREAM_DESK["text_strong"]', action_page_source)
        self.assertNotIn('fg=THEME["text"]', action_page_source)
        timer_start = source.index('text="Timer & LiveSplit Settings"')
        timer_end = source.index("button_row = tk.Frame(", timer_start)
        timer_source = source[timer_start:timer_end]
        self.assertIn('fg=STREAM_DESK["text_strong"]', timer_source)
        self.assertIn('fg=STREAM_DESK["muted"]', timer_source)
        self.assertNotIn('fg=THEME["text"]', timer_source)
        self.assertNotIn('fg=THEME["muted"]', timer_source)

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

    def test_stream_desk_shell_is_shared_by_dashboard_and_pages(self):
        self.assertIn("STREAM_DESK = {", self.source)
        build_ui = ast.get_source_segment(self.source, self.methods["_build_ui"])
        page_host = ast.get_source_segment(
            self.source,
            self.methods["_open_in_app_page"],
        )
        self.assertIn("self._build_navigation_rail", build_ui)
        self.assertIn("self.in_app_banner_frame", page_host)
        self.assertIn("self._set_navigation_rail_active", page_host)

    def test_navigation_rail_uses_requested_order_without_star_shortcut(self):
        build_rail = ast.get_source_segment(
            self.source,
            self.methods["_build_navigation_rail"],
        )
        assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "STREAM_DESK_NAVIGATION_ITEMS"
                for target in node.targets
            )
        )
        navigation_items = ast.literal_eval(assignment.value)

        self.assertEqual(
            navigation_items,
            (
                ("home", "dashboard", "Dashboard"),
                ("overview", "overview", "Overview"),
                ("tracker", "tracker", "My Tracker"),
                ("library", "library", "Game Library"),
                ("modes", "super_famicom_controller", "Game Modes"),
                ("smwcentral", "smw_central", "SMW Central"),
                ("language", "language", "Language"),
                ("settings", "settings", "Settings"),
            ),
        )
        self.assertNotIn('text="★"', build_rail)
        self.assertIn("self._bind_pointer_tooltip(button, accessible_name)", build_rail)
        self.assertIn("_render_navigation_rail_button", self.source)
        self.assertIn("_draw_stream_desk_icon", self.source)

        icon_source = ast.get_source_segment(
            self.source,
            self.methods["_draw_stream_desk_icon"],
        )
        for icon_key in (
            "dashboard",
            "overview",
            "tracker",
            "library",
            "settings",
        ):
            with self.subTest(icon=icon_key):
                self.assertIn(f'key == "{icon_key}"', icon_source)
        self.assertIn('key in {"controller", "platform"}', icon_source)
        self.assertIn("gear_points", icon_source)
        self.assertIn("reference_icon_keys", icon_source)
        self.assertIn("supersample = 4", icon_source)
        self.assertIn("Image.Resampling.LANCZOS", icon_source)
        self.assertIn("canvas._stream_desk_icon_photo", icon_source)

        render_source = ast.get_source_segment(
            self.source,
            self.methods["_render_navigation_rail_button"],
        )
        self.assertIn('fill=STREAM_DESK["surface_alt"]', render_source)
        self.assertIn('STREAM_DESK["text_strong"] if selected', render_source)
        self.assertIn("full_color=True", render_source)

        tooltip_source = ast.get_source_segment(
            self.source,
            self.methods["_bind_pointer_tooltip"],
        )
        self.assertIn("tk.Label", tooltip_source)
        self.assertIn("tooltip_label.place", tooltip_source)
        self.assertIn("tooltip_label.lift", tooltip_source)
        self.assertIn("self.root.winfo_rootx()", tooltip_source)
        self.assertIn("self.root.winfo_rooty()", tooltip_source)
        self.assertIn('widget.bind("<Enter>"', tooltip_source)
        self.assertIn('widget.bind("<Motion>"', tooltip_source)
        self.assertIn('widget.bind("<Leave>"', tooltip_source)
        self.assertIn("event.x_root", tooltip_source)
        self.assertIn("event.y_root", tooltip_source)

        for language in ("au", "es", "fr", "de", "pt-BR"):
            translation_pattern = re.compile(
                rf'"{re.escape(language)}"\s*:\s*\{{.*?"Dashboard"\s*:',
                re.DOTALL,
            )
            self.assertRegex(self.source, translation_pattern)

        close_page = ast.get_source_segment(
            self.source,
            self.methods["_close_in_app_page"],
        )
        self.assertIn('_translate_ui_text("Dashboard")', close_page)

    def test_rebuilds_destroy_the_navigation_rail_with_the_main_shell(self):
        for method_name in ("_apply_responsive_ui_scale", "_set_app_language"):
            method_source = ast.get_source_segment(
                self.source,
                self.methods[method_name],
            )
            with self.subTest(method=method_name):
                self.assertIn('"navigation_rail"', method_source)

    def test_dashboard_includes_the_session_timeline(self):
        build_ui = ast.get_source_segment(self.source, self.methods["_build_ui"])
        self.assertIn("self._make_session_timeline", build_ui)
        self.assertIn("_refresh_session_timeline", self.methods)


if __name__ == "__main__":
    unittest.main()
