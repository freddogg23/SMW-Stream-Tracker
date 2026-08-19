import ast
from pathlib import Path
import unittest


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


class DownloaderResponsiveOpenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source)
        tracker = next(
            node
            for node in cls.module.body
            if isinstance(node, ast.ClassDef) and node.name == "TrackerApp"
        )
        cls.methods = {
            node.name: node
            for node in tracker.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def method_source(self, name):
        return ast.get_source_segment(self.source, self.methods[name])

    def test_library_inventory_runs_on_a_daemon_worker(self):
        source = self.method_source("_start_downloader_inventory_scan")
        self.assertIn("rom_builder_scan_existing_roms(", source)
        self.assertIn("rom_builder_load_index_inventory_fast(", source)
        self.assertIn("if deep_scan or not existing_paths:", source)
        self.assertIn("threading.Thread(", source)
        self.assertIn('name="SMWTrackerLibraryInventory"', source)
        self.assertIn("daemon=True", source)
        self.assertIn("self.root.after(0, finish)", source)

    def test_initial_inventory_prefers_the_written_library_index(self):
        source = self.method_source("_refresh_downloader_preview")
        call = source.index("self._start_downloader_inventory_scan(")
        scan_call = source[call : source.index(")", call) + 1]
        self.assertIn("deep_scan=force_library_scan", scan_call)

    def test_preview_returns_while_uncached_inventory_is_loading(self):
        source = self.method_source("_refresh_downloader_preview")
        call = source.index("self._start_downloader_inventory_scan(")
        return_after_call = source.index("return", call)
        self.assertGreater(return_after_call, call)
        self.assertNotIn("rom_builder_scan_existing_roms(", source)

    def test_loading_state_disables_download_until_inventory_finishes(self):
        source = self.method_source("_start_downloader_inventory_scan")
        self.assertIn('primary_button.configure(state="disabled")', source)
        self.assertIn('progress.configure(mode="indeterminate")', source)
        self.assertIn('current_progress.configure(mode="determinate", value=0)', source)
        self.assertIn("self._refresh_downloader_preview()", source)

    def test_catalog_preparation_runs_on_a_daemon_worker(self):
        source = self.method_source("_start_downloader_preview_build")
        self.assertIn("for catalog_entry in current_metadata", source)
        self.assertIn("threading.Thread(", source)
        self.assertIn('name="SMWTrackerDownloaderPreview"', source)
        self.assertIn("daemon=True", source)
        self.assertIn("self.root.after(0, finish)", source)

    def test_preview_returns_while_catalog_preparation_is_loading(self):
        source = self.method_source("_refresh_downloader_preview")
        call = source.index("self._start_downloader_preview_build(")
        return_after_call = source.index("return", call)
        self.assertGreater(return_after_call, call)
        self.assertIn('prepared_preview.get("filtered", ())', source)

    def test_large_initial_catalog_is_inserted_in_event_loop_chunks(self):
        source = self.method_source("_refresh_downloader_preview")
        self.assertIn("if len(new_rows) > 240:", source)
        self.assertIn("chunk_size = 256", source)
        self.assertIn("chunk_budget_seconds = 0.012", source)
        self.assertIn("time.perf_counter() >= chunk_deadline", source)
        self.assertIn("tree.after(4, insert_next_chunk)", source)
        self.assertIn('widgets["row_population_active"]', source)
        self.assertIn('tree.configure(**{scroll_option: ""})', source)
        self.assertIn("restore_population_scroll_commands()", source)

    def test_downloader_materializes_only_an_initial_window_of_rows(self):
        source = self.method_source("_refresh_downloader_preview")
        self.assertIn('widgets["virtual_row_limit"] = 96', source)
        self.assertIn('widgets["virtual_row_total"] = virtual_total', source)
        self.assertIn('display_games = display_games[:virtual_limit]', source)
        self.assertIn(
            'widgets["virtual_has_more"] = virtual_limit < virtual_total',
            source,
        )
        self.assertLess(
            source.index('display_games = display_games[:virtual_limit]'),
            source.index("for row_index, display_game in enumerate(display_games)"),
        )

    def test_scrolling_extends_the_materialized_row_window(self):
        source = self.method_source("open_hack_downloader")
        self.assertIn("near_bottom = float(last) >= 0.92", source)
        self.assertIn('widgets["virtual_expand_pending"] = True', source)
        self.assertIn("current_limit + page_size", source)
        self.assertIn("tree.after_idle(expand_visible_rows)", source)

    def test_prepared_preview_is_reused_after_reopening_page(self):
        open_source = self.method_source("open_hack_downloader")
        build_source = self.method_source("_start_downloader_preview_build")
        self.assertIn('"_downloader_prepared_preview_cache"', open_source)
        self.assertIn(
            "self._downloader_prepared_preview_cache = prepared",
            build_source,
        )

    def test_page_sizing_cannot_trigger_preview_work_synchronously(self):
        source = self.method_source("open_hack_downloader")
        fit_call = source.index("self._fit_dialog_height_to_contents(")
        refresh_schedule = source.index(
            "dialog.after(40, self._refresh_downloader_preview)"
        )
        self.assertGreater(refresh_schedule, fit_call)
        self.assertNotIn(
            "dialog.after_idle(self._refresh_downloader_preview)",
            source,
        )

    def test_initial_population_does_not_retag_every_catalog_row(self):
        source = self.method_source("_refresh_downloader_preview")
        self.assertNotIn(
            "self._retag_treeview_alternating(\n            tree,",
            source,
        )

    def test_downloader_skips_redundant_recursive_restyle(self):
        source = self.method_source("open_hack_downloader")
        self.assertNotIn("self._apply_widget_appearance(", source)

    def test_every_visible_downloadable_hack_can_be_selected(self):
        refresh_source = self.method_source("_refresh_downloader_preview")
        toggle_source = self.method_source("_toggle_downloader_row_selection")
        self.assertIn(
            "selection_source = missing if only_missing else filtered",
            refresh_source,
        )
        self.assertIn("selectable_games = [", refresh_source)
        self.assertIn("elif row_key in selectable_row_keys:", refresh_source)
        self.assertIn(
            "[] if catalog_view_only else selectable_games",
            refresh_source,
        )
        self.assertNotIn('game.get("download_existing"', toggle_source)

    def test_selecting_a_row_repaints_the_cell_divider_immediately(self):
        source = self.method_source("_toggle_downloader_row_selection")
        self.assertIn(
            "self._schedule_treeview_cell_grid(tree, 0, restart=True)",
            source,
        )

    def test_existing_local_roms_can_be_copied_to_selected_fxpak_sd(self):
        source = self.method_source("_filtered_hack_download_worker")
        existing_branch = source[source.index("if exists:") :]
        self.assertIn("if sd_root is not None and local_exists:", existing_branch)
        self.assertIn("rom_builder_copy_rom_to_sd(", existing_branch)
        self.assertIn('"sd_copy_status": sd_copy_status', existing_branch)


if __name__ == "__main__":
    unittest.main()
