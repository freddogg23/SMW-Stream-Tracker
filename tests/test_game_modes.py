import importlib.util
import inspect
from pathlib import Path
import sys
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_game_modes_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GameModesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_game_modes_offers_all_requested_modes(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        expected_modes = {
            "Play Random Hack": "self._play_random_main_hack",
            "Hack Draft": "self._open_hack_draft",
            "Difficulty Ladder": "self._open_difficulty_ladder",
            "Creator Spotlight": "self._open_creator_spotlight",
            "Time Capsule": "self._open_time_capsule",
            "Hall of Fame Tour": "self._open_hall_of_fame_tour",
            "Hot Potato": "self._open_hot_potato",
            "Mario Kaizo Challenge": "self._open_mario_kaizo_challenge",
        }
        for label, command in expected_modes.items():
            with self.subTest(label=label):
                self.assertIn(label, source)
                self.assertIn(command, source)
        self.assertNotIn("Hack Gauntlet", source)
        self.assertNotIn("_open_hack_gauntlet_maker", source)

    def test_every_game_mode_uses_title_creator_difficulty_type_filters(self):
        shared_source = inspect.getsource(
            self.tracker.TrackerApp._build_game_mode_filter_panel
        )
        self.assertIn('("Search", "search", None)', shared_source)
        self.assertIn('("Creator", "creator", creator_values)', shared_source)
        self.assertIn('("Difficulty", "difficulty"', shared_source)
        self.assertIn('("Type", "hack_type"', shared_source)
        self.assertIn('("Released", "released"', shared_source)
        self.assertIn('"Hall of Fame", "hall_of_fame"', shared_source)
        self.assertIn('"RetroAchievements"', shared_source)

        for method_name in (
            "_open_hack_draft",
            "_open_grouped_game_mode_picker",
            "_open_hot_potato",
            "_play_random_main_hack",
        ):
            with self.subTest(method=method_name):
                source = inspect.getsource(
                    getattr(self.tracker.TrackerApp, method_name)
                )
                self.assertIn("_build_game_mode_filter_panel", source)

        mario_source = inspect.getsource(
            self.tracker.TrackerApp._open_mario_kaizo_challenge
        )
        curator_source = inspect.getsource(
            self.tracker.TrackerApp._open_mario_kaizo_playlist_curator
        )
        self.assertIn('("Search", "Creator", "Difficulty", "Type")', mario_source)
        self.assertIn('("Search", "Creator", "Difficulty", "Type")', curator_source)

        self.assertTrue(
            callable(getattr(self.tracker.TrackerApp, "_skip_mario_kaizo_hack"))
        )

    def test_shared_filters_apply_hall_of_fame_and_retroachievements(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "en"
        app._translate_ui_text = lambda text: str(text)
        games = [
            {
                "title": "Achievement Hall",
                "author": "Maker",
                "difficulty": "Expert",
                "hack_type": "Kaizo",
                "hall_of_fame": True,
                "_retroachievements_game_id": 123,
            },
            {
                "title": "Regular Run",
                "author": "Maker",
                "difficulty": "Expert",
                "hack_type": "Kaizo",
                "hall_of_fame": False,
                "_retroachievements_game_id": 0,
            },
        ]

        matches = app._game_mode_filtered_hacks(
            games,
            "",
            "Any",
            "Any",
            "Any",
            "Any",
            "Yes",
            "Yes",
        )

        self.assertEqual(
            [game["title"] for game in matches],
            ["Achievement Hall"],
        )

    def test_shared_search_matches_creator_names(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app._translate_ui_text = lambda text: str(text)
        games = [
            {
                "title": "Shell Summit",
                "author": "Pixel Pilot",
                "difficulty": "Expert",
                "hack_type": "Kaizo",
            },
            {
                "title": "Cloud Run",
                "author": "Other Maker",
                "difficulty": "Casual",
                "hack_type": "Standard",
            },
        ]
        matches = app._game_mode_filtered_hacks(
            games,
            "pixel pilot",
            "Any",
            "Any",
            "Any",
        )
        self.assertEqual([game["title"] for game in matches], ["Shell Summit"])

    def test_random_mode_queue_populates_dashboard_up_next(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.active_game_mode_name = "Play Random Hack"
        app.config = {}
        app.active_game_mode_queue = []
        app.active_game_mode_queue_index = -1
        app._refresh_mario_kaizo_dashboard_queue = mock.Mock()
        current = {"catalog_key": "one", "title": "One"}
        candidates = [
            current,
            {"catalog_key": "two", "title": "Two"},
            {"catalog_key": "three", "title": "Three"},
        ]

        with mock.patch.object(self.tracker.random, "shuffle"):
            app._prepare_active_game_mode_queue(current, candidates)

        self.assertEqual(app.active_game_mode_queue_index, 0)
        self.assertEqual(
            [game["title"] for game in app._active_game_mode_up_next_games(3)],
            ["Two", "Three"],
        )
        app._refresh_mario_kaizo_dashboard_queue.assert_called_once_with()

    def test_switching_modes_requires_confirmation_and_replaces_state(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {"mario_kaizo_challenge_active": False}
        app.active_game_mode_name = "Hack Draft"
        app.active_game_mode_queue = [{"title": "Old Hack"}]
        app.active_game_mode_queue_index = 0
        app.hot_potato_active = False
        app.hot_potato_rotating = False
        app.hot_potato_rotate_after_id = None
        app.hot_potato_dashboard_status = ""
        app.hot_potato_queue = []
        app.hot_potato_index = -1
        app.game_mode_dialog = None
        app.root = mock.Mock()
        app._cancel_hot_potato_rotation_wait = mock.Mock()
        app._close_hot_potato_status = mock.Mock()
        app._refresh_mario_kaizo_dashboard_queue = mock.Mock()
        app._format_ui_text = lambda text, **values: text.format(**values)
        app._ask_localized_yes_no = mock.Mock(return_value=True)
        app._set_active_game_mode_session = mock.Mock(
            side_effect=lambda mode: setattr(
                app,
                "active_game_mode_name",
                str(mode or ""),
            )
        )
        launch_new_mode = mock.Mock()

        app._request_game_mode_start("Difficulty Ladder", launch_new_mode)

        app._ask_localized_yes_no.assert_called_once()
        self.assertEqual(app.active_game_mode_name, "")
        self.assertEqual(app.active_game_mode_queue, [])
        self.assertEqual(app.active_game_mode_queue_index, -1)
        launch_new_mode.assert_called_once_with()

    def test_declining_mode_switch_keeps_current_mode(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {"mario_kaizo_challenge_active": False}
        app.active_game_mode_name = "Creator Spotlight"
        app.hot_potato_active = False
        app.game_mode_dialog = None
        app.root = mock.Mock()
        app._format_ui_text = lambda text, **values: text.format(**values)
        app._ask_localized_yes_no = mock.Mock(return_value=False)
        app._stop_active_game_mode_for_switch = mock.Mock()
        launch_new_mode = mock.Mock()

        app._request_game_mode_start("Time Capsule", launch_new_mode)

        app._stop_active_game_mode_for_switch.assert_not_called()
        launch_new_mode.assert_not_called()
        self.assertEqual(app.active_game_mode_name, "Creator Spotlight")

    def test_dashboard_mode_control_bar_and_connection_dots_are_wired(self):
        dashboard_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_dashboard
        )
        rail_source = inspect.getsource(
            self.tracker.TrackerApp._build_navigation_rail
        )
        connection_source = inspect.getsource(
            self.tracker.TrackerApp._set_connection_display
        )

        self.assertIn("stream_dashboard_mode_controls_host", dashboard_source)
        self.assertIn("_refresh_game_mode_dashboard_controls", dashboard_source)
        self.assertIn("navigation_connection_dot", rail_source)
        self.assertIn('"partial": STREAM_DESK["yellow"]', rail_source)
        self.assertIn("_open_settings_dialog", rail_source)
        self.assertIn("navigation_connection_dot.configure", connection_source)

    def test_game_modes_use_requested_order_and_matching_icon_map(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )
        expected_order = (
            "Hot Potato",
            "Mario Kaizo Challenge",
            "Play Random Hack",
            "Hack Draft",
            "Difficulty Ladder",
            "Creator Spotlight",
            "Time Capsule",
            "Hall of Fame Tour",
        )
        positions = [source.index(f'"{label}"') for label in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(
            self.tracker.GAME_MODE_ICON_KEYS,
            {
                "hot_potato": "hot_potato",
                "mario_kaizo_challenge": "mario_hat",
                "play_random_hack": "random",
                "hack_draft": "hack_draft",
                "difficulty_ladder": "ladder",
                "creator_spotlight": "spotlight",
                "time_capsule": "time_attack",
                "hall_of_fame_tour": "first_place_medal",
            },
        )

        builder_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_modes
        )
        self.assertIn("_draw_stream_desk_icon", builder_source)
        self.assertIn("mode_icon_canvases", builder_source)
        self.assertIn("symbol_var.get()", builder_source)

    def test_active_game_modes_layout_is_large_and_responsive(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_modes
        )

        self.assertIn('detail.rowconfigure(1, weight=1)', source)
        self.assertIn('uniform="game_mode_menu_rows"', source)
        self.assertIn('page.bind("<Configure>"', source)
        self.assertIn('page_width >= self._ui_px(1500)', source)
        self.assertIn('page_width >= self._ui_px(1100)', source)
        self.assertIn('stat_columns = 2', source)
        self.assertIn('card.grid_configure(', source)
        self.assertIn('copy_wraplength', source)
        self.assertIn('symbol_canvas.configure(width=symbol_size', source)
        self.assertIn('"apply_responsive_layout": apply_responsive_layout', source)

    def test_game_mode_menu_updates_description_on_hover(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        self.assertIn('"<Enter>"', source)
        self.assertIn('"<Leave>"', source)
        self.assertIn("description_var.set", source)

    def test_game_mode_menu_uses_selector_and_details_layout(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        self.assertIn('home_text="Back"', source)
        self.assertIn("selector_panel", source)
        self.assertIn("selector_list", source)
        self.assertIn("details_card", source)
        self.assertIn("mode_title_var", source)
        self.assertIn("mode_rules_var", source)
        self.assertIn("mode_symbol_var", source)
        self.assertIn("select_mode", source)
        self.assertIn("start_selected_mode", source)
        self.assertNotIn("show_rules", source)
        self.assertNotIn('self._translate_ui_text("Rules")', source)
        self.assertIn('self._translate_ui_text("Start Mode")', source)

    def test_game_mode_menu_adapts_to_compact_windows(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )

        self.assertIn("apply_responsive_layout", source)
        self.assertIn('page.bind("<Configure>"', source)
        self.assertIn("symbol_panel.grid_configure", source)
        self.assertIn("page_width < self._ui_px(900)", source)
        self.assertIn("copy_wraplength", source)

    def test_game_mode_popups_use_line_icons_without_gif_assets(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )
        random_source = inspect.getsource(
            self.tracker.TrackerApp._play_random_main_hack
        )

        self.assertFalse(hasattr(self.tracker, "GAME_MODE_GIF_FILES"))
        self.assertIn("GAME_MODE_ICON_KEYS", shell_source)
        self.assertIn("_draw_stream_desk_icon", shell_source)
        self.assertNotIn("_create_game_mode_stage", shell_source)
        self.assertNotIn("_create_game_mode_stage", random_source)

    def test_game_mode_windows_share_the_stream_desk_popup_shell(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )
        random_source = inspect.getsource(
            self.tracker.TrackerApp._play_random_main_hack
        )

        self.assertIn('text=self._translate_ui_text("GAME MODES")', shell_source)
        self.assertIn('bg=palette["window"]', shell_source)
        self.assertIn('highlightbackground=palette["border"]', shell_source)
        self.assertIn('dialog.bind("<Configure>"', shell_source)
        self.assertIn("_game_mode_dialog_shell", random_source)

    def test_game_mode_popups_keep_action_buttons_visible_on_small_screens(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )

        self.assertIn("body_canvas", shell_source)
        self.assertIn("body_scrollbar", shell_source)
        self.assertIn("refresh_body_scroll_region", shell_source)
        self.assertIn('dialog.bind("<MouseWheel>"', shell_source)
        self.assertIn("child.pack_configure(before=body_shell)", shell_source)

    def test_active_game_mode_controls_stay_beside_the_yellow_heading(self):
        dashboard_source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_dashboard
        )
        controls_pack = dashboard_source[
            dashboard_source.index(
                "self.stream_dashboard_mode_controls_host.pack("
            ):
        ]

        self.assertIn('side="left"', controls_pack.split(")", 1)[0])
        self.assertIn("stream_dashboard_mode_rules_var", dashboard_source)
        self.assertIn("stream_dashboard_mode_rules_label", dashboard_source)

    def test_game_mode_popup_palette_is_created_before_first_use(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )

        self.assertLess(
            shell_source.index("palette = self._library_palette()"),
            shell_source.index('dialog.configure(bg=palette["window"])'),
        )

    def test_game_mode_popup_restores_the_shared_full_width_banner(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )

        self.assertIn("dialog_banner_frame", shell_source)
        self.assertIn("_build_cropped_stream_desk_banner", shell_source)
        self.assertIn("_game_mode_banner_photo", shell_source)
        self.assertIn('dialog_banner_frame.bind(', shell_source)

    def test_game_mode_popup_resize_ignores_child_configure_events(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )

        self.assertIn(
            'getattr(event, "widget", None) is not dialog',
            source,
        )
        self.assertIn("popup_layout_state", source)
        self.assertIn("dialog.after_cancel", source)
        self.assertIn("render_popup_layout", source)
        self.assertIn("current_width = int(dialog.winfo_width())", source)

    def test_game_mode_popup_maps_with_the_selected_native_theme(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )

        self.assertIn("dialog.withdraw()", source)
        self.assertIn("finish_popup_mapping", source)
        self.assertIn("self._apply_widget_appearance(dialog, dark=dark)", source)
        self.assertIn("dialog.deiconify()", source)
        self.assertIn("self._set_windows_titlebar_theme", source)

    def test_game_mode_stage_has_distinct_scenery_for_every_mode(self):
        visible_size_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_stage_visible_dimensions
        )
        self.assertIn("ancestor.winfo_width()", visible_size_source)
        self.assertIn("ancestor.winfo_height()", visible_size_source)
        self.assertIn("visible_bottom", visible_size_source)

        image_source = inspect.getsource(
            self.tracker.TrackerApp._draw_game_mode_stage_image
        )

        self.assertIn("GAME_MODE_STAGE_IMAGE_FILES", image_source)
        self.assertIn('getattr(resampling, "NEAREST", 0)', image_source)
        self.assertIn(
            "height / max(1, source_height)",
            image_source,
        )
        self.assertIn('Image.new("RGB", (width, height))', image_source)
        self.assertIn("rendered.paste(level_strip", image_source)
        self.assertIn(
            "_game_mode_stage_visible_dimensions(canvas)",
            image_source,
        )
        self.assertIn('canvas.tag_lower("game_mode_stage")', image_source)
        animation_source = inspect.getsource(
            self.tracker.TrackerApp._show_game_mode_animation
        )
        self.assertIn("canvas.create_image", animation_source)
        self.assertIn("canvas.itemconfigure", animation_source)
        self.assertIn("GAME_MODE_STAGE_SPRITE_SCALES", animation_source)
        self.assertIn("min(requested_scale, fit_scale)", animation_source)
        self.assertIn(
            "_game_mode_stage_visible_dimensions(canvas)",
            animation_source,
        )
        self.assertNotIn("min(\n                            24", animation_source)
        self.assertNotIn("image_label.configure", animation_source)
        menu_source = inspect.getsource(
            self.tracker.TrackerApp._open_game_modes_page
        )
        self.assertIn("_create_game_mode_stage", menu_source)
        self.assertIn("symbol_panel.grid", menu_source)

    def test_game_mode_animation_assets_are_not_packaged(self):
        spec_text = (MODULE_PATH.parent / "SMWStreamTracker.spec").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(
            "('game_mode_assets', 'game_mode_assets')",
            spec_text,
        )

    def test_game_mode_launch_returns_to_the_dashboard(self):
        launch_source = inspect.getsource(
            self.tracker.TrackerApp._launch_game_mode_hack
        )
        random_source = inspect.getsource(
            self.tracker.TrackerApp._launch_filtered_random_main_hack
        )
        return_source = inspect.getsource(
            self.tracker.TrackerApp._return_game_modes_to_dashboard
        )
        self.assertIn("_return_game_modes_to_dashboard", launch_source)
        self.assertIn("_return_game_modes_to_dashboard", random_source)
        self.assertIn('page.page_key == "game_modes"', return_source)
        self.assertIn("page.request_close()", return_source)

    def test_game_mode_launch_guards_retroarch_speed_hotkey_handoff(self):
        launch_source = inspect.getsource(
            self.tracker.TrackerApp._launch_game_mode_hack
        )
        ladder_source = inspect.getsource(
            self.tracker.TrackerApp._open_difficulty_ladder
        )
        thread_source = inspect.getsource(
            self.tracker.TrackerApp._launch_catalog_game_thread
        )

        self.assertIn("_guard_retroarch_launch_input", launch_source)
        self.assertIn("_retroarch_force_fresh_process", ladder_source)
        self.assertIn("_wait_for_retroarch_launch_input_release", thread_source)
        self.assertIn('selected_platform == "RetroArch"', thread_source)

        button_source = inspect.getsource(
            self.tracker.OutlinedButton.__init__
        )
        self.assertIn("<KeyRelease-space>", button_source)
        self.assertNotIn('"<space>"', button_source)

    def test_new_game_mode_text_is_translated_in_every_language(self):
        phrases = (
            "SELECT A GAME MODE",
            "Rules",
            "Start Mode",
            "Select a mode on the left to preview its rules, then start it when you are ready.",
            "Game modes only use downloaded and patched hacks that are ready on your selected platform. Selecting a mode does not launch anything until you press Start Mode.",
            "Hack Draft",
            "Difficulty Ladder",
            "Creator Spotlight",
            "Time Capsule",
            "Hall of Fame Tour",
            "Hot Potato",
            "Deaths per turn",
            "Session goal",
            "Most exits",
            "One new exit per hack",
            "Rotate Now",
            "Hack Complete",
            "Stop Hot Potato",
            "Switch Game Mode",
            "You are currently playing {current_mode}. Stop it and start {new_mode}?",
            "Hack marked complete. It will not appear again.",
            "Every queued hack has been marked complete. Hot Potato complete!",
            "Death limit reached. Waiting for the current retry to finish safely...",
            "The retry is stable. Rotating to the next hack...",
            "The tracker must reconnect before Hot Potato can rotate safely.",
            "Ready-to-Play Hack",
            "Launch Selected Hack",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for phrase in phrases:
                with self.subTest(language=language, phrase=phrase):
                    self.assertIn(phrase, translations)
                    self.assertTrue(translations[phrase].strip())

    def test_duplicate_draft_labels_remain_selectable(self):
        games = [
            {"title": "Same Hack", "author": "Creator"},
            {"title": "Same Hack", "author": "Creator"},
        ]

        labels, mapped = (
            self.tracker.TrackerApp._game_mode_unique_labels(games)
        )

        self.assertEqual(len(labels), 2)
        self.assertEqual(len(mapped), 2)
        self.assertNotEqual(labels[0], labels[1])

    def test_hot_potato_counts_only_new_session_exits(self):
        queue = [
            {
                "_hot_potato_baseline_exits": 4,
                "_hot_potato_best_exits": 6,
            },
            {
                "_hot_potato_baseline_exits": 10,
                "_hot_potato_best_exits": 11,
            },
            {
                "_hot_potato_baseline_exits": None,
                "_hot_potato_best_exits": None,
            },
        ]

        total = self.tracker.TrackerApp._hot_potato_session_exits(queue)

        self.assertEqual(total, 3)

    def test_hot_potato_one_exit_goal_requires_every_hack(self):
        complete_queue = [
            {
                "_hot_potato_baseline_exits": 2,
                "_hot_potato_best_exits": 3,
            },
            {
                "_hot_potato_baseline_exits": 7,
                "_hot_potato_best_exits": 8,
            },
        ]
        incomplete_queue = [
            *complete_queue,
            {
                "_hot_potato_baseline_exits": 5,
                "_hot_potato_best_exits": 5,
            },
        ]

        self.assertTrue(
            self.tracker.TrackerApp._hot_potato_goal_is_complete(
                complete_queue
            )
        )
        self.assertFalse(
            self.tracker.TrackerApp._hot_potato_goal_is_complete(
                incomplete_queue
            )
        )

    def test_hot_potato_completed_hacks_are_skipped_permanently(self):
        queue = [
            {"title": "First", "_hot_potato_completed": False},
            {"title": "Retired", "_hot_potato_completed": True},
            {"title": "Third", "_hot_potato_completed": False},
        ]

        self.assertEqual(
            self.tracker.TrackerApp._hot_potato_next_unfinished_index(
                queue,
                0,
            ),
            2,
        )
        self.assertEqual(
            self.tracker.TrackerApp._hot_potato_next_unfinished_index(
                queue,
                2,
            ),
            0,
        )
        queue[0]["_hot_potato_completed"] = True
        queue[2]["_hot_potato_completed"] = True
        self.assertIsNone(
            self.tracker.TrackerApp._hot_potato_next_unfinished_index(
                queue,
                2,
            )
        )

    def test_hot_potato_runtime_controls_live_on_dashboard(self):
        control_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dashboard_control_definitions
        )
        status_source = inspect.getsource(
            self.tracker.TrackerApp._show_hot_potato_status
        )
        start_source = inspect.getsource(
            self.tracker.TrackerApp._start_hot_potato
        )
        complete_source = inspect.getsource(
            self.tracker.TrackerApp._complete_current_hot_potato_hack
        )
        rotate_source = inspect.getsource(
            self.tracker.TrackerApp._rotate_hot_potato
        )

        for label in ("Rotate Now", "Hack Complete", "Stop Hot Potato"):
            self.assertIn(f'"{label}"', control_source)
        self.assertIn("_rotate_hot_potato_now", control_source)
        self.assertIn("_complete_current_hot_potato_hack", control_source)
        self.assertIn("_request_stop_hot_potato", control_source)
        self.assertNotIn("_create_tracker_dialog", status_source)
        self.assertNotIn("_show_hot_potato_status", start_source)
        self.assertIn('current["_hot_potato_completed"] = True', complete_source)
        self.assertIn("_hot_potato_next_unfinished_index", rotate_source)

    def test_hot_potato_uses_confirmed_death_events(self):
        worker_source = inspect.getsource(
            self.tracker.TrackerWorker.record_death
        )
        event_source = inspect.getsource(
            self.tracker.TrackerApp.process_events
        )
        handler_source = inspect.getsource(
            self.tracker.TrackerApp._handle_hot_potato_death
        )
        readiness_source = inspect.getsource(
            self.tracker.TrackerWorker.update_hot_potato_rotation_readiness
        )

        self.assertIn('"death_recorded"', worker_source)
        self.assertIn('event_type == "death_recorded"', event_source)
        self.assertIn(
            'event_type == "hot_potato_rotation_ready"',
            event_source,
        )
        self.assertIn("hot_potato_death_limit", handler_source)
        self.assertIn("request_hot_potato_safe_rotation", handler_source)
        self.assertNotIn("1500", handler_source)
        self.assertIn('"hot_potato_rotation_ready"', readiness_source)
        self.assertIn("HOT_POTATO_ROTATION_STABLE_SAMPLES", readiness_source)

    def test_hot_potato_defaults_are_sized_for_hard_hacks(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._open_hot_potato
        )

        self.assertIn('(\"3\", \"4\", \"5\")', source)
        self.assertIn('(\"10\", \"25\", \"50\", \"100\")', source)
        self.assertIn('saved.get("death_limit", 50)', source)

    def test_catalog_launch_has_no_gauntlet_callback(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._finish_catalog_game_launch
        )

        self.assertNotIn("_finish_hack_gauntlet_launch", source)

    def test_gauntlet_is_not_part_of_default_configuration(self):
        self.assertNotIn(
            "hack_gauntlet_settings",
            self.tracker.DEFAULT_CONFIG,
        )


if __name__ == "__main__":
    unittest.main()
