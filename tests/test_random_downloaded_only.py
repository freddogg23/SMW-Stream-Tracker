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
