import unittest

from SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER import TrackerApp


class _FakeTree:
    def __init__(self):
        self.tags = {
            "waiting-row": ("waiting", "downloader_even"),
            "hall-row": ("hall_of_fame", "downloader_odd"),
            "normal-row": ("downloader_even",),
        }
        self.configured = {}

    def winfo_exists(self):
        return True

    def get_children(self, parent=""):
        return tuple(self.tags) if not parent else ()

    def item(self, iid, option=None, **kwargs):
        if "tags" in kwargs:
            self.tags[iid] = tuple(kwargs["tags"])
        if option == "tags":
            return self.tags[iid]
        return {"tags": self.tags[iid]}

    def tag_configure(self, name, **kwargs):
        self.configured[name] = kwargs


class _LegacyDifficultyTree:
    def __init__(self):
        self.tags = {
            "row": (
                "tracker_even",
                "difficulty_palette_FF00FF",
                "hall_of_fame",
            ),
        }

    def item(self, iid, option=None, **kwargs):
        if "tags" in kwargs:
            self.tags[iid] = tuple(kwargs["tags"])
        if option == "tags":
            return self.tags[iid]
        return {"tags": self.tags[iid]}


class SemanticTableColorTests(unittest.TestCase):
    def test_tracker_backing_rows_drop_legacy_difficulty_colors(self):
        app = TrackerApp.__new__(TrackerApp)
        tree = _LegacyDifficultyTree()

        app._apply_difficulty_color_to_tree_item(
            tree,
            "row",
            "Expert",
        )

        self.assertEqual(
            tree.tags["row"],
            ("tracker_even", "hall_of_fame"),
        )

    def test_downloader_appearance_does_not_color_entire_semantic_rows(self):
        app = TrackerApp.__new__(TrackerApp)
        app._library_palette = lambda: {
            "tree": "#101827",
            "panel_alt": "#1E2D46",
            "text": "#F2F6FF",
        }
        app._statistics_table_style = lambda _key: None
        tree = _FakeTree()

        app._apply_statistics_table_colors(tree, "missing_hacks")

        self.assertNotIn("even_waiting", tree.configured)
        self.assertNotIn("odd_hall_of_fame", tree.configured)
        self.assertEqual(
            tree.configured["downloader_even"]["foreground"],
            "#F2F6FF",
        )
        self.assertEqual(
            tree.configured["downloader_odd"]["foreground"],
            "#F2F6FF",
        )


if __name__ == "__main__":
    unittest.main()
