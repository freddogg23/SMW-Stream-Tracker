import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACKER_SOURCE = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_stream_tracker_catalog_status_test_module",
        TRACKER_SOURCE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CatalogStatusHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_reports_new_hacks_from_remote_catalog_count(self):
        self.assertEqual(
            self.tracker.catalog_available_new_hack_count(
                2750,
                {"hack_count": 2754},
            ),
            4,
        )

    def test_never_reports_a_negative_new_hack_count(self):
        self.assertEqual(
            self.tracker.catalog_available_new_hack_count(
                2755,
                {"hack_count": 2754},
            ),
            0,
        )

    def test_missing_remote_count_is_unavailable(self):
        self.assertIsNone(
            self.tracker.catalog_available_new_hack_count(
                2750,
                {},
            )
        )


if __name__ == "__main__":
    unittest.main()
