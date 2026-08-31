"""SMW Central SPC audio fingerprint indexing and matching.

The database contains non-reconstructive frequency-landmark hashes plus the
public metadata needed to link a result back to SMW Central. Captured audio is
never uploaded; an optional cloud lookup sends only compact, non-reconstructive
fingerprint numbers and falls back to the installed catalog when unavailable.
"""

from __future__ import annotations

from array import array
import base64
import binascii
from collections import Counter, defaultdict
from contextlib import closing
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import wave
import zlib


INDEX_SCHEMA_VERSION = 2
FINGERPRINT_ALGORITHM = "smwc-chromaprint-v1"
CHROMAPRINT_VERSION = "1.6.1"
CHROMAPRINT_TOKEN_SHIFT = 20
CHROMAPRINT_TOKEN_STRIDE = 2
CHROMAPRINT_MINIMUM_VALUES = 40
CHROMAPRINT_MAXIMUM_DISTANCE = 0.24
CHROMAPRINT_RUNNER_SEPARATION = 0.025
CHROMAPRINT_SECTION_COUNT = 3
CHROMAPRINT_SECTION_MINIMUM_TOTAL_VALUES = (
    CHROMAPRINT_MINIMUM_VALUES * CHROMAPRINT_SECTION_COUNT
)
TARGET_SAMPLE_RATE = 11025
FFT_WINDOW = 2048
FFT_HOP = 512
PEAKS_PER_FRAME = 4
PAIR_TARGET_FRAME_OFFSETS = (11, 22, 43)
HASH_RETENTION_MODULUS = 64
MINIMUM_MATCH_VOTES = 6
MATCH_SAMPLE_RATE_FACTORS = (1.0, 0.9975, 1.0025, 0.995, 1.005)
QUERY_FREQUENCY_BIN_OFFSETS = (-4, -2, 0, 2, 4)
QUERY_TIME_FRAME_OFFSETS = (-2, -1, 0, 1, 2)
SQLITE_QUERY_CHUNK = 450
FILE_HASH_CHUNK = 1024 * 1024
MUSIC_INDEX_DOWNLOAD_LIMIT = 512 * 1024 * 1024
MUSIC_INDEX_INCREMENTAL_DOWNLOAD_LIMIT = 128 * 1024 * 1024
MUSIC_INDEX_MANIFEST_LIMIT = 256 * 1024
COMMUNITY_API_RESPONSE_LIMIT = 32 * 1024 * 1024
MUSIC_MATCH_API_RESPONSE_LIMIT = 512 * 1024
COMMUNITY_MODEL_MAXIMUM_EXAMPLES = 50_000
MUSIC_INDEX_ALLOWED_HOSTS = frozenset(
    {
        "raw.githubusercontent.com",
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
MUSIC_INDEX_LOCK = threading.RLock()

# Live game audio is not a clean SPC render. Short Mario voices, jumps,
# doors, spin sounds, and similar effects create brief vertical bursts across
# the spectrum. A temporal spectral limiter keeps tones that persist between
# neighboring frames and turns down energy that appears only for a moment.
# The unfiltered recording remains a fallback, so percussion-heavy ports are
# not made unmatchable by the cleanup pass.
MUSIC_FOCUS_TEMPORAL_RADIUS = 4
MUSIC_FOCUS_TRANSIENT_LIMIT = 1.45
MUSIC_FOCUS_MINIMUM_GAIN = 0.08
MUSIC_QUALITY_WINDOW_SECONDS = 4.8
MUSIC_QUALITY_HOP_SECONDS = 1.4
MUSIC_QUALITY_MAXIMUM_WINDOWS = 3

# The adaptive model stores only non-reconstructive Chromaprint sequences from
# matches the user explicitly confirms.  Those live-capture examples teach the
# matcher the user's real capture card, volume, and room/SFX characteristics
# without retaining any recorded audio.
LEARNED_MODEL_SCHEMA_VERSION = 1
LEARNED_MODEL_MAX_SAMPLES_PER_TRACK_SOURCE = 8
LEARNED_MODEL_MAXIMUM_DISTANCE = 0.19
LEARNED_MODEL_CROSS_SOURCE_MAXIMUM_DISTANCE = 0.16
LEARNED_MODEL_RUNNER_SEPARATION = 0.018


class MusicIndexError(RuntimeError):
    """Raised when an SMW Central music index cannot be used safely."""


class MusicIndexIncompleteError(MusicIndexError):
    """Raised when only the bundled starter catalog is installed."""


def _numpy():
    try:
        import numpy as np
    except ImportError as error:
        raise MusicIndexError(
            "Local music matching support is missing NumPy."
        ) from error
    return np


def _connect(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    database_path = Path(path).resolve()
    if read_only:
        connection = sqlite3.connect(
            f"file:{database_path.as_posix()}?mode=ro",
            uri=True,
            timeout=20,
        )
    else:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path, timeout=30)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_music_index(
    path: Path,
    *,
    index_version: str = "0",
    catalog_updated_at: str = "",
    catalog_complete: bool = True,
) -> None:
    """Create or upgrade the small, append-friendly SQLite index schema."""
    with closing(_connect(path)) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                track_key TEXT NOT NULL UNIQUE,
                submission_id TEXT NOT NULL,
                submission_updated_at TEXT NOT NULL DEFAULT '',
                spc_filename TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT '',
                submission_url TEXT NOT NULL DEFAULT '',
                download_url TEXT NOT NULL DEFAULT '',
                duration_seconds REAL NOT NULL DEFAULT 0,
                fingerprint_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS fingerprints (
                hash INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                frame INTEGER NOT NULL,
                FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS fingerprints_hash_idx
                ON fingerprints(hash);
            CREATE INDEX IF NOT EXISTS fingerprints_track_idx
                ON fingerprints(track_id);
            CREATE TABLE IF NOT EXISTS chromaprint_data (
                track_id INTEGER PRIMARY KEY,
                value_count INTEGER NOT NULL,
                fingerprint BLOB NOT NULL,
                FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS chromaprint_tokens (
                token INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                frame INTEGER NOT NULL,
                FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS chromaprint_tokens_token_idx
                ON chromaprint_tokens(token);
            CREATE INDEX IF NOT EXISTS chromaprint_tokens_track_idx
                ON chromaprint_tokens(track_id);
            """
        )
        metadata = {
            "schema_version": str(INDEX_SCHEMA_VERSION),
            "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "index_version": str(index_version),
            "catalog_updated_at": str(catalog_updated_at),
            "catalog_complete": "1" if catalog_complete else "0",
            "chromaprint_version": CHROMAPRINT_VERSION,
        }
        connection.executemany(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)",
            metadata.items(),
        )
        connection.commit()


def music_index_metadata(path: Path) -> dict[str, str]:
    if not Path(path).is_file():
        return {}
    try:
        with closing(_connect(path, read_only=True)) as connection:
            rows = connection.execute(
                "SELECT key, value FROM metadata"
            ).fetchall()
    except sqlite3.Error:
        return {}
    return {str(row["key"]): str(row["value"]) for row in rows}


def update_music_index_metadata(path: Path, values: dict[str, object]) -> None:
    """Update publication metadata without rebuilding the fingerprint tables."""
    with closing(_connect(path)) as connection:
        connection.executemany(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)",
            ((str(key), str(value)) for key, value in values.items()),
        )
        connection.commit()


def validate_music_index(
    path: Path,
    *,
    require_tracks: bool = False,
    require_complete: bool = False,
) -> dict[str, Any]:
    """Validate compatibility and run SQLite's inexpensive integrity check."""
    database_path = Path(path)
    if not database_path.is_file():
        raise MusicIndexError("The SMW Central music index is not installed.")
    try:
        with closing(_connect(database_path, read_only=True)) as connection:
            integrity = connection.execute("PRAGMA quick_check").fetchone()
            if integrity is None or str(integrity[0]).casefold() != "ok":
                raise MusicIndexError("The SMW Central music index is damaged.")
            metadata = {
                str(row["key"]): str(row["value"])
                for row in connection.execute(
                    "SELECT key, value FROM metadata"
                ).fetchall()
            }
            track_count = int(
                connection.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
            )
            fingerprint_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM fingerprints"
                ).fetchone()[0]
            )
            chromaprint_track_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM chromaprint_data"
                ).fetchone()[0]
            )
            chromaprint_token_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM chromaprint_tokens"
                ).fetchone()[0]
            )
    except sqlite3.Error as error:
        raise MusicIndexError(
            "The SMW Central music index could not be opened."
        ) from error
    if metadata.get("schema_version") != str(INDEX_SCHEMA_VERSION):
        raise MusicIndexError("The installed music index uses an unsupported format.")
    if metadata.get("fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        raise MusicIndexError(
            "The installed music index uses an incompatible fingerprint algorithm."
        )
    if require_tracks and (
        track_count <= 0
        or (fingerprint_count <= 0 and chromaprint_track_count <= 0)
    ):
        raise MusicIndexError("The installed SMW Central music index is empty.")
    if require_complete and metadata.get("catalog_complete") != "1":
        raise MusicIndexIncompleteError(
            "Only the starter music index is installed. Check Music Index to "
            "download the complete SMW Central catalog before identifying a song."
        )
    return {
        **metadata,
        "track_count": track_count,
        "fingerprint_count": fingerprint_count,
        "chromaprint_track_count": chromaprint_track_count,
        "chromaprint_token_count": chromaprint_token_count,
        "size_bytes": database_path.stat().st_size,
    }


def _version_key(value: object) -> tuple[tuple[int, object], ...]:
    parts = []
    for part in str(value or "").replace("-", ".").split("."):
        if part.isdigit():
            parts.append((1, int(part)))
        else:
            parts.append((0, part.casefold()))
    return tuple(parts)


def _atomic_index_copy(source: Path, destination: Path) -> dict[str, Any]:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        destination.name + f".{os.getpid()}.{threading.get_ident()}.tmp"
    )
    try:
        with Path(source).open("rb") as source_file, temporary.open("wb") as output:
            while True:
                chunk = source_file.read(FILE_HASH_CHUNK)
                if not chunk:
                    break
                output.write(chunk)
        details = validate_music_index(temporary, require_tracks=True)
        os.replace(temporary, destination)
        return details
    finally:
        temporary.unlink(missing_ok=True)


def ensure_bundled_music_index(
    bundled_path: Path,
    installed_path: Path,
) -> dict[str, Any]:
    """Install the bundled starter index, preserving a newer downloaded one."""
    bundled = validate_music_index(Path(bundled_path), require_tracks=True)
    installed: dict[str, Any] = {}
    try:
        installed = validate_music_index(Path(installed_path), require_tracks=True)
    except MusicIndexError:
        installed = {}
    if installed and _version_key(installed.get("index_version")) >= _version_key(
        bundled.get("index_version")
    ):
        return installed
    with MUSIC_INDEX_LOCK:
        return _atomic_index_copy(Path(bundled_path), Path(installed_path))


def validate_index_manifest(document: object) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise MusicIndexError("The music-index update information is invalid.")
    try:
        schema_version = int(document.get("schema_version", -1))
        size_bytes = int(document.get("size_bytes", 0))
        track_count = int(document.get("track_count", 0))
    except (TypeError, ValueError) as error:
        raise MusicIndexError("The music-index update information is invalid.") from error
    sha256 = str(document.get("sha256", "")).strip().casefold()
    download_url = str(document.get("download_url", "")).strip()
    parsed = urlparse(download_url)
    if schema_version != INDEX_SCHEMA_VERSION:
        raise MusicIndexError("The available music index uses an unsupported format.")
    if str(document.get("fingerprint_algorithm", "")) != FINGERPRINT_ALGORITHM:
        raise MusicIndexError("The available music index uses an incompatible matcher.")
    if document.get("catalog_complete") is not True:
        raise MusicIndexIncompleteError(
            "The available music-index update does not contain the complete catalog."
        )
    if not str(document.get("index_version", "")).strip():
        raise MusicIndexError("The music-index update has no version.")
    if not (1 <= size_bytes <= MUSIC_INDEX_DOWNLOAD_LIMIT):
        raise MusicIndexError("The available music index has an invalid size.")
    if track_count <= 0 or not re_full_sha256(sha256):
        raise MusicIndexError("The music-index update failed its safety information check.")
    if (
        parsed.scheme.casefold() != "https"
        or (parsed.hostname or "").casefold() not in MUSIC_INDEX_ALLOWED_HOSTS
    ):
        raise MusicIndexError("The music-index update location is not trusted.")
    return {
        **document,
        "schema_version": schema_version,
        "size_bytes": size_bytes,
        "track_count": track_count,
        "catalog_complete": True,
        "sha256": sha256,
        "download_url": download_url,
        "index_version": str(document["index_version"]),
    }


def music_index_update_needed(
    manifest: dict[str, Any],
    installed_details: dict[str, Any],
) -> bool:
    checked = validate_index_manifest(manifest)
    return _version_key(checked["index_version"]) > _version_key(
        installed_details.get("index_version", "")
    )


def validate_incremental_update_manifest(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Validate the small cumulative update advertised by the catalog."""
    checked_manifest = validate_index_manifest(manifest)
    document = checked_manifest.get("incremental_update")
    if not isinstance(document, dict):
        raise MusicIndexError(
            "New music is available in a newer app version, but no incremental "
            "music update was published."
        )
    try:
        size_bytes = int(document.get("size_bytes", 0))
        submission_count = int(document.get("submission_count", 0))
        track_count = int(document.get("track_count", 0))
        deleted_submission_count = int(
            document.get("deleted_submission_count", 0)
        )
    except (TypeError, ValueError) as error:
        raise MusicIndexError(
            "The incremental music update information is invalid."
        ) from error
    base_version = str(document.get("base_index_version", "")).strip()
    target_version = str(document.get("index_version", "")).strip()
    sha256 = str(document.get("sha256", "")).strip().casefold()
    download_url = str(document.get("download_url", "")).strip()
    parsed = urlparse(download_url)
    if not base_version or target_version != checked_manifest["index_version"]:
        raise MusicIndexError(
            "The incremental music update has incompatible version information."
        )
    if not (1 <= size_bytes <= MUSIC_INDEX_INCREMENTAL_DOWNLOAD_LIMIT):
        raise MusicIndexError("The incremental music update has an invalid size.")
    if min(submission_count, track_count, deleted_submission_count) < 0:
        raise MusicIndexError("The incremental music update has invalid counts.")
    if submission_count + deleted_submission_count <= 0:
        raise MusicIndexError("The incremental music update contains no changes.")
    if not re_full_sha256(sha256):
        raise MusicIndexError(
            "The incremental music update failed its safety information check."
        )
    if (
        parsed.scheme.casefold() != "https"
        or (parsed.hostname or "").casefold() not in MUSIC_INDEX_ALLOWED_HOSTS
    ):
        raise MusicIndexError(
            "The incremental music update location is not trusted."
        )
    return {
        **document,
        "base_index_version": base_version,
        "index_version": target_version,
        "size_bytes": size_bytes,
        "submission_count": submission_count,
        "track_count": track_count,
        "deleted_submission_count": deleted_submission_count,
        "sha256": sha256,
        "download_url": download_url,
    }


def re_full_sha256(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _read_limited_response(response: Any, maximum_bytes: int) -> bytes:
    try:
        expected = int(response.headers.get("Content-Length", "0") or 0)
    except (AttributeError, TypeError, ValueError):
        expected = 0
    if expected > maximum_bytes:
        raise MusicIndexError("The music-index download is unexpectedly large.")
    payload = bytearray()
    while True:
        chunk = response.read(min(FILE_HASH_CHUNK, maximum_bytes + 1 - len(payload)))
        if not chunk:
            break
        payload.extend(chunk)
        if len(payload) > maximum_bytes:
            raise MusicIndexError("The music-index download exceeded its safe limit.")
    return bytes(payload)


def fetch_music_index_manifest(manifest_url: str) -> dict[str, Any]:
    parsed = urlparse(str(manifest_url))
    if (
        parsed.scheme.casefold() != "https"
        or (parsed.hostname or "").casefold() not in MUSIC_INDEX_ALLOWED_HOSTS
    ):
        raise MusicIndexError("The music-index update location is not trusted.")
    request = Request(
        str(manifest_url),
        headers={"User-Agent": "SMW-Stream-Tracker-Music-Index/1.0"},
    )
    try:
        with urlopen(request, timeout=25) as response:
            payload = _read_limited_response(response, MUSIC_INDEX_MANIFEST_LIMIT)
        document = json.loads(payload.decode("utf-8"))
    except (HTTPError, URLError, OSError, ValueError) as error:
        raise MusicIndexError("The music-index update check could not be completed.") from error
    return validate_index_manifest(document)


def download_music_index_update(
    manifest: dict[str, Any],
    installed_path: Path,
    *,
    progress_callback=None,
) -> dict[str, Any]:
    """Download, checksum, validate, then atomically activate one index."""
    checked = validate_index_manifest(manifest)
    destination = Path(installed_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        destination.name + f".{os.getpid()}.{threading.get_ident()}.download"
    )
    request = Request(
        checked["download_url"],
        headers={"User-Agent": "SMW-Stream-Tracker-Music-Index/1.0"},
    )
    digest = hashlib.sha256()
    downloaded = 0
    try:
        try:
            response_context = urlopen(request, timeout=60)
        except (HTTPError, URLError, OSError) as error:
            raise MusicIndexError("The updated music index could not be downloaded.") from error
        with response_context as response, temporary.open("wb") as output:
            while True:
                chunk = response.read(FILE_HASH_CHUNK)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MUSIC_INDEX_DOWNLOAD_LIMIT:
                    raise MusicIndexError("The music-index download exceeded its safe limit.")
                output.write(chunk)
                digest.update(chunk)
                if progress_callback is not None:
                    progress_callback(downloaded, checked["size_bytes"])
        if downloaded != checked["size_bytes"]:
            raise MusicIndexError("The music-index download was incomplete.")
        if digest.hexdigest().casefold() != checked["sha256"]:
            raise MusicIndexError("The music-index download failed its safety check.")
        details = validate_music_index(
            temporary,
            require_tracks=True,
            require_complete=True,
        )
        if str(details.get("index_version", "")) != checked["index_version"]:
            raise MusicIndexError("The downloaded music index has the wrong version.")
        if int(details.get("track_count", 0)) != checked["track_count"]:
            raise MusicIndexError("The downloaded music index is incomplete.")
        with MUSIC_INDEX_LOCK:
            os.replace(temporary, destination)
        return details
    finally:
        temporary.unlink(missing_ok=True)


def download_incremental_music_update(
    manifest: dict[str, Any],
    installed_path: Path,
    *,
    progress_callback=None,
) -> dict[str, Any]:
    """Download and merge only new, changed, or removed music submissions."""
    checked = validate_incremental_update_manifest(manifest)
    installed = validate_music_index(
        installed_path,
        require_tracks=True,
        require_complete=True,
    )
    if _version_key(installed.get("index_version", "")) >= _version_key(
        checked["index_version"]
    ):
        return installed
    if _version_key(installed.get("index_version", "")) < _version_key(
        checked["base_index_version"]
    ):
        raise MusicIndexError(
            "This music update needs the catalog bundled with a newer app version."
        )

    destination = Path(installed_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        destination.name
        + f".{os.getpid()}.{threading.get_ident()}.incremental-download"
    )
    request = Request(
        checked["download_url"],
        headers={"User-Agent": "SMW-Stream-Tracker-Music-Index/2.0"},
    )
    digest = hashlib.sha256()
    downloaded = 0
    try:
        try:
            response_context = urlopen(request, timeout=60)
        except (HTTPError, URLError, OSError) as error:
            raise MusicIndexError(
                "The new and changed songs could not be downloaded."
            ) from error
        with response_context as response, temporary.open("wb") as output:
            while True:
                chunk = response.read(FILE_HASH_CHUNK)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MUSIC_INDEX_INCREMENTAL_DOWNLOAD_LIMIT:
                    raise MusicIndexError(
                        "The incremental music update exceeded its safe limit."
                    )
                output.write(chunk)
                digest.update(chunk)
                if progress_callback is not None:
                    progress_callback(downloaded, checked["size_bytes"])
        if downloaded != checked["size_bytes"]:
            raise MusicIndexError(
                "The incremental music update download was incomplete."
            )
        if digest.hexdigest().casefold() != checked["sha256"]:
            raise MusicIndexError(
                "The incremental music update failed its safety check."
            )
        update = validate_incremental_music_update(temporary)
        if str(update.get("base_index_version", "")) != checked[
            "base_index_version"
        ] or str(update.get("index_version", "")) != checked["index_version"]:
            raise MusicIndexError(
                "The downloaded music update has the wrong version."
            )
        if int(update.get("track_count", 0)) != checked["track_count"]:
            raise MusicIndexError(
                "The downloaded music update has an invalid track count."
            )
        return apply_incremental_music_update(destination, temporary)
    finally:
        temporary.unlink(missing_ok=True)


def _pcm16_channel_variants(path: Path) -> tuple[list[tuple[str, Any]], int]:
    """Return normalized mix/left/right candidates for a captured WAV.

    Capture interfaces frequently route game audio to only one side, or put a
    microphone/monitor mix on the other side. Averaging those inputs can bury
    the SPC landmarks or even cancel them. Keeping the useful channels as
    independent query candidates makes live HDMI and mixer captures match the
    same reference data without changing the index format.
    """
    np = _numpy()
    with wave.open(str(path), "rb") as audio_file:
        channels = int(audio_file.getnchannels())
        width = int(audio_file.getsampwidth())
        sample_rate = int(audio_file.getframerate())
        compression = audio_file.getcomptype()
        raw_frames = audio_file.readframes(audio_file.getnframes())
    if width != 2 or compression != "NONE":
        raise MusicIndexError("Music fingerprints require an uncompressed 16-bit WAV.")
    samples = np.frombuffer(raw_frames, dtype="<i2").astype(np.float32)
    channel_count = max(1, channels)
    complete = samples.size - (samples.size % channel_count)
    if complete < max(FFT_WINDOW, sample_rate) * channel_count:
        raise MusicIndexError("The audio sample is too short to identify.")
    matrix = samples[:complete].reshape((-1, channel_count))
    raw_candidates: list[tuple[str, Any]] = []
    if channel_count == 1:
        raw_candidates.append(("mono", matrix[:, 0]))
    else:
        raw_candidates.append(("stereo mix", matrix.mean(axis=1)))
        raw_candidates.extend(
            (f"channel {channel_index + 1}", matrix[:, channel_index])
            for channel_index in range(min(2, channel_count))
        )

    variants: list[tuple[str, Any]] = []
    for label, candidate in raw_candidates:
        normalized = candidate.astype(np.float32, copy=True)
        normalized -= float(normalized.mean())
        peak = float(np.max(np.abs(normalized)))
        if not math.isfinite(peak) or peak < 32.0:
            continue
        normalized /= peak
        if any(
            existing.size == normalized.size
            and bool(np.allclose(existing, normalized, atol=1e-5, rtol=1e-5))
            for _existing_label, existing in variants
        ):
            continue
        variants.append((label, normalized))
    if not variants:
        raise MusicIndexError("The selected source did not contain usable music.")
    return variants, sample_rate


def _pcm16_mono(path: Path) -> tuple[Any, int]:
    variants, sample_rate = _pcm16_channel_variants(path)
    return variants[0][1], sample_rate


def default_chromaprint_executable() -> Path:
    """Return the bundled Windows fpcalc executable used for local matching."""
    application_root = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    )
    candidates = (
        application_root / "chromaprint" / "fpcalc.exe",
        Path(__file__).resolve().parent / "tools" / "chromaprint" / "fpcalc.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise MusicIndexError(
        "The local Chromaprint audio matcher is missing from this application build."
    )


def chromaprint_fingerprint_wav(
    path: Path,
    executable: Path | None = None,
) -> list[int]:
    """Generate a raw, non-reconstructive Chromaprint sequence locally."""
    tool = Path(executable) if executable is not None else default_chromaprint_executable()
    if not tool.is_file():
        raise MusicIndexError("The local Chromaprint audio matcher was not found.")
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        completed = subprocess.run(
            [
                str(tool),
                "-raw",
                "-json",
                "-length",
                "180",
                str(Path(path)),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=210,
            creationflags=creation_flags,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise MusicIndexError(
            "The local Chromaprint audio matcher could not process the sample."
        ) from error
    if completed.returncode != 0:
        raise MusicIndexError(
            "The local Chromaprint audio matcher could not process the sample."
        )
    try:
        document = json.loads(completed.stdout)
        values = [
            int(value) & 0xFFFFFFFF
            for value in document.get("fingerprint", [])
        ]
    except (AttributeError, TypeError, ValueError) as error:
        raise MusicIndexError(
            "The local Chromaprint audio matcher returned invalid data."
        ) from error
    if len(values) < CHROMAPRINT_MINIMUM_VALUES:
        raise MusicIndexError("The audio sample is too short to identify.")
    return values


def _encode_chromaprint_values(values: Sequence[int]) -> bytes:
    packed = array("I", (int(value) & 0xFFFFFFFF for value in values))
    if packed.itemsize != 4:
        raise MusicIndexError("This computer cannot encode music fingerprints.")
    if sys.byteorder != "little":
        packed.byteswap()
    return zlib.compress(packed.tobytes(), level=9)


def _decode_chromaprint_values(payload: bytes) -> list[int]:
    try:
        raw = zlib.decompress(bytes(payload))
    except zlib.error as error:
        raise MusicIndexError("The installed music index is damaged.") from error
    packed = array("I")
    packed.frombytes(raw)
    if packed.itemsize != 4:
        raise MusicIndexError("This computer cannot decode music fingerprints.")
    if sys.byteorder != "little":
        packed.byteswap()
    return [int(value) & 0xFFFFFFFF for value in packed]


def _resample(samples: Any, source_rate: int) -> Any:
    np = _numpy()
    if int(source_rate) == TARGET_SAMPLE_RATE:
        return samples.astype(np.float32, copy=False)
    output_count = max(
        FFT_WINDOW,
        round(samples.size * TARGET_SAMPLE_RATE / max(1, int(source_rate))),
    )
    source_positions = np.linspace(
        0.0,
        1.0,
        num=samples.size,
        endpoint=False,
        dtype=np.float64,
    )
    destination_positions = np.linspace(
        0.0,
        1.0,
        num=output_count,
        endpoint=False,
        dtype=np.float64,
    )
    return np.interp(
        destination_positions,
        source_positions,
        samples,
    ).astype(np.float32)


def _music_focused_samples(samples: Any, sample_rate: int) -> Any:
    """Suppress short voices and game effects while retaining the music bed.

    This is deliberately a lightweight, local alternative to a vocal-removal
    service. It performs a short-time Fourier transform and limits spectral
    energy that is not present in the surrounding half-second. Sustained SPC
    notes survive, while broadband Mario noises and voice clips contribute
    much less to both Chromaprint and landmark matching.
    """
    np = _numpy()
    source = _resample(samples, int(sample_rate)).astype(np.float32, copy=True)
    if source.size < FFT_WINDOW:
        return source
    source -= float(source.mean())
    source_peak = float(np.max(np.abs(source)))
    if not math.isfinite(source_peak) or source_peak <= 1e-7:
        return source
    source /= source_peak

    frame_starts = list(range(0, source.size - FFT_WINDOW + 1, FFT_HOP))
    final_start = max(0, source.size - FFT_WINDOW)
    if not frame_starts or frame_starts[-1] != final_start:
        frame_starts.append(final_start)
    window = np.hanning(FFT_WINDOW).astype(np.float32)
    framed = np.stack(
        [source[start : start + FFT_WINDOW] * window for start in frame_starts]
    )
    spectra = np.fft.rfft(framed, axis=1)
    magnitude = np.abs(spectra).astype(np.float32)

    radius = MUSIC_FOCUS_TEMPORAL_RADIUS
    padded = np.pad(magnitude, ((radius, radius), (0, 0)), mode="edge")
    neighbors = np.stack(
        [
            padded[offset : offset + magnitude.shape[0]]
            for offset in range((radius * 2) + 1)
        ],
        axis=0,
    )
    persistent = np.median(neighbors, axis=0)
    allowed = persistent * MUSIC_FOCUS_TRANSIENT_LIMIT
    epsilon = np.finfo(np.float32).eps
    mask = np.clip(
        allowed / np.maximum(magnitude, epsilon),
        MUSIC_FOCUS_MINIMUM_GAIN,
        1.0,
    )

    # When one frame contains a large amount of non-persistent energy, lower
    # that entire frame slightly as well. This stops the quieter underlying
    # voice/noise bins from replacing the song's peaks merely because a sound
    # effect is very loud.
    transient_excess = np.maximum(0.0, magnitude - allowed)
    transient_share = transient_excess.sum(axis=1) / np.maximum(
        magnitude.sum(axis=1),
        epsilon,
    )
    frame_gain = 1.0 - 0.55 * np.clip(
        (transient_share - 0.08) / 0.42,
        0.0,
        1.0,
    )
    filtered_spectra = spectra * mask * frame_gain[:, None]

    focused = np.zeros(source.size, dtype=np.float32)
    normalization = np.zeros(source.size, dtype=np.float32)
    window_power = window * window
    for frame_index, start in enumerate(frame_starts):
        reconstructed = np.fft.irfft(
            filtered_spectra[frame_index],
            n=FFT_WINDOW,
        ).astype(np.float32)
        focused[start : start + FFT_WINDOW] += reconstructed * window
        normalization[start : start + FFT_WINDOW] += window_power
    usable = normalization > 1e-6
    focused[usable] /= normalization[usable]
    focused[~usable] = source[~usable]
    focused -= float(focused.mean())
    focused_peak = float(np.max(np.abs(focused)))
    focused_rms = float(np.sqrt(np.mean(focused * focused)))
    source_rms = float(np.sqrt(np.mean(source * source)))
    if (
        not math.isfinite(focused_peak)
        or focused_peak <= 1e-7
        or focused_rms < source_rms * 0.06
    ):
        return source
    focused /= focused_peak
    return focused.astype(np.float32, copy=False)


def _write_pcm16_mono_wav(path: Path, samples: Any, sample_rate: int) -> None:
    """Write normalized floating-point samples for the local fpcalc process."""
    np = _numpy()
    normalized = np.asarray(samples, dtype=np.float32)
    peak = float(np.max(np.abs(normalized))) if normalized.size else 0.0
    if not math.isfinite(peak) or peak <= 1e-7:
        raise MusicIndexError("The selected source did not contain usable music.")
    pcm = np.round(
        np.clip(normalized / peak, -1.0, 1.0) * 32767.0
    ).astype("<i2")
    with wave.open(str(path), "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(max(1, int(sample_rate)))
        audio_file.writeframes(pcm.tobytes())


def chromaprint_fingerprint_samples(
    samples: Any,
    sample_rate: int,
    executable: Path | None = None,
) -> list[int]:
    """Fingerprint an in-memory, music-focused query without retaining audio."""
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="smwc-music-focused-",
        suffix=".wav",
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        _write_pcm16_mono_wav(temporary_path, samples, sample_rate)
        return chromaprint_fingerprint_wav(temporary_path, executable)
    finally:
        temporary_path.unlink(missing_ok=True)


def learning_fingerprint_wav(path: Path) -> list[int]:
    """Return the cleaned, non-reconstructive fingerprint used for learning."""
    variants, sample_rate = _pcm16_channel_variants(Path(path))
    if not variants:
        return []
    focused = _music_focused_samples(variants[0][1], sample_rate)
    return chromaprint_fingerprint_samples(focused, TARGET_SAMPLE_RATE)


def _music_spectral_flatness(samples: Any, sample_rate: int) -> float:
    """Return median spectral flatness; broadband noise approaches one."""
    np = _numpy()
    resampled = _resample(samples, int(sample_rate))
    if resampled.size < FFT_WINDOW:
        return 1.0
    window = np.hanning(FFT_WINDOW).astype(np.float32)
    minimum_bin = max(1, round(80 * FFT_WINDOW / TARGET_SAMPLE_RATE))
    maximum_bin = min(
        FFT_WINDOW // 2,
        round(5000 * FFT_WINDOW / TARGET_SAMPLE_RATE),
    )
    measurements: list[float] = []
    for start in range(0, resampled.size - FFT_WINDOW + 1, FFT_WINDOW // 2):
        spectrum = np.abs(
            np.fft.rfft(resampled[start : start + FFT_WINDOW] * window)
        )[minimum_bin:maximum_bin]
        power = (spectrum * spectrum) + 1e-12
        measurements.append(
            float(np.exp(np.mean(np.log(power))) / np.mean(power))
        )
    return float(np.median(measurements)) if measurements else 1.0


def _music_window_quality(samples: Any, sample_rate: int) -> dict[str, float]:
    """Score one window for steady music rather than speech, SFX, or silence."""

    np = _numpy()
    source = _resample(samples, int(sample_rate)).astype(np.float32, copy=False)
    if source.size < FFT_WINDOW:
        return {
            "score": 0.0,
            "rms": 0.0,
            "flatness": 1.0,
            "transient_density": 1.0,
            "silence_share": 1.0,
            "clipping_share": 0.0,
            "speech_penalty": 1.0,
        }
    rms = float(np.sqrt(np.mean(source * source)))
    clipping_share = float(np.mean(np.abs(source) >= 0.985))
    frame_length = min(FFT_WINDOW, max(512, round(TARGET_SAMPLE_RATE * 0.12)))
    frame_hop = max(256, frame_length // 2)
    frame_rms_values = np.asarray(
        [
            float(np.sqrt(np.mean(source[start : start + frame_length] ** 2)))
            for start in range(0, source.size - frame_length + 1, frame_hop)
        ],
        dtype=np.float32,
    )
    if frame_rms_values.size < 2:
        transient_density = 1.0
        silence_share = 1.0
    else:
        log_levels = np.log10(np.maximum(frame_rms_values, 1e-6))
        level_jumps = np.abs(np.diff(log_levels))
        transient_density = float(np.mean(level_jumps > 0.34))
        median_level = float(np.median(frame_rms_values))
        silence_floor = max(0.0025, median_level * 0.18)
        silence_share = float(np.mean(frame_rms_values < silence_floor))

    flatness = _music_spectral_flatness(source, TARGET_SAMPLE_RATE)
    window = np.hanning(min(source.size, FFT_WINDOW * 4)).astype(np.float32)
    spectrum_source = source[: window.size] * window
    spectrum = np.abs(np.fft.rfft(spectrum_source)) ** 2
    frequencies = np.fft.rfftfreq(window.size, 1.0 / TARGET_SAMPLE_RATE)
    audible_energy = float(spectrum[(frequencies >= 80) & (frequencies <= 5200)].sum())
    speech_energy = float(spectrum[(frequencies >= 250) & (frequencies <= 3400)].sum())
    speech_share = speech_energy / max(1e-12, audible_energy)
    # Do not treat midrange-heavy SPC music as speech merely because it lacks
    # bass. The penalty applies only when that concentration is paired with a
    # comparatively noise-like spectrum or abrupt level changes.
    speech_penalty = max(0.0, min(1.0, (speech_share - 0.90) / 0.10))
    speech_penalty *= max(
        min(1.0, flatness / 0.16),
        min(1.0, transient_density / 0.20),
    )

    audible_level = max(0.0, min(1.0, (rms - 0.004) / 0.10))
    tonality = max(0.0, min(1.0, (0.50 - flatness) / 0.46))
    continuity = max(0.0, min(1.0, 1.0 - transient_density / 0.45))
    score = (
        0.42 * tonality
        + 0.28 * continuity
        + 0.20 * audible_level
        + 0.10 * (1.0 - silence_share)
        - 0.24 * speech_penalty
        - 0.35 * min(1.0, clipping_share / 0.08)
    )
    if rms < 0.003 or flatness > 0.58 or silence_share > 0.62:
        score *= 0.12
    return {
        "score": round(max(0.0, min(1.0, score)), 6),
        "rms": round(rms, 6),
        "flatness": round(float(flatness), 6),
        "transient_density": round(transient_density, 6),
        "silence_share": round(silence_share, 6),
        "clipping_share": round(clipping_share, 6),
        "speech_penalty": round(speech_penalty, 6),
    }


def _music_heavy_ranges(
    samples: Any,
    sample_rate: int,
    *,
    maximum_windows: int = MUSIC_QUALITY_MAXIMUM_WINDOWS,
) -> list[dict[str, float]]:
    """Choose separated, high-quality windows from a mixed live recording."""

    np = _numpy()
    source = np.asarray(samples, dtype=np.float32)
    rate = max(1, int(sample_rate))
    if source.size < max(FFT_WINDOW, rate * 3):
        return []
    window_size = min(
        source.size,
        max(FFT_WINDOW, round(MUSIC_QUALITY_WINDOW_SECONDS * rate)),
    )
    hop_size = max(FFT_HOP, round(MUSIC_QUALITY_HOP_SECONDS * rate))
    starts = list(range(0, max(1, source.size - window_size + 1), hop_size))
    final_start = max(0, source.size - window_size)
    if not starts or starts[-1] != final_start:
        starts.append(final_start)
    candidates: list[dict[str, float]] = []
    for start in starts:
        stop = min(source.size, start + window_size)
        features = _music_window_quality(source[start:stop], rate)
        candidates.append(
            {
                **features,
                "start_sample": float(start),
                "stop_sample": float(stop),
                "start_ratio": start / max(1, source.size),
                "stop_ratio": stop / max(1, source.size),
            }
        )
    selected: list[dict[str, float]] = []
    minimum_center_separation = window_size * 0.64
    for candidate in sorted(
        candidates,
        key=lambda item: (
            float(item.get("score", 0.0)),
            -float(item.get("speech_penalty", 0.0)),
        ),
        reverse=True,
    ):
        if float(candidate.get("score", 0.0)) < 0.20:
            continue
        center = (
            float(candidate["start_sample"])
            + float(candidate["stop_sample"])
        ) / 2.0
        if any(
            abs(
                center
                - (
                    float(existing["start_sample"])
                    + float(existing["stop_sample"])
                )
                / 2.0
            )
            < minimum_center_separation
            for existing in selected
        ):
            continue
        selected.append(candidate)
        if len(selected) >= max(1, int(maximum_windows)):
            break
    selected.sort(key=lambda item: float(item["start_sample"]))
    return selected


def _spectral_peaks(samples: Any) -> list[tuple[int, ...]]:
    np = _numpy()
    if samples.size < FFT_WINDOW:
        return []
    window = np.hanning(FFT_WINDOW).astype(np.float32)
    minimum_bin = max(1, round(80 * FFT_WINDOW / TARGET_SAMPLE_RATE))
    maximum_bin = min(
        FFT_WINDOW // 2,
        round(5000 * FFT_WINDOW / TARGET_SAMPLE_RATE),
    )
    frame_peaks: list[tuple[int, ...]] = []
    for start in range(0, samples.size - FFT_WINDOW + 1, FFT_HOP):
        frame = samples[start : start + FFT_WINDOW] * window
        magnitude = np.abs(np.fft.rfft(frame))[minimum_bin:maximum_bin]
        if magnitude.size < 3:
            frame_peaks.append(())
            continue
        log_magnitude = np.log1p(magnitude)
        local_peak_indexes = np.flatnonzero(
            (log_magnitude[1:-1] > log_magnitude[:-2])
            & (log_magnitude[1:-1] >= log_magnitude[2:])
        ) + 1
        if local_peak_indexes.size == 0:
            frame_peaks.append(())
            continue
        floor = float(np.percentile(log_magnitude, 72.0))
        local_peak_indexes = local_peak_indexes[
            log_magnitude[local_peak_indexes] >= floor
        ]
        if local_peak_indexes.size == 0:
            frame_peaks.append(())
            continue
        ordered = local_peak_indexes[
            np.argsort(log_magnitude[local_peak_indexes])[::-1]
        ]
        selected: list[int] = []
        for relative_bin in ordered:
            absolute_bin = int(relative_bin) + minimum_bin
            if all(abs(absolute_bin - existing) >= 4 for existing in selected):
                selected.append(absolute_bin)
                if len(selected) >= PEAKS_PER_FRAME:
                    break
        frame_peaks.append(tuple(sorted(selected)))
    return frame_peaks


def _landmark_hash(first_frequency: int, second_frequency: int, delta: int) -> int:
    packed = (
        int(first_frequency // 2).to_bytes(2, "little", signed=False)
        + int(second_frequency // 2).to_bytes(2, "little", signed=False)
        + int(max(0, delta) // 2).to_bytes(2, "little", signed=False)
    )
    return zlib.crc32(packed) & 0x7FFFFFFF


def fingerprint_samples(samples: Any, sample_rate: int) -> list[tuple[int, int]]:
    """Return deterministic ``(landmark_hash, anchor_frame)`` pairs."""
    resampled = _resample(samples, int(sample_rate))
    peaks = _spectral_peaks(resampled)
    fingerprints: list[tuple[int, int]] = []
    for anchor_frame, anchor_peaks in enumerate(peaks):
        if not anchor_peaks:
            continue
        for target_delta in PAIR_TARGET_FRAME_OFFSETS:
            target_frame = anchor_frame + target_delta
            if target_frame >= len(peaks):
                continue
            target_peaks = peaks[target_frame]
            if not target_peaks:
                continue
            for first_frequency in anchor_peaks[:2]:
                for second_frequency in target_peaks[:2]:
                    landmark = _landmark_hash(
                        first_frequency,
                        second_frequency,
                        target_delta,
                    )
                    if landmark % HASH_RETENTION_MODULUS == 0:
                        fingerprints.append((landmark, anchor_frame))
    return fingerprints


def fingerprint_query_samples(samples: Any, sample_rate: int) -> list[tuple[int, int]]:
    """Return capture-tolerant landmarks for searching an existing index.

    Reference SPC renders are clean and deterministic, while a live HDMI,
    mixer, or speaker-loopback recording is not.  Resampling, capture-clock
    drift, equalizers, and game sound effects can move a spectral peak by a
    few FFT bins or one neighboring frame.  The index intentionally stores
    only the exact compact reference hashes; a query can cheaply search a
    small neighborhood around each observed peak without enlarging the
    shipped database or weakening its offset-consistency check.
    """
    resampled = _resample(samples, int(sample_rate))
    peaks = _spectral_peaks(resampled)
    fingerprints: list[tuple[int, int]] = []
    for anchor_frame, anchor_peaks in enumerate(peaks):
        if not anchor_peaks:
            continue
        frame_landmarks: set[int] = set()
        for target_delta in PAIR_TARGET_FRAME_OFFSETS:
            for frame_adjustment in QUERY_TIME_FRAME_OFFSETS:
                target_frame = anchor_frame + target_delta + frame_adjustment
                if target_frame < 0 or target_frame >= len(peaks):
                    continue
                target_peaks = peaks[target_frame]
                if not target_peaks:
                    continue
                # The clean reference keeps its two strongest peaks.  Search
                # all four capture peaks so an overlaid sound effect cannot
                # push the underlying song just outside the query.
                for first_frequency in anchor_peaks[:PEAKS_PER_FRAME]:
                    for second_frequency in target_peaks[:PEAKS_PER_FRAME]:
                        for first_adjustment in QUERY_FREQUENCY_BIN_OFFSETS:
                            adjusted_first = first_frequency + first_adjustment
                            if adjusted_first <= 0:
                                continue
                            for second_adjustment in QUERY_FREQUENCY_BIN_OFFSETS:
                                adjusted_second = second_frequency + second_adjustment
                                if adjusted_second <= 0:
                                    continue
                                landmark = _landmark_hash(
                                    adjusted_first,
                                    adjusted_second,
                                    target_delta,
                                )
                                if landmark % HASH_RETENTION_MODULUS == 0:
                                    frame_landmarks.add(landmark)
        fingerprints.extend(
            (landmark, anchor_frame)
            for landmark in sorted(frame_landmarks)
        )
    return fingerprints


def fingerprint_wav(path: Path) -> list[tuple[int, int]]:
    samples, sample_rate = _pcm16_mono(Path(path))
    return fingerprint_samples(samples, sample_rate)


def stable_track_key(submission_id: object, spc_filename: object) -> str:
    normalized_filename = "/".join(
        part for part in str(spc_filename or "").replace("\\", "/").split("/") if part
    ).casefold()
    return hashlib.sha256(
        (str(submission_id).strip() + "\n" + normalized_filename).encode("utf-8")
    ).hexdigest()


def add_track_fingerprints(
    index_path: Path,
    metadata: dict[str, Any],
    fingerprints: Sequence[tuple[int, int]],
    chromaprint_values: Sequence[int] | None = None,
) -> int:
    """Atomically replace one SPC's metadata and landmarks."""
    if not fingerprints and not chromaprint_values:
        raise MusicIndexError("The reference SPC did not produce fingerprints.")
    track_key = str(metadata.get("track_key", "")).strip() or stable_track_key(
        metadata.get("submission_id", ""),
        metadata.get("spc_filename", ""),
    )
    with closing(_connect(index_path)) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        existing = connection.execute(
            "SELECT id FROM tracks WHERE track_key = ?",
            (track_key,),
        ).fetchone()
        if existing is None:
            cursor = connection.execute(
                """
                INSERT INTO tracks(
                    track_key, submission_id, submission_updated_at,
                    spc_filename, title, author, submission_url,
                    download_url, duration_seconds, fingerprint_count
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    track_key,
                    str(metadata.get("submission_id", "")),
                    str(metadata.get("submission_updated_at", "")),
                    str(metadata.get("spc_filename", "")),
                    str(metadata.get("title", "Unknown SMW Central music")),
                    str(metadata.get("author", "")),
                    str(metadata.get("submission_url", "")),
                    str(metadata.get("download_url", "")),
                    float(metadata.get("duration_seconds", 0) or 0),
                    len(fingerprints),
                ),
            )
            track_id = int(cursor.lastrowid)
        else:
            track_id = int(existing["id"])
            connection.execute(
                "DELETE FROM fingerprints WHERE track_id = ?",
                (track_id,),
            )
            connection.execute(
                """
                UPDATE tracks SET
                    submission_updated_at = ?, spc_filename = ?, title = ?,
                    author = ?, submission_url = ?, download_url = ?,
                    duration_seconds = ?, fingerprint_count = ?
                WHERE id = ?
                """,
                (
                    str(metadata.get("submission_updated_at", "")),
                    str(metadata.get("spc_filename", "")),
                    str(metadata.get("title", "Unknown SMW Central music")),
                    str(metadata.get("author", "")),
                    str(metadata.get("submission_url", "")),
                    str(metadata.get("download_url", "")),
                    float(metadata.get("duration_seconds", 0) or 0),
                    len(fingerprints),
                    track_id,
                ),
            )
        connection.executemany(
            "INSERT INTO fingerprints(hash, track_id, frame) VALUES(?, ?, ?)",
            (
                (int(landmark), track_id, int(frame))
                for landmark, frame in fingerprints
            ),
        )
        connection.execute(
            "DELETE FROM chromaprint_tokens WHERE track_id = ?",
            (track_id,),
        )
        connection.execute(
            "DELETE FROM chromaprint_data WHERE track_id = ?",
            (track_id,),
        )
        if chromaprint_values:
            normalized_values = [
                int(value) & 0xFFFFFFFF for value in chromaprint_values
            ]
            if len(normalized_values) < CHROMAPRINT_MINIMUM_VALUES:
                raise MusicIndexError(
                    "The reference SPC did not produce enough Chromaprint data."
                )
            connection.execute(
                "INSERT INTO chromaprint_data(track_id, value_count, fingerprint) "
                "VALUES(?, ?, ?)",
                (
                    track_id,
                    len(normalized_values),
                    sqlite3.Binary(_encode_chromaprint_values(normalized_values)),
                ),
            )
            connection.executemany(
                "INSERT INTO chromaprint_tokens(token, track_id, frame) "
                "VALUES(?, ?, ?)",
                (
                    (
                        int(value) >> CHROMAPRINT_TOKEN_SHIFT,
                        track_id,
                        frame,
                    )
                    for frame, value in enumerate(normalized_values)
                    if frame % CHROMAPRINT_TOKEN_STRIDE == 0
                ),
            )
        connection.commit()
    return track_id


def indexed_submission_versions(path: Path) -> dict[str, str]:
    """Return the newest catalog timestamp stored for every submission."""
    if not Path(path).is_file():
        return {}
    with closing(_connect(path, read_only=True)) as connection:
        rows = connection.execute(
            """
            SELECT submission_id, MAX(submission_updated_at) AS updated_at
            FROM tracks GROUP BY submission_id
            """
        ).fetchall()
    return {
        str(row["submission_id"]): str(row["updated_at"] or "")
        for row in rows
    }


def _copy_index_track(
    source: sqlite3.Connection,
    destination: sqlite3.Connection,
    track: sqlite3.Row,
    *,
    preserve_id: bool,
) -> int:
    """Copy one track and its fingerprint rows between compatible indexes."""
    columns = (
        "track_key",
        "submission_id",
        "submission_updated_at",
        "spc_filename",
        "title",
        "author",
        "submission_url",
        "download_url",
        "duration_seconds",
        "fingerprint_count",
    )
    values = tuple(track[column] for column in columns)
    if preserve_id:
        destination.execute(
            "INSERT INTO tracks(id, " + ", ".join(columns) + ") VALUES("
            + ", ".join("?" for _unused in range(len(columns) + 1))
            + ")",
            (int(track["id"]), *values),
        )
        destination_track_id = int(track["id"])
    else:
        cursor = destination.execute(
            "INSERT INTO tracks(" + ", ".join(columns) + ") VALUES("
            + ", ".join("?" for _unused in columns)
            + ")",
            values,
        )
        destination_track_id = int(cursor.lastrowid)
    source_track_id = int(track["id"])
    destination.executemany(
        "INSERT INTO fingerprints(hash, track_id, frame) VALUES(?, ?, ?)",
        (
            (int(row["hash"]), destination_track_id, int(row["frame"]))
            for row in source.execute(
                "SELECT hash, frame FROM fingerprints WHERE track_id = ?",
                (source_track_id,),
            )
        ),
    )
    chromaprint = source.execute(
        "SELECT value_count, fingerprint FROM chromaprint_data "
        "WHERE track_id = ?",
        (source_track_id,),
    ).fetchone()
    if chromaprint is not None:
        destination.execute(
            "INSERT INTO chromaprint_data(track_id, value_count, fingerprint) "
            "VALUES(?, ?, ?)",
            (
                destination_track_id,
                int(chromaprint["value_count"]),
                sqlite3.Binary(bytes(chromaprint["fingerprint"])),
            ),
        )
    destination.executemany(
        "INSERT INTO chromaprint_tokens(token, track_id, frame) "
        "VALUES(?, ?, ?)",
        (
            (int(row["token"]), destination_track_id, int(row["frame"]))
            for row in source.execute(
                "SELECT token, frame FROM chromaprint_tokens WHERE track_id = ?",
                (source_track_id,),
            )
        ),
    )
    return destination_track_id


def validate_incremental_music_update(path: Path) -> dict[str, Any]:
    """Validate a partial index containing only new and changed submissions."""
    details = validate_music_index(path)
    if details.get("catalog_complete") != "0":
        raise MusicIndexError(
            "The incremental music update is marked as a complete catalog."
        )
    base_version = str(details.get("incremental_base_version", "")).strip()
    target_version = str(details.get("incremental_target_version", "")).strip()
    if not base_version or not target_version:
        raise MusicIndexError(
            "The incremental music update is missing version information."
        )
    if str(details.get("index_version", "")) != target_version:
        raise MusicIndexError(
            "The incremental music update has inconsistent version information."
        )
    try:
        deleted_ids = json.loads(
            str(details.get("incremental_deleted_submissions", "[]"))
        )
    except (TypeError, ValueError) as error:
        raise MusicIndexError(
            "The incremental music update has invalid deletion information."
        ) from error
    if not isinstance(deleted_ids, list) or any(
        not str(value).strip() for value in deleted_ids
    ):
        raise MusicIndexError(
            "The incremental music update has invalid deletion information."
        )
    changed_ids = indexed_submission_versions(path)
    if not changed_ids and not deleted_ids:
        raise MusicIndexError("The incremental music update contains no changes.")
    return {
        **details,
        "base_index_version": base_version,
        "index_version": target_version,
        "changed_submission_ids": tuple(sorted(changed_ids)),
        "deleted_submission_ids": tuple(
            sorted({str(value) for value in deleted_ids})
        ),
    }


def create_incremental_music_update(
    base_index_path: Path,
    current_index_path: Path,
    update_path: Path,
) -> dict[str, Any]:
    """Build a cumulative patch containing changes since the bundled index."""
    base = validate_music_index(
        base_index_path,
        require_tracks=True,
        require_complete=True,
    )
    current = validate_music_index(
        current_index_path,
        require_tracks=True,
        require_complete=True,
    )
    base_version = str(base.get("index_version", ""))
    target_version = str(current.get("index_version", ""))
    if _version_key(target_version) < _version_key(base_version):
        raise MusicIndexError(
            "The current music index is older than the bundled base index."
        )
    base_submissions = indexed_submission_versions(base_index_path)
    current_submissions = indexed_submission_versions(current_index_path)
    changed_ids = sorted(
        submission_id
        for submission_id, updated_at in current_submissions.items()
        if base_submissions.get(submission_id) != updated_at
    )
    deleted_ids = sorted(set(base_submissions) - set(current_submissions))
    if not changed_ids and not deleted_ids:
        raise MusicIndexError("There are no new or changed songs to publish.")

    destination = Path(update_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        destination.name + f".{os.getpid()}.{threading.get_ident()}.tmp"
    )
    temporary.unlink(missing_ok=True)
    try:
        initialize_music_index(
            temporary,
            index_version=target_version,
            catalog_updated_at=str(current.get("catalog_updated_at", "")),
            catalog_complete=False,
        )
        update_music_index_metadata(
            temporary,
            {
                "incremental_base_version": base_version,
                "incremental_target_version": target_version,
                "incremental_deleted_submissions": json.dumps(
                    deleted_ids,
                    ensure_ascii=True,
                    separators=(",", ":"),
                ),
            },
        )
        with closing(_connect(current_index_path, read_only=True)) as source, closing(
            _connect(temporary)
        ) as output:
            output.execute("PRAGMA foreign_keys=ON")
            for submission_id in changed_ids:
                tracks = source.execute(
                    "SELECT * FROM tracks WHERE submission_id = ? ORDER BY id",
                    (submission_id,),
                ).fetchall()
                for track in tracks:
                    _copy_index_track(
                        source,
                        output,
                        track,
                        preserve_id=True,
                    )
            output.commit()
            output.execute("PRAGMA optimize")
        details = validate_incremental_music_update(temporary)
        os.replace(temporary, destination)
        return {
            **details,
            "submission_count": len(changed_ids),
            "deleted_submission_count": len(deleted_ids),
            "size_bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
        }
    finally:
        temporary.unlink(missing_ok=True)


def apply_incremental_music_update(
    installed_path: Path,
    update_path: Path,
) -> dict[str, Any]:
    """Safely merge a cumulative new/changed-song patch into the local index."""
    installed = validate_music_index(
        installed_path,
        require_tracks=True,
        require_complete=True,
    )
    update = validate_incremental_music_update(update_path)
    installed_version = str(installed.get("index_version", ""))
    if _version_key(installed_version) >= _version_key(update["index_version"]):
        return installed
    if _version_key(installed_version) < _version_key(
        update["base_index_version"]
    ):
        raise MusicIndexError(
            "This music update needs the catalog bundled with a newer app version."
        )

    destination = Path(installed_path)
    temporary = destination.with_name(
        destination.name + f".{os.getpid()}.{threading.get_ident()}.merge"
    )
    temporary.unlink(missing_ok=True)
    try:
        with MUSIC_INDEX_LOCK:
            _atomic_index_copy(destination, temporary)
            with closing(_connect(update_path, read_only=True)) as source, closing(
                _connect(temporary)
            ) as output:
                output.execute("PRAGMA foreign_keys=ON")
                replaced_ids = tuple(update["changed_submission_ids"])
                removed_ids = tuple(update["deleted_submission_ids"])
                for submission_id in (*replaced_ids, *removed_ids):
                    output.execute(
                        "DELETE FROM tracks WHERE submission_id = ?",
                        (submission_id,),
                    )
                for submission_id in replaced_ids:
                    tracks = source.execute(
                        "SELECT * FROM tracks WHERE submission_id = ? ORDER BY id",
                        (submission_id,),
                    ).fetchall()
                    for track in tracks:
                        _copy_index_track(
                            source,
                            output,
                            track,
                            preserve_id=False,
                        )
                output.executemany(
                    "INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)",
                    (
                        ("schema_version", str(INDEX_SCHEMA_VERSION)),
                        ("fingerprint_algorithm", FINGERPRINT_ALGORITHM),
                        ("chromaprint_version", CHROMAPRINT_VERSION),
                        ("index_version", str(update["index_version"])),
                        (
                            "catalog_updated_at",
                            str(update.get("catalog_updated_at", "")),
                        ),
                        ("catalog_complete", "1"),
                    ),
                )
                output.commit()
                output.execute("PRAGMA optimize")
            merged = validate_music_index(
                temporary,
                require_tracks=True,
                require_complete=True,
            )
            if str(merged.get("index_version", "")) != str(
                update["index_version"]
            ):
                raise MusicIndexError(
                    "The incremental music update did not finish correctly."
                )
            os.replace(temporary, destination)
        return validate_music_index(
            destination,
            require_tracks=True,
            require_complete=True,
        )
    finally:
        temporary.unlink(missing_ok=True)


def remove_submission_tracks(path: Path, submission_id: object) -> int:
    """Remove every SPC variant belonging to one changed catalog entry."""
    with closing(_connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        row = connection.execute(
            "SELECT COUNT(*) FROM tracks WHERE submission_id = ?",
            (str(submission_id),),
        ).fetchone()
        deleted = int(row[0]) if row is not None else 0
        connection.execute(
            "DELETE FROM tracks WHERE submission_id = ?",
            (str(submission_id),),
        )
        connection.commit()
    return deleted


def _chunks(values: Sequence[int], size: int) -> Iterable[Sequence[int]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _chromaprint_aligned_distance(
    query: Sequence[int],
    reference: Sequence[int],
    offset: int,
) -> tuple[float, int] | None:
    """Return a trimmed Hamming distance for one time alignment."""
    query_start = max(0, -int(offset))
    reference_start = max(0, int(offset))
    overlap = min(
        len(query) - query_start,
        len(reference) - reference_start,
    )
    minimum_overlap = max(
        CHROMAPRINT_MINIMUM_VALUES,
        math.ceil(len(query) * 0.68),
    )
    if overlap < minimum_overlap:
        return None
    distances = sorted(
        (
            int(query[query_start + position]
                ^ reference[reference_start + position]).bit_count()
            for position in range(overlap)
        )
    )
    # A jump, voice, or sound effect can briefly cover the music.  Ignore the
    # noisiest 15% of frames while still requiring most of the recording to
    # agree with one continuous reference position.
    keep_count = max(minimum_overlap, round(overlap * 0.85))
    kept = distances[:keep_count]
    return sum(kept) / (32.0 * len(kept)), overlap


def initialize_learned_music_model(path: Path) -> None:
    """Create the private, append-only model of user-confirmed captures."""
    with closing(_connect(Path(path))) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS model_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS confirmed_samples (
                id INTEGER PRIMARY KEY,
                track_key TEXT NOT NULL,
                submission_id TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL DEFAULT '',
                artist TEXT NOT NULL DEFAULT '',
                source_token TEXT NOT NULL DEFAULT '',
                value_count INTEGER NOT NULL,
                fingerprint BLOB NOT NULL,
                fingerprint_sha256 TEXT NOT NULL,
                created_at REAL NOT NULL,
                UNIQUE(track_key, source_token, fingerprint_sha256)
            );
            CREATE INDEX IF NOT EXISTS confirmed_samples_track_idx
                ON confirmed_samples(track_key);
            CREATE INDEX IF NOT EXISTS confirmed_samples_source_idx
                ON confirmed_samples(source_token);
            """
        )
        connection.execute(
            "INSERT OR REPLACE INTO model_metadata(key, value) VALUES(?, ?)",
            ("schema_version", str(LEARNED_MODEL_SCHEMA_VERSION)),
        )
        connection.commit()


def learned_music_model_stats(path: Path) -> dict[str, int]:
    """Return small counts suitable for showing in the Music Identifier UI."""
    model_path = Path(path)
    if not model_path.is_file():
        return {"sample_count": 0, "track_count": 0}
    try:
        with closing(_connect(model_path, read_only=True)) as connection:
            row = connection.execute(
                "SELECT COUNT(*), COUNT(DISTINCT track_key) FROM confirmed_samples"
            ).fetchone()
    except sqlite3.Error:
        return {"sample_count": 0, "track_count": 0}
    return {
        "sample_count": int(row[0]) if row is not None else 0,
        "track_count": int(row[1]) if row is not None else 0,
    }


def _community_api_url(endpoint: object, route: str) -> str:
    base = str(endpoint or "").strip().rstrip("/")
    parsed = urlparse(base)
    if (
        parsed.scheme.casefold() != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise MusicIndexError("The Community Song Results service address is invalid.")
    return base + "/" + str(route).lstrip("/")


def _community_api_json(
    endpoint: object,
    route: str,
    *,
    payload: dict[str, Any] | None = None,
    response_limit: int = COMMUNITY_API_RESPONSE_LIMIT,
    timeout: float = 18.0,
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": "SMW-Stream-Tracker-Community-Learning/1",
    }
    if payload is not None:
        data = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        _community_api_url(endpoint, route),
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(request, timeout=max(1.0, float(timeout))) as response:
            document = json.loads(
                _read_limited_response(response, int(response_limit)).decode("utf-8")
            )
    except HTTPError as error:
        message = ""
        try:
            response_document = json.loads(error.read(64 * 1024).decode("utf-8"))
            message = str(response_document.get("error", "")).strip()
        except (AttributeError, TypeError, ValueError, UnicodeDecodeError):
            message = ""
        raise MusicIndexError(
            message or f"The Community Song Results service returned error {error.code}."
        ) from error
    except (OSError, URLError, TimeoutError, UnicodeDecodeError, ValueError) as error:
        raise MusicIndexError(
            "The online SMW Central music service could not be reached. "
            "An Internet connection is required for music identification."
        ) from error
    if not isinstance(document, dict):
        raise MusicIndexError("The Community Song Results service returned invalid data.")
    return document


def fetch_cloud_music_catalog_status(endpoint: object) -> dict[str, Any]:
    """Return validated public metadata for the online SMW Central catalog."""

    response = _community_api_json(
        endpoint,
        "v1/music/catalog",
        response_limit=64 * 1024,
        timeout=5.0,
    )
    if response.get("ok") is not True:
        raise MusicIndexError(
            str(response.get("error", "The online music catalog is unavailable."))
        )
    if str(response.get("catalog", "")).strip().casefold() != "smwcentral":
        raise MusicIndexError("The online music service returned the wrong catalog.")
    try:
        track_count = int(response.get("track_count", 0) or 0)
    except (TypeError, ValueError) as error:
        raise MusicIndexError(
            "The online music catalog returned invalid status information."
        ) from error
    if track_count <= 0:
        raise MusicIndexError("The online SMW Central music catalog is empty.")
    return {
        "catalog": "smwcentral",
        "catalog_complete": "1",
        "cloud_only": True,
        "fingerprints_only": bool(response.get("fingerprints_only", True)),
        "raw_audio_collected": bool(response.get("raw_audio_collected", False)),
        "index_version": str(response.get("index_version", "")).strip(),
        "catalog_updated_at": str(
            response.get("catalog_updated_at", "")
        ).strip(),
        "cloud_updated_at": str(
            response.get("cloud_updated_at", "")
        ).strip(),
        "track_count": track_count,
    }


def match_cloud_chromaprint_values(
    endpoint: object,
    query_values: Sequence[int],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Query the shared SMW Central inverted fingerprint catalog.

    This is the same privacy boundary used by large-scale audio recognition:
    the client extracts a one-way acoustic signature and the server performs
    landmark candidate lookup plus strict time-alignment verification. Raw
    audio and the selected Windows application name are never included.
    """

    values = [int(value) & 0xFFFFFFFF for value in query_values]
    if len(values) < CHROMAPRINT_MINIMUM_VALUES:
        return []
    if len(values) > 4096:
        values = values[:4096]
    response = _community_api_json(
        endpoint,
        "v1/music/match",
        payload={
            "schema_version": 1,
            "catalog": "smwcentral",
            "fingerprint_values": values,
            "limit": max(1, min(5, int(limit))),
        },
        response_limit=MUSIC_MATCH_API_RESPONSE_LIMIT,
        timeout=5.0,
    )
    if response.get("ok") is not True:
        raise MusicIndexError(
            str(response.get("error", "The cloud music match was rejected."))
        )
    raw_matches = response.get("matches", [])
    if not isinstance(raw_matches, list):
        raise MusicIndexError("The cloud music service returned invalid data.")
    matches: list[dict[str, Any]] = []
    for raw_match in raw_matches[: max(1, min(5, int(limit)))]:
        if not isinstance(raw_match, dict):
            continue
        submission_id = str(raw_match.get("submission_id", "")).strip()
        title = " ".join(str(raw_match.get("title", "")).split())
        if not submission_id or not title:
            continue
        normalized = {
            "track_id": int(raw_match.get("track_id", 0) or 0),
            "track_key": str(raw_match.get("track_key", "")).strip(),
            "submission_id": submission_id,
            "spc_filename": str(raw_match.get("spc_filename", "")),
            "title": title,
            "artist": " ".join(str(raw_match.get("artist", "")).split()),
            "submission_url": str(raw_match.get("submission_url", "")).strip(),
            "download_url": str(raw_match.get("download_url", "")).strip(),
            "confidence": round(
                max(0.0, min(100.0, float(raw_match.get("confidence", 0.0) or 0.0))),
                1,
            ),
            "audio_distance": round(
                max(0.0, float(raw_match.get("audio_distance", 1.0))),
                4,
            ),
            "matching_frames": max(
                0, int(raw_match.get("matching_frames", 0) or 0)
            ),
            "offset_seconds": round(
                float(raw_match.get("offset_seconds", 0.0) or 0.0), 2
            ),
            "match_strategy": "Cloud landmark fingerprints with time alignment",
        }
        matches.append(normalized)
    return matches


def community_learning_contribution(
    match: dict[str, Any],
    fingerprint_values: Sequence[int],
    *,
    client_id_hash: object,
    catalog_version: object,
    app_version: object,
) -> dict[str, Any]:
    """Build the anonymous, fingerprints-only contribution document."""
    track_key = str(match.get("track_key", "")).strip().casefold()
    submission_id = str(match.get("submission_id", "")).strip()
    anonymous_id = str(client_id_hash or "").strip().casefold()
    if len(track_key) != 64 or any(character not in "0123456789abcdef" for character in track_key):
        raise MusicIndexError("The identified song is missing its catalog key.")
    if not submission_id:
        raise MusicIndexError("The identified song is missing its submission ID.")
    if len(anonymous_id) != 64 or any(
        character not in "0123456789abcdef" for character in anonymous_id
    ):
        raise MusicIndexError("The anonymous Community Song Results identifier is invalid.")
    values = [int(value) & 0xFFFFFFFF for value in fingerprint_values]
    if len(values) < CHROMAPRINT_MINIMUM_VALUES:
        raise MusicIndexError("The recording is too short to contribute.")
    confidence = float(
        match.get("confidence_value", match.get("confidence", 0.0)) or 0.0
    )
    if confidence < 78.0:
        raise MusicIndexError(
            "This match can be learned locally but is not confident enough to share."
        )
    encoded = _encode_chromaprint_values(values)
    return {
        "schema_version": 1,
        "user_confirmed": True,
        "track_key": track_key,
        "submission_id": submission_id,
        "client_id_hash": anonymous_id,
        "fingerprint_sha256": hashlib.sha256(encoded).hexdigest(),
        "fingerprint_base64": base64.b64encode(encoded).decode("ascii"),
        "value_count": len(values),
        "local_confidence": round(confidence, 2),
        "catalog_version": str(catalog_version or "")[:80],
        "app_version": str(app_version or "")[:40],
    }


def submit_community_learning_contribution(
    endpoint: object,
    contribution: dict[str, Any],
) -> dict[str, Any]:
    response = _community_api_json(
        endpoint,
        "v1/contributions",
        payload=dict(contribution),
        response_limit=128 * 1024,
    )
    if response.get("ok") is not True:
        raise MusicIndexError(
            str(response.get("error", "Community Song Results rejected the contribution."))
        )
    return response


def sync_community_learning_model(
    endpoint: object,
    destination: Path,
    *,
    current_revision: int = 0,
) -> dict[str, Any]:
    """Atomically replace the local community model with an approved snapshot."""
    manifest = _community_api_json(
        endpoint,
        "v1/model/manifest",
        response_limit=256 * 1024,
    )
    if int(manifest.get("schema_version", -1)) != 1:
        raise MusicIndexError("The Community Song Results model uses an unsupported format.")
    revision = max(0, int(manifest.get("model_revision", 0) or 0))
    total_examples = max(0, int(manifest.get("total_examples", 0) or 0))
    destination = Path(destination)
    if (
        revision <= max(0, int(current_revision))
        and destination.is_file()
    ):
        return {
            **learned_music_model_stats(destination),
            "model_revision": revision,
            "updated": False,
        }
    if total_examples > COMMUNITY_MODEL_MAXIMUM_EXAMPLES:
        raise MusicIndexError("The Community Song Results model is unexpectedly large.")
    examples: list[dict[str, Any]] = []
    cursor = 0
    seen_cursors: set[int] = set()
    while True:
        page = _community_api_json(
            endpoint,
            f"v1/model?cursor={cursor}&limit=200",
        )
        if int(page.get("schema_version", -1)) != 1:
            raise MusicIndexError("The Community Song Results model page is invalid.")
        page_examples = page.get("examples", [])
        if not isinstance(page_examples, list):
            raise MusicIndexError("The Community Song Results model page is invalid.")
        for example in page_examples:
            if not isinstance(example, dict):
                raise MusicIndexError("The Community Song Results model contains invalid data.")
            examples.append(example)
            if len(examples) > COMMUNITY_MODEL_MAXIMUM_EXAMPLES:
                raise MusicIndexError("The Community Song Results model is unexpectedly large.")
        next_cursor = page.get("next_cursor")
        if next_cursor is None:
            break
        next_cursor = int(next_cursor)
        if next_cursor <= cursor or next_cursor in seen_cursors:
            raise MusicIndexError("The Community Song Results model pagination is invalid.")
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    if len(examples) != total_examples:
        raise MusicIndexError("The Community Song Results model download was incomplete.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        destination.name + f".{os.getpid()}.{threading.get_ident()}.community"
    )
    temporary.unlink(missing_ok=True)
    try:
        initialize_learned_music_model(temporary)
        with closing(_connect(temporary)) as connection:
            for example in examples:
                track_key = str(example.get("track_key", "")).strip().casefold()
                submission_id = str(example.get("submission_id", "")).strip()
                digest = str(example.get("fingerprint_sha256", "")).strip().casefold()
                encoded_text = str(example.get("fingerprint_base64", "")).strip()
                if (
                    len(track_key) != 64
                    or any(character not in "0123456789abcdef" for character in track_key)
                    or not submission_id
                    or len(digest) != 64
                ):
                    raise MusicIndexError("The Community Song Results model contains invalid data.")
                try:
                    encoded = base64.b64decode(encoded_text, validate=True)
                except (binascii.Error, ValueError, TypeError) as error:
                    raise MusicIndexError(
                        "The Community Song Results model contains invalid fingerprints."
                    ) from error
                if hashlib.sha256(encoded).hexdigest() != digest:
                    raise MusicIndexError(
                        "A Community Song Results fingerprint failed its integrity check."
                    )
                values = _decode_chromaprint_values(encoded)
                value_count = int(example.get("value_count", 0) or 0)
                if value_count != len(values) or value_count < CHROMAPRINT_MINIMUM_VALUES:
                    raise MusicIndexError(
                        "A Community Song Results fingerprint has an invalid length."
                    )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO confirmed_samples(
                        track_key, submission_id, title, artist, source_token,
                        value_count, fingerprint, fingerprint_sha256, created_at
                    ) VALUES(?, ?, '', '', 'community', ?, ?, ?, ?)
                    """,
                    (
                        track_key,
                        submission_id,
                        value_count,
                        sqlite3.Binary(encoded),
                        digest,
                        float(int(example.get("id", 0) or 0)),
                    ),
                )
            connection.execute(
                "INSERT OR REPLACE INTO model_metadata(key, value) VALUES(?, ?)",
                ("community_revision", str(revision)),
            )
            connection.commit()
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        **learned_music_model_stats(destination),
        "model_revision": revision,
        "updated": True,
    }


def learn_confirmed_music_match(
    model_path: Path,
    match: dict[str, Any],
    fingerprint_values: Sequence[int],
    *,
    source_token: object = "",
) -> dict[str, int]:
    """Teach the local model from a result the user says is correct.

    The original WAV is never retained.  Only the same compressed,
    non-reconstructive Chromaprint values used by the catalog matcher are
    stored, and old examples are bounded so the model remains tiny.
    """
    track_key = str(match.get("track_key", "")).strip()
    if not track_key:
        raise MusicIndexError("The identified song is missing its catalog key.")
    values = [int(value) & 0xFFFFFFFF for value in fingerprint_values]
    if len(values) < CHROMAPRINT_MINIMUM_VALUES:
        raise MusicIndexError("The recording is too short to teach the matcher.")
    source = str(source_token or "").strip()
    payload = _encode_chromaprint_values(values)
    payload_hash = hashlib.sha256(payload).hexdigest()
    initialize_learned_music_model(Path(model_path))
    with closing(_connect(Path(model_path))) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO confirmed_samples(
                track_key, submission_id, title, artist, source_token,
                value_count, fingerprint, fingerprint_sha256, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                track_key,
                str(match.get("submission_id", "")),
                str(match.get("title", "")),
                str(match.get("artist", "")),
                source,
                len(values),
                sqlite3.Binary(payload),
                payload_hash,
                time.time(),
            ),
        )
        retained = connection.execute(
            """
            SELECT id FROM confirmed_samples
            WHERE track_key = ? AND source_token = ?
            ORDER BY created_at DESC, id DESC
            """,
            (track_key, source),
        ).fetchall()
        stale_ids = [
            int(row["id"])
            for row in retained[LEARNED_MODEL_MAX_SAMPLES_PER_TRACK_SOURCE:]
        ]
        if stale_ids:
            placeholders = ",".join("?" for _unused in stale_ids)
            connection.execute(
                f"DELETE FROM confirmed_samples WHERE id IN ({placeholders})",
                tuple(stale_ids),
            )
        connection.commit()
    return learned_music_model_stats(Path(model_path))


def _best_learned_chromaprint_alignment(
    query: Sequence[int],
    reference: Sequence[int],
) -> tuple[float, int, int] | None:
    query_times: dict[int, list[int]] = defaultdict(list)
    reference_times: dict[int, list[int]] = defaultdict(list)
    for frame, value in enumerate(query):
        query_times[(int(value) & 0xFFFFFFFF) >> CHROMAPRINT_TOKEN_SHIFT].append(frame)
    for frame, value in enumerate(reference):
        reference_times[(int(value) & 0xFFFFFFFF) >> CHROMAPRINT_TOKEN_SHIFT].append(frame)
    offset_votes: Counter[int] = Counter()
    for token in set(query_times).intersection(reference_times):
        for query_frame in query_times[token]:
            for reference_frame in reference_times[token]:
                offset_votes[reference_frame - query_frame] += 1
    if not offset_votes:
        return None
    best: tuple[float, int, int] | None = None
    checked_offsets: set[int] = set()
    for suggested_offset, _votes in offset_votes.most_common(8):
        for adjustment in range(-4, 5):
            offset = int(suggested_offset) + adjustment
            if offset in checked_offsets:
                continue
            checked_offsets.add(offset)
            measured = _chromaprint_aligned_distance(query, reference, offset)
            if measured is None:
                continue
            distance, overlap = measured
            candidate = (distance, -overlap, offset)
            if best is None or candidate < best:
                best = candidate
    if best is None:
        return None
    return best[0], -best[1], best[2]


def match_learned_chromaprint_values(
    model_path: Path,
    index_path: Path,
    query_values: Sequence[int],
    *,
    source_token: object = "",
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Ask the locally learned model before searching the full catalog."""
    query = [int(value) & 0xFFFFFFFF for value in query_values]
    model = Path(model_path)
    if len(query) < CHROMAPRINT_MINIMUM_VALUES or not model.is_file():
        return []
    try:
        with closing(_connect(model, read_only=True)) as connection:
            rows = connection.execute(
                "SELECT * FROM confirmed_samples ORDER BY created_at DESC"
            ).fetchall()
    except sqlite3.Error:
        return []
    requested_source = str(source_token or "").strip()
    scored_by_track: dict[str, tuple[float, int, int, bool, Any]] = {}
    examples_by_track: Counter[str] = Counter()
    for row in rows:
        track_key = str(row["track_key"])
        examples_by_track[track_key] += 1
        try:
            reference = _decode_chromaprint_values(row["fingerprint"])
        except MusicIndexError:
            continue
        measured = _best_learned_chromaprint_alignment(query, reference)
        if measured is None:
            continue
        distance, overlap, offset = measured
        same_source = bool(
            requested_source
            and str(row["source_token"]).strip() == requested_source
        )
        maximum_distance = (
            LEARNED_MODEL_MAXIMUM_DISTANCE
            if same_source
            else LEARNED_MODEL_CROSS_SOURCE_MAXIMUM_DISTANCE
        )
        if distance > maximum_distance:
            continue
        # Prefer examples learned through the current Windows audio path when
        # distances are effectively tied, without making other sources useless.
        ranking_distance = max(0.0, distance - (0.006 if same_source else 0.0))
        candidate = (ranking_distance, -overlap, offset, same_source, row)
        previous = scored_by_track.get(track_key)
        if previous is None or candidate[:2] < previous[:2]:
            scored_by_track[track_key] = candidate
    scored = sorted(scored_by_track.items(), key=lambda item: item[1][:2])
    if not scored:
        return []
    if (
        len(scored) > 1
        and scored[1][1][0] - scored[0][1][0] < LEARNED_MODEL_RUNNER_SEPARATION
    ):
        return []
    track_keys = [track_key for track_key, _score in scored[: max(8, limit * 3)]]
    placeholders = ",".join("?" for _unused in track_keys)
    with closing(_connect(Path(index_path), read_only=True)) as connection:
        metadata_rows = connection.execute(
            f"SELECT * FROM tracks WHERE track_key IN ({placeholders})",
            tuple(track_keys),
        ).fetchall()
    metadata = {str(row["track_key"]): row for row in metadata_rows}
    results: list[dict[str, Any]] = []
    returned_submissions: set[str] = set()
    for track_key, score in scored:
        row = metadata.get(track_key)
        if row is None:
            continue
        ranking_distance, negative_overlap, offset, same_source, _learned_row = score
        distance = ranking_distance + (0.006 if same_source else 0.0)
        submission_id = str(row["submission_id"])
        if submission_id in returned_submissions:
            continue
        maximum_distance = (
            LEARNED_MODEL_MAXIMUM_DISTANCE
            if same_source
            else LEARNED_MODEL_CROSS_SOURCE_MAXIMUM_DISTANCE
        )
        similarity = max(0.0, min(1.0, 1.0 - distance / maximum_distance))
        confidence = min(99.0, 78.0 + 21.0 * math.sqrt(similarity))
        results.append(
            {
                "track_id": int(row["id"]),
                "track_key": track_key,
                "submission_id": submission_id,
                "spc_filename": str(row["spc_filename"]),
                "title": str(row["title"]),
                "artist": str(row["author"]),
                "submission_url": str(row["submission_url"]),
                "download_url": str(row["download_url"]),
                "confidence": round(confidence, 1),
                "audio_distance": round(distance, 4),
                "matching_frames": -int(negative_overlap),
                "offset_seconds": round(offset * (4096.0 / 3.0 / 11025.0), 2),
                "match_strategy": "AI learning from confirmed recordings",
                "learned_examples": int(examples_by_track[track_key]),
            }
        )
        returned_submissions.add(submission_id)
        if len(results) >= max(1, int(limit)):
            break
    return results


def match_chromaprint_values(
    index_path: Path,
    query_values: Sequence[int],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Match a raw Chromaprint sequence against the local SMWC catalog."""
    query = [int(value) & 0xFFFFFFFF for value in query_values]
    if len(query) < CHROMAPRINT_MINIMUM_VALUES:
        return []
    query_times: dict[int, list[int]] = defaultdict(list)
    for frame, value in enumerate(query):
        query_times[value >> CHROMAPRINT_TOKEN_SHIFT].append(frame)

    offset_votes: Counter[tuple[int, int]] = Counter()
    with closing(_connect(index_path, read_only=True)) as connection:
        available = int(
            connection.execute(
                "SELECT COUNT(*) FROM chromaprint_data"
            ).fetchone()[0]
        )
        if available <= 0:
            return []
        tokens = sorted(query_times)
        for token_chunk in _chunks(tokens, SQLITE_QUERY_CHUNK):
            placeholders = ",".join("?" for _unused in token_chunk)
            rows = connection.execute(
                "SELECT token, track_id, frame FROM chromaprint_tokens "
                f"WHERE token IN ({placeholders})",
                tuple(token_chunk),
            ).fetchall()
            for row in rows:
                token = int(row["token"])
                track_id = int(row["track_id"])
                reference_frame = int(row["frame"])
                for query_frame in query_times.get(token, ()):
                    offset_votes[(track_id, reference_frame - query_frame)] += 1
        if not offset_votes:
            return []

        strongest_offsets: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for (track_id, offset), votes in offset_votes.most_common():
            candidates = strongest_offsets[track_id]
            if len(candidates) >= 5:
                continue
            if any(abs(offset - existing_offset) <= 2 for _votes, existing_offset in candidates):
                continue
            candidates.append((votes, offset))
        candidate_tracks = sorted(
            strongest_offsets,
            key=lambda track_id: strongest_offsets[track_id][0][0],
            reverse=True,
        )[:80]
        placeholders = ",".join("?" for _unused in candidate_tracks)
        rows = connection.execute(
            "SELECT tracks.*, chromaprint_data.fingerprint "
            "FROM tracks JOIN chromaprint_data "
            "ON chromaprint_data.track_id = tracks.id "
            f"WHERE tracks.id IN ({placeholders})",
            tuple(candidate_tracks),
        ).fetchall()

    scored: list[tuple[float, int, int, Any]] = []
    for row in rows:
        track_id = int(row["id"])
        reference = _decode_chromaprint_values(row["fingerprint"])
        best: tuple[float, int, int] | None = None
        for votes, suggested_offset in strongest_offsets.get(track_id, ()):
            for adjustment in range(-4, 5):
                offset = suggested_offset + adjustment
                measured = _chromaprint_aligned_distance(
                    query,
                    reference,
                    offset,
                )
                if measured is None:
                    continue
                distance, overlap = measured
                candidate = (distance, -overlap, offset)
                if best is None or candidate < best:
                    best = candidate
        if best is not None:
            scored.append((best[0], -best[1], best[2], row))
    scored.sort(key=lambda item: (item[0], -item[1]))
    if not scored or scored[0][0] > CHROMAPRINT_MAXIMUM_DISTANCE:
        return []

    winner_submission = str(scored[0][3]["submission_id"])
    distinct_runner = next(
        (
            candidate
            for candidate in scored[1:]
            if str(candidate[3]["submission_id"]) != winner_submission
        ),
        None,
    )
    if (
        distinct_runner is not None
        and distinct_runner[0] <= CHROMAPRINT_MAXIMUM_DISTANCE
        and distinct_runner[0] - scored[0][0] < CHROMAPRINT_RUNNER_SEPARATION
    ):
        return []

    results: list[dict[str, Any]] = []
    returned_submissions: set[str] = set()
    winner_distance = float(scored[0][0])
    if distinct_runner is None or distinct_runner[0] > CHROMAPRINT_MAXIMUM_DISTANCE:
        winner_separation = 1.0
    else:
        winner_separation = max(
            0.0,
            min(
                1.0,
                (float(distinct_runner[0]) - winner_distance)
                / max(0.001, CHROMAPRINT_MAXIMUM_DISTANCE - winner_distance),
            ),
        )
    for distance, overlap, offset, row in scored:
        if distance > CHROMAPRINT_MAXIMUM_DISTANCE:
            continue
        submission_id = str(row["submission_id"])
        if submission_id in returned_submissions:
            continue
        # ``distance`` measures literal waveform similarity, not the chance
        # that the catalog result is correct. Capture-card noise and game SFX
        # can raise that distance even when the song decisively beats every
        # other candidate. Calibrate accepted matches around that distinction
        # and reserve the final ten points for winner separation.
        similarity = max(
            0.0,
            min(1.0, 1.0 - distance / CHROMAPRINT_MAXIMUM_DISTANCE),
        )
        separation = (
            winner_separation
            if str(row["submission_id"]) == winner_submission
            else 0.0
        )
        confidence = max(
            0.0,
            min(
                100.0,
                50.0 + 40.0 * math.sqrt(similarity) + 10.0 * separation,
            ),
        )
        results.append(
            {
                "track_id": int(row["id"]),
                "track_key": str(row["track_key"]),
                "submission_id": submission_id,
                "spc_filename": str(row["spc_filename"]),
                "title": str(row["title"]),
                "artist": str(row["author"]),
                "submission_url": str(row["submission_url"]),
                "download_url": str(row["download_url"]),
                "confidence": round(confidence, 1),
                "audio_distance": round(distance, 4),
                "matching_frames": overlap,
                "offset_seconds": round(offset * (4096.0 / 3.0 / 11025.0), 2),
                "match_strategy": "Chromaprint waveform",
            }
        )
        returned_submissions.add(submission_id)
        if len(results) >= max(1, int(limit)):
            break
    return results


def _chromaprint_intro_middle_loop_sections(
    query_values: Sequence[int],
) -> list[list[int]]:
    """Return independent intro, middle, and late/loop query fingerprints."""

    query = [int(value) & 0xFFFFFFFF for value in query_values]
    if len(query) < CHROMAPRINT_SECTION_MINIMUM_TOTAL_VALUES:
        return []
    # A section is long enough to exceed Chromaprint's minimum while leaving
    # three substantially different views of the recording. Small overlap
    # protects a note that lands exactly on a section boundary.
    section_length = max(
        CHROMAPRINT_MINIMUM_VALUES,
        int(math.ceil(len(query) * 0.42)),
    )
    final_start = max(0, len(query) - section_length)
    starts = (0, final_start // 2, final_start)
    sections: list[list[int]] = []
    previous: tuple[int, ...] | None = None
    for start in starts:
        section = tuple(query[start : start + section_length])
        if len(section) < CHROMAPRINT_MINIMUM_VALUES or section == previous:
            continue
        sections.append(list(section))
        previous = section
    return sections if len(sections) == CHROMAPRINT_SECTION_COUNT else []


def _chromaprint_music_heavy_sections(
    query_values: Sequence[int],
    ranges: Sequence[dict[str, float]],
) -> list[list[int]]:
    """Map audio-quality ranges onto one full Chromaprint sequence."""

    query = [int(value) & 0xFFFFFFFF for value in query_values]
    if len(query) < CHROMAPRINT_MINIMUM_VALUES:
        return []
    sections: list[list[int]] = []
    seen_sections: set[tuple[int, ...]] = set()
    for music_range in ranges:
        start_ratio = max(
            0.0,
            min(1.0, float(music_range.get("start_ratio", 0.0) or 0.0)),
        )
        stop_ratio = max(
            start_ratio,
            min(1.0, float(music_range.get("stop_ratio", 1.0) or 1.0)),
        )
        start = max(0, min(len(query), round(start_ratio * len(query))))
        stop = max(start, min(len(query), round(stop_ratio * len(query))))
        if stop - start < CHROMAPRINT_MINIMUM_VALUES:
            center = (start + stop) // 2
            start = max(0, center - CHROMAPRINT_MINIMUM_VALUES // 2)
            stop = min(len(query), start + CHROMAPRINT_MINIMUM_VALUES)
            start = max(0, stop - CHROMAPRINT_MINIMUM_VALUES)
        section_tuple = tuple(query[start:stop])
        if (
            len(section_tuple) < CHROMAPRINT_MINIMUM_VALUES
            or section_tuple in seen_sections
        ):
            continue
        seen_sections.add(section_tuple)
        sections.append(list(section_tuple))
    return sections


def _match_chromaprint_section_candidates(
    index_path: Path,
    sections: Sequence[Sequence[int]],
    *,
    limit: int,
    strategy: str,
    progress_callback=None,
) -> list[dict[str, Any]]:
    """Require independent selected sections to agree on one song."""

    clean_sections = [
        list(section)
        for section in sections
        if len(section) >= CHROMAPRINT_MINIMUM_VALUES
    ]
    if len(clean_sections) < 2:
        return []
    winners: list[dict[str, Any]] = []
    for section_index, section in enumerate(clean_sections, start=1):
        if progress_callback is not None:
            progress_callback(section_index, len(clean_sections))
        matches = match_chromaprint_values(
            index_path,
            section,
            limit=max(2, int(limit)),
        )
        if matches:
            winners.append(dict(matches[0]))
    if len(winners) < 2:
        return []
    counts = Counter(
        str(winner.get("submission_id", "")).strip()
        for winner in winners
        if str(winner.get("submission_id", "")).strip()
    )
    if not counts:
        return []
    winning_submission, support = counts.most_common(1)[0]
    if support < 2:
        return []
    supporters = [
        winner
        for winner in winners
        if str(winner.get("submission_id", "")).strip()
        == winning_submission
    ]
    strongest = max(
        supporters,
        key=lambda winner: float(winner.get("confidence", 0.0) or 0.0),
    )
    result = dict(strongest)
    confidence_values = [
        float(winner.get("confidence", 0.0) or 0.0)
        for winner in supporters
    ]
    result["confidence"] = round(
        min(
            99.0,
            sum(confidence_values) / max(1, len(confidence_values))
            + (2.0 if support == len(clean_sections) else 0.0),
        ),
        1,
    )
    result["match_strategy"] = (
        f"{strategy} ({support}/{len(clean_sections)} sections)"
    )
    result["matching_sections"] = int(support)
    result["checked_sections"] = len(clean_sections)
    return [result]


def match_chromaprint_sections(
    index_path: Path,
    query_values: Sequence[int],
    *,
    limit: int = 3,
    progress_callback=None,
) -> list[dict[str, Any]]:
    """Require two of three audio sections to identify one submission."""

    sections = _chromaprint_intro_middle_loop_sections(query_values)
    if not sections:
        return []
    return _match_chromaprint_section_candidates(
        index_path,
        sections,
        limit=limit,
        strategy="Chromaprint intro/middle/loop consensus",
        progress_callback=progress_callback,
    )


def match_fingerprints(
    index_path: Path,
    query_fingerprints: Sequence[tuple[int, int]],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Rank tracks by matching landmarks with a consistent time offset."""
    if not query_fingerprints:
        return []
    query_times: dict[int, list[int]] = defaultdict(list)
    for landmark, frame in query_fingerprints:
        query_times[int(landmark)].append(int(frame))
    unique_hashes = sorted(query_times)
    offset_evidence: dict[tuple[int, int], set[tuple[int, int, int]]] = (
        defaultdict(set)
    )
    informative_hashes: set[int] = set()
    with closing(_connect(index_path, read_only=True)) as connection:
        track_count = max(
            1,
            int(connection.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]),
        )
        # Very common landmarks are usually silence, sustained notes, or sound
        # effects. They are poor identifiers and become especially misleading
        # in a full catalog, so ignore hashes shared by too many songs.
        maximum_tracks_per_hash = max(
            4,
            min(30, math.ceil(track_count * 0.005)),
        )
        for hash_chunk in _chunks(unique_hashes, SQLITE_QUERY_CHUNK):
            placeholders = ",".join("?" for _ in hash_chunk)
            rows = connection.execute(
                "SELECT hash, track_id, frame FROM fingerprints "
                f"WHERE hash IN ({placeholders})",
                tuple(hash_chunk),
            ).fetchall()
            rows_by_hash: dict[int, list[Any]] = defaultdict(list)
            tracks_by_hash: dict[int, set[int]] = defaultdict(set)
            for row in rows:
                landmark = int(row["hash"])
                track_id = int(row["track_id"])
                rows_by_hash[landmark].append(row)
                tracks_by_hash[landmark].add(track_id)
            for landmark, landmark_rows in rows_by_hash.items():
                if len(tracks_by_hash[landmark]) > maximum_tracks_per_hash:
                    continue
                informative_hashes.add(landmark)
                for row in landmark_rows:
                    track_id = int(row["track_id"])
                    reference_frame = int(row["frame"])
                    for query_frame in query_times.get(landmark, ()):
                        offset_bucket = round((reference_frame - query_frame) / 2)
                        offset_evidence[(track_id, offset_bucket)].add(
                            (landmark, query_frame, reference_frame)
                        )

        offset_votes: Counter[tuple[int, int]] = Counter(
            {
                key: len(evidence)
                for key, evidence in offset_evidence.items()
            }
        )
        offset_hashes: dict[tuple[int, int], set[int]] = {
            key: {landmark for landmark, _query, _reference in evidence}
            for key, evidence in offset_evidence.items()
        }

        strongest: dict[int, tuple[int, int]] = {}
        for (track_id, offset_bucket), votes in offset_votes.items():
            previous = strongest.get(track_id)
            if (
                previous is None
                or votes > previous[0]
                or (
                    votes == previous[0]
                    and len(offset_hashes[(track_id, offset_bucket)])
                    > len(offset_hashes[(track_id, previous[1])])
                )
            ):
                strongest[track_id] = (votes, offset_bucket)
        ranked = sorted(
            strongest.items(),
            key=lambda item: (
                item[1][0],
                len(offset_hashes[(item[0], item[1][1])]),
            ),
            reverse=True,
        )[: max(8, int(limit) * 4)]
        if not ranked:
            return []
        track_ids = [track_id for track_id, _details in ranked]
        placeholders = ",".join("?" for _ in track_ids)
        track_rows = {
            int(row["id"]): row
            for row in connection.execute(
                "SELECT * FROM tracks "
                f"WHERE id IN ({placeholders})",
                tuple(track_ids),
            ).fetchall()
        }

    results: list[dict[str, Any]] = []
    # Coverage and the minimum-match requirement must use the same distinctive
    # landmarks that were allowed to vote. Counting ignored, catalog-wide
    # sounds here made short but valid recordings fail as the catalog grew.
    query_unique_count = max(1, len(informative_hashes))
    winner_votes = ranked[0][1][0] if ranked else 0
    winner_unique_matches = (
        len(offset_hashes[(ranked[0][0], ranked[0][1][1])]) if ranked else 0
    )
    winner_row = track_rows.get(ranked[0][0]) if ranked else None
    winner_submission = (
        str(winner_row["submission_id"]) if winner_row is not None else ""
    )
    distinct_runner = next(
        (
            candidate
            for candidate in ranked[1:]
            if str(track_rows[candidate[0]]["submission_id"])
            != winner_submission
        ),
        None,
    )
    runner_up_votes = distinct_runner[1][0] if distinct_runner else 0
    runner_up_unique_matches = (
        len(
            offset_hashes[
                (distinct_runner[0], distinct_runner[1][1])
            ]
        )
        if distinct_runner
        else 0
    )
    minimum_unique_matches = max(3, min(8, math.ceil(query_unique_count * 0.20)))
    if (
        winner_votes < MINIMUM_MATCH_VOTES
        or winner_unique_matches < minimum_unique_matches
        or (
            runner_up_votes >= winner_votes * 0.88
            and runner_up_unique_matches >= winner_unique_matches * 0.88
        )
    ):
        return []
    returned_submissions: set[str] = set()
    for track_id, (votes, offset_bucket) in ranked:
        if votes < MINIMUM_MATCH_VOTES:
            continue
        row = track_rows.get(track_id)
        if row is None:
            continue
        submission_id = str(row["submission_id"])
        if submission_id in returned_submissions:
            continue
        result_index = len(results)
        unique_matches = len(offset_hashes[(track_id, offset_bucket)])
        coverage = unique_matches / query_unique_count
        if result_index == 0:
            vote_strength = min(1.0, votes / 25.0)
            separation = 1.0 - (runner_up_votes / max(1, votes))
            confidence = 100.0 * (
                0.35 * coverage
                + 0.35 * vote_strength
                + 0.30 * max(0.0, separation)
            )
        else:
            confidence = 100.0 * (
                0.55 * coverage
                + 0.45 * min(1.0, votes / max(1, winner_votes))
            )
        results.append(
            {
                "track_id": track_id,
                "track_key": str(row["track_key"]),
                "submission_id": submission_id,
                "spc_filename": str(row["spc_filename"]),
                "title": str(row["title"]),
                "artist": str(row["author"]),
                "submission_url": str(row["submission_url"]),
                "download_url": str(row["download_url"]),
                "confidence": round(confidence, 1),
                "votes": votes,
                "matching_hashes": unique_matches,
                "query_hashes": query_unique_count,
                "offset_seconds": round(
                    offset_bucket * 2 * FFT_HOP / TARGET_SAMPLE_RATE,
                    2,
                ),
            }
        )
        returned_submissions.add(submission_id)
        if len(results) >= max(1, int(limit)):
            break
    return results


def match_wav(
    index_path: Path,
    sample_path: Path,
    *,
    limit: int = 3,
    require_complete: bool = True,
    progress_callback=None,
    chromaprint_only: bool = False,
    learned_model_path: Path | None = None,
    community_model_path: Path | None = None,
    recognition_api_url: object = "",
    source_token: object = "",
    include_learning_fingerprint: bool = False,
    cloud_only: bool = False,
) -> list[dict[str, Any]]:
    variants, sample_rate = _pcm16_channel_variants(Path(sample_path))
    focused_variants = [
        (
            f"{label}, music-focused SFX filter",
            _music_focused_samples(samples, sample_rate),
        )
        for label, samples in variants
    ]
    query_plans = [
        (label, samples, TARGET_SAMPLE_RATE, factor)
        for factor in MATCH_SAMPLE_RATE_FACTORS
        for label, samples in focused_variants
    ] + [
        (label, samples, sample_rate, factor)
        for factor in MATCH_SAMPLE_RATE_FACTORS
        for label, samples in variants
    ]
    with MUSIC_INDEX_LOCK:
        if cloud_only:
            if not str(recognition_api_url or "").strip():
                raise MusicIndexError(
                    "This build requires the online SMW Central music service."
                )
            index_details: dict[str, Any] = {}
        else:
            index_details = validate_music_index(
                index_path,
                require_tracks=True,
                require_complete=require_complete,
            )
        chromaprint_available = int(
            index_details.get("chromaprint_track_count", 0) or 0
        ) > 0
        looks_like_music = min(
            _music_spectral_flatness(samples, sample_rate)
            for _label, samples in variants
        ) < 0.45
        # A Shazam-style recognizer must still attempt the acoustic signature
        # when speech, game effects, or a noisy stream raise spectral flatness.
        # Flatness remains useful for choosing cleanup windows, but it must not
        # disable the full-catalog fingerprint path.
        use_chromaprint = chromaprint_available
        raw_chromaprint_query: list[int] = []
        if use_chromaprint or recognition_api_url:
            try:
                raw_chromaprint_query = chromaprint_fingerprint_samples(
                    variants[0][1],
                    sample_rate,
                )
            except MusicIndexError:
                raw_chromaprint_query = []
        focused_chromaprint_query: list[int] = []
        if (
            use_chromaprint
            or recognition_api_url
            or (
                learned_model_path is not None
                and Path(learned_model_path).is_file()
            )
            or (
                community_model_path is not None
                and Path(community_model_path).is_file()
            )
        ):
            try:
                focused_chromaprint_query = chromaprint_fingerprint_samples(
                    focused_variants[0][1],
                    TARGET_SAMPLE_RATE,
                )
            except MusicIndexError:
                focused_chromaprint_query = []
        learning_query = focused_chromaprint_query or raw_chromaprint_query
        if (
            not cloud_only
            and learned_model_path is not None
            and focused_chromaprint_query
        ):
            learned_matches = match_learned_chromaprint_values(
                Path(learned_model_path),
                Path(index_path),
                focused_chromaprint_query,
                source_token=source_token,
                limit=limit,
            )
            if learned_matches:
                if include_learning_fingerprint:
                    learned_matches[0]["_learning_fingerprint"] = list(
                        focused_chromaprint_query
                    )
                return learned_matches
        if (
            not cloud_only
            and community_model_path is not None
            and focused_chromaprint_query
        ):
            community_matches = match_learned_chromaprint_values(
                Path(community_model_path),
                Path(index_path),
                focused_chromaprint_query,
                source_token=source_token,
                limit=limit,
            )
            if community_matches:
                for community_match in community_matches:
                    community_match["match_strategy"] = (
                        "Community Song Results from confirmed recordings"
                    )
                if include_learning_fingerprint:
                    community_matches[0]["_learning_fingerprint"] = list(
                        focused_chromaprint_query
                    )
                return community_matches
        if recognition_api_url and raw_chromaprint_query:
            if progress_callback is not None:
                progress_callback(0, 1)
            try:
                cloud_matches = match_cloud_chromaprint_values(
                    recognition_api_url,
                    raw_chromaprint_query,
                    limit=limit,
                )
            except MusicIndexError:
                if cloud_only:
                    raise
                cloud_matches = []
            if progress_callback is not None:
                progress_callback(1, 1)
            if cloud_matches:
                if include_learning_fingerprint and learning_query:
                    cloud_matches[0]["_learning_fingerprint"] = list(
                        learning_query
                    )
                return cloud_matches
        if cloud_only:
            if progress_callback is not None:
                progress_callback(1, 1)
            return []
        # Early checks use only the cleaned waveform for speed. The final pass
        # also retains the old raw-waveform fallback for unusual,
        # percussion-heavy SPC ports.
        chromaprint_plans: list[tuple[str, Any | None, int]] = []
        if use_chromaprint:
            chromaprint_plans.append(
                (focused_variants[0][0], focused_variants[0][1], TARGET_SAMPLE_RATE)
            )
            if not chromaprint_only:
                chromaprint_plans.append(("unfiltered fallback", None, sample_rate))
        music_heavy_ranges = (
            _music_heavy_ranges(
                focused_variants[0][1],
                TARGET_SAMPLE_RATE,
            )
            if use_chromaprint
            else []
        )
        quality_section_queries = (
            _chromaprint_music_heavy_sections(
                focused_chromaprint_query,
                music_heavy_ranges,
            )
            if use_chromaprint
            else []
        )
        section_queries = (
            _chromaprint_intro_middle_loop_sections(
                focused_chromaprint_query
            )
            if use_chromaprint
            else []
        )
        quality_section_plan_count = len(quality_section_queries)
        section_plan_count = len(section_queries)
        total = (
            len(query_plans)
            + len(chromaprint_plans)
            + quality_section_plan_count
            + section_plan_count
        )
        if len(quality_section_queries) >= 2:
            quality_matches = _match_chromaprint_section_candidates(
                index_path,
                quality_section_queries,
                limit=limit,
                strategy="Chromaprint clean music-window consensus",
                progress_callback=(
                    (lambda current, _section_total: progress_callback(
                        current,
                        total,
                    ))
                    if progress_callback is not None
                    else None
                ),
            )
            if quality_matches:
                for match in quality_matches:
                    match["match_strategy"] += (
                        ", speech/SFX-gated application audio"
                    )
                if include_learning_fingerprint:
                    quality_matches[0]["_learning_fingerprint"] = list(
                        focused_chromaprint_query
                    )
                if progress_callback is not None:
                    progress_callback(total, total)
                return quality_matches
        if section_queries:
            section_matches = match_chromaprint_sections(
                index_path,
                focused_chromaprint_query,
                limit=limit,
                progress_callback=(
                    (lambda current, _section_total: progress_callback(
                        quality_section_plan_count + current,
                        total,
                    ))
                    if progress_callback is not None
                    else None
                ),
            )
            if section_matches:
                for match in section_matches:
                    match["match_strategy"] += ", music-focused SFX filter"
                if include_learning_fingerprint:
                    section_matches[0]["_learning_fingerprint"] = list(
                        focused_chromaprint_query
                    )
                if progress_callback is not None:
                    progress_callback(total, total)
                return section_matches
        if use_chromaprint:
            for chromaprint_index, (_label, samples, plan_rate) in enumerate(
                chromaprint_plans,
                start=1,
            ):
                if progress_callback is not None:
                    progress_callback(
                        chromaprint_index
                        + quality_section_plan_count
                        + section_plan_count,
                        total,
                    )
                if samples is None:
                    chromaprint_query = chromaprint_fingerprint_wav(
                        Path(sample_path)
                    )
                elif chromaprint_index == 1 and focused_chromaprint_query:
                    chromaprint_query = focused_chromaprint_query
                else:
                    chromaprint_query = chromaprint_fingerprint_samples(
                        samples,
                        plan_rate,
                    )
                matches = match_chromaprint_values(
                    index_path,
                    chromaprint_query,
                    limit=limit,
                )
                if matches:
                    if samples is not None:
                        for match in matches:
                            match["match_strategy"] = (
                                "Chromaprint waveform, music-focused SFX filter"
                            )
                    if include_learning_fingerprint and focused_chromaprint_query:
                        matches[0]["_learning_fingerprint"] = list(
                            focused_chromaprint_query
                        )
                    if progress_callback is not None:
                        progress_callback(total, total)
                    return matches
        if chromaprint_only:
            if progress_callback is not None:
                progress_callback(total, total)
            return []
        progress_offset = (
            len(chromaprint_plans)
            + quality_section_plan_count
            + section_plan_count
        )
        for plan_index, (label, samples, plan_rate, rate_factor) in enumerate(
            query_plans,
            start=1,
        ):
            if progress_callback is not None:
                progress_callback(plan_index + progress_offset, total)
            query = fingerprint_samples(
                samples,
                max(1, round(plan_rate * rate_factor)),
            )
            matches = match_fingerprints(index_path, query, limit=limit)
            if matches:
                strategy = label
                if not math.isclose(rate_factor, 1.0):
                    strategy += f", timing {rate_factor:.4f}"
                for match in matches:
                    match["match_strategy"] = strategy
                if include_learning_fingerprint and focused_chromaprint_query:
                    matches[0]["_learning_fingerprint"] = list(
                        focused_chromaprint_query
                    )
                if progress_callback is not None:
                    progress_callback(total, total)
                return matches
        if progress_callback is not None:
            progress_callback(total, total)
    return []


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        while True:
            chunk = source.read(FILE_HASH_CHUNK)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def finalize_music_index(path: Path) -> None:
    """Checkpoint and compact a build so one immutable file can be shipped."""
    database_path = Path(path).resolve()
    with closing(sqlite3.connect(database_path, timeout=60)) as connection:
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("VACUUM")
        connection.execute("PRAGMA optimize")


def write_index_manifest(
    index_path: Path,
    destination: Path,
    *,
    download_url: str,
    index_version: str,
) -> dict[str, Any]:
    """Write the signed-by-hash manifest consumed by background updates."""
    database_path = Path(index_path)
    finalize_music_index(database_path)
    details = validate_music_index(database_path, require_tracks=True)
    digest = sha256_file(database_path)
    manifest = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "chromaprint_version": CHROMAPRINT_VERSION,
        "index_version": str(index_version),
        "catalog_updated_at": details.get("catalog_updated_at", ""),
        "catalog_complete": details.get("catalog_complete", "0") == "1",
        "track_count": details["track_count"],
        "fingerprint_count": details["fingerprint_count"],
        "chromaprint_track_count": details["chromaprint_track_count"],
        "chromaprint_token_count": details["chromaprint_token_count"],
        "size_bytes": database_path.stat().st_size,
        "sha256": digest,
        "download_url": str(download_url),
    }
    Path(destination).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
