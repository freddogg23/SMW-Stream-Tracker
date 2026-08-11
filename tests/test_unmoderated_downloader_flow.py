import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_unmoderated_downloader_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UnmoderatedDownloaderFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def method_source(self, name):
        return ast.get_source_segment(
            self.source,
            self.methods[name],
        )

    def test_saved_custom_hack_is_a_downloadable_catalog_record(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            catalog_key = database.save_custom(
                {
                    "title": "Unmoderated Test Hack",
                    "author": "Test Author",
                    "download_url": "https://example.com/test-hack.zip",
                }
            )
            game = database.get_catalog_game(catalog_key)

            self.assertIsNotNone(game)
            self.assertTrue(game["is_custom"])
            self.assertEqual(
                game["download_url"],
                "https://example.com/test-hack.zip",
            )

    def test_catalog_edits_reload_the_ui_immediately(self):
        source = self.method_source("_reload_database_catalog")
        self.assertIn(
            "self.hack_catalog = self.stats_db.load_catalog()",
            source,
        )
        self.assertIn(
            "self._downloader_catalog_metadata_cache = None",
            source,
        )
        self.assertIn("force_library_scan=True", source)

    def test_downloader_add_keeps_full_list_and_selects_saved_hack(self):
        source = self.method_source("_edit_custom_hack")
        for expected in (
            "return_to_downloader",
            "self.open_hack_downloader()",
            "self._reset_downloader_filters()",
            "saved_catalog_key = self.stats_db.save_custom(",
            'game.get("catalog_key", "")',
            "downloader_tree.selection_set(saved_iid)",
            "force_library_scan=True",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, source)
        self.assertNotIn("search_var.set(title)", source)

    def test_unmoderated_form_uses_correct_hack_type_label(self):
        source = self.method_source("_edit_custom_hack")
        self.assertIn('(\"Hack Type:\", \"type\")', source)
        self.assertNotIn('(\"Typee:\", \"type\")', source)

    def test_custom_hacks_use_generic_download_confirmation(self):
        source = self.method_source("_start_filtered_hack_download")
        self.assertIn("contains_unmoderated", source)
        self.assertIn(
            "Download and patch {count} matching hack(s)?",
            source,
        )

    def test_new_flow_text_is_translated_in_every_language(self):
        texts = (
            (
                "A direct download URL is required when adding a hack from "
                "Download & Patch Missing Hacks."
            ),
            (
                'Added "{title}" to Download & Patch Missing Hacks. It is '
                "selected and ready for Download & Patch All Matching Hacks."
            ),
            "Download and patch {count} matching hack(s)?",
            "Hack Type:",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in texts:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)
                    self.assertNotEqual(translations[text], text)


if __name__ == "__main__":
    unittest.main()
