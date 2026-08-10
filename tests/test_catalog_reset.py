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
        "smw_tracker_catalog_reset_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CatalogResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    @staticmethod
    def catalog_game(smwc_id, title):
        return {
            "smwc_id": str(smwc_id),
            "title": title,
            "author": "Catalog Author",
            "difficulty": "Intermediate",
            "hack_type": "Standard",
            "total_exits": 5,
        }

    def test_reset_removes_catalog_but_preserves_personal_data(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            games = [
                self.catalog_game(101, "Delete Me"),
                self.catalog_game(102, "Tracked Hack"),
                self.catalog_game(103, "Mapped Hack"),
            ]
            database.refresh_from_smwcentral(
                games,
                "2026-08-10T12:00:00-05:00",
                "test-catalog",
            )
            database.set_metadata("Catalog Sequence", "123")
            custom_key = database.save_custom(
                {
                    "title": "Personal Hack",
                    "author": "Player",
                }
            )

            with database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO tracked_hacks (catalog_key, title)
                    VALUES ('SMWC:102', 'Tracked Hack')
                    """
                )
                connection.execute(
                    """
                    INSERT INTO rom_mappings (
                        map_key, catalog_key, title, smwc_id, rom_path
                    ) VALUES (
                        'SMWC:103', 'SMWC:103', 'Mapped Hack', '103',
                        '/All_Hacks/M/Mapped Hack.sfc'
                    )
                    """
                )

            summary = database.reset_smwcentral_catalog()

            self.assertEqual(
                summary,
                {"removed": 3, "deleted": 1, "preserved": 2},
            )
            self.assertEqual(
                database.catalog_status_counts(),
                {"total": 0, "waiting": 0, "moderated": 0},
            )
            self.assertEqual(database.tracked_count(), 1)
            self.assertEqual(
                database.rom_mapping_map()["smwc:103"],
                "/All_Hacks/M/Mapped Hack.sfc",
            )

            rows = {
                game["catalog_key"]: game
                for game in database.load_catalog()
            }
            self.assertNotIn("SMWC:101", rows)
            self.assertTrue(rows["SMWC:102"]["is_custom"])
            self.assertTrue(rows["SMWC:103"]["is_custom"])
            self.assertIn(custom_key, rows)
            self.assertNotIn("Catalog Version", database.metadata())
            self.assertNotIn("Catalog Sequence", database.metadata())

            # A later refresh restores the preserved rows to the live catalog.
            database.refresh_from_smwcentral(
                games,
                "2026-08-11T12:00:00-05:00",
                "test-catalog-2",
            )
            refreshed_rows = {
                game["catalog_key"]: game
                for game in database.load_catalog()
            }
            self.assertFalse(refreshed_rows["SMWC:102"]["is_custom"])
            self.assertFalse(refreshed_rows["SMWC:103"]["is_custom"])
            self.assertTrue(refreshed_rows[custom_key]["is_custom"])
            self.assertEqual(database.tracked_count(), 1)

    def test_catalog_page_has_reset_button_and_blue_confirmation(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        browser_source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            methods["open_hack_downloader"],
        )
        reset_source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            methods["reset_smwcentral_catalog"],
        )

        self.assertIn('text="Reset Catalog"', browser_source)
        self.assertIn('command=self.reset_smwcentral_catalog', browser_source)
        self.assertIn("self._ask_localized_yes_no(", reset_source)
        self.assertIn("self._create_recovery_backup(", reset_source)

    def test_reset_text_is_translated_in_every_language(self):
        reset_text = (
            "Reset Catalog",
            "Reset SMW Central Catalog?",
            "Catalog Reset Complete",
            "Catalog reset complete.",
            (
                "The catalog could not be reset because a recovery backup "
                "could not be created."
            ),
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for text in reset_text:
                with self.subTest(language=language, text=text):
                    self.assertIn(text, translations)
                    self.assertNotEqual(translations[text], text)


if __name__ == "__main__":
    unittest.main()
