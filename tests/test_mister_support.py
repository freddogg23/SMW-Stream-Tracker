import importlib.util
import hashlib
import io
import inspect
import json
from pathlib import Path
import queue
import shlex
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
        self.assertFalse(
            self.tracker.DEFAULT_CONFIG["rom_builder_upload_to_mister"]
        )

    def test_completed_levels_request_the_tracker_installed_sram_flush(self):
        self.assertTrue(
            self.tracker.DEFAULT_CONFIG["mister_save_sram_after_level"]
        )
        self.assertEqual(
            self.tracker.MISTER_PERIODIC_SRAM_SAVE_INTERVAL_MS,
            5 * 60 * 1000,
        )
        flush_source = inspect.getsource(
            self.tracker.TrackerApp._flush_mister_sram_in_background
        )
        schedule_source = inspect.getsource(
            self.tracker.TrackerApp._schedule_mister_sram_save_after_level
        )
        event_source = inspect.getsource(self.tracker.TrackerApp.process_events)
        worker_source = inspect.getsource(
            self.tracker.TrackerWorker.send_level_completion_event
        )
        self.assertIn("smw_sram_save", flush_source)
        self.assertIn("/tmp/smw_sram_save_ack", flush_source)
        self.assertIn('acknowledgement == "requested"', flush_source)
        self.assertIn('event_data.get("mister_host")', schedule_source)
        self.assertIn("mister_host=normalize_mister_host", worker_source)
        self.assertIn('event_type == "level_complete"', event_source)
        self.assertIn("_schedule_mister_sram_save_after_level", event_source)

        main_source = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "input.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn('!strcmp(cmd, "smw_sram_save")', main_source)
        self.assertIn('user_io_status_set("[13]", 1)', main_source)
        self.assertIn('result = "saved\\n"', main_source)

        user_io_source = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "user_io.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn("smw_sram_write_generation++", user_io_source)

        binary_path = (
            MODULE_PATH.parent
            / "experiments"
            / "mister_instant_states"
            / "Main_MiSTer_20260707"
            / "bin_experimental"
            / "MiSTer-SMW-Virtual-States"
        )
        self.assertEqual(
            hashlib.sha256(binary_path.read_bytes()).hexdigest(),
            self.tracker.MISTER_VIRTUAL_STATES_BINARY_SHA256,
        )

    def test_sram_save_uses_the_console_that_emitted_the_completion(self):
        class FakeRoot:
            def __init__(self):
                self.delay = None
                self.callback = None

            def after(self, delay, callback):
                self.delay = delay
                self.callback = callback
                return "save-after"

            def after_cancel(self, _after_id):
                return None

        app = object.__new__(self.tracker.TrackerApp)
        app.root = FakeRoot()
        app.startup_check = False
        app.config = {
            "selected_platform": "MiSTer",
            "mister_save_sram_after_level": True,
            "mister_host": "192.168.50.116",
            "mister_ssh_user": "root",
            "mister_ssh_port": 22,
            "active_mister_profile": "Saved console",
        }
        app.mister_sram_save_after_id = None
        app.mister_sram_save_thread = None
        app.mister_sram_save_generation = 0
        app.mister_sram_save_last_requested_at = 0.0
        app.mister_sram_save_target = {}

        app._schedule_mister_sram_save_after_level(
            {
                "mister_host": "192.168.50.11",
                "mister_ssh_user": "root",
                "mister_ssh_port": 22,
                "mister_profile": "Online console",
            }
        )

        self.assertEqual(
            app.mister_sram_save_target,
            {
                "host": "192.168.50.11",
                "user": "root",
                "port": 22,
                "profile": "Online console",
                "reason": "safe gameplay boundary",
            },
        )
        self.assertEqual(app.mister_sram_save_after_id, "save-after")
        self.assertIsNotNone(app.root.callback)

    def test_sram_save_transition_reasons_are_event_driven(self):
        reasons = self.tracker.mister_sram_transition_reasons(
            previous_mode=self.tracker.LEVEL_MODE,
            mode=self.tracker.LEVEL_MODE,
            previous_midway=0,
            midway=1,
            session_active=True,
        )
        self.assertEqual(reasons, ("midpoint or checkpoint reached",))

        reasons = self.tracker.mister_sram_transition_reasons(
            previous_mode=self.tracker.LEVEL_MODE,
            mode=self.tracker.OVERWORLD_MODE,
            previous_midway=1,
            midway=0,
            session_active=True,
        )
        self.assertEqual(reasons, ("returned to the overworld",))

        self.assertEqual(
            self.tracker.mister_sram_transition_reasons(
                previous_mode=None,
                mode=self.tracker.OVERWORLD_MODE,
                previous_midway=None,
                midway=0,
                session_active=True,
            ),
            (),
        )
        self.assertEqual(
            self.tracker.mister_sram_transition_reasons(
                previous_mode=self.tracker.LEVEL_MODE,
                mode=self.tracker.OVERWORLD_MODE,
                previous_midway=0,
                midway=1,
                session_active=False,
            ),
            (),
        )

    def test_worker_sram_event_keeps_reason_and_exact_profile(self):
        events = queue.Queue()
        worker = self.tracker.TrackerWorker(
            {
                "selected_platform": "MiSTer",
                "mister_save_sram_after_level": True,
                "mister_host": "192.168.50.145",
                "mister_ssh_user": "root",
                "mister_ssh_port": 2222,
                "active_mister_profile": "Second MiSTer",
            },
            events,
        )
        worker.send_mister_sram_save_event("returned to the overworld")
        event = events.get_nowait()
        self.assertEqual(event["type"], "mister_sram_save")
        self.assertEqual(event["reason"], "returned to the overworld")
        self.assertEqual(event["mister_host"], "192.168.50.145")
        self.assertEqual(event["mister_ssh_port"], 2222)
        self.assertEqual(event["mister_profile"], "Second MiSTer")

    def test_periodic_sram_save_runs_only_during_active_mister_play(self):
        class FakeRoot:
            def __init__(self):
                self.delay = None
                self.callback = None

            def after(self, delay, callback):
                self.delay = delay
                self.callback = callback
                return "periodic-after"

            def after_cancel(self, _after_id):
                return None

        app = object.__new__(self.tracker.TrackerApp)
        app.root = FakeRoot()
        app.mister_sram_periodic_after_id = None
        app.connection_is_connected = True
        app.worker = SimpleNamespace(game_started=True)
        app.config = {
            "selected_platform": "MiSTer",
            "mister_save_sram_after_level": True,
        }
        app._schedule_mister_sram_save_after_level = mock.Mock()

        app._arm_mister_periodic_sram_save()
        self.assertEqual(
            app.root.delay,
            self.tracker.MISTER_PERIODIC_SRAM_SAVE_INTERVAL_MS,
        )
        app.root.callback()
        app._schedule_mister_sram_save_after_level.assert_called_once_with(
            {"reason": "five-minute interval"}
        )

    def test_mister_rom_root_stays_inside_the_snes_sd_folder(self):
        self.assertEqual(
            self.tracker.normalize_mister_rom_root(
                "/media/fat/games/SNES/My Hacks"
            ),
            "/media/fat/games/SNES/My Hacks",
        )
        with self.assertRaises(ValueError):
            self.tracker.normalize_mister_rom_root(
                "/media/fat/games/SNES/../../config"
            )
        with self.assertRaises(ValueError):
            self.tracker.normalize_mister_rom_root(
                "/media/fat/games/Genesis"
            )

    def test_mister_sd_upload_is_verified_and_atomic(self):
        class FakeSftp:
            def __init__(self):
                self.files = {}
                self.directories = {
                    "/",
                    "/media",
                    "/media/fat",
                    "/media/fat/games",
                    "/media/fat/games/SNES",
                }

            def stat(self, path):
                if path in self.files:
                    return SimpleNamespace(st_size=len(self.files[path]))
                if path in self.directories:
                    return SimpleNamespace(st_size=0)
                raise OSError(path)

            def mkdir(self, path):
                self.directories.add(path)

            def put(self, local_path, remote_path):
                self.files[remote_path] = Path(local_path).read_bytes()

            def open(self, path, mode):
                if mode != "rb" or path not in self.files:
                    raise OSError(path)
                import io

                return io.BytesIO(self.files[path])

            def remove(self, path):
                if path not in self.files:
                    raise OSError(path)
                del self.files[path]

            def posix_rename(self, source, destination):
                self.files[destination] = self.files.pop(source)

        app = object.__new__(self.tracker.TrackerApp)
        sftp = FakeSftp()
        payload = b"verified-rom" * 64
        with tempfile.TemporaryDirectory() as temporary_directory:
            local_rom = Path(temporary_directory) / "Hack.sfc"
            local_rom.write_bytes(payload)
            remote_path, status = app._upload_rom_to_mister_sd(
                mock.Mock(),
                sftp,
                local_rom,
                self.tracker.MISTER_DEFAULT_ROM_ROOT,
                {"title": "Hack", "smwc_id": "123"},
            )
            self.assertEqual(status, "uploaded")
            self.assertEqual(sftp.files[remote_path], payload)
            self.assertNotIn(remote_path + ".smwtracker-upload", sftp.files)

            repeated_path, repeated_status = app._upload_rom_to_mister_sd(
                mock.Mock(),
                sftp,
                local_rom,
                self.tracker.MISTER_DEFAULT_ROM_ROOT,
                {"title": "Hack", "smwc_id": "123"},
            )
            self.assertEqual(repeated_path, remote_path)
            self.assertEqual(repeated_status, "already_on_mister")

    def test_mister_bulk_upload_reuses_inventory_and_skips_existing_rom(self):
        class FakeSftp:
            def __init__(self):
                self.files = {}
                self.read_count = 0
                self.stat_count = 0
                self.list_count = 0
                self.directories = {
                    "/",
                    "/media",
                    "/media/fat",
                    "/media/fat/games",
                    "/media/fat/games/SNES",
                }

            def stat(self, path):
                self.stat_count += 1
                if path in self.files:
                    return SimpleNamespace(st_size=len(self.files[path]))
                if path in self.directories:
                    return SimpleNamespace(st_size=0)
                raise OSError(path)

            def mkdir(self, path):
                self.directories.add(path)

            def listdir_attr(self, path):
                self.list_count += 1
                prefix = path.rstrip("/") + "/"
                return [
                    SimpleNamespace(
                        filename=remote_path[len(prefix):],
                        st_mode=0,
                    )
                    for remote_path in self.files
                    if remote_path.startswith(prefix)
                    and "/" not in remote_path[len(prefix):]
                ]

            def put(self, local_path, remote_path, *, confirm=True):
                self.files[remote_path] = Path(local_path).read_bytes()

            def open(self, path, mode):
                if mode != "rb" or path not in self.files:
                    raise OSError(path)
                self.read_count += 1
                return io.BytesIO(self.files[path])

            def remove(self, path):
                if path not in self.files:
                    raise OSError(path)
                del self.files[path]

            def posix_rename(self, source, destination):
                self.files[destination] = self.files.pop(source)

        class FakeChannel:
            @staticmethod
            def recv_exit_status():
                return 0

        class FakeStream(io.BytesIO):
            def __init__(self, payload=b""):
                super().__init__(payload)
                self.channel = FakeChannel()

        class FakeClient:
            def __init__(self, sftp):
                self.sftp = sftp
                self.commands = []

            def exec_command(self, command, timeout=120):
                self.commands.append(command)
                remote_path = shlex.split(command)[1]
                digest = hashlib.sha256(self.sftp.files[remote_path]).hexdigest()
                return (
                    FakeStream(),
                    FakeStream(f"{digest}  {remote_path}\n".encode("ascii")),
                    FakeStream(),
                )

        app = object.__new__(self.tracker.TrackerApp)
        sftp = FakeSftp()
        client = FakeClient(sftp)
        payload = b"fast-verified-rom" * 256
        with tempfile.TemporaryDirectory() as temporary_directory:
            local_rom = Path(temporary_directory) / "Fast Hack.sfc"
            local_rom.write_bytes(payload)
            remote_path, status = app._upload_rom_to_mister_sd(
                client,
                sftp,
                local_rom,
                self.tracker.MISTER_DEFAULT_ROM_ROOT,
                {"title": "Fast Hack", "smwc_id": "456"},
            )
            first_directory_stat_count = sftp.stat_count
            local_rom.write_bytes(b"a-newer-local-rom-that-must-not-replace-it")
            with mock.patch.object(
                self.tracker,
                "file_sha256",
                side_effect=AssertionError(
                    "an existing MiSTer ROM must not be rehashed"
                ),
            ):
                repeated_path, repeated_status = app._upload_rom_to_mister_sd(
                    client,
                    sftp,
                    local_rom,
                    self.tracker.MISTER_DEFAULT_ROM_ROOT,
                    {"title": "Fast Hack", "smwc_id": "456"},
                )

        self.assertEqual(status, "uploaded")
        self.assertEqual(repeated_status, "already_on_mister")
        self.assertEqual(repeated_path, remote_path)
        self.assertEqual(sftp.files[remote_path], payload)
        self.assertEqual(sftp.read_count, 0)
        self.assertEqual(len(client.commands), 1)
        self.assertEqual(sftp.list_count, 1)
        self.assertEqual(sftp.stat_count - first_directory_stat_count, 0)

    def test_mister_downloader_checkbox_is_platform_specific(self):
        downloader_source = inspect.getsource(
            self.tracker.TrackerApp.open_hack_downloader
        )
        worker_source = inspect.getsource(
            self.tracker.TrackerApp._filtered_hack_download_worker
        )
        self.assertIn('selected_platform == "MiSTer"', downloader_source)
        self.assertIn('"Send to MiSTer SD Card"', downloader_source)
        self.assertIn('"mister_sd_option"', downloader_source)
        self.assertIn('selected_platform == "FXPAK Pro"', downloader_source)
        self.assertIn('upload_to_mister_var.set(False)', downloader_source)
        self.assertIn("mister_root", worker_source)
        self.assertIn("_verified_mister_peer", worker_source)
        self.assertIn("_upload_rom_to_mister_sd", worker_source)

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

    def test_mister_host_edit_is_saved_to_the_profile_shown_in_setup(self):
        app = object.__new__(self.tracker.TrackerApp)
        app.config = {
            "active_mister_profile": "Office",
            "mister_host": "192.168.50.145",
            "mister_ssh_user": "root",
            "mister_ssh_port": 22,
            "mister_ssh_fingerprint": "office-key",
            "mister_profiles": [
                {
                    "name": "Living Room",
                    "host": "192.168.50.116",
                    "user": "root",
                    "port": 22,
                    "fingerprint": "living-room-key",
                    "rom_root": "/media/fat/games/SNES/Living Room",
                    "menu_root": "/media/fat/_SMW Stream Tracker",
                },
                {
                    "name": "Office",
                    "host": "192.168.50.145",
                    "user": "root",
                    "port": 22,
                    "fingerprint": "office-key",
                    "rom_root": "/media/fat/games/SNES/Office",
                    "menu_root": "/media/fat/_SMW Stream Tracker",
                },
            ],
        }
        app.worker = None
        dialog_profiles = [dict(profile) for profile in app.config["mister_profiles"]]
        app.config["mister_profiles"][1]["host"] = "192.168.50.199"

        with mock.patch.object(self.tracker, "save_config") as save:
            values = app._save_mister_connection_settings(
                "ssh://192.168.50.200:22/",
                "root",
                "22",
                profile_name="Living Room",
                profile_records=dialog_profiles,
            )

        profiles, active = self.tracker.normalized_mister_profiles(app.config)
        living_room = next(
            profile for profile in profiles if profile["name"] == "Living Room"
        )
        office = next(profile for profile in profiles if profile["name"] == "Office")
        self.assertEqual(values, ("192.168.50.200", "root", 22))
        self.assertEqual(active, "Living Room")
        self.assertEqual(living_room["host"], "192.168.50.200")
        self.assertEqual(living_room["fingerprint"], "")
        self.assertEqual(
            living_room["rom_root"],
            "/media/fat/games/SNES/Living Room",
        )
        self.assertEqual(office["host"], "192.168.50.199")
        self.assertEqual(app.config["mister_host"], "192.168.50.200")
        self.assertEqual(
            app.config["platform_websocket_url"],
            "ws://192.168.50.200:23074",
        )
        save.assert_called_once_with(app.config)

    def test_auto_address_recovery_cannot_overwrite_a_different_console(self):
        events = queue.Queue()
        worker = self.tracker.TrackerWorker(
            {
                "selected_platform": "MiSTer",
                "active_mister_profile": "D-10 Nano",
                "mister_host": "192.168.50.145",
                "mister_ssh_user": "root",
                "mister_ssh_port": 22,
                "mister_ssh_fingerprint": "SHA256:nano-key",
                "mister_profiles": [
                    {
                        "name": "D-10 Nano",
                        "host": "192.168.50.145",
                        "user": "root",
                        "port": 22,
                        "fingerprint": "SHA256:nano-key",
                    },
                    {
                        "name": "Multisystem 2",
                        "host": "192.168.50.116",
                        "user": "root",
                        "port": 22,
                        "fingerprint": "SHA256:multisystem-key",
                    },
                ],
            },
            events,
        )
        worker.last_mister_connection_scan_at = 0.0
        with (
            mock.patch.object(
                worker,
                "_tracking_port_is_open",
                side_effect=lambda host, *_args: host == "192.168.50.11",
            ),
            mock.patch.object(
                self.tracker,
                "local_private_ipv4_addresses",
                return_value=["192.168.50.10"],
            ),
            mock.patch.object(
                self.tracker,
                "mister_local_scan_candidates",
                return_value=["192.168.50.11"],
            ),
            mock.patch.object(
                self.tracker,
                "mister_ssh_host_key_fingerprint",
                return_value="SHA256:some-other-console",
            ),
        ):
            worker.auto_select_mister_connection()

        profiles, active = self.tracker.normalized_mister_profiles(
            worker.config
        )
        nano = next(
            profile for profile in profiles if profile["name"] == "D-10 Nano"
        )
        self.assertEqual(active, "D-10 Nano")
        self.assertEqual(nano["host"], "192.168.50.145")
        self.assertEqual(worker.config["mister_host"], "192.168.50.145")
        self.assertTrue(events.empty())

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

    def test_live_tracking_is_enabled_for_normal_and_ra_snes_cores(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._configure_mister_snes_live_tracking
        )
        self.assertIn('(\"SNES\", \"RA_SNES\")', source)
        self.assertIn(
            'f\"/media/fat/config/uartmode.{core_name}\"',
            source,
        )
        install_source = inspect.getsource(
            self.tracker.TrackerApp._install_mister_support
        )
        self.assertIn(
            "self._configure_mister_snes_live_tracking(sftp)",
            install_source,
        )

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

    def test_normal_windows_build_packages_the_rebased_virtual_state_binary(self):
        build_spec = (MODULE_PATH.parent / "SMWStreamTracker.spec").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("MiSTer-SMW-Virtual-States", build_spec)
        self.assertIn("mister_experimental", build_spec)
        self.assertIn("Main_MiSTer_20260707", build_spec)
        self.assertIn("UPSTREAM_SOURCE.txt", build_spec)
        self.assertIn("Main_MiSTer_20260707\\\\LICENSE", build_spec)

    def test_windows_build_refuses_to_package_without_paramiko(self):
        build_spec = (MODULE_PATH.parent / "SMWStreamTracker.spec").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("import paramiko", build_spec)
        self.assertIn("Paramiko is incomplete", build_spec)
        self.assertIn("cannot be packaged without working MiSTer SSH", build_spec)

    def test_missing_paramiko_never_masks_the_real_setup_error(self):
        discovery_source = inspect.getsource(
            self.tracker.TrackerApp._discover_mister_host
        )
        self.assertNotIn(
            "except paramiko.AuthenticationException",
            discovery_source,
        )
        self.assertIn("paramiko is not None", discovery_source)

    def test_mister_launch_allows_the_rebased_virtual_state_main(self):
        launch_source = inspect.getsource(
            self.tracker.TrackerApp._run_mister_game_launch
        )
        self.assertNotIn(
            "current_main_sha256 == MISTER_VIRTUAL_STATES_BINARY_SHA256",
            launch_source,
        )
        self.assertNotIn("can corrupt HDMI output", launch_source)
        self.assertIn("mister_mgl_text(", launch_source)

    def test_packaged_startup_check_requires_complete_mister_ssh_support(self):
        startup_check_source = inspect.getsource(
            self.tracker._run_tk_startup_check
        )
        self.assertIn("paramiko is None", startup_check_source)
        self.assertIn('"AuthenticationException"', startup_check_source)
        self.assertIn('"SSHClient"', startup_check_source)
        self.assertIn('"SSHException"', startup_check_source)
        self.assertIn("return 22", startup_check_source)

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
        self.assertIn("_install_mister_virtual_states", setup_source)
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

    def test_mgl_targets_snes_core_and_full_rom_path(self):
        text = self.tracker.mister_mgl_text(
            "/media/fat/games/SNES/SMW Stream Tracker/My Hack.sfc"
        )
        self.assertIn("_Console/SNES", text)
        self.assertNotIn("RA_SNES", text)
        self.assertIn('index="0"', text)
        self.assertIn(
            'path="/media/fat/games/SNES/SMW Stream Tracker/My Hack.sfc"',
            text,
        )

    def test_mgl_can_target_the_official_retroachievements_snes_core(self):
        text = self.tracker.mister_mgl_text(
            "/media/fat/games/SNES/SMW Stream Tracker/My Hack.sfc",
            retroachievements=True,
        )
        self.assertIn("_RA_Cores/Cores/SNES", text)
        self.assertIn('<setname same_dir="1">RA_SNES</setname>', text)
        self.assertIn('index="0"', text)
        self.assertIn(
            'path="/media/fat/games/SNES/SMW Stream Tracker/My Hack.sfc"',
            text,
        )

    def test_mister_setup_strings_exist_in_every_language(self):
        for language in ("au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                for text in (
                    "Set Up MiSTer...",
                    "MiSTer Setup",
                    "MISTER CONNECTION",
                    "Connect, prepare, and verify MiSTer for live tracking and game launching.",
                    "Automatic setup",
                    "Recommended",
                    "Connection details",
                    "Find & Set Up MiSTer",
                    "Save & Select MiSTer",
                    "Looking for MiSTer on your network...",
                    "MiSTer is fully set up. The tracker found it, installed live tracking and save states 5–11, created the game folders, enabled automatic login for this app, selected MiSTer, and verified the connection. MiSTer is restarting.",
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

    def test_normal_mister_setup_installs_the_rebased_virtual_states(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        self.assertEqual(
            setup_source.count("self._install_mister_virtual_states("),
            1,
        )
        self.assertNotIn("Install Virtual Save State Slots", setup_source)
        self.assertNotIn("MiSTer Save States 5–11", setup_source)
        self.assertNotIn("virtual_states_body", setup_source)
        self.assertNotIn("Virtual Save States Disabled", setup_source)
        self.assertNotIn("can corrupt HDMI output", setup_source)
        self.assertIn("Find & Set Up MiSTer", setup_source)
        self.assertNotIn("Install Experimental States", setup_source)
        self.assertIn(
            "restore_original_button = self._make_action_button(\n"
            "            buttons,",
            setup_source,
        )
        self.assertNotIn("install_button = self._make_action_button(", setup_source)

    def test_mister_automatic_setup_instructions_are_complete(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        self.assertIn("The default SSH password is 1.", setup_source)
        self.assertIn("Virtual Save State Slots", setup_source)
        self.assertIn("smaller buttons to the right", setup_source)
        self.assertNotIn("smaller buttons below", setup_source)

    def test_mister_setup_uses_compact_stream_desk_cards(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        self.assertIn("self._create_stream_desk_page_header(", setup_source)
        self.assertIn('kicker="MISTER CONNECTION"', setup_source)
        self.assertEqual(setup_source.count("self._stream_desk_card("), 2)
        self.assertIn("dialog._uses_stream_desk_palette = True", setup_source)
        self.assertIn("self._size_dialog_for_ui(dialog, 980, 840, 820, 700)", setup_source)
        self.assertIn("footer = tk.Frame(", setup_source)
        self.assertIn("content.columnconfigure(0, weight=3", setup_source)
        self.assertNotIn('bg=THEME["blue"]', setup_source)

    def test_add_mister_profile_uses_themed_text_prompt(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        add_profile_start = setup_source.index("def add_mister_profile()")
        remove_profile_start = setup_source.index(
            "def remove_mister_profile()",
            add_profile_start,
        )
        add_profile_source = setup_source[
            add_profile_start:remove_profile_start
        ]
        self.assertIn("self._ask_stream_desk_string(", add_profile_source)
        self.assertNotIn("simpledialog.askstring(", add_profile_source)

    def test_mister_restore_button_uses_its_own_full_width_row(self):
        setup_source = inspect.getsource(self.tracker.TrackerApp.open_mister_setup)
        self.assertIn('self._translate_ui_text("Test Connection")', setup_source)
        self.assertGreaterEqual(setup_source.count("pad_y=11"), 2)
        self.assertIn('test_button.grid(\n            row=0', setup_source)
        self.assertIn(
            'restore_original_button.grid(\n            row=1',
            setup_source,
        )
        self.assertIn("buttons.columnconfigure(0, weight=1", setup_source)
        self.assertNotIn('uniform="mister_manual_actions"', setup_source)
        restore_start = setup_source.index("restore_original_button =")
        restore_end = setup_source.index(
            "restore_original_button.grid(",
            restore_start,
        )
        restore_source = setup_source[restore_start:restore_end]
        self.assertIn("width=34", restore_source)
        self.assertIn("font_size=10", restore_source)


if __name__ == "__main__":
    unittest.main()
