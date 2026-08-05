import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_obs_text_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ObsTextFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_author_and_exit_prefixes_can_be_removed(self):
        self.assertEqual(
            self.tracker.render_obs_text_template(
                "{author}",
                "By: {author}",
                author="Sample Creator",
            ),
            "Sample Creator",
        )
        self.assertEqual(
            self.tracker.render_obs_text_template(
                "{completed} / {total}",
                "Exits: {completed} / {total}",
                completed=7,
                total=12,
            ),
            "7 / 12",
        )

    def test_all_five_obs_files_are_created_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_folder = Path(temporary_directory)
            existing_hack_name = output_folder / "hack_name.txt"
            existing_hack_name.write_text(
                "Keep this value",
                encoding="utf-8",
            )
            config = {
                "output_folder": str(output_folder),
                "obs_author_text_format": "{author}",
                "obs_exits_text_format": "{completed}/{total}",
            }

            result = self.tracker.ensure_obs_text_files(config)

            self.assertEqual(result, output_folder)
            self.assertEqual(
                {path.name for path in output_folder.glob("*.txt")},
                {
                    "author.txt",
                    "exits.txt",
                    "hack_name.txt",
                    "level_timer.txt",
                    "game_timer.txt",
                },
            )
            self.assertEqual(
                existing_hack_name.read_text(encoding="utf-8"),
                "Keep this value",
            )
            self.assertEqual(
                (output_folder / "author.txt").read_text(
                    encoding="utf-8"
                ),
                "Unknown",
            )
            self.assertEqual(
                (output_folder / "exits.txt").read_text(
                    encoding="utf-8"
                ),
                "0/Unknown",
            )


if __name__ == "__main__":
    unittest.main()
