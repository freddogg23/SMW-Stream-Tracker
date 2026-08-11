import importlib.util
import ctypes
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
        "smw_tracker_retroarch_same_window_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(
    sys.platform.startswith("win"),
    "Win32 in-place RetroArch loading applies only to Windows.",
)
class RetroArchSameWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def make_app(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.config = {
            "retroarch_host": "127.0.0.1",
            "retroarch_port": 55355,
            "retroarch_executable_path": r"C:\RetroArch\retroarch.exe",
        }
        return app

    def test_load_content_reuses_running_retroarch_window(self):
        app = self.make_app()
        app._retroarch_status = mock.Mock(
            side_effect=[
                "GET_STATUS PLAYING snes,Old Hack,crc32=11111111",
                "GET_STATUS PLAYING snes,Old Hack,crc32=11111111",
                "GET_STATUS PLAYING snes,New Hack,crc32=22222222",
            ]
        )
        app._send_retroarch_network_command = mock.Mock(return_value="")
        app._post_retroarch_file_drop = mock.Mock(return_value=True)

        with mock.patch.object(self.tracker.time, "sleep", return_value=None):
            loaded, saved = app._load_retroarch_content_in_place(
                Path(r"C:\RetroArch\cores\snes9x_libretro.dll"),
                Path(r"C:\ROMs\New Hack.sfc"),
            )

        self.assertTrue(loaded)
        self.assertTrue(saved)
        commands = [call.args[0] for call in app._send_retroarch_network_command.call_args_list]
        self.assertEqual(commands[0], "SAVE_STATE")
        app._post_retroarch_file_drop.assert_called_once_with(
            Path(r"C:\RetroArch\retroarch.exe"),
            Path(r"C:\ROMs\New Hack.sfc"),
        )
        self.assertFalse(any(command.startswith("LOAD_CONTENT") for command in commands))
        self.assertNotIn("CLOSE_CONTENT", commands)
        self.assertNotIn("QUIT", commands)

    def test_launcher_does_not_spawn_second_process_after_in_place_load(self):
        app = self.make_app()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = root / "retroarch.exe"
            core = root / "cores" / "snes9x_libretro.dll"
            rom = root / "roms" / "New Hack.sfc"
            core.parent.mkdir()
            rom.parent.mkdir()
            executable.write_bytes(b"EXE")
            core.write_bytes(b"CORE")
            rom.write_bytes(b"ROM")
            app.config.update(
                {
                    "retroarch_executable_path": str(executable),
                    "retroarch_core_path": str(core),
                }
            )
            app._resolve_local_rom_path = mock.Mock(
                return_value=(rom, "exact local filename match")
            )
            app._load_retroarch_content_in_place = mock.Mock(
                return_value=(True, True)
            )

            with mock.patch.object(self.tracker.subprocess, "Popen") as popen:
                result = app._run_local_emulator_launcher(
                    {"title": "New Hack"},
                    "RetroArch",
                )

        popen.assert_not_called()
        self.assertIn("existing RetroArch window", result["method"])

    def test_launcher_never_opens_duplicate_when_reuse_fails(self):
        app = self.make_app()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = root / "retroarch.exe"
            core = root / "cores" / "snes9x_libretro.dll"
            rom = root / "roms" / "New Hack.sfc"
            core.parent.mkdir()
            rom.parent.mkdir()
            executable.write_bytes(b"EXE")
            core.write_bytes(b"CORE")
            rom.write_bytes(b"ROM")
            app.config.update(
                {
                    "retroarch_executable_path": str(executable),
                    "retroarch_core_path": str(core),
                }
            )
            app._resolve_local_rom_path = mock.Mock(
                return_value=(rom, "exact local filename match")
            )
            app._load_retroarch_content_in_place = mock.Mock(
                return_value=(False, True)
            )
            app._retroarch_status = mock.Mock(
                return_value="GET_STATUS PLAYING snes,Old Hack"
            )

            with mock.patch.object(self.tracker.subprocess, "Popen") as popen:
                with self.assertRaisesRegex(RuntimeError, "duplicate"):
                    app._run_local_emulator_launcher(
                        {"title": "New Hack"},
                        "RetroArch",
                    )

        popen.assert_not_called()

    def test_file_drop_accepts_64_bit_window_and_memory_handles(self):
        class FakeFunction:
            def __init__(self, result):
                self.result = result
                self.calls = []
                self.argtypes = None
                self.restype = None

            def __call__(self, *args):
                self.calls.append(args)
                return self.result

        app = self.make_app()
        large_window_handle = 0x000001ABCDEF1234
        memory = ctypes.create_string_buffer(4096)
        large_memory_handle = ctypes.addressof(memory)
        app._find_windows_for_executable = mock.Mock(
            return_value=[large_window_handle]
        )

        global_alloc = FakeFunction(large_memory_handle)
        global_lock = FakeFunction(large_memory_handle)
        global_unlock = FakeFunction(True)
        global_free = FakeFunction(0)
        post_message = FakeFunction(True)
        fake_windll = SimpleNamespace(
            kernel32=SimpleNamespace(
                GlobalAlloc=global_alloc,
                GlobalLock=global_lock,
                GlobalUnlock=global_unlock,
                GlobalFree=global_free,
            ),
            user32=SimpleNamespace(PostMessageW=post_message),
        )

        with mock.patch.object(self.tracker.ctypes, "windll", fake_windll):
            sent = app._post_retroarch_file_drop(
                Path(r"C:\RetroArch\retroarch.exe"),
                Path(r"C:\ROMs\New Hack.sfc"),
            )

        self.assertTrue(sent)
        self.assertEqual(post_message.calls[0][0], large_window_handle)
        self.assertEqual(post_message.calls[0][2], large_memory_handle)
        self.assertEqual(
            global_lock.argtypes,
            [self.tracker.wintypes.HGLOBAL],
        )
        self.assertEqual(
            post_message.argtypes[2],
            self.tracker.wintypes.WPARAM,
        )


if __name__ == "__main__":
    unittest.main()
