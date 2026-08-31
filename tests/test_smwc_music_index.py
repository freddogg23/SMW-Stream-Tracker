from array import array
import math
from pathlib import Path
import random
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock
import wave

import smwc_music_index as music_index


SAMPLE_RATE = 22050


def _song_samples(seconds, *, seed, gain=0.72, noise=0.0):
    """Create a deterministic, changing tune with percussion-like attacks."""
    rng = random.Random(seed)
    note_choices = (196.0, 220.0, 246.94, 261.63, 293.66, 329.63, 392.0)
    note_count = max(1, math.ceil(seconds / 0.5))
    notes = [rng.choice(note_choices) for _ in range(note_count)]
    output = array("h")
    for sample_index in range(round(seconds * SAMPLE_RATE)):
        time_seconds = sample_index / SAMPLE_RATE
        note_index = min(len(notes) - 1, int(time_seconds / 0.5))
        local_time = time_seconds - note_index * 0.5
        frequency = notes[note_index]
        envelope = min(1.0, local_time * 25.0) * math.exp(-local_time * 0.42)
        value = (
            math.sin(2.0 * math.pi * frequency * time_seconds)
            + 0.48 * math.sin(2.0 * math.pi * frequency * 1.5 * time_seconds)
            + 0.27 * math.sin(2.0 * math.pi * frequency * 2.0 * time_seconds)
        )
        if local_time < 0.035:
            value += 0.35 * math.sin(2.0 * math.pi * 1250.0 * time_seconds)
        if noise:
            value += rng.uniform(-noise, noise)
        pcm_value = int(max(-1.0, min(1.0, gain * envelope * value / 1.8)) * 32767)
        output.append(pcm_value)
    return output


def _write_wav(path, samples, sample_rate=SAMPLE_RATE):
    with wave.open(str(path), "wb") as destination:
        destination.setnchannels(1)
        destination.setsampwidth(2)
        destination.setframerate(sample_rate)
        destination.writeframes(samples.tobytes())


def _write_stereo_wav(path, left_samples, right_samples, sample_rate=SAMPLE_RATE):
    stereo = array("h")
    for left, right in zip(left_samples, right_samples):
        stereo.extend((left, right))
    with wave.open(str(path), "wb") as destination:
        destination.setnchannels(2)
        destination.setsampwidth(2)
        destination.setframerate(sample_rate)
        destination.writeframes(stereo.tobytes())


class SmwcMusicIndexTests(unittest.TestCase):
    def _build_index(self, folder, *, version, submission_id, seed):
        database = folder / f"music-{version}.sqlite3"
        reference_path = folder / f"reference-{version}.wav"
        _write_wav(reference_path, _song_samples(14.0, seed=seed))
        music_index.initialize_music_index(database, index_version=version)
        music_index.add_track_fingerprints(
            database,
            {
                "submission_id": submission_id,
                "spc_filename": "tune.spc",
                "title": f"Tune {version}",
            },
            music_index.fingerprint_wav(reference_path),
        )
        music_index.finalize_music_index(database)
        return database

    def test_partial_noisy_capture_matches_the_correct_reference(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "music.sqlite3"
            reference_path = folder / "reference.wav"
            other_path = folder / "other.wav"
            query_path = folder / "query.wav"

            reference = _song_samples(28.0, seed=451)
            other = _song_samples(28.0, seed=993)
            _write_wav(reference_path, reference)
            _write_wav(other_path, other)

            start = round(8.0 * SAMPLE_RATE)
            query = array("h", reference[start : start + round(12.0 * SAMPLE_RATE)])
            rng = random.Random(77)
            for index, value in enumerate(query):
                query[index] = max(
                    -32768,
                    min(32767, int(value * 0.58) + rng.randint(-190, 190)),
                )
            _write_wav(query_path, query)

            music_index.initialize_music_index(
                database,
                index_version="2026-08-25.1",
                catalog_updated_at="2026-08-25T00:00:00Z",
            )
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "451",
                    "spc_filename": "reference.spc",
                    "title": "Reference Song",
                    "author": "Composer One",
                    "submission_url": "https://www.smwcentral.net/?p=section&a=details&id=451",
                },
                music_index.fingerprint_wav(reference_path),
            )
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "993",
                    "spc_filename": "other.spc",
                    "title": "Other Song",
                    "author": "Composer Two",
                },
                music_index.fingerprint_wav(other_path),
            )

            matches = music_index.match_wav(database, query_path)

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "451")
            self.assertEqual(matches[0]["title"], "Reference Song")
            self.assertGreaterEqual(matches[0]["confidence"], 55.0)
            self.assertAlmostEqual(matches[0]["offset_seconds"], 8.0, delta=0.5)

    def test_music_focus_filter_suppresses_short_voice_and_effect_bursts(self):
        np = music_index._numpy()
        sample_rate = music_index.TARGET_SAMPLE_RATE
        seconds = 6.0
        times = np.arange(round(seconds * sample_rate), dtype=np.float32) / sample_rate
        music = (
            0.28 * np.sin(2.0 * np.pi * 220.0 * times)
            + 0.17 * np.sin(2.0 * np.pi * 330.0 * times)
        ).astype(np.float32)
        contaminated = music.copy()
        rng = np.random.default_rng(712)
        burst_ranges = []
        for start_seconds in (1.25, 2.85, 4.45):
            start = round(start_seconds * sample_rate)
            stop = start + round(0.16 * sample_rate)
            burst_ranges.append((start, stop))
            envelope = np.hanning((stop - start) * 2)[: stop - start]
            # A loud broadband burst plus a short voice-like formant stack.
            local_times = times[start:stop]
            effect = (
                0.72 * rng.uniform(-1.0, 1.0, stop - start)
                + 0.40 * np.sin(2.0 * np.pi * 720.0 * local_times)
                + 0.30 * np.sin(2.0 * np.pi * 1180.0 * local_times)
            )
            contaminated[start:stop] += effect * envelope

        focused = music_index._music_focused_samples(contaminated, sample_rate)

        clean_mask = np.ones(contaminated.size, dtype=bool)
        burst_mask = np.zeros(contaminated.size, dtype=bool)
        for start, stop in burst_ranges:
            burst_mask[start:stop] = True
            clean_mask[max(0, start - 200): min(clean_mask.size, stop + 200)] = False
        input_burst_ratio = np.sqrt(np.mean(contaminated[burst_mask] ** 2)) / np.sqrt(
            np.mean(contaminated[clean_mask] ** 2)
        )
        focused_burst_ratio = np.sqrt(np.mean(focused[burst_mask] ** 2)) / np.sqrt(
            np.mean(focused[clean_mask] ** 2)
        )
        self.assertLess(focused_burst_ratio, input_burst_ratio * 0.78)
        self.assertGreater(np.sqrt(np.mean(focused[clean_mask] ** 2)), 0.08)

    def test_music_heavy_windows_skip_speech_noise_and_silence(self):
        np = music_index._numpy()
        sample_rate = music_index.TARGET_SAMPLE_RATE
        seconds = 18.0
        times = np.arange(round(seconds * sample_rate), dtype=np.float32) / sample_rate
        recording = np.zeros(times.size, dtype=np.float32)

        noisy_stop = round(5.0 * sample_rate)
        rng = np.random.default_rng(83)
        recording[:noisy_stop] = (
            0.28 * np.sin(2.0 * np.pi * 160.0 * times[:noisy_stop])
            + 0.24 * np.sin(2.0 * np.pi * 840.0 * times[:noisy_stop])
            + 0.18 * rng.uniform(-1.0, 1.0, noisy_stop)
        )
        # Speech-like syllable envelopes create abrupt voice-dominant bursts.
        recording[:noisy_stop] *= (
            0.15
            + 0.85
            * (np.sin(2.0 * np.pi * 3.7 * times[:noisy_stop]) > 0).astype(
                np.float32
            )
        )

        music_start = noisy_stop
        music_stop = round(13.5 * sample_rate)
        music_times = times[music_start:music_stop]
        recording[music_start:music_stop] = (
            0.31 * np.sin(2.0 * np.pi * 220.0 * music_times)
            + 0.20 * np.sin(2.0 * np.pi * 330.0 * music_times)
            + 0.12 * np.sin(2.0 * np.pi * 440.0 * music_times)
        )

        ranges = music_index._music_heavy_ranges(recording, sample_rate)

        self.assertGreaterEqual(len(ranges), 1)
        strongest = max(ranges, key=lambda item: item["score"])
        strongest_center_seconds = (
            strongest["start_sample"] + strongest["stop_sample"]
        ) / (2.0 * sample_rate)
        self.assertGreater(strongest_center_seconds, 5.0)
        self.assertLess(strongest_center_seconds, 13.8)
        self.assertLess(strongest["speech_penalty"], 0.35)

    def test_manifest_and_validation_report_index_contents(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "music.sqlite3"
            reference_path = folder / "reference.wav"
            manifest_path = folder / "manifest.json"
            _write_wav(reference_path, _song_samples(14.0, seed=12))
            music_index.initialize_music_index(database, index_version="12")
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "12",
                    "spc_filename": "tune.spc",
                    "title": "Tune",
                },
                music_index.fingerprint_wav(reference_path),
            )

            details = music_index.validate_music_index(database, require_tracks=True)
            manifest = music_index.write_index_manifest(
                database,
                manifest_path,
                download_url="https://example.invalid/music.sqlite3",
                index_version="12",
            )

            self.assertEqual(details["track_count"], 1)
            self.assertGreater(details["fingerprint_count"], 0)
            self.assertEqual(manifest["track_count"], 1)
            self.assertTrue(manifest["catalog_complete"])
            self.assertEqual(len(manifest["sha256"]), 64)
            self.assertTrue(manifest_path.is_file())

    def test_bundled_index_installs_but_does_not_replace_a_newer_copy(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            bundled = self._build_index(
                folder, version="2026082501", submission_id="1", seed=3
            )
            newer = self._build_index(
                folder, version="2026082502", submission_id="2", seed=4
            )
            installed = folder / "installed.sqlite3"

            first = music_index.ensure_bundled_music_index(bundled, installed)
            self.assertEqual(first["index_version"], "2026082501")
            music_index.ensure_bundled_music_index(newer, installed)
            preserved = music_index.ensure_bundled_music_index(bundled, installed)

            self.assertEqual(preserved["index_version"], "2026082502")
            self.assertEqual(preserved["track_count"], 1)

    def test_downloaded_update_is_verified_before_it_replaces_the_index(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
                self.position = 0
                self.headers = {"Content-Length": str(len(payload))}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, count=-1):
                if self.position >= len(self.payload):
                    return b""
                if count < 0:
                    count = len(self.payload) - self.position
                chunk = self.payload[self.position : self.position + count]
                self.position += len(chunk)
                return chunk

        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            bundled = self._build_index(
                folder, version="2026082501", submission_id="1", seed=5
            )
            update = self._build_index(
                folder, version="2026082502", submission_id="2", seed=6
            )
            installed = folder / "installed.sqlite3"
            music_index.ensure_bundled_music_index(bundled, installed)
            payload = update.read_bytes()
            manifest = {
                "schema_version": music_index.INDEX_SCHEMA_VERSION,
                "fingerprint_algorithm": music_index.FINGERPRINT_ALGORITHM,
                "index_version": "2026082502",
                "track_count": 1,
                "catalog_complete": True,
                "size_bytes": len(payload),
                "sha256": music_index.sha256_file(update),
                "download_url": "https://github.com/example/music.sqlite3",
            }
            progress = []

            with mock.patch.object(
                music_index,
                "urlopen",
                return_value=FakeResponse(payload),
            ):
                installed_details = music_index.download_music_index_update(
                    manifest,
                    installed,
                    progress_callback=lambda current, total: progress.append(
                        (current, total)
                    ),
                )

            self.assertEqual(installed_details["index_version"], "2026082502")
            self.assertEqual(
                music_index.validate_music_index(installed)["index_version"],
                "2026082502",
            )
            self.assertEqual(progress[-1], (len(payload), len(payload)))

    def test_incomplete_starter_index_cannot_claim_a_song_match(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "starter.sqlite3"
            reference_path = folder / "reference.wav"
            _write_wav(reference_path, _song_samples(18.0, seed=101))
            music_index.initialize_music_index(
                database,
                index_version="starter",
                catalog_complete=False,
            )
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "101",
                    "spc_filename": "starter.spc",
                    "title": "Starter Song",
                },
                music_index.fingerprint_wav(reference_path),
            )

            with self.assertRaises(music_index.MusicIndexIncompleteError):
                music_index.match_wav(database, reference_path)

    def test_identical_candidates_are_rejected_as_ambiguous(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "ambiguous.sqlite3"
            reference_path = folder / "reference.wav"
            _write_wav(reference_path, _song_samples(18.0, seed=202))
            fingerprints = music_index.fingerprint_wav(reference_path)
            music_index.initialize_music_index(database, index_version="complete")
            for submission_id in ("202", "203"):
                music_index.add_track_fingerprints(
                    database,
                    {
                        "submission_id": submission_id,
                        "spc_filename": f"{submission_id}.spc",
                        "title": f"Candidate {submission_id}",
                    },
                    fingerprints,
                )

            self.assertEqual(
                music_index.match_wav(database, reference_path),
                [],
            )

    def test_variants_from_one_submission_are_not_rejected_as_ambiguous(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "variants.sqlite3"
            reference_path = folder / "reference.wav"
            _write_wav(reference_path, _song_samples(18.0, seed=303))
            fingerprints = music_index.fingerprint_wav(reference_path)
            music_index.initialize_music_index(database, index_version="complete")
            for filename in ("original.spc", "yoshi-drums.spc"):
                music_index.add_track_fingerprints(
                    database,
                    {
                        "submission_id": "303",
                        "spc_filename": filename,
                        "title": "One Submission",
                    },
                    fingerprints,
                )

            matches = music_index.match_wav(database, reference_path)

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "303")
            self.assertEqual(len(matches), 1)

    def test_stereo_phase_cancellation_still_matches_an_individual_channel(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "stereo.sqlite3"
            reference_path = folder / "reference.wav"
            query_path = folder / "stereo-query.wav"
            reference = _song_samples(18.0, seed=404)
            _write_wav(reference_path, reference)
            _write_stereo_wav(
                query_path,
                reference,
                array("h", (-value for value in reference)),
            )
            music_index.initialize_music_index(database, index_version="complete")
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "404",
                    "spc_filename": "phase-safe.spc",
                    "title": "Phase Safe",
                },
                music_index.fingerprint_wav(reference_path),
            )
            progress = []

            matches = music_index.match_wav(
                database,
                query_path,
                progress_callback=lambda current, total: progress.append(
                    (current, total)
                ),
            )

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "404")
            self.assertIn("channel", matches[0]["match_strategy"])
            self.assertTrue(progress)
            self.assertEqual(progress[-1][1], progress[-1][0])

    def test_chromaprint_sequence_matches_with_capture_bit_errors(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            database = Path(temp_folder) / "chromaprint.sqlite3"
            music_index.initialize_music_index(database, index_version="complete")
            reference = [
                ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
                for position in range(600)
            ]
            distractor = [
                ((position * 2_246_822_519) ^ 0xA5A55A5A) & 0xFFFFFFFF
                for position in range(600)
            ]
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "correct",
                    "spc_filename": "correct.spc",
                    "title": "Correct Waveform",
                },
                [(64_000, 0)],
                reference,
            )
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "other",
                    "spc_filename": "other.spc",
                    "title": "Other Waveform",
                },
                [(64_064, 0)],
                distractor,
            )
            query = [
                value ^ (0x3 if position % 7 == 0 else 0)
                for position, value in enumerate(reference[170:330])
            ]

            matches = music_index.match_chromaprint_values(database, query)

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "correct")
            self.assertEqual(matches[0]["match_strategy"], "Chromaprint waveform")
            self.assertGreater(matches[0]["confidence"], 90.0)

    def test_noisy_but_unambiguous_match_has_calibrated_confidence(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            database = Path(temp_folder) / "noisy-match.sqlite3"
            music_index.initialize_music_index(database, index_version="complete")
            reference = [
                ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
                for position in range(500)
            ]
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "correct",
                    "spc_filename": "correct.spc",
                    "title": "Noisy but Correct",
                },
                [(64_000, 0)],
                reference,
            )
            query = [value ^ 0x3F for value in reference[120:280]]

            matches = music_index.match_chromaprint_values(database, query)

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "correct")
            self.assertGreaterEqual(matches[0]["confidence"], 75.0)
            self.assertLess(matches[0]["confidence"], 90.0)

    def test_confirmed_capture_teaches_the_local_adaptive_model(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "catalog.sqlite3"
            learned_model = folder / "learned.sqlite3"
            music_index.initialize_music_index(database, index_version="complete")
            reference = [
                ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
                for position in range(650)
            ]
            track_key = music_index.stable_track_key("learned", "learned.spc")
            music_index.add_track_fingerprints(
                database,
                {
                    "track_key": track_key,
                    "submission_id": "learned",
                    "spc_filename": "learned.spc",
                    "title": "Learned Song",
                    "author": "Adaptive Composer",
                },
                [(64_000, 0)],
                reference,
            )
            confirmed_capture = [
                value ^ (0x7 if position % 9 == 0 else 0)
                for position, value in enumerate(reference[140:360])
            ]
            stats = music_index.learn_confirmed_music_match(
                learned_model,
                {
                    "track_key": track_key,
                    "submission_id": "learned",
                    "title": "Learned Song",
                    "artist": "Adaptive Composer",
                },
                confirmed_capture,
                source_token="capture-card-1",
            )
            query = [
                value ^ (0x3 if position % 7 == 0 else 0)
                for position, value in enumerate(reference[175:335])
            ]

            matches = music_index.match_learned_chromaprint_values(
                learned_model,
                database,
                query,
                source_token="capture-card-1",
            )

            self.assertEqual(stats, {"sample_count": 1, "track_count": 1})
            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "learned")
            self.assertIn("AI learning", matches[0]["match_strategy"])
            self.assertGreater(matches[0]["confidence"], 85.0)

    def test_unrelated_audio_is_not_forced_into_a_learned_match(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            database = folder / "catalog.sqlite3"
            learned_model = folder / "learned.sqlite3"
            music_index.initialize_music_index(database, index_version="complete")
            reference = [
                ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
                for position in range(500)
            ]
            track_key = music_index.stable_track_key("one", "one.spc")
            music_index.add_track_fingerprints(
                database,
                {
                    "track_key": track_key,
                    "submission_id": "one",
                    "spc_filename": "one.spc",
                    "title": "One Song",
                },
                [(64_000, 0)],
                reference,
            )
            music_index.learn_confirmed_music_match(
                learned_model,
                {"track_key": track_key, "submission_id": "one"},
                reference[100:300],
                source_token="capture-card-1",
            )
            unrelated = [
                ((position * 2_246_822_519) ^ 0xA5A55A5A) & 0xFFFFFFFF
                for position in range(180)
            ]

            self.assertEqual(
                music_index.match_learned_chromaprint_values(
                    learned_model,
                    database,
                    unrelated,
                    source_token="capture-card-1",
                ),
                [],
            )

    def test_community_contribution_contains_only_anonymous_fingerprints(self):
        track_key = music_index.stable_track_key("shared", "shared.spc")
        values = [
            ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
            for position in range(180)
        ]
        contribution = music_index.community_learning_contribution(
            {
                "track_key": track_key,
                "submission_id": "shared",
                "confidence_value": 94.0,
                "title": "Must Not Be Uploaded",
                "artist": "Must Not Be Uploaded",
            },
            values,
            client_id_hash="a" * 64,
            catalog_version="2026-08-27",
            app_version="2.2.0",
        )

        self.assertTrue(contribution["user_confirmed"])
        self.assertEqual(contribution["track_key"], track_key)
        self.assertEqual(contribution["value_count"], len(values))
        self.assertNotIn("title", contribution)
        self.assertNotIn("artist", contribution)
        self.assertNotIn("audio", contribution)
        self.assertNotIn("username", contribution)
        with self.assertRaises(music_index.MusicIndexError):
            music_index.community_learning_contribution(
                {
                    "track_key": track_key,
                    "submission_id": "shared",
                    "confidence_value": 60.0,
                },
                values,
                client_id_hash="a" * 64,
                catalog_version="test",
                app_version="test",
            )

    def test_cloud_landmark_lookup_sends_fingerprints_and_normalizes_result(self):
        values = [
            ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
            for position in range(160)
        ]
        requests = []

        def fake_api(endpoint, route, **options):
            requests.append((endpoint, route, options))
            return {
                "ok": True,
                "matches": [
                    {
                        "track_id": 77,
                        "track_key": "a" * 64,
                        "submission_id": "9911",
                        "spc_filename": "song.spc",
                        "title": "  Cloud   Song  ",
                        "artist": "Porter",
                        "submission_url": "https://www.smwcentral.net/?p=section&id=9911",
                        "download_url": "https://www.smwcentral.net/download/9911",
                        "confidence": 96.35,
                        "audio_distance": 0.07123,
                        "matching_frames": 103,
                        "offset_seconds": 4.875,
                    }
                ],
            }

        with mock.patch.object(
            music_index,
            "_community_api_json",
            side_effect=fake_api,
        ):
            matches = music_index.match_cloud_chromaprint_values(
                "https://recognition.example.test",
                values,
                limit=2,
            )

        self.assertEqual(matches[0]["title"], "Cloud Song")
        self.assertEqual(
            matches[0]["match_strategy"],
            "Cloud landmark fingerprints with time alignment",
        )
        self.assertEqual(requests[0][1], "v1/music/match")
        payload = requests[0][2]["payload"]
        self.assertEqual(payload["catalog"], "smwcentral")
        self.assertEqual(payload["fingerprint_values"], values)
        self.assertNotIn("audio", payload)

    def test_cloud_catalog_status_is_validated_without_downloading_an_index(self):
        with mock.patch.object(
            music_index,
            "_community_api_json",
            return_value={
                "ok": True,
                "catalog": "smwcentral",
                "index_version": "20260829212637",
                "catalog_updated_at": "2026-08-29T21:26:37Z",
                "cloud_updated_at": "2026-08-29T21:31:04Z",
                "track_count": "12353",
                "fingerprints_only": True,
                "raw_audio_collected": False,
            },
        ) as api:
            status = music_index.fetch_cloud_music_catalog_status(
                "https://recognition.example.test"
            )

        self.assertTrue(status["cloud_only"])
        self.assertEqual(status["track_count"], 12353)
        self.assertEqual(status["cloud_updated_at"], "2026-08-29T21:31:04Z")
        self.assertFalse(status["raw_audio_collected"])
        self.assertEqual(api.call_args.args[1], "v1/music/catalog")

    def test_cloud_only_match_does_not_require_or_fall_back_to_local_index(self):
        values = [position * 17 for position in range(180)]
        cloud_result = {
            "track_id": 1,
            "track_key": "b" * 64,
            "submission_id": "9911",
            "spc_filename": "cloud.spc",
            "title": "Cloud Only Song",
            "artist": "Porter",
            "submission_url": "https://www.smwcentral.net/?p=section&id=9911",
            "download_url": "https://www.smwcentral.net/download/9911",
            "confidence": 98.0,
            "match_strategy": "Cloud landmark fingerprints with time alignment",
        }
        samples = [0.0] * 4096
        with (
            mock.patch.object(
                music_index,
                "_pcm16_channel_variants",
                return_value=([("mono", samples)], 22050),
            ),
            mock.patch.object(
                music_index,
                "_music_focused_samples",
                return_value=samples,
            ),
            mock.patch.object(
                music_index,
                "_music_spectral_flatness",
                return_value=0.1,
            ),
            mock.patch.object(
                music_index,
                "chromaprint_fingerprint_samples",
                return_value=values,
            ),
            mock.patch.object(
                music_index,
                "match_cloud_chromaprint_values",
                return_value=[cloud_result],
            ) as cloud_match,
            mock.patch.object(
                music_index,
                "validate_music_index",
                side_effect=AssertionError("local index must not be opened"),
            ),
        ):
            matches = music_index.match_wav(
                Path("missing-local-index.sqlite3"),
                Path("temporary-sample.wav"),
                recognition_api_url="https://recognition.example.test",
                cloud_only=True,
            )

        self.assertEqual(matches[0]["title"], "Cloud Only Song")
        cloud_match.assert_called_once()

    def test_approved_community_model_syncs_and_matches_locally(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            catalog = folder / "catalog.sqlite3"
            community_model = folder / "community.sqlite3"
            music_index.initialize_music_index(catalog, index_version="complete")
            reference = [
                ((position * 2_654_435_761) ^ (position << 9)) & 0xFFFFFFFF
                for position in range(520)
            ]
            track_key = music_index.stable_track_key("shared", "shared.spc")
            music_index.add_track_fingerprints(
                catalog,
                {
                    "track_key": track_key,
                    "submission_id": "shared",
                    "spc_filename": "shared.spc",
                    "title": "Community Song",
                    "author": "Community Composer",
                },
                [(64_000, 0)],
                reference,
            )
            confirmed = reference[120:340]
            contribution = music_index.community_learning_contribution(
                {
                    "track_key": track_key,
                    "submission_id": "shared",
                    "confidence_value": 96.0,
                },
                confirmed,
                client_id_hash="b" * 64,
                catalog_version="complete",
                app_version="test",
            )
            approved_example = {
                "id": 7,
                "track_key": contribution["track_key"],
                "submission_id": contribution["submission_id"],
                "fingerprint_sha256": contribution["fingerprint_sha256"],
                "fingerprint_base64": contribution["fingerprint_base64"],
                "value_count": contribution["value_count"],
            }

            def fake_api(_endpoint, route, **_options):
                if route == "v1/model/manifest":
                    return {
                        "schema_version": 1,
                        "model_revision": 4,
                        "total_examples": 1,
                    }
                return {
                    "schema_version": 1,
                    "examples": [approved_example],
                    "next_cursor": None,
                }

            with mock.patch.object(
                music_index,
                "_community_api_json",
                side_effect=fake_api,
            ):
                details = music_index.sync_community_learning_model(
                    "https://community.example.test",
                    community_model,
                )

            query = [
                value ^ (0x3 if position % 11 == 0 else 0)
                for position, value in enumerate(reference[150:320])
            ]
            matches = music_index.match_learned_chromaprint_values(
                community_model,
                catalog,
                query,
                source_token="different-capture-card",
            )

            self.assertTrue(details["updated"])
            self.assertEqual(details["model_revision"], 4)
            self.assertEqual(details["sample_count"], 1)
            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "shared")

    def test_incremental_update_replaces_only_changed_submissions(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            base = folder / "base.sqlite3"
            current = folder / "current.sqlite3"
            update = folder / "update.sqlite3"
            installed = folder / "installed.sqlite3"

            music_index.initialize_music_index(base, index_version="100")
            music_index.initialize_music_index(current, index_version="200")

            def add_track(database, submission_id, updated_at, title):
                music_index.add_track_fingerprints(
                    database,
                    {
                        "submission_id": submission_id,
                        "submission_updated_at": updated_at,
                        "spc_filename": f"{submission_id}.spc",
                        "title": title,
                    },
                    [(40_000 + int(submission_id), 0)],
                )

            add_track(base, "1", "10", "Old Song")
            add_track(base, "2", "10", "Removed Song")
            add_track(current, "1", "20", "Updated Song")
            add_track(current, "3", "20", "New Song")
            music_index.finalize_music_index(base)
            music_index.finalize_music_index(current)

            update_details = music_index.create_incremental_music_update(
                base,
                current,
                update,
            )
            shutil.copyfile(base, installed)
            installed_details = music_index.apply_incremental_music_update(
                installed,
                update,
            )

            self.assertEqual(update_details["submission_count"], 2)
            self.assertEqual(update_details["deleted_submission_count"], 1)
            self.assertEqual(installed_details["index_version"], "200")
            connection = sqlite3.connect(installed)
            try:
                rows = connection.execute(
                    "SELECT submission_id, title FROM tracks "
                    "ORDER BY submission_id"
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(
                rows,
                [("1", "Updated Song"), ("3", "New Song")],
            )

    def test_incremental_download_never_replaces_the_full_database(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
                self.position = 0

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, count=-1):
                if self.position >= len(self.payload):
                    return b""
                if count < 0:
                    count = len(self.payload) - self.position
                chunk = self.payload[self.position : self.position + count]
                self.position += len(chunk)
                return chunk

        with tempfile.TemporaryDirectory() as temp_folder:
            folder = Path(temp_folder)
            base = folder / "base.sqlite3"
            current = folder / "current.sqlite3"
            update = folder / "update.sqlite3"
            installed = folder / "installed.sqlite3"
            manifest_path = folder / "manifest.json"
            music_index.initialize_music_index(base, index_version="100")
            music_index.initialize_music_index(current, index_version="200")
            for database, title, updated_at in (
                (base, "Bundled Song", "10"),
                (current, "Changed Song", "20"),
            ):
                music_index.add_track_fingerprints(
                    database,
                    {
                        "submission_id": "1",
                        "submission_updated_at": updated_at,
                        "spc_filename": "song.spc",
                        "title": title,
                    },
                    [(51_000, 0)],
                )
                music_index.finalize_music_index(database)
            update_details = music_index.create_incremental_music_update(
                base,
                current,
                update,
            )
            manifest = music_index.write_index_manifest(
                current,
                manifest_path,
                download_url="https://github.com/example/full.sqlite3",
                index_version="200",
            )
            payload = update.read_bytes()
            manifest["incremental_update"] = {
                "base_index_version": "100",
                "index_version": "200",
                "submission_count": 1,
                "deleted_submission_count": 0,
                "track_count": update_details["track_count"],
                "size_bytes": len(payload),
                "sha256": music_index.sha256_file(update),
                "download_url": "https://github.com/example/update.sqlite3",
            }
            shutil.copyfile(base, installed)
            progress = []

            with mock.patch.object(
                music_index,
                "urlopen",
                return_value=FakeResponse(payload),
            ):
                result = music_index.download_incremental_music_update(
                    manifest,
                    installed,
                    progress_callback=lambda current_bytes, total: progress.append(
                        (current_bytes, total)
                    ),
                )

            self.assertEqual(result["index_version"], "200")
            self.assertEqual(progress[-1], (len(payload), len(payload)))
            self.assertGreater(result["track_count"], 0)

    def test_common_catalog_hashes_do_not_penalize_a_distinctive_match(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            database = Path(temp_folder) / "catalog.sqlite3"
            music_index.initialize_music_index(database, index_version="complete")
            common_hashes = list(range(20_000, 20_040))
            for track_number in range(31):
                music_index.add_track_fingerprints(
                    database,
                    {
                        "submission_id": f"common-{track_number}",
                        "spc_filename": f"common-{track_number}.spc",
                        "title": f"Common Track {track_number}",
                    },
                    [(landmark, position) for position, landmark in enumerate(common_hashes)],
                )

            distinctive_reference = [
                (31_001, 100),
                (31_001, 110),
                (31_002, 102),
                (31_003, 104),
                (31_004, 106),
                (31_005, 108),
            ]
            music_index.add_track_fingerprints(
                database,
                {
                    "submission_id": "correct",
                    "spc_filename": "correct.spc",
                    "title": "Correct Track",
                },
                [(landmark, position) for position, landmark in enumerate(common_hashes)]
                + distinctive_reference,
            )
            query = [
                (landmark, position) for position, landmark in enumerate(common_hashes)
            ] + [
                (31_001, 0),
                (31_001, 10),
                (31_002, 2),
                (31_003, 4),
                (31_004, 6),
                (31_005, 8),
            ]

            matches = music_index.match_fingerprints(database, query)

            self.assertTrue(matches)
            self.assertEqual(matches[0]["submission_id"], "correct")
            self.assertEqual(matches[0]["matching_hashes"], 5)
            self.assertEqual(matches[0]["query_hashes"], 5)

    def test_multi_section_chromaprint_requires_two_matching_sections(self):
        correct = {
            "submission_id": "correct",
            "title": "Correct Track",
            "confidence": 88.0,
        }
        wrong = {
            "submission_id": "wrong",
            "title": "Wrong Track",
            "confidence": 92.0,
        }
        query = list(range(
            music_index.CHROMAPRINT_SECTION_MINIMUM_TOTAL_VALUES + 12
        ))
        with mock.patch.object(
            music_index,
            "match_chromaprint_values",
            side_effect=[[correct], [wrong], [correct]],
        ):
            matches = music_index.match_chromaprint_sections(
                Path("unused.sqlite3"),
                query,
            )

        self.assertTrue(matches)
        self.assertEqual(matches[0]["submission_id"], "correct")
        self.assertEqual(matches[0]["matching_sections"], 2)
        self.assertEqual(matches[0]["checked_sections"], 3)
        self.assertIn("intro/middle/loop", matches[0]["match_strategy"])

    def test_multi_section_chromaprint_rejects_three_different_songs(self):
        query = list(range(
            music_index.CHROMAPRINT_SECTION_MINIMUM_TOTAL_VALUES + 12
        ))
        section_results = [
            [{"submission_id": submission, "confidence": 90.0}]
            for submission in ("intro", "middle", "loop")
        ]
        with mock.patch.object(
            music_index,
            "match_chromaprint_values",
            side_effect=section_results,
        ):
            matches = music_index.match_chromaprint_sections(
                Path("unused.sqlite3"),
                query,
            )

        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
