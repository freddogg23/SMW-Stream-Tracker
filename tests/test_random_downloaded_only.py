import ast
import importlib.util
import inspect
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
        "smw_tracker_random_download_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Value:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class TkRecorder:
    def __init__(self):
        self.calls = []

    def call(self, *arguments):
        self.calls.append(arguments)


class UpdateBadge:
    def __init__(self):
        self.tk = TkRecorder()
        self._w = ".update_badge"
        self.place_options = None

    def winfo_exists(self):
        return True

    def place(self, **options):
        self.place_options = options

    def place_forget(self):
        self.place_options = None

    def lift(self):
        raise AssertionError("Canvas.lift() must not be used for the badge")


class MenuRecorder:
    def __init__(self):
        self.entry_options = {}

    def entryconfigure(self, index, **options):
        self.entry_options[index] = options


class AfterDialog:
    def __init__(self):
        self.scheduled = []
        self.cancelled = []

    def winfo_exists(self):
        return True

    def after(self, milliseconds, callback):
        identifier = f"after-{len(self.scheduled) + 1}"
        self.scheduled.append((identifier, milliseconds, callback))
        return identifier

    def after_cancel(self, identifier):
        self.cancelled.append(identifier)


class ButtonRecorder:
    def __init__(self):
        self.options = {}

    def configure(self, **options):
        self.options.update(options)


class RandomDownloadedOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self, platform):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.platform_var = Value(platform)
        app.config = {
            "platform_rom_mappings": {},
            "fxpak_rom_mappings": {},
        }
        app.fxpak_path_map = {}
        return app

    def test_catalog_only_game_is_not_random_eligible(self):
        app = self.make_app("FXPAK Pro")
        game = {"title": "Catalog Only", "smwc_id": "10"}
        self.assertFalse(app._catalog_game_has_downloaded_rom(game))

    def test_fxpak_mapping_is_random_eligible(self):
        app = self.make_app("FXPAK Pro")
        game = {"title": "Downloaded", "smwc_id": "11"}
        app.config["fxpak_rom_mappings"] = {
            "smwc:11": "/All_Hacks/D/Downloaded.sfc",
        }
        self.assertTrue(app._catalog_game_has_downloaded_rom(game))

    def test_retroarch_requires_an_existing_local_file(self):
        app = self.make_app("RetroArch")
        game = {"title": "Local", "smwc_id": "12"}
        with tempfile.TemporaryDirectory() as temporary_directory:
            rom_path = Path(temporary_directory) / "Local.sfc"
            app.config["platform_rom_mappings"] = {
                "RetroArch": {"smwc:12": str(rom_path)},
            }
            self.assertFalse(app._catalog_game_has_downloaded_rom(game))
            rom_path.write_bytes(b"ROM")
            self.assertTrue(app._catalog_game_has_downloaded_rom(game))

    def test_catalog_recognizes_roms_in_configured_library(self):
        app = self.make_app("FXPAK Pro")
        game = {"title": "The Downloaded Adventure", "smwc_id": "13"}
        with tempfile.TemporaryDirectory() as temporary_directory:
            library_root = Path(temporary_directory) / "Patched ROMs"
            rom_path = library_root / "D" / "The Downloaded Adventure.sfc"
            rom_path.parent.mkdir(parents=True)
            rom_path.write_bytes(b"ROM")
            app.config["rom_builder_library_folder"] = temporary_directory

            self.assertTrue(app._catalog_game_has_downloaded_rom(game))

    def test_update_badge_raises_widget_without_canvas_tag_error(self):
        app = self.make_app("FXPAK Pro")
        badge = UpdateBadge()
        app.help_update_badge = badge
        app.update_available_version = "TEST"
        app._ui_px = lambda value: value

        app._refresh_help_update_badge()

        self.assertIsNotNone(badge.place_options)
        self.assertEqual(
            badge.tk.calls,
            [("raise", ".update_badge")],
        )

    def test_update_badge_adds_red_dot_to_about_menu_entry(self):
        app = self.make_app("FXPAK Pro")
        app.app_language = "en"
        app.help_update_badge = UpdateBadge()
        app.update_available_version = "TEST"
        app._ui_px = lambda value: value
        app.help_menu = MenuRecorder()
        app.about_updates_menu_index = 3
        app.about_update_dot_image = "red-dot"
        app.about_dialog = None
        app.about_update_button = None

        app._refresh_help_update_badge()

        self.assertEqual(
            app.help_menu.entry_options[3]["image"],
            "red-dot",
        )

    def test_about_update_button_flashes_update_available(self):
        app = self.make_app("FXPAK Pro")
        app.app_language = "en"
        app.update_available_version = "TEST"
        app.about_dialog = AfterDialog()
        app.about_update_button = ButtonRecorder()
        app.about_update_flash_after_id = None
        app.about_update_flash_on = False

        app._refresh_about_update_button()

        self.assertEqual(
            app.about_update_button.options["text"],
            "Update Available",
        )
        self.assertEqual(
            app.about_update_button.options["bg"],
            self.tracker.THEME["red"],
        )
        self.assertEqual(
            app.about_dialog.scheduled[0][1],
            700,
        )

    def test_retroarch_settings_are_added_and_existing_values_replaced(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "retroarch.cfg"
            config_path.write_text(
                'video_driver = "gl"\n'
                'network_cmd_enable = "false"\n'
                'quit_press_twice = "true"\n',
                encoding="utf-8",
            )
            self.tracker.write_retroarch_tracker_settings(config_path)
            text = config_path.read_text(encoding="utf-8")
            self.assertIn('video_driver = "gl"', text)
            self.assertIn('network_cmd_enable = "true"', text)
            self.assertIn('network_cmd_port = "55355"', text)
            self.assertIn('quit_press_twice = "false"', text)
            self.assertEqual(text.count("network_cmd_enable ="), 1)

    def test_main_random_filters_only_include_matching_downloaded_roms(self):
        app = self.make_app("FXPAK Pro")
        app.hack_catalog = [
            {
                "title": "Expert Downloaded",
                "smwc_id": "20",
                "difficulty": "Expert",
                "hack_type": "Kaizo",
                "rating": 4.7,
            },
            {
                "title": "Casual Downloaded",
                "smwc_id": "21",
                "difficulty": "Casual",
                "hack_type": "Standard",
                "rating": 4.9,
            },
            {
                "title": "Expert Catalog Only",
                "smwc_id": "22",
                "difficulty": "Expert",
                "hack_type": "Kaizo",
                "rating": 5.0,
            },
        ]
        app.config["fxpak_rom_mappings"] = {
            "smwc:20": "/All_Hacks/E/Expert Downloaded.sfc",
            "smwc:21": "/All_Hacks/C/Casual Downloaded.sfc",
        }

        candidates = app._random_main_hack_candidates(
            "4+",
            "Expert",
            "Kaizo",
        )

        self.assertEqual(
            [game["title"] for game in candidates],
            ["Expert Downloaded"],
        )

    def test_action_button_calls_only_use_supported_arguments(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        allowed = set(
            inspect.signature(
                self.tracker.TrackerApp._make_action_button
            ).parameters
        )
        invalid = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "_make_action_button"
            ):
                continue
            for keyword in node.keywords:
                if keyword.arg is not None and keyword.arg not in allowed:
                    invalid.append(keyword.arg)
        self.assertEqual(invalid, [])

    def test_open_widget_text_can_switch_languages_without_restart(self):
        app = self.make_app("FXPAK Pro")
        app.app_language = "es"
        spanish = app._translate_ui_text("⚙ SETTINGS")
        self.assertIn("CONFIGURACIÓN", spanish)
        self.assertEqual(
            app._translate_ui_text("GAME TIME"),
            "TIEMPO DE JUEGO",
        )

        app.app_language = "fr"
        french = app._translate_ui_text(spanish)
        self.assertIn("PARAMÈTRES", french)
        self.assertEqual(
            app._translate_ui_text("Finish Game Timer"),
            "Terminer le temps de jeu",
        )

        app.app_language = "en"
        self.assertEqual(app._translate_ui_text(french), "⚙ SETTINGS")

    def test_every_supported_translation_has_the_same_interface_keys(self):
        translation_sets = {
            language: set(translations)
            for language, translations in self.tracker.UI_TRANSLATIONS.items()
        }
        expected = translation_sets["es"]
        for language, translated_keys in translation_sets.items():
            self.assertEqual(expected, translated_keys, language)

    def test_secondary_menu_commands_are_translated(self):
        app = self.make_app("FXPAK Pro")
        app.app_language = "de"

        self.assertEqual(
            app._translate_ui_text("Manage SD Card Hacks…"),
            "Hacks auf der SD-Karte verwalten…",
        )
        self.assertEqual(
            app._translate_ui_text("Google Sheets Sync…"),
            "Google-Sheets-Synchronisierung…",
        )
        self.assertEqual(
            app._translate_ui_text("Open Automatic Backups Folder"),
            "Ordner für automatische Sicherungen öffnen",
        )

    def test_every_menu_label_has_a_translation_key(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        translation_keys = set(
            next(iter(self.tracker.UI_TRANSLATIONS.values()))
        )
        labels = set()

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function_name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else (
                    node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else ""
                )
            )
            label_index = 0 if function_name == "create_menu_button" else 1
            if (
                function_name in {
                    "create_menu_button",
                    "add_mario_command",
                    "add_mario_radio",
                }
                and len(node.args) > label_index
                and isinstance(node.args[label_index], ast.Constant)
                and isinstance(node.args[label_index].value, str)
            ):
                labels.add(node.args[label_index].value)
            if function_name == "add_cascade":
                for keyword in node.keywords:
                    if (
                        keyword.arg == "label"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        labels.add(keyword.value.value)
            if function_name == "protected_menu_action":
                for index in (1, 2):
                    if (
                        len(node.args) > index
                        and isinstance(node.args[index], ast.Constant)
                        and isinstance(node.args[index].value, str)
                    ):
                        labels.add(node.args[index].value)

        untranslated = labels - translation_keys - {
            "FXPAK Pro",
            "RetroArch",
        }
        self.assertEqual(untranslated, set())

    def test_switching_from_german_relocalizes_persistent_main_labels(self):
        app = self.make_app("FXPAK Pro")
        app.app_language = "en"
        app.connection_var = Value("Verbunden — SD2SNES COM5")
        app.catalog_last_refresh_var = Value(
            "Zuletzt aktualisiert: Aug 5, 2026 8:08 PM"
        )
        app.catalog_new_hacks_var = Value(
            "0 neue Hacks seit der letzten Aktualisierung"
        )
        app.author_var = Value("Von: Anonymous")
        app.exits_var = Value("Ausgänge: 0 / 9")
        app.difficulty_var = Value("Schwierigkeit: Advanced")
        app.smwc_rating_var = Value("SMW-Central-Bewertung: 0/5")

        app._relocalize_main_text_variables()

        self.assertEqual(app.connection_var.get(), "Connected — SD2SNES COM5")
        self.assertTrue(app.catalog_last_refresh_var.get().startswith("Last refreshed:"))
        self.assertEqual(
            app.catalog_new_hacks_var.get(),
            "0 new hacks since last refresh",
        )
        self.assertEqual(app.author_var.get(), "By: Anonymous")
        self.assertEqual(app.exits_var.get(), "Exits: 0 / 9")
        self.assertEqual(app.difficulty_var.get(), "Difficulty: Advanced")
        self.assertEqual(app.smwc_rating_var.get(), "SMWCentral Rating: 0/5")


if __name__ == "__main__":
    unittest.main()
