import ast
import gc
import importlib.util
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
        "smw_tracker_fxpak_safe_upload_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FxpakSafeUploadNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_safe_title_names_every_emoji_and_keeps_readable_title(self):
        safe_title = self.tracker.rom_builder_fxpak_safe_title(
            "✨ Pokémon Adventure 🎮",
            "12345",
        )

        self.assertEqual(
            safe_title,
            "Sparkles Pokémon Adventure Video Game",
        )
        self.assertTrue(safe_title.isprintable())
        self.assertNotIn("✨", safe_title)
        self.assertNotIn("🎮", safe_title)

    def test_emoji_only_title_uses_readable_unicode_names(self):
        self.assertEqual(
            self.tracker.rom_builder_fxpak_safe_title("🐸🥣", "32897"),
            "Frog Face Bowl With Spoon",
        )

    def test_symbol_class_stopwatch_is_removed_from_fxpak_path(self):
        game = {
            "title": "⏱︎ Slow Motion Mario",
            "smwc_id": "39168",
        }

        self.assertEqual(
            self.tracker.rom_builder_fxpak_relative_rom_path(game).as_posix(),
            "S/Stopwatch Slow Motion Mario.sfc",
        )
        self.assertNotIn(
            "⏱",
            self.tracker.rom_builder_fxpak_safe_title(
                game["title"],
                game["smwc_id"],
            ),
        )

    def test_emoji_only_fxpak_path_keeps_catalog_title_unchanged(self):
        game = {
            "title": "🐸🥣",
            "smwc_id": "32897",
        }

        self.assertEqual(
            self.tracker.rom_builder_fxpak_relative_rom_path(game).as_posix(),
            "F/Frog Face Bowl With Spoon.sfc",
        )
        self.assertEqual(game["title"], "🐸🥣")

    def test_emoji_only_local_rom_remains_discoverable(self):
        game = {
            "title": "🐸🥣",
            "smwc_id": "32897",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            library_root = Path(temporary_directory)
            rom_path = library_root / "#" / "🐸🥣.sfc"
            rom_path.parent.mkdir()
            rom_path.write_bytes(b"existing-rom")

            existing_by_name = self.tracker.rom_builder_scan_existing_roms(
                library_root
            )
            exists, status, found_path = (
                self.tracker.rom_builder_existing_game(
                    game,
                    library_root,
                    existing_by_name,
                    {},
                    include_fxpak_mapping=False,
                )
            )

            self.assertTrue(exists)
            self.assertEqual(status, "Already in local library")
            self.assertEqual(Path(found_path), rom_path)

    def test_sd_copy_uses_safe_name_without_renaming_local_rom(self):
        game = {
            "title": "🌟 Amazing Hack 🎮",
            "smwc_id": "42",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            local_rom = root / "🌟 Amazing Hack 🎮.sfc"
            sd_root = root / "All_Hacks"
            local_rom.write_bytes(b"test-rom")
            sd_root.mkdir()

            destination, status = self.tracker.rom_builder_copy_rom_to_sd(
                local_rom,
                sd_root,
                game,
            )

            self.assertEqual(status, "copied")
            self.assertEqual(
                destination.relative_to(sd_root),
                Path("G") / "Glowing Star Amazing Hack Video Game.sfc",
            )
            self.assertEqual(destination.read_bytes(), b"test-rom")
            self.assertTrue(local_rom.exists())

    def test_download_usb_path_uses_fxpak_safe_path_builder(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        worker = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_filtered_hack_download_worker"
        )
        called_names = {
            node.func.id
            for node in ast.walk(worker)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        }

        self.assertIn("rom_builder_fxpak_relative_rom_path", called_names)

    def test_existing_emoji_rom_is_uploaded_instead_of_skipped(self):
        class DummyRoot:
            def after(self, _delay, callback):
                callback()

        class DummyWebSocket:
            def settimeout(self, _timeout):
                return None

            def close(self):
                return None

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_rom_path = root / "base.sfc"
            base_rom_path.write_bytes(b"base-rom")
            library_root = root / "library"
            local_rom = library_root / "#" / "🐸🥣.sfc"
            local_rom.parent.mkdir(parents=True)
            local_rom.write_bytes(b"existing-rom")
            game = {
                "title": "🐸🥣",
                "smwc_id": "32897",
                "local_rom_path": str(local_rom),
                "download_url": "https://example.invalid/unused.zip",
            }

            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.root = DummyRoot()
            app.config = {}
            app.downloader_cancel_event = self.tracker.threading.Event()
            app._post_downloader_progress = lambda *_args: None
            app._translate_ui_text = lambda text: text
            app._connect_fxpak_for_launch = (
                lambda *_args: (DummyWebSocket(), "FXPAK")
            )
            bridge_handoff = []
            pause_token = object()
            app._pause_tracker_bridge_for_fxpak_files = lambda: (
                bridge_handoff.append("paused") or pause_token
            )
            app._resume_tracker_bridge_after_fxpak_files = (
                lambda worker: bridge_handoff.append(
                    "resumed" if worker is pause_token else "wrong-worker"
                )
            )
            uploaded = {}

            def upload(_ws, source_path, remote_path):
                uploaded["source_name"] = Path(source_path).name
                uploaded["source_bytes"] = Path(source_path).read_bytes()
                uploaded["remote"] = remote_path
                return "uploaded"

            app._upload_rom_to_fxpak_usb = upload
            completed = {}
            app._finish_filtered_hack_download = (
                lambda results, *_args: completed.update(results=results)
            )

            app._filtered_hack_download_worker(
                [game],
                base_rom_path,
                library_root,
                None,
                "/All_Hacks",
                "ws://localhost:23074",
                "",
            )

            self.assertEqual(
                uploaded["source_name"],
                "Frog Face Bowl With Spoon.sfc",
            )
            self.assertEqual(uploaded["source_bytes"], b"existing-rom")
            self.assertTrue(local_rom.exists())
            self.assertEqual(
                uploaded["remote"],
                "/All_Hacks/F/Frog Face Bowl With Spoon.sfc",
            )
            self.assertEqual(
                completed["results"][0]["fxpak_path"],
                "/All_Hacks/F/Frog Face Bowl With Spoon.sfc",
            )
            self.assertEqual(
                completed["results"][0]["usb_upload_status"],
                "uploaded",
            )
            self.assertEqual(bridge_handoff, ["paused", "resumed"])

    def test_usb_destination_error_uses_blue_app_popup(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        expected = '''self._show_localized_info(
                    "Hack Downloader",
                    (
                        "The FXPAK Pro USB destination is not ready. "'''

        self.assertIn(expected, source)

    def test_download_completion_saves_usb_mapping_without_worker_helper(self):
        class DummyWidget:
            def configure(self, **_values):
                return None

        class DummyVariable:
            def __init__(self):
                self.value = ""

            def set(self, value):
                self.value = value

        class DummyDatabase:
            def update_catalog_rom_path(self, *_args, **_kwargs):
                return None

            def save_rom_mapping(self, *_args, **_kwargs):
                return None

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.downloader_widgets = {
            "download_button": DummyWidget(),
            "cancel_button": DummyWidget(),
            "status_var": DummyVariable(),
        }
        app.config = {"fxpak_rom_mappings": {}}
        app.hack_catalog = [{"smwc_id": "123", "title": "Test Hack"}]
        app.stats_db = DummyDatabase()
        app.worker = None
        app.status_var = DummyVariable()
        app._translate_ui_text = lambda text: text
        app._refresh_downloader_preview = lambda **_values: None
        # Intentionally omit fxpak_path_map to reproduce the packaged-build
        # failure that occurred when the first USB mapping was completed.
        with mock.patch.object(self.tracker, "save_config"):
            app._finish_filtered_hack_download(
                [
                    {
                        "status": "ok",
                        "smwc_id": "123",
                        "fxpak_path": "/All_Hacks/T/Test Hack.sfc",
                    }
                ],
                {},
                True,
                "",
                Path("C:/TestLibrary"),
                None,
                "/All_Hacks",
            )

        self.assertEqual(
            app.fxpak_path_map["smwc:123"],
            "/All_Hacks/T/Test Hack.sfc",
        )
        self.assertEqual(
            app.config["fxpak_rom_mappings"]["smwc:123"],
            "/All_Hacks/T/Test Hack.sfc",
        )

    def test_saved_safe_filename_alias_displays_original_catalog_title(self):
        worker = self.tracker.TrackerWorker.__new__(
            self.tracker.TrackerWorker
        )
        game = {
            "catalog_key": "SMWC:9876",
            "mapping_key": "SMWC:9876",
            "smwc_id": "9876",
            "title": "🎮✨",
            "author": "Creator",
            "total_exits": 5,
        }
        worker.config = {}
        worker.fxpak_path_map = {}
        worker.hack_catalog = [dict(game)]
        worker.database = {}

        worker.register_fxpak_mapping(
            game,
            "/All_Hacks/V/Video Game Sparkles.sfc",
        )
        matched, _method = worker.find_hack(
            "Video Game Sparkles",
            worker.database,
        )

        self.assertIsNotNone(matched)
        self.assertEqual(matched["title"], "🎮✨")

    def test_saved_readable_alias_is_not_offered_as_missing_again(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        game = {
            "title": "🐸🥣",
            "smwc_id": "32897",
        }
        safe_path = "/All_Hacks/F/Frog Face Bowl With Spoon.sfc"
        app.config = {
            "fxpak_rom_mappings": {
                "smwc:32897": safe_path,
            }
        }
        app.fxpak_path_map = {}

        self.assertTrue(app._catalog_game_has_fxpak_alias_mapping(game))
        preview_source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "and not self._catalog_game_has_fxpak_alias_mapping(\n"
            "                    display_game\n"
            "                )",
            preview_source,
        )

    def test_stale_emoji_mapping_still_requests_readable_alias_repair(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        game = {
            "title": "🐸🥣",
            "smwc_id": "32897",
            "rom_path": "/All_Hacks/#/🐸🥣.sfc",
        }
        app.config = {"fxpak_rom_mappings": {}}
        app.fxpak_path_map = {}

        self.assertFalse(app._catalog_game_has_fxpak_alias_mapping(game))

    def test_launcher_finds_readable_alias_for_emoji_catalog_title(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        game = {
            "title": "\U0001f438\U0001f963",
            "smwc_id": "32897",
            "rom_path": "/All_Hacks/X/Old Missing Alias.sfc",
        }
        visited = []

        def list_folder(_websocket, folder):
            visited.append(folder)
            if folder == "/All_Hacks/F":
                return ["Frog Face Bowl With Spoon.sfc"]
            return []

        app._list_fxpak_folder = list_folder
        path, method = app._resolve_fxpak_rom_path(
            object(),
            game,
            "/All_Hacks",
        )

        self.assertIn("/All_Hacks/F", visited)
        self.assertIn("/All_Hacks/X", visited)
        self.assertEqual(
            path,
            "/All_Hacks/F/Frog Face Bowl With Spoon.sfc",
        )
        self.assertEqual(method, "exact SD-card title match")
        self.assertEqual(game["title"], "\U0001f438\U0001f963")

    def test_launcher_repairs_missing_emoji_alias_from_local_rom(self):
        class DummyWebSocket:
            def close(self):
                return None

        with tempfile.TemporaryDirectory() as temporary_directory:
            local_rom = Path(temporary_directory) / "\U0001f438\U0001f963.sfc"
            local_rom.write_bytes(b"patched-rom")
            game = {
                "title": "\U0001f438\U0001f963",
                "smwc_id": "32897",
                "local_rom_path": str(local_rom),
            }
            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.config = {}
            app._ensure_qusb2snes_running = lambda *_args: None
            app._connect_fxpak_for_launch = (
                lambda *_args: (DummyWebSocket(), "FXPAK Pro")
            )
            app._resolve_fxpak_rom_path = mock.Mock(
                side_effect=FileNotFoundError("missing")
            )
            uploaded = {}

            def upload(_websocket, source_path, remote_path):
                uploaded["source_name"] = Path(source_path).name
                uploaded["source_bytes"] = Path(source_path).read_bytes()
                uploaded["remote"] = remote_path
                return "uploaded"

            app._upload_rom_to_fxpak_usb = upload
            requests = []
            app._fxpak_request = (
                lambda _websocket, command, operands=None: requests.append(
                    (command, operands)
                )
            )

            with mock.patch.object(self.tracker.time, "sleep"):
                result = app._run_direct_fxpak_launcher(
                    game,
                    {
                        "WebSocketURL": "ws://localhost:23074",
                        "DeviceName": "",
                        "SDRoot": "/All_Hacks",
                    },
                )

            expected_path = "/All_Hacks/F/Frog Face Bowl With Spoon.sfc"
            self.assertEqual(
                uploaded["source_name"],
                "Frog Face Bowl With Spoon.sfc",
            )
            self.assertEqual(uploaded["source_bytes"], b"patched-rom")
            self.assertTrue(local_rom.exists())
            self.assertEqual(uploaded["remote"], expected_path)
            self.assertEqual(result["path"], expected_path)
            self.assertIn(("Boot", [expected_path]), requests)

    def test_database_uses_smwc_id_as_canonical_alias_mapping(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = self.tracker.TrackerDatabase(
                Path(temporary_directory) / "tracker.db"
            )
            game = {
                "title": "\U0001f438\U0001f963",
                "smwc_id": "32897",
                "mapping_key": "TITLE:old emoji title",
            }
            remote_path = "/All_Hacks/F/Frog Face Bowl With Spoon.sfc"

            database.save_rom_mapping(game, remote_path)

            connection = database.connect()
            try:
                row = connection.execute(
                    "SELECT map_key, smwc_id, title, rom_path "
                    "FROM rom_mappings"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(row["map_key"], "SMWC:32897")
            self.assertEqual(row["smwc_id"], "32897")
            self.assertEqual(row["title"], "\U0001f438\U0001f963")
            self.assertEqual(row["rom_path"], remote_path)
            del connection
            del database
            gc.collect()


if __name__ == "__main__":
    unittest.main()
