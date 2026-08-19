import importlib.util
import inspect
import json
from pathlib import Path
import queue
import sys
from types import SimpleNamespace
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_mister_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeWebSocket:
    def __init__(self, devices):
        self.devices = list(devices)
        self.sent = []
        self.closed = False

    def send(self, payload):
        self.sent.append(json.loads(payload))

    def recv(self):
        return json.dumps({"Results": self.devices})

    def close(self):
        self.closed = True


class MisterSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_mister_is_a_first_class_platform(self):
        self.assertIn("MiSTer", self.tracker.PLATFORM_OPTIONS)
        self.assertIn("mister", self.tracker.PLATFORM_DEVICE_HINTS["MiSTer"])
        self.assertEqual(
            self.tracker.PLATFORM_ASSET_FILES["MiSTer"],
            "mister.png",
        )
        self.assertEqual(
            self.tracker.DEFAULT_CONFIG["mister_rom_root"],
            "/media/fat/games/SNES/SMW Stream Tracker",
        )

    def test_mister_uses_the_transparent_cat_asset_not_the_old_badge(self):
        asset_path = MODULE_PATH.parent / "platform_assets" / "mister.png"
        self.assertTrue(asset_path.is_file())
        with self.tracker.Image.open(asset_path) as cat_image:
            self.assertEqual(cat_image.mode, "RGBA")
            self.assertEqual(cat_image.getpixel((0, 0))[3], 0)

        image_loader_source = inspect.getsource(
            self.tracker.TrackerApp._load_brand_assets
        )
        self.assertNotIn("mister_draw", image_loader_source)
        self.assertNotIn('mister_draw.text', image_loader_source)

    def test_mister_host_accepts_friendly_and_url_values(self):
        self.assertEqual(self.tracker.normalize_mister_host("MiSTer"), "mister")
        self.assertEqual(
            self.tracker.normalize_mister_host("ssh://192.168.1.44:22/path"),
            "192.168.1.44",
        )
        self.assertEqual(
            self.tracker.mister_websocket_url({"mister_host": "192.168.1.44"}),
            "ws://192.168.1.44:23074",
        )

    def test_selected_mister_uses_remote_bridge_instead_of_local_sni(self):
        config = dict(self.tracker.DEFAULT_CONFIG)
        config.update(
            {
                "selected_platform": "MiSTer",
                "mister_host": "10.0.0.25",
                "platform_websocket_url": "ws://localhost:23074",
            }
        )
        self.assertEqual(
            self.tracker.selected_platform_websocket_url(config),
            "ws://10.0.0.25:23074",
        )

    def test_retroarch_ignores_stale_mister_websocket_url(self):
        config = dict(self.tracker.DEFAULT_CONFIG)
        config.update(
            {
                "selected_platform": "RetroArch",
                "mister_host": "192.168.50.41",
                "platform_websocket_url": "ws://192.168.50.41:23074",
                "fxpak_websocket_url": "ws://localhost:23074",
            }
        )
        self.assertEqual(
            self.tracker.selected_platform_websocket_url(config),
            "ws://localhost:23074",
        )

    def test_mister_support_repairs_old_uartmode_and_waits_for_tracking(self):
        self.assertIn("d4469d2a3d", self.tracker.MISTER_UARTMODE_DOWNLOAD_URL)
        self.assertEqual(len(self.tracker.MISTER_UARTMODE_DOWNLOAD_SHA256), 64)
        source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_support
        )
        self.assertIn("/usr/sbin/uartmode.smwtracker.bak", source)
        self.assertIn("/usr/sbin/uartmode", source)
        self.assertIn("/media/fat/.snid-smwtracker-new", source)
        self.assertIn(
            "mv -f /media/fat/.snid-smwtracker-new /media/fat/snid",
            source,
        )
        self.assertLess(
            source.index("uartmode 0 || true"),
            source.index(
                "mv -f /media/fat/.snid-smwtracker-new /media/fat/snid"
            ),
        )
        self.assertIn("nohup uartmode 6", source)
        self.assertIn("self._test_tcp_port(host, 23074)", source)

    def test_experimental_mister_binary_matches_the_embedded_safety_hash(self):
        binary_path = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "bin_experimental"
            / "MiSTer-SMW-Virtual-States"
        )
        self.assertTrue(binary_path.is_file())
        import hashlib

        self.assertEqual(
            hashlib.sha256(binary_path.read_bytes()).hexdigest(),
            self.tracker.MISTER_VIRTUAL_STATES_BINARY_SHA256,
        )

    def test_experimental_mister_base_matches_the_official_release(self):
        base_path = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "releases"
            / "MiSTer_20260707"
        )
        self.assertTrue(base_path.is_file())
        import hashlib

        self.assertEqual(
            hashlib.sha256(base_path.read_bytes()).hexdigest(),
            self.tracker.MISTER_VIRTUAL_STATES_BASE_SHA256,
        )
        self.assertEqual(
            self.tracker.MISTER_VIRTUAL_STATES_BASE_VERSION,
            "20260707",
        )

    def test_virtual_state_bridge_waits_before_restoring_native_slot_four(self):
        source_path = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "user_io.cpp"
        )
        source = source_path.read_text(encoding="utf-8")
        load_start = source.index("static int ss_virtual_state_load")
        save_start = source.index("static int ss_virtual_state_save")
        load_source = source[load_start:save_start]
        self.assertIn(
            "ss_schedule_native_slot_four_restore(SMW_VIRTUAL_LOAD_GUARD_MS)",
            load_source,
        )
        self.assertNotIn("ss_restore_native_slot_four();", load_source)
        self.assertIn("ss_virtual_restore_pending", source)
        self.assertIn("ss_virtual_state_busy()", source)
        self.assertIn("slot >= 5 && slot <= 11", source)
        self.assertIn("key >= KEY_F5 && key <= KEY_F10", source)
        self.assertIn("if (key == KEY_F11) return 11", source)
        self.assertNotIn("if (key == KEY_F12) return 12", source)
        self.assertNotIn("ss_virtual_f12_held", source)
        self.assertIn("int virtual_shortcut = virtual_slot;", source)
        self.assertIn("%.*s%d%s", source)

    def test_experimental_build_defaults_to_the_compatible_20260707_source(self):
        build_script = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "build_mister_experimental.ps1"
        ).read_text(encoding="utf-8-sig")
        self.assertIn(
            '[string]$SourceDirectory = "Main_MiSTer_20260707"',
            build_script,
        )

    def test_normal_windows_build_contains_virtual_state_support(self):
        build_spec = (MODULE_PATH.parent / "SMWStreamTracker.spec").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("MiSTer-SMW-Virtual-States", build_spec)
        self.assertIn("mister_experimental", build_spec)

    def test_tracker_update_can_replace_only_its_own_mister_build(self):
        original_hash = "1" * 64
        installed_hash = "2" * 64
        next_hash = "3" * 64
        manifest = {
            "original_sha256": original_hash,
            "experimental_sha256": installed_hash,
        }
        allowed = self.tracker.mister_virtual_states_allowed_current_hashes(
            manifest,
            next_hash,
        )
        self.assertEqual(
            allowed,
            frozenset({original_hash, installed_hash, next_hash}),
        )
        self.assertNotIn("4" * 64, allowed)

    def test_mister_update_is_detected_before_custom_main_is_installed(self):
        install_source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_virtual_states
        )
        self.assertIn("current_sha256", install_source)
        self.assertIn(
            "mister_virtual_states_allowed_current_hashes",
            install_source,
        )
        self.assertLess(
            install_source.index("current_sha256 not in allowed_current_hashes"),
            install_source.index("staged_binary ="),
        )
        self.assertIn(
            "original_sha256 != MISTER_VIRTUAL_STATES_BASE_SHA256",
            install_source,
        )
        self.assertLess(
            install_source.index(
                "original_sha256 != MISTER_VIRTUAL_STATES_BASE_SHA256"
            ),
            install_source.index("staged_binary ="),
        )

    def test_experimental_restore_path_is_hash_bound_and_rejects_tampering(self):
        original_hash = "a" * 64
        backup_path = self.tracker.mister_virtual_states_backup_path(
            original_hash
        )
        self.assertEqual(
            self.tracker.mister_virtual_states_manifest_backup_path(
                {
                    "original_sha256": original_hash,
                    "backup_path": backup_path,
                }
            ),
            backup_path,
        )
        with self.assertRaises(ValueError):
            self.tracker.mister_virtual_states_manifest_backup_path(
                {
                    "original_sha256": original_hash,
                    "backup_path": "/media/fat/MiSTer",
                }
            )

    def test_experimental_install_and_restore_keep_an_exact_backup(self):
        install_source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_virtual_states
        )
        restore_source = inspect.getsource(
            self.tracker.TrackerApp._restore_mister_before_virtual_states
        )
        self.assertIn("/media/fat/MiSTer", install_source)
        self.assertIn("original_sha256", install_source)
        self.assertIn("backup_path", install_source)
        self.assertIn("MISTER_VIRTUAL_STATES_BINARY_SHA256", install_source)
        self.assertIn("ldd /media/fat/.MiSTer-smw-virtual-states-new", install_source)
        self.assertIn("not found|version .* not found", install_source)
        self.assertLess(
            install_source.index("ldd /media/fat/.MiSTer-smw-virtual-states-new"),
            install_source.index(
                "mv -f /media/fat/.MiSTer-smw-virtual-states-new"
            ),
        )
        self.assertIn("mister_virtual_states_manifest_backup_path", restore_source)
        self.assertIn("original_sha256", restore_source)
        self.assertIn("MISTER_VIRTUAL_STATES_MARKER", restore_source)

    def test_local_mister_scan_is_bounded_to_the_local_subnet(self):
        candidates = self.tracker.mister_local_scan_candidates(
            ["192.168.50.229"]
        )
        self.assertEqual(len(candidates), 253)
        self.assertIn("192.168.50.1", candidates)
        self.assertIn("192.168.50.254", candidates)
        self.assertNotIn("192.168.50.229", candidates)

    def test_automatic_discovery_positively_identifies_mister(self):
        client = mock.Mock()
        fake_app = SimpleNamespace(
            config={"mister_host": "MiSTer"},
            _tcp_port_is_open=lambda *_args, **_kwargs: True,
            _open_mister_ssh_client=lambda *_args, **_kwargs: client,
            _verified_mister_peer=lambda _client: "192.168.50.229",
            _mister_host_key_fingerprint=lambda _client: "SHA256:test",
            _remember_mister_host_key=mock.Mock(),
            _set_optional_install_status=mock.Mock(),
        )

        host, fingerprint = self.tracker.TrackerApp._discover_mister_host(
            fake_app,
            "MiSTer",
            "root",
            22,
            "1",
            mock.Mock(),
        )

        self.assertEqual(host, "192.168.50.229")
        self.assertEqual(fingerprint, "SHA256:test")
        fake_app._remember_mister_host_key.assert_called_once_with(client)
        client.close.assert_called_once()

    def test_one_click_setup_installs_persistent_login_and_verifies_it(self):
        setup_source = inspect.getsource(
            self.tracker.TrackerApp.open_mister_setup
        )
        key_source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_app_ssh_key
        )
        self.assertIn("_discover_mister_host", setup_source)
        self.assertIn("_install_mister_support", setup_source)
        self.assertIn("_verified_mister_peer(key_client)", setup_source)
        self.assertIn("mister_id_rsa", key_source)
        self.assertIn("authorized_keys", key_source)
        self.assertNotIn("mister_session_password\"]", key_source)

    def test_worker_selects_mister_device(self):
        config = dict(self.tracker.DEFAULT_CONFIG)
        config["selected_platform"] = "MiSTer"
        worker = self.tracker.TrackerWorker(config, queue.Queue())
        fake_socket = FakeWebSocket(["RetroArch", "MiSTer"])
        worker.try_connect_websocket = lambda: fake_socket
        worker.stop_event.wait = lambda _timeout: False

        connected_socket, device = worker.connect_to_fxpak()

        self.assertIs(connected_socket, fake_socket)
        self.assertEqual(device, "MiSTer")
        self.assertIn(
            {"Opcode": "Attach", "Space": "SNES", "Operands": ["MiSTer"]},
            fake_socket.sent,
        )

    def test_missing_mister_bridge_does_not_launch_local_connection_apps(self):
        config = dict(self.tracker.DEFAULT_CONFIG)
        config.update(
            {
                "selected_platform": "MiSTer",
                "mister_host": "10.0.0.25",
                "sni_path": "C:/Tools/sni.exe",
            }
        )
        worker = self.tracker.TrackerWorker(config, queue.Queue())
        with (
            mock.patch.object(
                worker,
                "try_connect_websocket",
                side_effect=OSError("offline"),
            ),
            mock.patch.object(
                self.tracker,
                "launch_local_application",
            ) as launcher,
        ):
            with self.assertRaisesRegex(RuntimeError, "MiSTer is not responding"):
                worker.start_qusb2snes_if_needed()
        launcher.assert_not_called()

    def test_mister_filename_removes_emoji_but_keeps_identity(self):
        game = {"title": "🐸 🍜", "smwc_id": "12345"}
        filename = self.tracker.mister_safe_rom_filename(game, ".sfc")
        filename.encode("ascii")
        self.assertTrue(filename.endswith(".sfc"))
        self.assertNotIn("🐸", filename)
        self.assertNotIn("🍜", filename)

    def test_mgl_targets_snes_core_and_relative_rom(self):
        text = self.tracker.mister_mgl_text(
            "SMW Stream Tracker/My Hack.sfc"
        )
        self.assertIn("_Console/SNES", text)
        self.assertNotIn("RA_SNES", text)
        self.assertIn('index="0"', text)
        self.assertIn('path="SMW Stream Tracker/My Hack.sfc"', text)

    def test_mgl_can_target_the_official_retroachievements_snes_core(self):
        text = self.tracker.mister_mgl_text(
            "SMW Stream Tracker/My Hack.sfc",
            retroachievements=True,
        )
        self.assertIn("_RA_Cores/Cores/SNES", text)
        self.assertIn('<setname same_dir="1">RA_SNES</setname>', text)
        self.assertIn('path="SMW Stream Tracker/My Hack.sfc"', text)

    def test_mister_setup_strings_exist_in_every_language(self):
        for language in ("au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                for text in (
                    "Set Up MiSTer...",
                    "MiSTer Setup",
                    "Find & Set Up MiSTer",
                    "Install Virtual Save State Slots",
                    "Save & Select MiSTer",
                    "Looking for MiSTer on your network...",
                    "MiSTer is fully set up. The tracker found it, installed live tracking and save states 5–11, created the game folders, enabled automatic login for this app, selected MiSTer, and verified the connection. MiSTer is restarting.",
                    "MiSTer Save States 5–11",
                    "Restore Previous MiSTer Version",
                    "Restore the Previous MiSTer Version?",
                    "Checking compatibility with this MiSTer...",
                    "This MiSTer save-state build is not compatible with the system files on this MiSTer. The current MiSTer file was not changed.",
                    "MiSTer support and save states 5–11 are installed. MiSTer is restarting. In the SNES core, use Alt+F5 through Alt+F11 to save and F5 through F11 to load states 5–11. F12 still opens the MiSTer menu.",
                    "Your exact previous MiSTer file was restored and states 5–11 were disabled. MiSTer is restarting.",
                ):
                    self.assertIn(text, translations)

    def test_every_mister_save_state_message_is_translated(self):
        language_columns = {
            "au": 1,
            "es": 2,
            "fr": 3,
            "de": 4,
            "pt-BR": 5,
        }
        for row in self.tracker._MISTER_EXPERIMENT_LOCALIZATION_ROWS:
            english_text = row[0]
            for language, column in language_columns.items():
                with self.subTest(text=english_text, language=language):
                    self.assertEqual(
                        self.tracker.UI_TRANSLATIONS[language][english_text],
                        row[column],
                    )

    def test_normal_mister_setup_installs_states_without_experimental_button(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        self.assertEqual(setup_source.count("self._install_mister_virtual_states("), 2)
        self.assertIn("Install Virtual Save State Slots", setup_source)
        self.assertIn("Find & Set Up MiSTer", setup_source)
        self.assertNotIn("Install Experimental States", setup_source)
        self.assertNotIn("install_experimental_button", setup_source)
        self.assertIn(
            "restore_original_button = self._make_action_button(\n"
            "            buttons,",
            setup_source,
        )
        self.assertIn(
            "install_button = self._make_action_button(\n"
            "            virtual_states_buttons,",
            setup_source,
        )


if __name__ == "__main__":
    unittest.main()
