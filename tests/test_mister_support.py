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
        self.assertIn('index="0"', text)
        self.assertIn('path="SMW Stream Tracker/My Hack.sfc"', text)

    def test_mister_setup_strings_exist_in_every_language(self):
        for language in ("au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                for text in (
                    "Set Up MiSTer...",
                    "MiSTer Setup",
                    "Find & Set Up MiSTer",
                    "Install / Repair Support",
                    "Save & Select MiSTer",
                    "Looking for MiSTer on your network...",
                    "MiSTer is fully set up. The tracker found it, installed live tracking, created the game folders, enabled automatic login for this app, selected MiSTer, and verified the connection.",
                ):
                    self.assertIn(text, translations)


if __name__ == "__main__":
    unittest.main()
