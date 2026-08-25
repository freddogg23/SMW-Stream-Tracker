import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_catalog_tags_details_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CatalogTagsAndDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_live_api_parser_keeps_tags_description_and_screenshots(self):
        game = self.tracker.parse_smwcentral_api_game(
            {
                "id": 42841,
                "name": "Critter Quest",
                "authors": [{"id": 1, "name": "JakesBRjust"}],
                "tags": ["animal crossing", "custom music", "traditional"],
                "images": [
                    "https://dl.smwcentral.net/image/125821.png",
                    "https://dl.smwcentral.net/image/125822.png",
                ],
                "rating": 5,
                "raw_fields": {
                    "difficulty": "diff_4",
                    "type": ["kaizo"],
                    "length": 10,
                    "description": "A detailed description.",
                },
            },
            {
                "difficulty": {"diff_4": "Advanced"},
                "type": {"kaizo": "Kaizo"},
            },
        )

        self.assertEqual(game["tags"], "animal crossing, custom music, traditional")
        self.assertEqual(game["description"], "A detailed description.")
        self.assertEqual(len(game["screenshots"]), 2)
        self.assertIn("custom music", self.tracker.catalog_search_text(game))

    def test_catalog_database_round_trips_detail_metadata(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = self.tracker.TrackerDatabase(Path(folder) / "tracker.db")
            database.refresh_from_smwcentral(
                [
                    {
                        "smwc_id": "123",
                        "title": "Tagged Hack",
                        "author": "Creator",
                        "difficulty": "Expert",
                        "hack_type": "Kaizo",
                        "total_exits": 4,
                        "tags": "chocolate, custom music",
                        "description": "Stored locally.",
                        "screenshots": [
                            "https://dl.smwcentral.net/image/1.png",
                            "https://dl.smwcentral.net/image/2.png",
                        ],
                    }
                ],
                "2026-08-15T12:00:00-05:00",
                "test",
            )

            game = database.load_catalog()[0]
            self.assertEqual(game["tags"], "chocolate, custom music")
            self.assertEqual(game["description"], "Stored locally.")
            self.assertEqual(
                game["screenshots"],
                [
                    "https://dl.smwcentral.net/image/1.png",
                    "https://dl.smwcentral.net/image/2.png",
                ],
            )

            updated = database.update_catalog_feature_metadata(
                game["catalog_key"],
                {
                    "tags": "updated tag",
                    "description": "Updated on demand.",
                    "screenshots": [
                        "https://dl.smwcentral.net/image/3.png"
                    ],
                },
            )
            self.assertEqual(updated["tags"], "updated tag")
            self.assertEqual(updated["description"], "Updated on demand.")
            self.assertEqual(
                updated["screenshots"],
                ["https://dl.smwcentral.net/image/3.png"],
            )

    def test_single_hack_metadata_fetch_uses_exact_smwcentral_id(self):
        payload = {
            "data": [
                {
                    "id": 999,
                    "name": "Same Name",
                    "tags": ["wrong"],
                    "images": [],
                    "raw_fields": {"description": "Wrong entry"},
                },
                {
                    "id": 123,
                    "name": "Same Name",
                    "tags": ["chocolate", "traditional"],
                    "images": ["https://dl.smwcentral.net/image/4.png"],
                    "raw_fields": {"description": "Correct entry"},
                },
            ]
        }
        with patch.object(
            self.tracker,
            "smwc_api_json",
            return_value=payload,
        ) as request:
            metadata = self.tracker.fetch_smwcentral_hack_feature_metadata(
                {"smwc_id": "123", "title": "Same Name"}
            )
        self.assertEqual(metadata["description"], "Correct entry")
        self.assertEqual(metadata["tags"], "chocolate, traditional")
        self.assertEqual(len(metadata["screenshots"]), 1)
        self.assertEqual(request.call_args.args[0]["f[name]"], "Same Name")

    def test_resolved_tracker_record_preserves_blank_tracker_only_fields(self):
        class CatalogDatabase:
            @staticmethod
            def get_catalog_game(_catalog_key):
                return {
                    "catalog_key": "SMWC:123",
                    "title": "Blank Rating World",
                    "rating": 4.0,
                }

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.stats_db = CatalogDatabase()
        app.hack_catalog = []
        resolved = app._resolved_hack_details_record(
            {
                "catalog_key": "SMWC:123",
                "title": "Blank Rating World",
                "personal_rating": None,
                "smwc_rating": None,
            }
        )

        self.assertIn("personal_rating", resolved)
        self.assertIsNone(resolved["personal_rating"])
        self.assertIn("smwc_rating", resolved)
        self.assertIsNone(resolved["smwc_rating"])

    def test_every_supported_language_has_new_labels(self):
        labels = (
            "Search title, creator, or tag",
            "Search title, creator, or tag:",
            "Description",
            "Screenshots",
            "Tags:",
            "No description is available for this hack.",
            "No screenshots are available for this hack.",
            "View Hack Details",
            "Loading the description, tags, and screenshots from SMW Central…",
            "The full hack details could not be loaded from SMW Central.",
            "Click any screenshot to enlarge it.",
            "Screenshot Viewer",
            "Previous Screenshot",
            "Next Screenshot",
            "Screenshot {current} of {total}",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for label in labels:
                with self.subTest(language=language, label=label):
                    self.assertIn(label, translations)
                    self.assertTrue(translations[label].strip())

    def test_ui_uses_shared_tag_index_and_modern_details_popup(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        popup_source = ast.get_source_segment(
            source,
            methods["_show_hack_details_popup"],
        )
        current_source = ast.get_source_segment(
            source,
            methods["open_current_hack_page"],
        )
        self.assertIn("dialog._uses_stream_desk_palette = True", popup_source)
        self.assertIn("self._create_stream_desk_page_header", popup_source)
        self.assertIn('kicker="SMW CENTRAL"', popup_source)
        self.assertIn('bg=STREAM_DESK["green"]', popup_source)
        self.assertIn("description_body = self._stream_desk_card", popup_source)
        self.assertIn("screenshots_body = self._stream_desk_card", popup_source)
        self.assertNotIn("title_bar = tk.Frame", popup_source)
        self.assertIn('"Description"', popup_source)
        self.assertIn('"Screenshots"', popup_source)
        self.assertIn("open_hack_details", current_source)
        self.assertIn("fetch_smwcentral_hack_feature_metadata", source)
        self.assertIn("_show_hack_screenshot_viewer", popup_source)
        self.assertIn("bind_hack_details_wheel(dialog)", popup_source)
        self.assertIn("bind_hack_details_wheel(gallery)", popup_source)
        self.assertIn('"<MouseWheel>"', popup_source)
        self.assertIn('"<Button-4>"', popup_source)
        self.assertIn('"<Button-5>"', popup_source)
        self.assertIn("canvas.yview_scroll(units, \"units\")", popup_source)
        self.assertIn("return \"break\"", popup_source)
        viewer_source = ast.get_source_segment(
            source,
            methods["_show_hack_screenshot_viewer"],
        )
        self.assertIn('dialog.bind("<Left>"', viewer_source)
        self.assertIn('dialog.bind("<Right>"', viewer_source)
        self.assertIn('"Screenshot {current} of {total}"', viewer_source)
        self.assertIn("image_panel.columnconfigure(1, weight=1)", viewer_source)
        self.assertIn('text="◀"', viewer_source)
        self.assertIn('text="▶"', viewer_source)
        self.assertIn('getattr(resampling, "NEAREST", 0)', viewer_source)
        self.assertIn("if fit_scale >= 2:", viewer_source)
        self.assertIn("_smw_hack_details_resolver", source)
        self.assertGreaterEqual(source.count('"View Hack Details"'), 4)
        self.assertGreaterEqual(source.count("catalog_search_text("), 6)
        self.assertIn("textvariable=self.hack_type_var", source)
        self.assertIn(
            "metadata_missing",
            self.tracker.TrackerApp._show_hack_details_popup.__code__.co_varnames,
        )
        self.assertNotIn(
            "metadata_missing",
            self.tracker.TrackerApp.open_mister_setup.__code__.co_varnames,
        )

    def test_context_menus_keep_actions_but_remove_legacy_color_options(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        shared_menu = ast.get_source_segment(
            source,
            methods["_show_table_appearance_menu"],
        )
        tracker_menu = ast.get_source_segment(
            source,
            methods["_show_tracker_appearance_menu"],
        )
        overview_menu = ast.get_source_segment(
            source,
            methods["_show_statistics_table_color_menu"],
        )
        downloader = ast.get_source_segment(
            source,
            methods["open_hack_downloader"],
        )

        removed_labels = (
            "Solid color for",
            "Gradient for",
            "Alternating rows for",
            "Edit gradient data bar",
            "Set color for all",
            "Choose another difficulty color",
            "Use Overview alternating colors",
            "Restore Mario theme colors",
            "Restore default table colors",
        )
        for menu_source in (shared_menu, tracker_menu, overview_menu):
            for label in removed_labels:
                with self.subTest(method=menu_source[:40], label=label):
                    self.assertNotIn(label, menu_source)

        self.assertIn('"View Hack Details"', shared_menu)
        self.assertIn("tree.selection()", shared_menu)
        self.assertIn('"View Hack Details"', tracker_menu)
        self.assertIn('"View Hack Details"', overview_menu)
        self.assertIn("details_resolver=lambda iid:", downloader)


if __name__ == "__main__":
    unittest.main()
