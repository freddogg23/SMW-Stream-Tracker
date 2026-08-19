import ast
import importlib.util
import inspect
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


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
        self.assertEqual(
            self.tracker.render_obs_text_template(
                "{deaths}",
                "Level Deaths: {deaths}",
                deaths=9,
            ),
            "9",
        )
        self.assertEqual(
            self.tracker.render_obs_text_template(
                "{total_deaths}",
                "Total Deaths: {total_deaths}",
                total_deaths=42,
            ),
            "42",
        )

    def test_obs_setup_dialog_has_no_out_of_scope_chart_scale(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_guided_obs_text_setup
        )
        self.assertNotIn("chart_scale", source)

    def test_obs_capture_mode_is_opt_in_and_saved_from_obs_settings(self):
        self.assertIs(self.tracker.DEFAULT_CONFIG["obs_capture_mode"], False)
        source = inspect.getsource(
            self.tracker.TrackerApp.open_obs_settings_dialog
        )
        self.assertIn("obs_capture_mode_var = tk.BooleanVar", source)
        self.assertIn("Show tracker popups inside the main app window", source)
        self.assertIn(
            '"obs_capture_mode": bool(obs_capture_mode_var.get())',
            source,
        )

    def test_capture_mode_uses_in_app_dialog_factory(self):
        factory_source = inspect.getsource(
            self.tracker.TrackerApp._create_tracker_dialog
        )
        self.assertIn("InAppOverlayDialog", factory_source)
        self.assertIn("obs_capture_mode", factory_source)
        self.assertTrue(
            issubclass(self.tracker.InAppOverlayDialog, self.tracker.tk.Frame)
        )

    def test_only_intentional_native_toplevels_bypass_capture_mode(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        parent_by_node = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parent_by_node[child] = parent

        native_callers = set()
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "tk"
                and node.func.attr == "Toplevel"
            ):
                continue
            owner = node
            while owner is not None and not isinstance(
                owner,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                owner = parent_by_node.get(owner)
            native_callers.add(owner.name if owner is not None else "<module>")

        self.assertEqual(
            native_callers,
            {
                "_create_tracker_dialog",
                "_post_main_hack_selector_popup",
            },
        )
        timer_source = inspect.getsource(
            self.tracker.TrackerApp.open_native_obs_timer_window
        )
        self.assertIn(
            "self._create_tracker_dialog(self.root, force_native=True)",
            timer_source,
        )

    def test_capture_mode_wording_is_translated_in_every_language(self):
        keys = (
            "OBS Capture Mode",
            "Show tracker popups inside the main app window",
            "One OBS Window Capture source will then include the tracker's blue popups.",
            "External browsers, installers, and file pickers remain separate windows.",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                for key in keys:
                    self.assertIn(key, self.tracker.UI_TRANSLATIONS[language])
                    self.assertTrue(
                        self.tracker.UI_TRANSLATIONS[language][key].strip()
                    )

    def test_all_obs_files_are_created_without_overwriting(self):
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
                "obs_deaths_text_format": "{deaths}",
                "obs_total_deaths_text_format": "{total_deaths}",
            }

            result = self.tracker.ensure_obs_text_files(config)

            self.assertEqual(result, output_folder)
            self.assertEqual(
                {path.name for path in output_folder.glob("*.txt")},
                {
                    "author.txt",
                    "death_counter.txt",
                    "level_deaths.txt",
                    "total_deaths.txt",
                    "exits.txt",
                    "hack_name.txt",
                    "level_timer.txt",
                    "game_timer.txt",
                    "streamerbot_level_events.txt",
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
            self.assertEqual(
                (output_folder / "death_counter.txt").read_text(
                    encoding="utf-8"
                ),
                "0",
            )
            self.assertEqual(
                (output_folder / "level_deaths.txt").read_text(
                    encoding="utf-8"
                ),
                "0",
            )
            self.assertEqual(
                (output_folder / "total_deaths.txt").read_text(
                    encoding="utf-8"
                ),
                "0",
            )

    def test_guided_setup_selects_folder_and_immediately_creates_paths(self):
        class Value:
            def __init__(self, value=""):
                self.value = value

            def get(self):
                return self.value

            def set(self, value):
                self.value = value

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_folder = Path(temporary_directory) / "OBS Text Files"
            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.output_folder_var = Value()
            app.config = {}
            app.worker = None
            app.root = object()
            app._translate_ui_text = lambda text: text
            app._show_localized_info = lambda *_args, **_kwargs: None

            with (
                mock.patch.object(
                    self.tracker.filedialog,
                    "askdirectory",
                    return_value=str(output_folder),
                ),
                mock.patch.object(self.tracker, "save_config"),
            ):
                selected = app._select_guided_obs_text_folder()

            self.assertEqual(selected, output_folder)
            self.assertEqual(app.output_folder_var.get(), str(output_folder))
            self.assertEqual(app.config["output_folder"], str(output_folder))
            for filename in (
                "hack_name.txt",
                "author.txt",
                "exits.txt",
                "level_deaths.txt",
                "total_deaths.txt",
            ):
                self.assertTrue((output_folder / filename).is_file())


if __name__ == "__main__":
    unittest.main()
