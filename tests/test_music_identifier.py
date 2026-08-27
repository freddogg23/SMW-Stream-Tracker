import importlib.util
import inspect
from array import array
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import wave


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_music_identifier_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeStream:
    def __init__(self, channels=1):
        self.closed = False
        self.channels = channels

    def read(self, frame_count, exception_on_overflow=False):
        del exception_on_overflow
        return array(
            "h",
            [1200] * frame_count * self.channels,
        ).tobytes()

    def stop_stream(self):
        return None

    def close(self):
        self.closed = True


class FakeAudio:
    devices = (
        {
            "name": "USB Capture Audio",
            "maxInputChannels": 2,
            "defaultSampleRate": 48000,
            "hostApi": 0,
        },
        {
            "name": "Speakers (Game Audio)",
            "maxInputChannels": 2,
            "defaultSampleRate": 48000,
            "hostApi": 0,
            "isLoopbackDevice": True,
        },
        {
            "name": "Speakers (Output Only)",
            "maxInputChannels": 0,
            "defaultSampleRate": 48000,
            "hostApi": 0,
        },
    )

    def __init__(self):
        self.stream = None

    def get_device_count(self):
        return len(self.devices)

    def get_device_info_by_index(self, index):
        return dict(self.devices[index])

    def get_host_api_info_by_index(self, index):
        del index
        return {"name": "Windows WASAPI"}

    def open(self, **kwargs):
        self.open_kwargs = dict(kwargs)
        self.stream = FakeStream(int(kwargs.get("channels", 1)))
        return self.stream

    def get_sample_size(self, sample_format):
        del sample_format
        return 2

    def terminate(self):
        return None


class FakeAudioModule:
    paInt16 = 8
    PyAudio = FakeAudio


class FakeVar:
    def __init__(self, value=None):
        self.value = value

    def set(self, value):
        self.value = value


class FakeRunningThread:
    def is_alive(self):
        return True


class FakeRoot:
    def __init__(self):
        self.cancelled_after_ids = []

    def after_cancel(self, after_id):
        self.cancelled_after_ids.append(after_id)


class MusicIdentifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_music_identifier_is_directly_above_settings(self):
        sections = [
            section
            for section, _icon, _label
            in self.tracker.STREAM_DESK_NAVIGATION_ITEMS
        ]
        settings_index = sections.index("settings")
        self.assertEqual(sections[settings_index - 1], "music_identifier")
        music_item = self.tracker.STREAM_DESK_NAVIGATION_ITEMS[
            settings_index - 1
        ]
        self.assertEqual(music_item[1], "music_note")
        self.assertEqual(music_item[2], "Music Identifier & Radio")

    def test_radio_and_found_song_player_are_on_the_music_page(self):
        page_source = inspect.getsource(
            self.tracker.TrackerApp._open_music_identifier_page
        )
        player_source = inspect.getsource(
            self.tracker.TrackerApp._play_music_identifier_match
        )
        state_source = inspect.getsource(
            self.tracker.TrackerApp._set_music_identifier_running_ui
        )
        self.assertIn('"Music Identifier & Radio"', page_source)
        self.assertIn('text="Play SMW Central Radio"', page_source)
        self.assertIn("command=self._open_smwcentral_radio", page_source)
        self.assertIn('text="Play Found Song"', page_source)
        self.assertIn('play_button.pack(side="top", fill="x")', page_source)
        self.assertIn("_open_smwcentral_music_player", player_source)
        self.assertIn('widgets.get("play_button")', state_source)
        self.assertIn("play_button.pack_forget()", state_source)

    def test_music_index_rechecks_every_thirty_minutes(self):
        self.assertEqual(
            self.tracker.SMWC_MUSIC_INDEX_CHECK_INTERVAL_MS,
            30 * 60 * 1000,
        )

    def test_audio_sources_include_input_and_loopback_but_not_outputs(self):
        sources = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )
        self.assertEqual(len(sources), 2)
        self.assertTrue(sources[0]["is_loopback"])
        self.assertIn("System audio", sources[0]["label"])
        self.assertFalse(sources[1]["is_loopback"])
        self.assertIn("Audio input", sources[1]["label"])
        self.assertTrue(sources[0]["token"])

    def test_recorded_sample_is_a_nonempty_wav(self):
        source = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )[0]
        progress = []
        with tempfile.TemporaryDirectory() as temp_folder:
            wav_path = Path(temp_folder) / "sample.wav"
            details = self.tracker.record_windows_music_sample(
                source,
                wav_path,
                seconds=3,
                audio_module=FakeAudioModule,
                progress_callback=lambda amount, remaining: progress.append(
                    (amount, remaining)
                ),
            )
            self.assertTrue(wav_path.is_file())
            self.assertGreater(wav_path.stat().st_size, 44)
        self.assertEqual(details["channels"], 2)
        self.assertEqual(details["sample_rate"], 48000)
        self.assertGreater(details["peak_amplitude"], 48)
        self.assertAlmostEqual(progress[-1][0], 1.0)
        self.assertEqual(progress[-1][1], 0)

    def test_cancelled_recording_stops_before_writing(self):
        source = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )[0]
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as temp_folder:
            wav_path = Path(temp_folder) / "cancelled.wav"
            with self.assertRaises(self.tracker.MusicIdentifierCancelled):
                self.tracker.record_windows_music_sample(
                    source,
                    wav_path,
                    seconds=3,
                    cancel_event=cancel_event,
                    audio_module=FakeAudioModule,
                )
            self.assertFalse(wav_path.exists())

    def test_stop_listening_updates_the_ui_without_waiting_for_worker_cleanup(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.music_identifier_thread = FakeRunningThread()
        app.music_identifier_cancel_event = threading.Event()
        app.music_identifier_state = "listening"
        app.music_identifier_progress_var = FakeVar(0.5)
        app.music_identifier_status_var = FakeVar("Listening…")
        app.music_identifier_detail_var = FakeVar("Listening")
        app.music_identifier_animation_after_id = "pulse-after-id"
        app.root = FakeRoot()
        running_ui_calls = []
        app._translate_ui_text = lambda text: text
        app._set_music_identifier_running_ui = (
            lambda running, **options: running_ui_calls.append((running, options))
        )
        app._draw_music_identifier_listening_art = lambda: None
        app._draw_music_identifier_progress = lambda: None
        app._queue_music_identifier_poll = lambda: None

        app._cancel_music_identifier()

        self.assertTrue(app.music_identifier_cancel_event.is_set())
        self.assertEqual(app.music_identifier_state, "cancelled")
        self.assertEqual(app.music_identifier_status_var.value, "Listening stopped")
        self.assertEqual(app.music_identifier_progress_var.value, 0.0)
        self.assertIsNone(app.music_identifier_animation_after_id)
        self.assertEqual(app.root.cancelled_after_ids, ["pulse-after-id"])
        self.assertEqual(
            running_ui_calls,
            [(False, {"cleanup_pending": True})],
        )

    def test_recording_can_stop_at_an_early_match_checkpoint(self):
        source = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )[0]
        checkpoints = []
        progress = []
        with tempfile.TemporaryDirectory() as temp_folder:
            wav_path = Path(temp_folder) / "early-match.wav"
            details = self.tracker.record_windows_music_sample(
                source,
                wav_path,
                seconds=10,
                audio_module=FakeAudioModule,
                checkpoint_seconds=(4, 8),
                checkpoint_callback=lambda path, seconds: (
                    checkpoints.append((path, seconds)) or True
                ),
                progress_callback=lambda amount, remaining: progress.append(
                    (amount, remaining)
                ),
            )

            self.assertTrue(wav_path.is_file())
            self.assertGreater(wav_path.stat().st_size, 44)
        self.assertTrue(details["stopped_early"])
        self.assertLess(details["seconds"], 5.0)
        self.assertEqual([seconds for _path, seconds in checkpoints], [4])
        self.assertLess(progress[-1][0], 1.0)

    def test_music_search_links_to_smw_central(self):
        result = self.tracker.smwcentral_music_search_url(
            "Stickerbush Symphony"
        )
        self.assertIn("s=smwmusic", result)
        self.assertIn("Stickerbush", result)

    def test_bundled_local_music_index_is_usable(self):
        details = self.tracker.smwc_music_index.validate_music_index(
            self.tracker.SMWC_BUNDLED_MUSIC_INDEX_FILE,
            require_tracks=True,
        )
        self.assertGreaterEqual(details["track_count"], 50)
        self.assertEqual(
            details["fingerprint_algorithm"],
            self.tracker.smwc_music_index.FINGERPRINT_ALGORITHM,
        )

    def test_music_identifier_no_longer_uses_shazam(self):
        project_root = MODULE_PATH.parent
        requirements = (
            project_root / "release" / "requirements-build.txt"
        ).read_text(encoding="utf-8").casefold()
        source = MODULE_PATH.read_text(encoding="utf-8").casefold()
        self.assertNotIn("shazam", requirements)
        self.assertNotIn("shazam", source)
        self.assertIn("numpy", requirements)

    def test_windows_build_refuses_to_omit_music_dependencies(self):
        project_root = MODULE_PATH.parent
        build_spec = (project_root / "SMWStreamTracker.spec").read_text(
            encoding="utf-8-sig"
        )
        build_script = (
            project_root / "release" / "build_release.ps1"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("import pyaudiowpatch", build_spec)
        self.assertIn("import numpy", build_spec)
        self.assertIn("cannot be packaged without Windows music", build_spec)
        self.assertIn("import pyaudiowpatch", build_script)
        self.assertIn("import numpy", build_script)
        self.assertIn("PyAudioWPatch", build_script)
        self.assertIn("NumPy", build_script)
        startup_check = inspect.getsource(
            self.tracker._run_tk_startup_check
        )
        self.assertIn("import pyaudiowpatch", startup_check)
        self.assertIn("import numpy", startup_check)
        self.assertIn("return 24", startup_check)

    def test_recorded_audio_is_cleaned_normalized_and_made_mono(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            source_path = Path(temp_folder) / "stereo.wav"
            prepared_path = Path(temp_folder) / "prepared.wav"
            stereo_samples = array("h")
            for sample_index in range(4800):
                value = 240 if sample_index % 16 < 8 else -240
                stereo_samples.extend((value + 80, value + 80))
            with wave.open(str(source_path), "wb") as source_wave:
                source_wave.setnchannels(2)
                source_wave.setsampwidth(2)
                source_wave.setframerate(48000)
                source_wave.writeframes(stereo_samples.tobytes())

            details = self.tracker.prepare_music_identifier_wav(
                source_path,
                prepared_path,
            )

            with wave.open(str(prepared_path), "rb") as prepared_wave:
                self.assertEqual(prepared_wave.getnchannels(), 1)
                self.assertEqual(prepared_wave.getsampwidth(), 2)
                prepared_samples = array(
                    "h",
                    prepared_wave.readframes(prepared_wave.getnframes()),
                )
            self.assertGreater(max(abs(value) for value in prepared_samples), 240)
            self.assertGreater(details["gain"], 1.0)

if __name__ == "__main__":
    unittest.main()
