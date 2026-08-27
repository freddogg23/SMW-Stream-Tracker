import importlib.util
import inspect
from pathlib import Path
import sys
import unittest
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_comments_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SmwCentralCommentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_hack_page_opens_at_the_real_comments_section(self):
        url = self.tracker._smwcentral_comments_url(
            "https://www.smwcentral.net/?p=section&a=details&id=9033"
        )
        self.assertEqual(
            url,
            (
                "https://www.smwcentral.net/"
                "?p=section&a=details&id=9033#comments"
            ),
        )

    def test_embedded_window_rejects_non_smwcentral_urls(self):
        for url in (
            "http://www.smwcentral.net/?p=login",
            "https://example.com/?p=login",
            "javascript:alert(1)",
            "",
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.tracker._validated_smwcentral_webview_url(url),
                    "",
                )

    def test_home_feed_links_allow_public_https_inside_the_app(self):
        external_url = "https://docs.google.com/forms/d/example/viewform"
        self.assertEqual(
            self.tracker._validated_smwcentral_home_link_url(external_url),
            external_url,
        )
        for unsafe_url in (
            "http://example.com/",
            "javascript:alert(1)",
            "https://user:password@example.com/private",
            "",
        ):
            with self.subTest(url=unsafe_url):
                self.assertEqual(
                    self.tracker._validated_smwcentral_home_link_url(
                        unsafe_url
                    ),
                    "",
                )

        command = self.tracker._smwcentral_webview_command(
            external_url,
            mode="feed_link",
        )
        parsed_url, _language, mode, _payload = (
            self.tracker._smwcentral_webview_values_from_arguments(command)
        )
        self.assertEqual(parsed_url, external_url)
        self.assertEqual(mode, "feed_link")

    def test_child_command_round_trips_review_submission(self):
        target = (
            "https://www.smwcentral.net/"
            "?p=section&a=details&id=9033#comments"
        )
        payload = {
            "target_url": target,
            "rating": 5,
            "comment": "Sehr gut!",
            "automatic_login": True,
        }
        command = self.tracker._smwcentral_webview_command(
            target,
            "de",
            mode="review",
            payload=payload,
        )
        parsed_url, language, mode, parsed_payload = (
            self.tracker._smwcentral_webview_values_from_arguments(command)
        )
        self.assertEqual(parsed_url, target)
        self.assertEqual(language, "de")
        self.assertEqual(mode, "review")
        self.assertEqual(parsed_payload, payload)

    def test_launch_home_is_a_native_page_with_a_hidden_live_feed(self):
        command = self.tracker._smwcentral_webview_command(
            self.tracker.SMW_CENTRAL_WEBSITE_URL,
            "fr",
            mode="home_feed",
        )
        parsed_url, language, mode, payload = (
            self.tracker._smwcentral_webview_values_from_arguments(command)
        )
        self.assertEqual(parsed_url, self.tracker.SMW_CENTRAL_WEBSITE_URL)
        self.assertEqual(language, "fr")
        self.assertEqual(mode, "home_feed")
        self.assertEqual(payload, {})

        javascript = self.tracker._smwcentral_home_feed_javascript()
        for selector in (
            "#calendar",
            "#recent-news",
            "#new-submissions",
            "#featured-submissions",
        ):
            self.assertIn(selector, javascript)
        runner_source = inspect.getsource(
            self.tracker._run_smwcentral_webview
        )
        self.assertIn('normalized_mode == "home_feed"', runner_source)
        self.assertIn('"hidden": normalized_mode == "home_feed"', runner_source)
        self.assertIn("_write_smwcentral_home_feed_cache", runner_source)
        self.assertIn("window.destroy()", runner_source)

        app_source = inspect.getsource(self.tracker.TrackerApp.__init__)
        self.assertNotIn("self.open_smwcentral_home", app_source)
        opener_source = inspect.getsource(
            self.tracker.TrackerApp.open_smwcentral_home
        )
        self.assertIn("self._open_in_app_page", opener_source)
        self.assertIn('home_text="Go to Dashboard"', opener_source)
        self.assertNotIn("self._open_smwcentral_webview", opener_source)
        refresh_source = inspect.getsource(
            self.tracker.TrackerApp._refresh_smwcentral_home_feed
        )
        self.assertIn('mode="home_feed"', refresh_source)

    def test_home_feed_validation_keeps_public_https_links(self):
        payload = {
            "fetched_at": "2026-08-16T02:30:00+00:00",
            "events": [],
            "news": [
                {
                    "title": "News",
                    "text": "A public update",
                    "url": "https://www.smwcentral.net/?p=news",
                    "image_url": "https://bin.smwcentral.net/u/1/a.png",
                    "links": [
                        {"label": "Official", "url": "https://smwc.me/1"},
                        {"label": "External", "url": "https://example.com/"},
                    ],
                }
            ],
            "latest_content": [],
            "content_of_day": [],
        }
        feed = self.tracker._normalized_smwcentral_home_feed(payload)
        self.assertEqual(feed["news"][0]["title"], "News")
        self.assertEqual(len(feed["news"][0]["links"]), 2)
        self.assertEqual(
            feed["news"][0]["image_url"],
            "https://bin.smwcentral.net/u/1/a.png",
        )

    def test_home_feed_plays_animated_gif_previews(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._queue_smwcentral_home_image
        )
        self.assertIn('getattr(source_image, "n_frames", 1)', source)
        self.assertIn("source_image.seek(frame_index)", source)
        self.assertIn("_smwc_home_photos", source)
        self.assertIn("advance_frame", source)
        self.assertIn("self.root.after", source)
        self.assertIn("frame.resize", source)

    def test_latest_and_daily_content_are_auto_rotating_carousels(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._render_smwcentral_home_feed
        )
        self.assertIn("carousel: bool = False", source)
        self.assertGreaterEqual(source.count("carousel=True"), 2)
        self.assertIn("_render_smwcentral_home_carousel_card", source)
        self.assertEqual(
            self.tracker.SMWC_HOME_CAROUSEL_INTERVAL_MS,
            7000,
        )
        self.assertIn("SMWC_HOME_CAROUSEL_INTERVAL_MS", source)
        self.assertIn("preview_ready", source)
        self.assertIn("on_ready=preview_ready", source)
        self.assertIn("_prefetch_smwcentral_home_images", source)
        self.assertIn('panel.bind("<Enter>"', source)
        self.assertIn('panel.bind("<Leave>"', source)
        self.assertIn("position_var", source)
        self.assertIn("selector_host", source)
        self.assertIn("selector_labels", source)
        self.assertIn('palette["selected"] if selected', source)
        self.assertIn("height=self._ui_px(470)", source)
        self.assertIn("layout_sections", source)
        self.assertIn("use_two_columns", source)
        self.assertNotIn("panel.configure(height=self._ui_px(720))", source)
        self.assertNotIn("cards.pack_propagate(False)", source)
        self.assertIn("carousel_host.grid_propagate(False)", source)
        self.assertIn("detail_host.pack_propagate(False)", source)
        self.assertIn("fit_description", source)
        self.assertIn("body.columnconfigure(text_column, weight=1)", source)
        self.assertNotIn("tk.Event[Any]", source)

        preview_source = inspect.getsource(
            self.tracker.TrackerApp._render_smwcentral_home_carousel_card
        )
        self.assertIn("(self._ui_px(340), self._ui_px(220))", preview_source)
        self.assertIn('bg=card_bg', preview_source)
        self.assertNotIn('bg="#151D2B"', preview_source)
        self.assertIn("image_slot.pack_propagate(False)", preview_source)
        self.assertIn("image_label.place", preview_source)
        self.assertIn('font=("Segoe UI", 17, "bold")', preview_source)
        self.assertIn('font=("Segoe UI", 12)', preview_source)
        self.assertIn("on_ready=on_ready", preview_source)
        self.assertNotIn("len(visible_links) >= 2", preview_source)

        self.assertIn("image_slot.grid_propagate(False)", source)

    def test_music_feed_items_open_the_compact_spc_player(self):
        music_item = {
            "title": "A music submission",
            "category": "SMW Music",
            "url": (
                "https://www.smwcentral.net/"
                "?p=section&a=details&id=42323"
            ),
            "links": [],
        }
        self.assertTrue(
            self.tracker._smwcentral_home_item_is_music(music_item)
        )
        self.assertFalse(
            self.tracker._smwcentral_home_item_is_music(
                {
                    **music_item,
                    "category": "SMW Hack",
                }
            )
        )

        command = self.tracker._smwcentral_webview_command(
            music_item["url"],
            "es",
            mode="spc_player",
        )
        parsed_url, language, mode, payload = (
            self.tracker._smwcentral_webview_values_from_arguments(command)
        )
        self.assertEqual(parsed_url, music_item["url"])
        self.assertEqual(language, "es")
        self.assertEqual(mode, "spc_player")
        self.assertEqual(payload, {})

        card_source = inspect.getsource(
            self.tracker.TrackerApp._render_smwcentral_home_carousel_card
        )
        opener_source = inspect.getsource(
            self.tracker.TrackerApp._open_smwcentral_music_player
        )
        webview_opener_source = inspect.getsource(
            self.tracker.TrackerApp._open_smwcentral_webview
        )
        webview_stop_source = inspect.getsource(
            self.tracker.TrackerApp._stop_smwcentral_webview_process
        )
        popup_source = inspect.getsource(
            self.tracker.TrackerApp._create_smwcentral_spc_popup_payload
        )
        player_javascript = (
            self.tracker._smwcentral_spc_player_javascript("de")
        )
        native_state_javascript = (
            self.tracker._smwcentral_native_spc_state_javascript()
        )
        native_command_javascript = (
            self.tracker._smwcentral_native_spc_command_javascript(
                {"action": "toggle", "id": "test"}
            )
        )
        loop_command_javascript = (
            self.tracker._smwcentral_native_spc_command_javascript(
                {"action": "loop", "value": True, "id": "loop-test"}
            )
        )
        seek_command_javascript = (
            self.tracker._smwcentral_native_spc_command_javascript(
                {"action": "seek", "value": 0.5, "id": "seek-test"}
            )
        )
        runner_source = inspect.getsource(
            self.tracker._run_smwcentral_webview
        )
        watcher_source = inspect.getsource(
            self.tracker.TrackerApp._watch_smwcentral_spc_player_process
        )
        native_player_source = inspect.getsource(
            self.tracker.TrackerApp._render_smwcentral_native_spc_player
        )
        native_player_draw_source = inspect.getsource(
            self.tracker.TrackerApp._draw_smwcentral_native_spc_player
        )
        native_player_toggle_source = inspect.getsource(
            self.tracker.TrackerApp._toggle_smwcentral_native_spc_player
        )
        native_player_update_source = inspect.getsource(
            self.tracker.TrackerApp._update_smwcentral_native_spc_player
        )
        native_player_begin_drag_source = inspect.getsource(
            self.tracker.TrackerApp._begin_smwcentral_native_spc_drag
        )
        native_player_move_drag_source = inspect.getsource(
            self.tracker.TrackerApp._move_smwcentral_native_spc_drag
        )
        native_player_apply_drag_source = inspect.getsource(
            self.tracker.TrackerApp._apply_smwcentral_native_spc_drag_position
        )
        native_player_finish_drag_source = inspect.getsource(
            self.tracker.TrackerApp._finish_smwcentral_native_spc_drag
        )
        native_window_source = inspect.getsource(
            self.tracker._configure_windows_spc_player_window
        )
        player_api_source = inspect.getsource(
            self.tracker._SpcPlayerWebviewApi
        )
        self.assertIn("play_tile = tk.Canvas", card_source)
        self.assertIn("draw_play_tile", card_source)
        self.assertIn("play_tile.place", card_source)
        self.assertIn("relx=0.5", card_source)
        self.assertIn("rely=0.5", card_source)
        self.assertIn('anchor="center"', card_source)
        self.assertNotIn("play_tile.lift", card_source)
        self.assertIn('text="▶"', card_source)
        self.assertIn('mode="spc_player"', opener_source)
        self.assertIn(
            "_create_smwcentral_spc_popup_payload",
            webview_opener_source,
        )
        self.assertIn(
            "_watch_smwcentral_spc_player_process",
            webview_opener_source,
        )
        self.assertIn("overlay_host = tk.Frame", popup_source)
        self.assertIn("Loading SPC Player", popup_source)
        self.assertIn("Retry SPC Player", watcher_source)
        self.assertIn("time.monotonic", watcher_source)
        self.assertIn("embed_parent_hwnd", popup_source)
        self.assertIn("embed_root_hwnd", popup_source)
        self.assertIn('"preload": bool(preload)', popup_source)
        self.assertIn('"native_panel": True', popup_source)
        self.assertIn('"player_state_path"', popup_source)
        self.assertIn('"player_command_path"', popup_source)
        self.assertIn("self._ui_px(460)", popup_source)
        self.assertIn("self._ui_px(220)", popup_source)
        self.assertIn("_render_smwcentral_native_spc_player", popup_source)
        self.assertIn("root_x + root_width", popup_source)
        self.assertIn("root_y + root_height", popup_source)
        self.assertIn("file-preview-button", player_javascript)
        self.assertIn("previewLaunched", player_javascript)
        self.assertIn("previewAttempts < 30", player_javascript)
        self.assertIn("const previewLoaded", player_javascript)
        self.assertLess(
            player_javascript.index("preview.dispatchEvent"),
            player_javascript.index("if (!player ||"),
        )
        self.assertIn("spc-player-interface", player_javascript)
        self.assertIn("spc-player-header", player_javascript)
        self.assertIn(
            "body > *:not(#spc-player-container):not(#spc-player-interface)",
            player_javascript,
        )
        self.assertIn("document.body.appendChild(player)", player_javascript)
        self.assertIn("spc-player-toggle", player_javascript)
        self.assertIn("spc-player-loop", player_javascript)
        self.assertIn("volume-slider", player_javascript)
        self.assertIn("track-info", player_javascript)
        self.assertIn("spc-player-interface", native_state_javascript)
        self.assertIn("track-time-elapsed", native_state_javascript)
        self.assertIn("engine_ready", native_state_javascript)
        self.assertIn("const trackReady", native_state_javascript)
        self.assertIn("const officialProgress", native_state_javascript)
        self.assertIn("matchAll", native_state_javascript)
        self.assertIn("can_skip", native_state_javascript)
        self.assertIn("can_restart", native_state_javascript)
        self.assertIn("can_loop", native_state_javascript)
        self.assertIn("__smwTrackerNativePlaybackClock", native_state_javascript)
        self.assertIn("const clockProgress", native_state_javascript)
        self.assertIn("formatPlayerTime", native_state_javascript)
        self.assertIn("const loopControl", native_state_javascript)
        self.assertIn("spc-player-up-next-link", native_state_javascript)
        self.assertIn("command.action", native_command_javascript)
        self.assertIn("volume-slider", native_command_javascript)
        self.assertIn("desiredLooping", loop_command_javascript)
        self.assertIn("checkbox.click()", loop_command_javascript)
        self.assertIn("checkbox.checked = desiredLooping", loop_command_javascript)
        self.assertIn(
            "new Event('change', { bubbles: true })",
            loop_command_javascript,
        )
        self.assertIn("action === 'seek'", seek_command_javascript)
        self.assertIn("getBoundingClientRect", seek_command_javascript)
        self.assertIn("new MouseEvent('mousemove'", seek_command_javascript)
        self.assertIn("new MouseEvent('mouseup'", seek_command_javascript)
        self.assertIn("commits a seek on mouseup", seek_command_javascript)
        self.assertIn("Object.defineProperty(event, 'offsetX'", seek_command_javascript)
        self.assertIn("clock.baseSeconds = duration * ratio", seek_command_javascript)
        self.assertNotIn("smw-tracker-owned-player", player_javascript)
        self.assertNotIn("smw-tracker-player-title", player_javascript)
        self.assertIn("close_spc_player", player_javascript)
        self.assertIn("background: transparent !important", player_javascript)
        self.assertIn("height: 100% !important", player_javascript)
        self.assertIn("smw-tracker-collapsed", player_javascript)
        self.assertIn("width: 100% !important", player_javascript)
        self.assertIn("border-radius: 12px !important", player_javascript)
        self.assertIn("fallback_script", runner_source)
        self.assertIn(
            "_smwcentral_custom_spc_player_javascript",
            runner_source,
        )
        self.assertIn("-webkit-line-clamp: 2", player_javascript)
        self.assertIn("MouseEvent", player_javascript)
        self.assertIn("event.stopImmediatePropagation()", player_javascript)
        self.assertIn("resize_embedded_spc_player", player_javascript)
        self.assertIn("targetHeight = trackerCollapsed ? 42 : 220", player_javascript)
        self.assertIn("begin_embedded_spc_player_drag", player_javascript)
        self.assertIn("move_embedded_spc_player_drag", player_javascript)
        self.assertIn("finish_embedded_spc_player_drag", player_javascript)
        self.assertIn("previousInstall?.running", player_javascript)
        self.assertIn("installState.running = false", player_javascript)
        self.assertIn('status.textContent = text.unavailable', player_javascript)
        self.assertIn('normalized_mode == "spc_player"', runner_source)
        self.assertIn("_smwcentral_spc_player_javascript", runner_source)
        self.assertIn("smwTrackerSpcReady", runner_source)
        self.assertIn("_configure_windows_spc_player_identity", runner_source)
        self.assertIn("_spc_player_popup_geometry", runner_source)
        self.assertIn("window.events.before_show", runner_source)
        self.assertIn("window.events.shown", runner_source)
        self.assertIn("_configure_windows_spc_player_window", runner_source)
        self.assertIn("attach_embedded_spc_player", runner_source)
        self.assertIn('"frameless": True', runner_source)
        self.assertIn('"on_top": not bool', runner_source)
        self.assertIn('"shadow": False', runner_source)
        self.assertNotIn('"transparent": True', runner_source)
        self.assertIn('window_options["transparent"] = True', runner_source)
        self.assertIn('"hidden": True', runner_source)
        self.assertIn('"focus": False', runner_source)
        self.assertIn("install_player_layer", runner_source)
        self.assertIn("start_player_watchdog", runner_source)
        self.assertIn("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", runner_source)
        self.assertIn("--autoplay-policy=no-user-gesture-required", runner_source)
        self.assertIn("--disable-background-timer-throttling", runner_source)
        self.assertIn("--disable-backgrounding-occluded-windows", runner_source)
        self.assertIn("--disable-renderer-backgrounding", runner_source)
        self.assertIn("player_watchdog_stop.wait(0.18)", runner_source)
        self.assertIn("native_panel_requested", runner_source)
        self.assertIn("sync_native_player_bridge", runner_source)
        self.assertIn('state["player_mode"]', runner_source)
        self.assertIn("_smwcentral_native_spc_state_javascript", runner_source)
        self.assertIn("_smwcentral_native_spc_command_javascript", runner_source)
        self.assertIn("_read_smwcentral_spc_state", watcher_source)
        self.assertIn("self.root.after(\n            180,", watcher_source)
        self.assertIn("_render_smwcentral_native_spc_player", watcher_source)
        self.assertIn("_update_smwcentral_native_spc_player", watcher_source)
        self.assertIn("canvas = tk.Canvas", native_player_source)
        self.assertIn(
            "_draw_smwcentral_native_spc_player",
            native_player_source,
        )
        self.assertIn('header = "#29271F"', native_player_draw_source)
        self.assertIn('background = "#29271F"', native_player_draw_source)
        self.assertIn('button = "#494640"', native_player_draw_source)
        self.assertIn('button_active = "#3F5A63"', native_player_draw_source)
        self.assertIn('progress_fill = "#16BC10"', native_player_draw_source)
        self.assertIn('volume_fill = "#2498D2"', native_player_draw_source)
        self.assertIn("button_size = px(34)", native_player_draw_source)
        self.assertIn("supersample = 4", native_player_draw_source)
        self.assertIn("render_supersample = 2", native_player_draw_source)
        self.assertIn("Image.Resampling.LANCZOS", native_player_draw_source)
        self.assertIn("hit_bounds", native_player_draw_source)
        control_box_source = native_player_draw_source.split(
            "def control_box", 1
        )[1]
        self.assertLess(
            control_box_source.index("coordinate_scale ="),
            control_box_source.index("surface_draw.rounded_rectangle"),
        )
        self.assertIn('player_mode == "radio"', native_player_draw_source)
        self.assertIn('player_mode == "song"', native_player_draw_source)
        self.assertIn(
            "can_skip, can_restart, can_loop = True, True, True",
            native_player_draw_source,
        )
        self.assertIn("can_skip", native_player_draw_source)
        self.assertIn("can_restart", native_player_draw_source)
        self.assertIn("can_loop", native_player_draw_source)
        self.assertIn('icon="restart"', native_player_draw_source)
        self.assertIn('icon="loop"', native_player_draw_source)
        self.assertIn('sync_glyph = "\\uE895"', native_player_draw_source)
        self.assertIn('"segmdl2.ttf"', native_player_draw_source)
        self.assertIn('"#B9E9F7" if active', native_player_draw_source)
        self.assertIn("ImageFilter.MaxFilter", native_player_draw_source)
        self.assertIn("thicken_radius", native_player_draw_source)
        self.assertIn('icon="skip"', native_player_draw_source)
        self.assertIn('"restart": "Replay Track"', native_player_draw_source)
        self.assertIn('"loop": "Toggle Looping"', native_player_draw_source)
        self.assertIn('outline="#8DD5EA" if active else None', native_player_draw_source)
        self.assertIn("marquee_surface = Image.new", native_player_draw_source)
        self.assertIn("marquee_started_at", native_player_draw_source)
        self.assertIn("compact_progress_left", native_player_draw_source)
        self.assertIn("compact_knob_x", native_player_draw_source)
        self.assertIn("progress_knob_x", native_player_draw_source)
        self.assertIn('regions["progress"]', native_player_draw_source)
        self.assertIn("local_point(16, 6)", native_player_draw_source)
        self.assertIn("local_point(8, 18)", native_player_draw_source)
        self.assertIn("self._ui_px(64)", native_player_toggle_source)
        self.assertIn("start_marquee", native_player_toggle_source)
        self.assertIn("current_title != previous_title", native_player_update_source)
        self.assertIn("pending_looping", native_player_source)
        self.assertIn("pending_looping", native_player_update_source)
        self.assertIn('"progress_drag": False', native_player_source)
        self.assertIn("set_progress_from_pointer", native_player_source)
        self.assertIn('"seek", seek_ratio', native_player_source)
        self.assertIn("pending_seek", native_player_update_source)
        self.assertIn('widgets.get("volume_drag")', native_player_update_source)
        self.assertIn('cursor_name = "fleur"', native_player_source)
        self.assertIn("winfo_width", native_player_begin_drag_source)
        self.assertNotIn("winfo_width", native_player_move_drag_source)
        self.assertIn('widgets["drag_pending_position"]', native_player_move_drag_source)
        self.assertIn("self.root.after(\n                    8,", native_player_move_drag_source)
        self.assertIn("place_configure", native_player_apply_drag_source)
        self.assertIn("_apply_smwcentral_native_spc_drag_position", native_player_finish_drag_source)
        self.assertIn("redraw_after_drag", native_player_update_source)
        self.assertNotIn("draw_play_pause(", native_player_draw_source)
        self.assertNotIn("draw_restart(", native_player_draw_source)
        self.assertNotIn("draw_loop(", native_player_draw_source)
        self.assertNotIn("draw_skip(", native_player_draw_source)
        self.assertIn('"SPC Player"', native_player_draw_source)
        self.assertIn("_retain_smooth_canvas_photo", native_player_draw_source)
        self.assertIn('environment.pop("PYINSTALLER_RESET_ENVIRONMENT"', webview_opener_source)
        self.assertNotIn('variable_name.startswith("_PYI_")', webview_opener_source)
        self.assertIn("window.events.before_load", runner_source)
        self.assertIn("window.events.closed", runner_source)
        self.assertIn("SMWCentralPlayerLayerWatchdog", runner_source)
        self.assertIn("window.hide()", runner_source)
        self.assertIn("window.show()", runner_source)
        self.assertIn("window.evaluate_js(player_script)", runner_source)
        self.assertIn('"js_api": spc_api', runner_source)
        self.assertIn("38 if spc_api and spc_api.is_embedded else 220", runner_source)
        self.assertIn('"resizable": not bool', runner_source)
        self.assertIn('"easy_drag": False', runner_source)
        self.assertIn("ShowInTaskbar = True", native_window_source)
        self.assertIn("SetWindowPos", native_window_source)
        self.assertIn("SetWindowPos", player_api_source)
        self.assertIn("attach_embedded_spc_player", player_api_source)
        self.assertIn("IsWindowVisible", player_api_source)
        self.assertIn("BringWindowToTop", player_api_source)
        self.assertIn("GetAncestor", player_api_source)
        self.assertIn("resize_embedded_spc_player", player_api_source)
        self.assertIn("ScreenToClient", player_api_source)
        self.assertIn("GWLP_HWNDPARENT", player_api_source)
        self.assertIn("self._window", player_api_source)
        self.assertNotIn("self.window", player_api_source)
        self.assertIn("GetDpiForWindow", player_api_source)
        self.assertIn("self._window.show()", player_api_source)
        self.assertIn("SPC player panel attachment failed", player_api_source)
        self.assertIn("SPC player visible fallback failed", runner_source)
        self.assertGreaterEqual(
            runner_source.count("_configure_windows_spc_player_window"),
            2,
        )
        self.assertIn("SWP_NOSIZE", player_api_source)
        self.assertIn("HWND_TOPMOST", native_window_source)
        self.assertIn("CreateRoundRectRgn", native_window_source)
        self.assertIn("SetWindowRgn", native_window_source)
        self.assertIn("GetDpiForWindow", native_window_source)
        self.assertIn("dpi_scale", native_window_source)
        self.assertIn("_windows_monitor_work_area_for_point", native_window_source)
        self.assertIn('"taskkill"', webview_stop_source)
        self.assertIn('"/T"', webview_stop_source)
        self.assertIn("shutil.rmtree", webview_stop_source)
        self.assertIn('SMWC_WEBVIEW_STORAGE_DIR / "SPCPlayerCache"', runner_source)
        self.assertIn("preload_requested", runner_source)
        self.assertIn("radio_activation_requested", runner_source)
        self.assertIn("activate_now", runner_source)

        class FakeWindow:
            def __init__(self):
                self.minimized = False
                self.resized_to = None
                self.resize_fix_point = None
                self.moved_to = None

            def minimize(self):
                self.minimized = True

            def resize(self, width, height, fix_point=None):
                self.resized_to = (width, height)
                self.resize_fix_point = fix_point

            def move(self, x, y):
                self.moved_to = (x, y)

        fake_window = FakeWindow()
        api = self.tracker._SpcPlayerWebviewApi()
        api._window = fake_window
        self.assertTrue(api.minimize_spc_player())
        self.assertTrue(fake_window.minimized)
        with mock.patch.object(
            self.tracker,
            "_configure_windows_spc_player_window",
            return_value=True,
        ):
            self.assertTrue(api.resize_spc_player(900, 500))
        self.assertEqual(fake_window.resized_to, (900, 500))
        with mock.patch.object(
            self.tracker,
            "_configure_windows_spc_player_window",
            return_value=True,
        ):
            self.assertTrue(
                api.resize_spc_player_from_top_left(760, 320)
            )
        self.assertEqual(fake_window.resized_to, (760, 320))
        self.assertIsNotNone(fake_window.resize_fix_point)
        self.assertTrue(api.resize_spc_player_from_edges(700, 300, "sw"))
        self.assertEqual(fake_window.resized_to, (700, 300))
        self.assertIsNotNone(fake_window.resize_fix_point)
        self.assertTrue(api.move_spc_player(125, 80))
        self.assertEqual(fake_window.moved_to, (125, 80))

        width, height, x, y = self.tracker._spc_player_popup_geometry()
        self.assertEqual((width, height), (400, 220))
        if self.tracker.IS_WINDOWS:
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
        with mock.patch.object(
            self.tracker,
            "_windows_monitor_work_area_for_point",
            return_value=(0, 0, 1920, 1040),
        ):
            self.assertEqual(
                self.tracker._spc_player_popup_geometry(
                    {
                        "embed_width": 820,
                        "embed_height": 420,
                        "popup_x": 1590,
                        "popup_y": 860,
                    }
                ),
                (400, 220, 1504, 804),
            )

    def test_smwcentral_radio_and_updates_are_available_from_the_top_menu(self):
        command = self.tracker._smwcentral_webview_command(
            "https://www.smwcentral.net/?p=section&s=smwmusic",
            "fr",
            mode="radio",
        )
        parsed_url, language, mode, payload = (
            self.tracker._smwcentral_webview_values_from_arguments(command)
        )
        self.assertIn("s=smwmusic", parsed_url)
        self.assertEqual(language, "fr")
        self.assertEqual(mode, "radio")
        self.assertEqual(payload, {})
        opener_source = inspect.getsource(
            self.tracker.TrackerApp._open_smwcentral_radio
        )
        webview_opener_source = inspect.getsource(
            self.tracker.TrackerApp._open_smwcentral_webview
        )
        home_source = inspect.getsource(
            self.tracker.TrackerApp.open_smwcentral_home
        )
        dashboard_source = inspect.getsource(
            self.tracker.TrackerApp._build_ui
        )
        menu_source = inspect.getsource(
            self.tracker.TrackerApp._build_menu_bar
        )
        runner_source = inspect.getsource(
            self.tracker._run_smwcentral_webview
        )
        radio_javascript = self.tracker._smwcentral_radio_javascript()
        self.assertIn('mode="radio"', opener_source)
        self.assertNotIn('"SMW Central Radio"', home_source)
        self.assertNotIn('"SMW Central Radio"', dashboard_source)
        self.assertNotIn('"SMW Central Updates"', dashboard_source)
        self.assertNotIn('"SMW Central Radio"', menu_source)
        self.assertIn('"SMW Central Updates"', menu_source)
        self.assertIn("self.open_smwcentral_home", menu_source)
        self.assertIn(
            "_create_smwcentral_spc_popup_payload",
            webview_opener_source,
        )
        self.assertIn('normalized_mode == "radio"', runner_source)
        self.assertIn("_smwcentral_radio_javascript", runner_source)
        self.assertIn("_smwcentral_spc_player_javascript", runner_source)
        radio_player = self.tracker._smwcentral_spc_player_javascript(
            "fr", launch_preview=False
        )
        self.assertIn("spc-player-interface", radio_player)
        self.assertIn("const launchPreview = false", radio_player)
        self.assertNotIn("smw-tracker-owned-player", radio_player)
        self.assertIn("smwTrackerRadioActivated", radio_javascript)
        self.assertIn('data-spc-radio="enable-button"', radio_javascript)
        self.assertIn("spc-radio-enabled", radio_javascript)
        self.assertIn("#spc-player-interface.shown", radio_javascript)
        self.assertIn("radio.click()", radio_javascript)
        self.assertIn("isVisible", radio_javascript)
        self.assertIn("/(^|\\s)radio(\\s|$)/i", radio_javascript)
        self.assertNotIn("sessionStorage", radio_javascript)

    def test_home_feed_links_are_all_kept_and_open_inside_the_app(self):
        normalizer_source = inspect.getsource(
            self.tracker._normalized_smwcentral_home_feed
        )
        javascript = self.tracker._smwcentral_home_feed_javascript()
        renderer_source = inspect.getsource(
            self.tracker.TrackerApp._render_smwcentral_home_feed
        )
        opener_source = inspect.getsource(
            self.tracker.TrackerApp._open_smwcentral_home_link
        )
        self.assertIn('"links": links[:8]', normalizer_source)
        self.assertIn("plainUrls", javascript)
        self.assertIn("/https:\\/\\/[^", javascript)
        self.assertNotIn("len(visible_links) >= 2", renderer_source)
        self.assertIn("self._open_smwcentral_webview", opener_source)
        self.assertIn('mode="feed_link"', opener_source)

    def test_home_feed_preview_downloads_are_shared(self):
        loader_source = inspect.getsource(
            self.tracker.TrackerApp._load_smwcentral_home_image_bytes
        )
        prefetch_source = inspect.getsource(
            self.tracker.TrackerApp._prefetch_smwcentral_home_images
        )
        self.assertIn("_smwc_home_asset_byte_cache", inspect.getsource(
            self.tracker.TrackerApp._ensure_smwcentral_home_image_cache
        ))
        self.assertIn("in_flight", loader_source)
        self.assertIn("fetch_event.wait", loader_source)
        self.assertIn("SMWCentralHomeImagePrefetch", prefetch_source)

    def test_webview_persists_only_the_sites_own_session(self):
        source = inspect.getsource(self.tracker._run_smwcentral_webview)
        self.assertIn('"private_mode": (', source)
        self.assertIn('"storage_path": str(storage_path)', source)
        self.assertIn('SMWC_WEBVIEW_STORAGE_DIR / "SPCPlayerCache"', source)
        self.assertNotIn('storage_session_token', source)
        self.assertNotIn("get_cookies", source)
        self.assertIn('"js_api": spc_api', source)

    def test_login_window_closes_after_the_site_reports_a_login(self):
        source = inspect.getsource(self.tracker._run_smwcentral_webview)
        self.assertIn('normalized_mode == "login"', source)
        self.assertIn("window.destroy()", source)
        self.assertIn("window.events.loaded += loaded_handler", source)

    def test_automatic_login_controls_session_reuse(self):
        account_source = inspect.getsource(
            self.tracker.TrackerApp.open_smwcentral_account
        )
        webview_source = inspect.getsource(
            self.tracker._run_smwcentral_webview
        )
        self.assertIn("self.smwc_automatic_login_var.get()", account_source)
        self.assertIn('normalized_mode in {"login", "review"}', webview_source)
        self.assertIn("and not automatic_login", webview_source)

    def test_smwcentral_rating_requires_a_whole_number_from_one_to_five(self):
        expected_ratings = {1: 1, 2.0: 2, "3": 3, 4: 4, 5.0: 5}
        for rating, expected in expected_ratings.items():
            with self.subTest(rating=rating):
                self.assertEqual(
                    self.tracker._smwcentral_submission_rating(rating),
                    expected,
                )
        for rating in (
            0,
            6,
            4.5,
            "nope",
            None,
            float("nan"),
            float("inf"),
        ):
            with self.subTest(rating=rating):
                with self.assertRaises(ValueError):
                    self.tracker._smwcentral_submission_rating(rating)

    def test_review_prefills_but_never_submits_for_the_user(self):
        javascript = self.tracker._smwcentral_prefill_javascript(
            5,
            "A thoughtful public comment.",
            "en",
        )
        self.assertIn("A thoughtful public comment.", javascript)
        self.assertIn('"ratingValue": 5', javascript)
        self.assertIn("textarea", javascript)
        self.assertNotIn(".requestSubmit(", javascript)
        self.assertNotIn(".submit(", javascript)
        self.assertNotIn(".click(", javascript)

    def test_all_hack_page_actions_use_the_embedded_comment_window(self):
        for method_name in (
            "_open_selected_tracker_page",
            "_open_selected_library_page",
            "open_current_hack_page",
        ):
            with self.subTest(method=method_name):
                source = inspect.getsource(
                    getattr(self.tracker.TrackerApp, method_name)
                )
                self.assertIn("open_smwcentral_comments", source)
                self.assertNotIn("webbrowser.open_new_tab", source)

    def test_every_language_has_an_account_window_title(self):
        for mode in ("browse", "login", "review", "spc_player"):
            with self.subTest(mode=mode):
                titles = {
                    language: self.tracker._smwcentral_window_title(
                        language,
                        mode,
                    )
                    for language in ("en", "au", "es", "fr", "de", "pt-BR")
                }
                self.assertEqual(len(set(titles.values())), len(titles))
                self.assertIn("mate", titles["au"].casefold())

    def test_every_language_has_review_instructions(self):
        instructions = {
            language: self.tracker._smwcentral_review_texts(language)
            for language in ("en", "au", "es", "fr", "de", "pt-BR")
        }
        for language, text in instructions.items():
            with self.subTest(language=language):
                self.assertTrue(text["heading"])
                self.assertTrue(text["ready"])
                self.assertTrue(text["partial"])
                self.assertTrue(text["rating"])
                self.assertTrue(text["comment"])
        self.assertIn("mate", instructions["au"]["heading"].casefold())

    def test_complete_hack_page_contains_public_submission_controls(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.complete_in_spreadsheet
        )
        self.assertIn(
            'self._open_in_app_page(\n            "complete_hack"',
            source,
        )
        self.assertNotIn("tk.Toplevel", source)
        self.assertNotIn("self.root.wait_window", source)
        self.assertIn("SMW Central comment (optional):", source)
        self.assertIn("Post my rating and comment to SMW Central", source)
        self.assertIn("Automatically reuse my SMW Central login", source)
        self.assertIn("pending_smwcentral_completion", source)
        self.assertIn('uniform="complete_hack_fields"', source)
        self.assertIn('uniform="complete_hack_actions"', source)
        self.assertIn("rating_panel = tk.Frame", source)
        self.assertIn("submission_panel = tk.Frame", source)
        self.assertIn("personal_rating_var = tk.StringVar()", source)
        self.assertIn("smwc_rating_var = tk.StringVar()", source)
        self.assertIn(
            '"Personal Rating (1-5, decimals allowed):"',
            source,
        )
        self.assertIn(
            '"SMW Central Rating (1-5, no decimals allowed):"',
            source,
        )
        self.assertIn(
            "_smwcentral_submission_rating(\n"
            "                        smwc_rating_var.get().strip()",
            source,
        )
        self.assertNotIn("quick_rating", source)
        self.assertNotIn("rating_preview", source)

    def test_saved_completion_opens_smwcentral_review(self):
        source = inspect.getsource(self.tracker.TrackerApp.process_events)
        self.assertIn("open_smwcentral_completion_review", source)

    def test_dedicated_smwcentral_menu_and_login_preference_dialog(self):
        source = inspect.getsource(self.tracker.TrackerApp._build_menu_bar)
        account_source = inspect.getsource(
            self.tracker.TrackerApp.open_smwcentral_account
        )
        self.assertIn('create_menu_button(\n                "SMW Central"', source)
        self.assertIn("SMW Central Updates", source)
        self.assertNotIn("SMW Central Radio", source)
        self.assertIn("Log In to SMW Central...", source)
        self.assertIn("Visit SMW Central", source)
        self.assertNotIn("Automatic SMW Central Login", source)
        self.assertIn("Automatic SMW Central Login", account_source)
        self.assertIn("automatic_login_var", account_source)
        self.assertIn("self._save_smwcentral_login_preference()", account_source)


if __name__ == "__main__":
    unittest.main()
