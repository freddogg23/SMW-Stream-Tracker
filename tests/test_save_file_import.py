import importlib.util
import inspect
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_save_import_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeMenu:
    def __init__(self):
        self.commands = []

    def add_command(self, **values):
        self.commands.append(values)


class SaveFileImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self, config=None):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = dict(config or {})
        return app

    def test_local_import_renames_source_and_backs_up_existing_save(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "downloaded-save-with-another-name.sav"
            destination = root / "saves" / "Actual Hack Name.srm"
            source.write_bytes(b"new-save")
            destination.parent.mkdir()
            destination.write_bytes(b"old-save")

            backup = self.tracker.TrackerApp._install_local_save_file(
                source,
                destination,
            )

            self.assertEqual(destination.read_bytes(), b"new-save")
            self.assertIsNotNone(backup)
            self.assertEqual(backup.read_bytes(), b"old-save")
            self.assertIn(".backup-", backup.name)
            self.assertTrue(source.is_file())

    def test_retroarch_destination_uses_real_rom_name_and_configured_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = root / "RetroArch" / "retroarch.exe"
            executable.parent.mkdir()
            executable.write_bytes(b"exe")
            rom = root / "library" / "Actual Patched Filename.sfc"
            rom.parent.mkdir()
            rom.write_bytes(b"rom")
            save_root = root / "custom saves"
            nested = save_root / "bsnes-mercury Performance"
            nested.mkdir(parents=True)
            existing = nested / "Actual Patched Filename.srm"
            existing.write_bytes(b"old")
            (executable.parent / "retroarch.cfg").write_text(
                f'savefile_directory = "{save_root}"\n'
                'sort_savefiles_enable = "true"\n',
                encoding="utf-8",
            )
            app = self.make_app(
                {
                    "retroarch_executable_path": str(executable),
                    "retroarch_core_path": str(
                        executable.parent
                        / "cores"
                        / "bsnes_mercury_performance_libretro.dll"
                    ),
                }
            )
            app._resolve_local_rom_path = mock.Mock(
                return_value=(rom, "saved local ROM mapping")
            )

            destination, method = app._retroarch_save_destination(
                {"title": "Catalog Title Can Be Different"}
            )

            self.assertEqual(destination, existing)
            self.assertEqual(method, "saved local ROM mapping")

    def test_mister_destination_mirrors_rom_subfolders_and_basename(self):
        app = self.make_app()
        destination = app._mister_save_destination(
            {
                "title": "Catalog Name",
                "rom_path": (
                    "/media/fat/games/SNES/SMW Stream Tracker/A/"
                    "Actual MiSTer Name.sfc"
                ),
            }
        )

        self.assertEqual(
            destination,
            (
                "/media/fat/saves/SNES/SMW Stream Tracker/A/"
                "Actual MiSTer Name.sav"
            ),
        )

    def test_mister_default_rom_root_is_mirrored_in_save_destination(self):
        app = self.make_app(
            {"mister_rom_root": "/media/fat/games/SNES/SMW Stream Tracker"}
        )
        app._resolve_local_rom_path = mock.Mock(
            return_value=(Path("Tortured Souls 3.sfc"), "test")
        )

        destination = app._mister_save_destination(
            {"title": "Tortured Souls 3"}
        )

        self.assertEqual(
            destination,
            "/media/fat/saves/SNES/SMW Stream Tracker/Tortured Souls 3.sav",
        )

    def test_raw_snes_save_payload_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "Mario A B C.sav"
            payload = bytes(range(256)) * 8
            source.write_bytes(payload)

            normalized, header_removed = (
                self.tracker.TrackerApp._normalized_snes_save_payload(source)
            )

            self.assertEqual(normalized, payload)
            self.assertFalse(header_removed)

    def test_512_byte_copier_header_is_removed_from_snes_save(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "headered.srm"
            payload = bytes(range(256)) * 8
            source.write_bytes((b"header" + bytes(506)) + payload)

            normalized, header_removed = (
                self.tracker.TrackerApp._normalized_snes_save_payload(source)
            )

            self.assertEqual(normalized, payload)
            self.assertTrue(header_removed)

    def test_non_sram_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "save-state.sav"
            source.write_bytes(b"not a raw SRAM file")

            with self.assertRaisesRegex(ValueError, "Save states"):
                self.tracker.TrackerApp._normalized_snes_save_payload(source)

    def test_mister_import_releases_core_verifies_bytes_and_relaunches(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._perform_mister_save_import
        )
        self.assertIn("_release_mister_save_for_import", source)
        self.assertIn("uploaded_payload != payload", source)
        self.assertIn("MiSTer could not commit the imported save file.", source)
        self.assertIn("_run_mister_game_launch(dict(game))", source)

    def test_mister_release_returns_to_menu_before_import(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._release_mister_save_for_import
        )
        self.assertIn("load_core menu.rbf", source)
        self.assertIn('"sync"', source)

    def test_fxpak_mounted_destination_uses_firmware_save_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            card_root = Path(temporary_directory) / "FXPAK"
            hacks = card_root / "All_Hacks"
            (card_root / "sd2snes").mkdir(parents=True)
            hacks.mkdir()
            app = self.make_app({"rom_builder_sd_folder": str(hacks)})

            destination = app._fxpak_mounted_save_destination(
                "Actual FXPAK Name.srm"
            )

            self.assertEqual(
                destination,
                card_root / "sd2snes" / "saves" / "Actual FXPAK Name.srm",
            )

    def test_shared_hack_menu_exposes_import_action(self):
        app = self.make_app()
        app._translate_ui_text = lambda text: text
        app.open_hack_details = mock.Mock()
        app._import_save_file_for_game = mock.Mock()
        menu = FakeMenu()

        added = app._add_hack_context_actions(
            menu,
            {"title": "Test Hack", "smwc_id": "1"},
        )

        self.assertTrue(added)
        self.assertEqual(
            [command["label"] for command in menu.commands],
            ["View Hack Details", "Import Save File"],
        )
        menu.commands[1]["command"]()
        app._import_save_file_for_game.assert_called_once_with(
            {"title": "Test Hack", "smwc_id": "1"}
        )

    def test_game_library_row_resolves_directly_to_import_capable_menu(self):
        class FakeTree:
            def __init__(self):
                self.selected = ""
                self.focused = ""

            def identify_row(self, _y):
                return "game::4"

            def selection_set(self, iid):
                self.selected = iid

            def focus(self, iid):
                self.focused = iid

        app = self.make_app()
        tree = FakeTree()
        game = {"title": "Library Hack", "smwc_id": "44"}
        app.game_library_widgets = {"tree": tree}
        app.game_library_games_by_iid = {"game::4": game}
        app._update_game_library_selection = mock.Mock()
        app._show_hack_details_context_menu = mock.Mock(return_value="break")
        event = SimpleNamespace(y=12)

        result = app._show_game_library_row_context_menu(event)

        self.assertEqual(result, "break")
        self.assertEqual(tree.selected, "game::4")
        self.assertEqual(tree.focused, "game::4")
        app._show_hack_details_context_menu.assert_called_once_with(
            event,
            game,
        )

    def test_game_library_has_visible_import_button_and_direct_binding(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        self.assertIn("self._show_game_library_row_context_menu", source)
        self.assertIn("self._import_selected_library_save_file", source)
        self.assertIn('text=self._translate_ui_text("Import Save File")', source)

    def test_game_library_platform_is_centered_selector_that_refreshes_rows(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._build_stream_desk_game_library
        )
        self.assertIn("values=PLATFORM_OPTIONS", source)
        self.assertIn('justify="center"', source)
        self.assertIn('"<<ComboboxSelected>>"', source)
        self.assertIn("self.platform_var.set(selected_platform)", source)
        self.assertIn(
            "ready_games[:] = games_ready_for_platform(selected_platform)",
            source,
        )

    def test_confirmation_explicitly_warns_about_backup_and_closing_game(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._import_save_file_for_game
        )
        self.assertIn("Make sure you have a backup", source)
        self.assertIn("Close the game/emulator", source)
        self.assertIn("renamed to match this hack", source)


if __name__ == "__main__":
    unittest.main()
