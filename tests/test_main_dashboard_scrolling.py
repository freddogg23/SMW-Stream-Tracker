import ast
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class MainDashboardScrollingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    @classmethod
    def method_source(cls, name):
        method = next(
            node
            for node in ast.walk(cls.tree)
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
        return ast.get_source_segment(cls.source, method)

    def test_main_dashboard_uses_a_canvas_viewport_and_scrollbar(self):
        build_source = self.method_source("_build_ui")
        self.assertIn("self.main_canvas = tk.Canvas", build_source)
        self.assertIn("self.main_canvas.create_window", build_source)
        self.assertIn("self.main_scrollbar = YellowCanvasScrollbar", build_source)
        self.assertIn("yscrollcommand=self.main_scrollbar.set", build_source)

    def test_dashboard_scrollbar_only_appears_when_content_is_taller(self):
        layout_source = self.method_source("_sync_main_canvas_layout")
        self.assertIn("requested_height > viewport_height", layout_source)
        self.assertIn("scrollbar.grid()", layout_source)
        self.assertIn("scrollbar.grid_remove()", layout_source)
        self.assertIn("canvas.yview_moveto(0.0)", layout_source)

    def test_window_moves_postpone_a_pending_responsive_rebuild(self):
        responsive_source = self.method_source("_queue_responsive_ui_scale")
        quiet_source = self.method_source(
            "_apply_responsive_ui_scale_when_quiet"
        )
        self.assertIn("_last_root_configure_size", responsive_source)
        self.assertIn("configured_size == self._last_root_configure_size", responsive_source)
        self.assertIn("if self.responsive_ui_after_id is None", responsive_source)
        self.assertIn("_last_root_configure_at = time.monotonic()", responsive_source)
        self.assertIn("_apply_responsive_ui_scale_when_quiet", responsive_source)
        self.assertIn("if self.responsive_ui_after_id is not None", responsive_source)
        self.assertIn("remaining_seconds = 0.65 - quiet_seconds", quiet_source)

    def test_full_size_dialog_destroy_callback_accepts_missing_event(self):
        source = self.method_source("_activate_full_size_dialog_ui")
        self.assertIn("lambda event=None, tracked=dialog", source)
        self.assertIn('getattr(event, "widget", None) is tracked', source)

    def test_small_cross_monitor_scale_changes_do_not_rebuild(self):
        responsive_source = self.method_source("_apply_responsive_ui_scale")
        self.assertIn(
            "abs(target_scale - self.main_ui_scale) < 0.11",
            responsive_source,
        )

    def test_responsive_scale_uses_pixel_friendly_quarter_steps(self):
        scale_source = self.method_source("_target_main_ui_scale")
        self.assertIn("pixel_friendly_scales", scale_source)
        for expected_scale in (
            "0.75",
            "1.0",
            "1.25",
            "1.5",
            "1.75",
            "2.0",
        ):
            self.assertIn(expected_scale, scale_source)
        self.assertNotIn("round(target * 20) / 20", scale_source)

    def test_scaled_layout_dimensions_snap_half_up_to_pixels(self):
        pixel_source = self.method_source("_ui_px")
        self.assertIn(
            "int(float(value) * self.main_ui_scale + 0.5)",
            pixel_source,
        )

    def test_all_tk_font_fallbacks_use_antialiased_truetype_families(self):
        font_source = self.method_source("_configure_antialiased_text")
        self.assertIn("self._configure_antialiased_text()", self.source)
        for font_name in (
            "TkDefaultFont",
            "TkTextFont",
            "TkMenuFont",
            "TkHeadingFont",
            "TkFixedFont",
        ):
            self.assertIn(font_name, font_source)
        self.assertIn('"Segoe UI"', font_source)
        self.assertIn('"Consolas"', font_source)
        self.assertIn('ttk.Style(self.root).configure', font_source)

    def test_custom_text_outline_preserves_antialiased_glyph_edges(self):
        helper_source = self.method_source("create_outlined_canvas_text")
        self.assertIn("ANTIALIASED_TEXT_OUTLINE_OFFSETS", helper_source)
        self.assertGreaterEqual(
            self.source.count("ANTIALIASED_TEXT_OUTLINE_OFFSETS"),
            4,
        )
        self.assertNotIn("(-1, -1)", self.source)

    def test_responsive_rebuild_is_themed_before_it_is_mapped(self):
        responsive_source = self.method_source("_apply_responsive_ui_scale")
        build_source = self.method_source("_build_ui")
        self.assertIn("_build_ui(defer_mapping=True)", responsive_source)
        self.assertIn("if defer_mapping:", build_source)
        self.assertLess(
            build_source.index("self._set_appearance("),
            build_source.index("self.custom_menu_bar.pack("),
        )
        self.assertIn(
            "refresh_native_titlebar=not defer_mapping",
            build_source,
        )

    def test_tracker_canvas_does_not_receive_duplicate_floating_grid(self):
        installer_source = self.method_source("_install_treeview_cell_grid")
        self.assertIn('"MyTracker.Treeview"', installer_source)
        self.assertIn("_smw_cell_grid_uses_tracker_canvas", installer_source)
        overlay_source = self.method_source("_draw_tracker_cell_overlay")
        self.assertIn("outline=border_color", overlay_source)

    def test_shared_grid_debounces_dividers_while_scrolling(self):
        installer_source = self.method_source("_install_treeview_cell_grid")
        scheduler_source = self.method_source("_schedule_treeview_cell_grid")
        self.assertIn("hide_lines", installer_source)
        self.assertIn("restart=True", installer_source)
        self.assertIn("tree.after_cancel", scheduler_source)

    def test_tracker_rows_stay_covered_until_cell_canvas_is_ready(self):
        refresh_source = self.method_source("_refresh_my_tracker")
        render_source = self.method_source("_render_tracker_cell_overlays")
        self.assertIn("self._show_tracker_paint_cover()", refresh_source)
        self.assertIn("self._hide_tracker_paint_cover()", render_source)
        self.assertIn("tracker_overlay_retry_count", render_source)

    def test_tracker_initial_paint_uses_one_in_memory_catalog_merge(self):
        refresh_source = self.method_source("_refresh_my_tracker")
        open_source = self.method_source("open_my_tracker")
        page_source = self.method_source("_open_in_app_page")
        self.assertIn("record = dict(tracked_record)", refresh_source)
        self.assertNotIn("self._resolved_hack_details_record(", refresh_source)
        self.assertIn("apply_generic_appearance=False", open_source)
        self.assertIn('"my_tracker"', page_source)

    def test_tracker_canvas_redraw_is_debounced_during_resize(self):
        scheduler_source = self.method_source(
            "_schedule_tracker_cell_overlays"
        )
        self.assertIn("configure_event", scheduler_source)
        self.assertIn("root.after_cancel", scheduler_source)
        self.assertIn("110 if configure_event else 16", scheduler_source)

    def test_brand_artwork_is_cached_for_each_responsive_scale(self):
        loader_source = self.method_source("_load_brand_assets")
        self.assertIn("brand_asset_cache.get(scale_key)", loader_source)
        self.assertIn("self.brand_asset_cache[scale_key]", loader_source)
        self.assertIn("self._set_tracking_icon", loader_source)

    def test_completed_banner_sizes_are_reused_without_rendering(self):
        build_source = self.method_source("_build_ui")
        render_source = self.method_source("_render_responsive_banner")
        restore_source = self.method_source("_restore_cached_banner_photo")
        self.assertIn("allow_fallback=True", build_source)
        self.assertIn("_restore_cached_banner_photo(requested_size)", render_source)
        self.assertIn("banner_photo_cache.get", restore_source)

    def test_dashboard_cards_are_content_sized_stacked_and_full_width(self):
        dashboard_source = self.method_source("_build_stream_desk_dashboard")
        self.assertIn("dashboard_density = 0.97", dashboard_source)
        self.assertIn("def dashboard_px", dashboard_source)
        self.assertIn('body.pack(fill="x", expand=False)', dashboard_source)
        self.assertIn('sticky="ew"', dashboard_source)
        self.assertIn("visible_body_width", dashboard_source)
        self.assertIn("root_width", dashboard_source)
        self.assertNotIn("GetDpiForWindow", dashboard_source)
        self.assertNotIn("stack_breakpoint", dashboard_source)
        self.assertNotIn("stack_panels", dashboard_source)
        self.assertIn("run_width = available_width", dashboard_source)
        self.assertIn("queue_width = available_width", dashboard_source)
        self.assertIn("columnspan=2", dashboard_source)
        self.assertIn("row=1", dashboard_source)
        self.assertIn('getattr(self, "main_canvas", None)', dashboard_source)
        self.assertIn("run_action_columns", dashboard_source)
        self.assertIn("queue_action_columns", dashboard_source)
        self.assertIn(
            "self.stream_dashboard_resize_callback = resize_dashboard_panels",
            dashboard_source,
        )
        self.assertIn("dashboard_root_bind_id", dashboard_source)
        self.assertIn("release_dashboard_root_binding", dashboard_source)
        self.assertNotIn(
            'body.rowconfigure(0, weight=1, minsize=self._ui_px(300))',
            dashboard_source,
        )

    def test_dashboard_icon_uses_the_asymmetric_reference_tiles(self):
        icon_source = self.method_source("_draw_stream_desk_icon")
        for tile in (
            "(8, 8, 22, 27)",
            "(28, 8, 41, 20)",
            "(8, 32, 22, 41)",
            "(28, 25, 41, 41)",
        ):
            self.assertIn(tile, icon_source)

    def test_every_app_scrollbar_uses_the_yellow_canvas_component(self):
        self.assertNotIn("ttk.Scrollbar(", self.source)
        self.assertNotIn("tk.Scrollbar(", self.source)
        self.assertGreaterEqual(
            self.source.count("YellowCanvasScrollbar("),
            20,
        )

    def test_timeline_markers_are_supersampled_and_cached(self):
        marker_source = self.method_source("_timeline_marker_photo")
        refresh_source = self.method_source("_refresh_session_timeline")
        self.assertIn("supersample = 4", marker_source)
        self.assertIn("Image.Resampling.LANCZOS", marker_source)
        self.assertIn("_timeline_marker_photo_cache", marker_source)
        self.assertIn("self._timeline_marker_photo(", refresh_source)
        self.assertIn("canvas.create_image(", refresh_source)
        self.assertIn("canvas._timeline_marker_images", refresh_source)

    def test_canvas_layout_refreshes_the_dashboard_breakpoint(self):
        layout_source = self.method_source("_sync_main_canvas_layout")
        self.assertIn("stream_dashboard_resize_callback", layout_source)
        self.assertIn("if callable(dashboard_resize)", layout_source)
        self.assertIn("dashboard_resize()", layout_source)


if __name__ == "__main__":
    unittest.main()
