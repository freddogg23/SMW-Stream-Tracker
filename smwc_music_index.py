"""Local SMW Central SPC audio fingerprint indexing and matching.

The database contains non-reconstructive frequency-landmark hashes plus the
public metadata needed to link a result back to SMW Central.  Captured audio is
never uploaded by this module.
"""

from __future__ import annotations

from array import array
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
import threading
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
MUSIC_INDEX_ALLOWED_HOSTS = frozenset(
    {
        "raw.githubusercontent.com",
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
MUSIC_INDEX_LOCK = threading.RLock()


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
) -> list[dict[str, Any]]:
    variants, sample_rate = _pcm16_channel_variants(Path(sample_path))
    query_plans = [
        (label, samples, factor)
        for factor in MATCH_SAMPLE_RATE_FACTORS
        for label, samples in variants
    ]
    with MUSIC_INDEX_LOCK:
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
        use_chromaprint = chromaprint_available and looks_like_music
        total = len(query_plans) + (1 if use_chromaprint else 0)
        if use_chromaprint:
            if progress_callback is not None:
                progress_callback(1, total)
            chromaprint_query = chromaprint_fingerprint_wav(Path(sample_path))
            matches = match_chromaprint_values(
                index_path,
                chromaprint_query,
                limit=limit,
            )
            if matches:
                if progress_callback is not None:
                    progress_callback(total, total)
                return matches
        if chromaprint_only:
            if progress_callback is not None:
                progress_callback(total, total)
            return []
        progress_offset = 1 if use_chromaprint else 0
        for plan_index, (label, samples, rate_factor) in enumerate(
            query_plans,
            start=1,
        ):
            if progress_callback is not None:
                progress_callback(plan_index + progress_offset, total)
            query = fingerprint_samples(
                samples,
                max(1, round(sample_rate * rate_factor)),
            )
            matches = match_fingerprints(index_path, query, limit=limit)
            if matches:
                strategy = label
                if not math.isclose(rate_factor, 1.0):
                    strategy += f", timing {rate_factor:.4f}"
                for match in matches:
                    match["match_strategy"] = strategy
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
