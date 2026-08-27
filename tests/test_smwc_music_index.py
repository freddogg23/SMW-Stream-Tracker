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


if __name__ == "__main__":
    unittest.main()
