import importlib.util
import inspect
import math
from array import array
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
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


class FakeAudioProcess:
    def __init__(self, pid, name, window_title):
        self.pid = pid
        self.name = name
        self.window_title = window_title


class FakeProcessAudioCapture:
    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def enumerate_audio_processes(cls):
        return [
            FakeAudioProcess(101, "firefox.exe", "SMW Speedruns - Twitch"),
            FakeAudioProcess(202, "chrome.exe", "SMW Central - Google Chrome"),
        ]


class FakeMovedBrowserAudioCapture:
    current_pid = 202

    @classmethod
    def enumerate_audio_processes(cls):
        return [
            FakeAudioProcess(
                cls.current_pid,
                "chrome.exe",
                "SMW Central - Google Chrome",
            )
        ]


class FakeBlockAudioCapture:
    @classmethod
    def enumerate_audio_processes(cls):
        return [FakeAudioProcess(101, "firefox.exe", "Twitch")]

    def __init__(self, pid, output_path, level_callback=None):
        self.pid = pid
        self.output_path = Path(output_path)
        self.level_callback = level_callback

    def start(self):
        if self.level_callback is not None:
            self.level_callback(-12.0)

    def stop(self):
        sample_rate = 16000
        frame_count = round(3.2 * sample_rate)
        samples = array("h")
        for frame_index in range(frame_count):
            value = 7000 if frame_index % 48 < 24 else -7000
            samples.extend((value, value))
        with wave.open(str(self.output_path), "wb") as output_wave:
            output_wave.setnchannels(2)
            output_wave.setsampwidth(2)
            output_wave.setframerate(sample_rate)
            output_wave.writeframes(samples.tobytes())


class FakeVar:
    def __init__(self, value=None):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class FakeWidget:
    def __init__(self):
        self.configurations = []

    def configure(self, **kwargs):
        self.configurations.append(dict(kwargs))


class FakeRunningThread:
    def is_alive(self):
        return True


class FakeVoiceAnalyzer:
    sample_rate = 16000
    frame_samples = 512

    def __init__(self, probabilities):
        self.probabilities = list(probabilities)

    def analyze(self, pcm_samples, channels, sample_rate):
        del pcm_samples, channels, sample_rate
        return []


class ScriptedBlockVoiceAnalyzer:
    def __init__(self):
        self.probabilities = []
        self.calls = 0

    def analyze(self, pcm_samples, channels, sample_rate):
        del pcm_samples, channels, sample_rate
        self.calls += 1
        new_probabilities = (
            [0.96] * 5 if self.calls == 1 else [0.01] * 5
        )
        self.probabilities.extend(new_probabilities)
        return new_probabilities


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

    def test_community_results_are_opt_in_and_identification_is_cloud_only(self):
        page_source = inspect.getsource(
            self.tracker.TrackerApp._open_music_identifier_page
        )
        identify_source = inspect.getsource(
            self.tracker.TrackerApp._start_music_identifier
        )
        teach_source = inspect.getsource(
            self.tracker.TrackerApp._teach_music_identifier_match
        )
        self.assertIn("Use & Contribute to Community Song Results", page_source)
        self.assertIn("No recordings, usernames, Twitch data", page_source)
        self.assertIn('text="Check Cloud Catalog"', page_source)
        self.assertIn("cloud_only=True", identify_source)
        self.assertNotIn("community_model_path", identify_source)
        self.assertNotIn("validate_music_index", identify_source)
        self.assertIn("_share_confirmed_music_learning", teach_source)
        self.assertNotIn("learn_confirmed_music_match", teach_source)

    def test_audio_sources_only_show_playback_sources_by_default(self):
        sources = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )
        self.assertEqual(len(sources), 1)
        self.assertTrue(sources[0]["is_loopback"])
        self.assertIn("System audio", sources[0]["label"])
        self.assertTrue(sources[0]["token"])

        all_capture_sources = (
            self.tracker.enumerate_windows_music_audio_sources(
                FakeAudioModule,
                include_inputs=True,
            )
        )
        self.assertEqual(len(all_capture_sources), 2)
        self.assertFalse(all_capture_sources[1]["is_loopback"])
        self.assertIn("Audio input", all_capture_sources[1]["label"])

    def test_source_refresh_only_uses_application_audio(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.music_identifier_source_var = FakeVar("")
        app.music_identifier_status_var = FakeVar("")
        app.music_identifier_detail_var = FakeVar("")
        app.music_identifier_sources = {}
        app.music_identifier_state = "ready"
        app.config = {}
        app.root = type(
            "RefreshRoot",
            (),
            {"update_idletasks": lambda self: None},
        )()
        source_box = FakeWidget()
        refresh_button = FakeWidget()
        app.music_identifier_widgets = {
            "source_box": source_box,
            "refresh_button": refresh_button,
        }
        app._translate_ui_text = lambda text: text
        application_source = {
            "label": "Google Chrome — Application audio",
            "token": "application|chrome.exe",
        }

        with (
            patch.object(
                self.tracker,
                "enumerate_windows_music_application_sources",
                return_value=[application_source],
            ),
            patch.object(
                self.tracker,
                "enumerate_windows_music_audio_sources",
            ) as device_sources,
            patch.object(self.tracker, "save_config"),
        ):
            self.tracker.TrackerApp._refresh_music_identifier_sources(app)

        self.assertEqual(
            tuple(app.music_identifier_sources),
            ("Google Chrome — Application audio",),
        )
        self.assertEqual(
            app.music_identifier_source_var.get(),
            "Google Chrome — Application audio",
        )
        self.assertEqual(
            app.config["music_identifier_audio_source"],
            "application|chrome.exe",
        )
        self.assertEqual(source_box.configurations[-1]["state"], "readonly")
        self.assertEqual(refresh_button.configurations[-1]["state"], "normal")
        device_sources.assert_not_called()

    def test_manual_source_refresh_scans_in_background_and_reports_new_apps(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.music_identifier_source_var = FakeVar("")
        app.music_identifier_status_var = FakeVar("")
        app.music_identifier_detail_var = FakeVar("")
        app.music_identifier_sources = {}
        app.music_identifier_state = "ready"
        app.music_identifier_source_refresh_generation = 0
        app.music_identifier_source_refresh_thread = None
        app.config = {}
        app.root = type(
            "RefreshRoot",
            (),
            {"after": lambda self, _delay, callback: callback()},
        )()
        source_box = FakeWidget()
        refresh_button = FakeWidget()
        app.music_identifier_widgets = {
            "source_box": source_box,
            "refresh_button": refresh_button,
        }
        app._translate_ui_text = lambda text: text
        application_source = {
            "label": "Google Chrome — Application audio",
            "token": "application|chrome.exe",
        }
        scan_gate = threading.Event()

        def delayed_scan():
            scan_gate.wait(timeout=5)
            return [application_source], []

        app._scan_music_identifier_sources = delayed_scan
        with patch.object(self.tracker, "save_config"):
            self.tracker.TrackerApp._refresh_music_identifier_sources(
                app,
                manual=True,
            )
            refresh_thread = app.music_identifier_source_refresh_thread
            self.assertIsNotNone(refresh_thread)
            self.assertEqual(
                app.music_identifier_status_var.get(),
                "Refreshing audio sources…",
            )
            self.assertEqual(source_box.configurations[-1]["state"], "disabled")
            scan_gate.set()
            refresh_thread.join(timeout=5)

        self.assertFalse(refresh_thread.is_alive())
        self.assertEqual(
            app.music_identifier_status_var.get(),
            "Sources refreshed — 1 app found (1 new)",
        )
        self.assertEqual(source_box.configurations[-1]["state"], "readonly")
        self.assertEqual(refresh_button.configurations[-1]["state"], "normal")

    def test_application_audio_sources_list_the_browser_the_user_can_select(self):
        sources = self.tracker.enumerate_windows_music_application_sources(
            FakeProcessAudioCapture
        )

        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["name"], "Google Chrome")
        self.assertEqual(sources[0]["capture_type"], "process")
        self.assertTrue(sources[0]["is_browser"])
        self.assertIn("Application audio", sources[0]["label"])
        self.assertIn("chrome.exe", sources[0]["token"])
        self.assertEqual(sources[1]["name"], "Mozilla Firefox")

    def test_volume_mixer_chrome_session_is_listed_and_enriched(self):
        class NoActiveAudioCapture:
            @classmethod
            def is_supported(cls):
                return True

            @classmethod
            def enumerate_audio_processes(cls):
                return []

        sources = self.tracker.enumerate_windows_music_application_sources(
            NoActiveAudioCapture,
            volume_mixer_processes=(
                {
                    "pid": 707,
                    "name": "chrome.exe",
                    "window_title": "",
                    "is_active": True,
                },
            ),
            running_processes=(
                {
                    "pid": 404,
                    "name": "chrome.exe",
                    "window_title": "Twitch - Google Chrome",
                    "is_visible": True,
                },
            ),
            process_snapshot={
                707: (404, "chrome.exe"),
                404: (100, "chrome.exe"),
                100: (0, "explorer.exe"),
            },
        )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["name"], "Google Chrome")
        self.assertEqual(sources[0]["capture_type"], "process")
        self.assertEqual(sources[0]["capture_pid"], 404)
        self.assertIn("Twitch - Google Chrome", sources[0]["label"])

    def test_volume_mixer_scan_reads_every_active_playback_device(self):
        class FakeProcess:
            def __init__(self, name):
                self.process_name = name

            def name(self):
                return self.process_name

        class FakeSession:
            def __init__(self, pid, name, state):
                self.ProcessId = pid
                self.Process = FakeProcess(name) if name else None
                self.State = state

            def QueryInterface(self, _interface):
                return self

        class FakeEnumerator:
            def __init__(self, sessions):
                self.sessions = list(sessions)

            def GetCount(self):
                return len(self.sessions)

            def GetSession(self, index):
                return self.sessions[index]

        class FakeManager:
            def __init__(self, sessions):
                self.enumerator = FakeEnumerator(sessions)

            def GetSessionEnumerator(self):
                return self.enumerator

        class FakeDevice:
            def __init__(self, name, sessions):
                self.FriendlyName = name
                self.AudioSessionManager = FakeManager(sessions)

        class FakeAudioUtilities:
            calls = []

            @classmethod
            def GetAllDevices(cls, data_flow, device_state):
                cls.calls.append((data_flow, device_state))
                return (
                    FakeDevice(
                        "Game output",
                        (FakeSession(101, "retroarch.exe", 1),),
                    ),
                    FakeDevice(
                        "Music output",
                        (
                            FakeSession(202, "chrome.exe", 1),
                            FakeSession(0, "", 0),
                        ),
                    ),
                )

        class FakeComtypes:
            initialized = 0
            uninitialized = 0

            @classmethod
            def CoInitialize(cls):
                cls.initialized += 1

            @classmethod
            def CoUninitialize(cls):
                cls.uninitialized += 1

        enum_value = type("EnumValue", (), {"value": 7})()
        fake_data_flow = type("DataFlow", (), {"eRender": enum_value})
        fake_device_state = type("DeviceState", (), {"ACTIVE": enum_value})
        runtime = (
            FakeComtypes,
            FakeAudioUtilities,
            lambda control: control,
            object(),
            fake_data_flow,
            fake_device_state,
        )

        sessions = self.tracker._windows_volume_mixer_application_processes(
            runtime=runtime,
        )

        self.assertEqual(
            {(session["name"], session["audio_device"]) for session in sessions},
            {
                ("retroarch.exe", "Game output"),
                ("chrome.exe", "Music output"),
            },
        )
        self.assertEqual(FakeAudioUtilities.calls, [(7, 7)])
        self.assertEqual(FakeComtypes.initialized, 1)
        self.assertEqual(FakeComtypes.uninitialized, 1)

    def test_application_source_refreshes_when_browser_moves_audio_process(self):
        source = {
            "capture_type": "process",
            "pid": 202,
            "process_name": "chrome.exe",
            "window_title": "SMW Central - Google Chrome",
            "token": "application|chrome.exe",
        }
        FakeMovedBrowserAudioCapture.current_pid = 707

        refreshed = self.tracker.refresh_windows_music_application_source(
            source,
            FakeMovedBrowserAudioCapture,
        )

        self.assertEqual(refreshed["pid"], 707)
        self.assertEqual(refreshed["token"], "application|chrome.exe")

    def test_browser_capture_uses_stable_same_executable_parent(self):
        source = {
            "pid": 707,
            "process_name": "chrome.exe",
            "window_title": "SMW Central - Google Chrome",
        }
        processes = [
            FakeAudioProcess(
                707,
                "chrome.exe",
                "SMW Central - Google Chrome",
            )
        ]
        process_snapshot = {
            707: (404, "chrome.exe"),
            404: (111, "chrome.exe"),
            111: (88, "explorer.exe"),
        }

        capture_pid = (
            self.tracker._resolve_windows_music_application_capture_pid(
                source,
                processes,
                process_snapshot=process_snapshot,
            )
        )

        self.assertEqual(capture_pid, 404)

    def test_voice_free_sections_are_crossfaded_without_silent_seams(self):
        np = self.tracker.smwc_music_index._numpy()
        first = np.full((400, 2), 6000, dtype=np.int16)
        second = np.full((400, 2), 6000, dtype=np.int16)

        joined = self.tracker._crossfade_pcm_sections(
            (first, second),
            sample_rate=16000,
        )

        self.assertLess(joined.shape[0], first.shape[0] + second.shape[0])
        self.assertGreater(float(np.min(np.abs(joined))), 5000.0)

    def test_application_float_audio_is_converted_for_the_local_matcher(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            source_path = folder / "application-float.wav"
            destination_path = folder / "matcher-pcm.wav"
            values = [0.2, -0.2] * 4800
            audio_data = struct.pack("<" + "f" * len(values), *values)
            subformat_guid = struct.pack(
                "<IHH8s",
                3,
                0,
                0x0010,
                b"\x80\x00\x00\xaa\x00\x38\x9b\x71",
            )
            format_data = (
                struct.pack(
                    "<HHIIHHH",
                    0xFFFE,
                    2,
                    48000,
                    48000 * 8,
                    8,
                    32,
                    22,
                )
                + struct.pack("<HI", 32, 3)
                + subformat_guid
            )
            payload = (
                b"WAVEfmt "
                + struct.pack("<I", len(format_data))
                + format_data
                + b"data"
                + struct.pack("<I", len(audio_data))
                + audio_data
            )
            source_path.write_bytes(
                b"RIFF" + struct.pack("<I", len(payload)) + payload
            )

            details = self.tracker._convert_application_capture_wav_to_pcm16(
                source_path,
                destination_path,
            )

            with wave.open(str(destination_path), "rb") as converted:
                self.assertEqual(converted.getnchannels(), 2)
                self.assertEqual(converted.getsampwidth(), 2)
                self.assertEqual(converted.getframerate(), 48000)
                converted_values = array(
                    "h",
                    converted.readframes(converted.getnframes()),
                )
            self.assertGreater(details["peak_amplitude"], 6000)
            self.assertGreater(max(converted_values), 6000)

    def test_voice_gate_stitches_only_voice_free_music_into_the_match_sample(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            source_path = folder / "mixed.wav"
            voice_free_path = folder / "voice-free.wav"
            sample_rate = 16000
            seconds = 8
            samples = array(
                "h",
                (
                    round(
                        9000
                        * math.sin(2.0 * math.pi * 330.0 * index / sample_rate)
                    )
                    for index in range(sample_rate * seconds)
                ),
            )
            with wave.open(str(source_path), "wb") as source_wave:
                source_wave.setnchannels(1)
                source_wave.setsampwidth(2)
                source_wave.setframerate(sample_rate)
                source_wave.writeframes(samples.tobytes())
            probability_count = math.ceil(
                sample_rate * seconds / FakeVoiceAnalyzer.frame_samples
            )
            probabilities = [0.01] * probability_count
            voice_start = round(2.0 * sample_rate / FakeVoiceAnalyzer.frame_samples)
            voice_stop = round(3.4 * sample_rate / FakeVoiceAnalyzer.frame_samples)
            probabilities[voice_start:voice_stop] = [0.94] * (
                voice_stop - voice_start
            )

            details = self.tracker._compile_voice_free_pcm16_wav(
                source_path,
                voice_free_path,
                analyzer=FakeVoiceAnalyzer(probabilities),
            )

            with wave.open(str(voice_free_path), "rb") as compiled_wave:
                compiled_seconds = (
                    compiled_wave.getnframes() / compiled_wave.getframerate()
                )
            self.assertTrue(details["voice_gated"])
            self.assertGreater(details["voice_seconds"], 1.2)
            self.assertGreater(compiled_seconds, 5.0)
            self.assertLess(compiled_seconds, seconds - 1.0)

    def test_application_capture_preserves_one_continuous_timeline(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            destination = Path(temp_folder) / "compiled.wav"
            voice_states = []
            details = self.tracker.record_windows_application_music_sample(
                {
                    "pid": 101,
                    "process_name": "firefox.exe",
                },
                destination,
                seconds=3,
                voice_state_callback=(
                    lambda state, _clean, _target: voice_states.append(state)
                ),
                process_capture_class=FakeBlockAudioCapture,
                voice_analyzer=ScriptedBlockVoiceAnalyzer(),
            )

            self.assertTrue(destination.is_file())
            self.assertEqual(voice_states, ["continuous"])
            self.assertFalse(details["voice_gated"])
            self.assertTrue(details["continuous_timeline"])
            self.assertEqual(details["voice_blocks"], 0)
            self.assertGreaterEqual(details["clean_seconds"], 3.0)

    def test_quiet_sustained_voice_beats_isolated_music_onset_spikes(self):
        self.assertTrue(
            self.tracker._voice_probabilities_have_speech([0.24] * 6)
        )
        self.assertFalse(
            self.tracker._voice_probabilities_have_speech(
                [0.38, 0.22] + [0.01] * 36
            )
        )

    def test_input_level_meter_draws_before_any_match_result_exists(self):
        class FakeCanvas:
            def __init__(self):
                self.rectangles = []

            @staticmethod
            def winfo_width():
                return 280

            @staticmethod
            def winfo_height():
                return 8

            @staticmethod
            def delete(_tag):
                return None

            def create_rectangle(self, *coordinates, **options):
                self.rectangles.append((coordinates, options))

        class MeterHost:
            def __init__(self):
                self.canvas = FakeCanvas()
                self.music_identifier_widgets = {"level_canvas": self.canvas}
                self.music_identifier_input_level = 0.5

            @staticmethod
            def _ui_px(value):
                return int(value)

        host = MeterHost()
        self.tracker.TrackerApp._draw_music_identifier_input_level(host)
        self.assertEqual(len(host.canvas.rectangles), 15)

    def test_offline_voice_model_is_available_to_source_and_packaged_builds(self):
        runtime = self.tracker._voice_activity_runtime()
        self.assertIsNotNone(runtime)
        self.assertTrue(runtime[1].is_file())
        analyzer = self.tracker._OfflineVoiceAnalyzer()
        self.assertIsNotNone(analyzer.session)

    def test_recorded_sample_is_a_nonempty_wav(self):
        source = self.tracker.enumerate_windows_music_audio_sources(
            FakeAudioModule
        )[0]
        progress = []
        levels = []
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
                level_callback=levels.append,
            )
            self.assertTrue(wav_path.is_file())
            self.assertGreater(wav_path.stat().st_size, 44)
        self.assertEqual(details["channels"], 2)
        self.assertEqual(details["sample_rate"], 48000)
        self.assertGreater(details["peak_amplitude"], 48)
        self.assertAlmostEqual(progress[-1][0], 1.0)
        self.assertEqual(progress[-1][1], 0)
        self.assertTrue(levels)
        self.assertTrue(all(0.0 <= level <= 1.0 for level in levels))
        self.assertGreater(levels[-1], 0.1)

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
        app.music_identifier_input_status_var = FakeVar("INPUT LEVEL: source heard")
        app.music_identifier_input_level = 0.5
        app.music_identifier_animation_after_id = "pulse-after-id"
        app.root = FakeRoot()
        running_ui_calls = []
        app._translate_ui_text = lambda text: text
        app._set_music_identifier_running_ui = (
            lambda running, **options: running_ui_calls.append((running, options))
        )
        app._draw_music_identifier_listening_art = lambda: None
        app._draw_music_identifier_input_level = lambda: None
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

    def test_windows_build_does_not_bundle_or_install_an_offline_music_index(self):
        project_root = MODULE_PATH.parent
        build_spec = (project_root / "SMWStreamTracker.spec").read_text(
            encoding="utf-8-sig"
        )
        app_init_source = inspect.getsource(self.tracker.TrackerApp.__init__)
        self.assertNotIn("music_index\\\\bundled", build_spec)
        self.assertNotIn("ensure_bundled_music_index", app_init_source)
        self.assertIn("legacy_path.unlink", app_init_source)

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
        self.assertIn("import process_audio_capture", build_spec)
        self.assertIn("from pycaw.pycaw import AudioUtilities", build_spec)
        self.assertIn("import comtypes", build_spec)
        self.assertIn("import onnxruntime", build_spec)
        self.assertIn("silero_vad_16k.onnx", build_script)
        self.assertIn("cannot be packaged without Windows music", build_spec)
        self.assertIn("import pyaudiowpatch", build_script)
        self.assertIn("import numpy", build_script)
        self.assertIn("PyAudioWPatch", build_script)
        self.assertIn("ProcessAudioCapture", build_script)
        self.assertIn("Pycaw", build_script)
        self.assertIn("Comtypes", build_script)
        self.assertIn("ONNX Runtime", build_script)
        self.assertIn("NumPy", build_script)
        startup_check = inspect.getsource(
            self.tracker._run_tk_startup_check
        )
        self.assertIn("import pyaudiowpatch", startup_check)
        self.assertIn("import numpy", startup_check)
        self.assertIn("_OfflineVoiceAnalyzer", startup_check)
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
