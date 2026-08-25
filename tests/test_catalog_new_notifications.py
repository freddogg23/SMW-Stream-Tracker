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
        "smw_tracker_catalog_new_notifications_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CatalogNewNotificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    @staticmethod
    def game(smwc_id: int, title: str, *, waiting: bool = False):
        return {
            "smwc_id": str(smwc_id),
            "title": title,
            "author": "Catalog Author",
            "difficulty": "Intermediate",
            "hack_type": "Standard",
            "total_exits": 5,
            "added_date": "2026-08-24",
            "is_waiting": waiting,
        }

    def test_moderated_refresh_persists_exact_new_keys_and_date(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = self.tracker.TrackerDatabase(Path(folder) / "tracker.db")
            database.refresh_from_smwcentral(
                [self.game(101, "Already Here")],
                "2026-08-23T12:00:00-05:00",
                "first",
            )
            summary = database.refresh_from_smwcentral(
                [
                    self.game(101, "Already Here"),
                    self.game(102, "Brand New Hack"),
                ],
                "2026-08-24T09:30:00-05:00",
                "second",
            )

            metadata = database.metadata()
            self.assertEqual(summary["new"], 1)
            self.assertEqual(metadata["Catalog New Since Last Refresh"], "1")
            self.assertEqual(
                self.tracker.catalog_new_keys_from_metadata(
                    metadata["Catalog New Keys Since Last Refresh"]
                ),
                {"SMWC:102"},
            )
            self.assertEqual(
                metadata["Catalog New Refresh Date"],
                "2026-08-24T09:30:00-05:00",
            )

    def test_waiting_refresh_persists_exact_new_keys_and_date(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = self.tracker.TrackerDatabase(Path(folder) / "tracker.db")
            database.refresh_waiting_from_smwcentral(
                [self.game(201, "Already Waiting", waiting=True)],
                "2026-08-23T12:00:00-05:00",
            )
            summary = database.refresh_waiting_from_smwcentral(
                [
                    self.game(201, "Already Waiting", waiting=True),
                    self.game(202, "New Waiting Hack", waiting=True),
                ],
                "2026-08-24T10:15:00-05:00",
            )

            metadata = database.metadata()
            self.assertEqual(summary["new"], 1)
            self.assertEqual(metadata["Waiting New Since Last Refresh"], "1")
            self.assertEqual(
                self.tracker.catalog_new_keys_from_metadata(
                    metadata["Waiting New Keys Since Last Refresh"]
                ),
                {"SMWC:202"},
            )
            self.assertEqual(
                metadata["Waiting New Refresh Date"],
                "2026-08-24T10:15:00-05:00",
            )

    def test_invalid_new_key_metadata_is_safe(self):
        self.assertEqual(
            self.tracker.catalog_new_keys_from_metadata("not-json"),
            set(),
        )

    def test_waiting_availability_compares_remote_ids_to_local_queue(self):
        local = [
            self.game(301, "Known Waiting", waiting=True),
            self.game(999, "Moderated", waiting=False),
        ]
        remote = [
            self.game(301, "Known Waiting", waiting=True),
            self.game(302, "New Waiting One", waiting=True),
            self.game(303, "New Waiting Two", waiting=True),
        ]
        self.assertEqual(
            self.tracker.catalog_available_waiting_hack_count(local, remote),
            2,
        )
        self.assertEqual(
            self.tracker.catalog_new_keys_from_metadata('{"wrong": true}'),
            set(),
        )

    def test_snes_rom_tab_does_not_reference_smw_only_new_filter(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        syntax_tree = ast.parse(source)
        tracker_class = next(
            node
            for node in syntax_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TrackerApp"
        )
        non_smw_builder = next(
            node
            for node in tracker_class.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_build_non_smw_game_library_tab"
        )
        referenced_names = {
            node.id
            for node in ast.walk(non_smw_builder)
            if isinstance(node, ast.Name)
        }
        self.assertNotIn("new_since_filter_var", referenced_names)

    def test_smw_new_filter_is_saved_with_game_library_controls(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        syntax_tree = ast.parse(source)
        tracker_class = next(
            node
            for node in syntax_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TrackerApp"
        )
        smw_builder = next(
            node
            for node in tracker_class.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_build_stream_desk_game_library"
        )
        builder_source = ast.get_source_segment(source, smw_builder) or ""
        self.assertIn("new_since_filter_var = tk.StringVar", builder_source)
        self.assertIn(
            '"new_since_filter_var": new_since_filter_var',
            builder_source,
        )


if __name__ == "__main__":
    unittest.main()
