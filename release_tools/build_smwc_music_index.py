"""Build the distributable SMW Central SPC fingerprint index.

This is a Windows release-maintenance tool.  It downloads only changed SMW
Central submissions, renders their SPC previews locally, and stores compact
non-reconstructive landmarks in SQLite.  Interrupted runs are resumable.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import smwc_music_index as music_index


SMWC_API_URL = "https://www.smwcentral.net/ajax.php"
SMWC_DETAILS_URL = "https://www.smwcentral.net/?p=section&a=details&id={}"
USER_AGENT = "SMW-Stream-Tracker-Music-Index/1.0"
PAGE_DELAY_SECONDS = 1.25
DOWNLOAD_DELAY_SECONDS = 0.35
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024
MAX_SPC_BYTES = 2 * 1024 * 1024
DEFAULT_RENDER_SECONDS = 120
SPC_RENDERER_URL = (
    "https://github.com/niekvlessert/spc2vgm/releases/download/v0.8/"
    "spc2vgm-windows-intel.zip"
)
SPC_RENDERER_SHA256 = (
    "970cee40a40b2bdc3c89cb19ff43eccd8429d06b314ce920f0cd7440c7af6fef"
)
CHROMAPRINT_URL = (
    "https://github.com/acoustid/chromaprint/releases/download/v1.6.1/"
    "chromaprint-fpcalc-1.6.1-windows-x86_64.zip"
)
CHROMAPRINT_SHA256 = (
    "735d6182b38e9f364b84ce6f4ccd682c75e2851de89735711d6b762d12b92a4e"
)


def _utc_version() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _request_bytes(url: str, *, attempts: int = 6) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=60) as response:
                expected = int(response.headers.get("Content-Length", "0") or 0)
                if expected > MAX_DOWNLOAD_BYTES:
                    raise RuntimeError(f"Download is unexpectedly large: {url}")
                chunks: list[bytes] = []
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise RuntimeError(f"Download exceeded the safe limit: {url}")
                    chunks.append(chunk)
                return b"".join(chunks)
        except HTTPError as error:
            last_error = error
            retry_after = error.headers.get("Retry-After") if error.headers else None
            if error.code not in (429, 500, 502, 503, 504):
                raise
            try:
                delay = max(2.0, float(retry_after))
            except (TypeError, ValueError):
                delay = min(90.0, 3.0 * (2**attempt))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            delay = min(90.0, 3.0 * (2**attempt))
        if attempt + 1 < attempts:
            print(f"  Network pause: retrying in {delay:.0f} seconds...")
            time.sleep(delay)
    raise RuntimeError(f"Unable to download {url}: {last_error}")


def _request_json(url: str) -> dict[str, Any]:
    document = json.loads(_request_bytes(url).decode("utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError("SMW Central returned an invalid catalog document.")
    return document


def _atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _load_catalog(path: Path) -> tuple[dict[str, dict[str, Any]], bool]:
    if not path.is_file():
        return {}, False
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, False
    submissions = document.get("submissions", {}) if isinstance(document, dict) else {}
    return (
        {
            str(key): value
            for key, value in submissions.items()
            if isinstance(value, dict)
        },
        bool(document.get("complete", False)) if isinstance(document, dict) else False,
    )


def _save_catalog(
    path: Path,
    submissions: dict[str, dict[str, Any]],
    *,
    complete: bool,
) -> None:
    document = {
        "section": "smwmusic",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "complete": bool(complete),
        "submissions": submissions,
    }
    _atomic_bytes(
        path,
        (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


def fetch_catalog(
    cache_path: Path,
    *,
    full: bool = False,
    maximum_submissions: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """Refresh newest-first pages and stop after two unchanged pages."""
    cached, cached_complete = _load_catalog(cache_path)
    merged = dict(cached)
    page = 1
    last_page = 1
    unchanged_page_streak = 0
    complete = False
    collected = 0
    while page <= last_page:
        query = urlencode(
            {"a": "getsectionlist", "s": "smwmusic", "u": "0", "n": page}
        )
        print(f"Reading SMW Central music page {page} of {last_page}...")
        payload = _request_json(f"{SMWC_API_URL}?{query}")
        try:
            last_page = max(page, int(payload.get("last_page", page) or page))
        except (TypeError, ValueError):
            last_page = page
        raw_submissions = payload.get("data", [])
        if not isinstance(raw_submissions, list):
            raise RuntimeError("SMW Central returned an invalid music list.")
        if not raw_submissions:
            complete = True
            break
        page_unchanged = True
        for raw in raw_submissions:
            if not isinstance(raw, dict) or not raw.get("id"):
                continue
            submission_id = str(raw["id"])
            old = cached.get(submission_id)
            old_time = str(old.get("time", "")) if old else ""
            new_time = str(raw.get("time", ""))
            if old_time != new_time:
                page_unchanged = False
            merged[submission_id] = raw
            collected += 1
            if maximum_submissions and collected >= maximum_submissions:
                _save_catalog(cache_path, merged, complete=False)
                selected = sorted(
                    merged.values(), key=lambda item: int(item.get("time", 0) or 0), reverse=True
                )[:maximum_submissions]
                return selected, False
        if cached and cached_complete and page_unchanged and not full:
            unchanged_page_streak += 1
        else:
            unchanged_page_streak = 0
        if unchanged_page_streak >= 2:
            complete = cached_complete
            break
        page += 1
        if page > last_page:
            complete = True
            break
        time.sleep(PAGE_DELAY_SECONDS)
    _save_catalog(cache_path, merged, complete=complete)
    return list(merged.values()), complete


def _renderer_executable(cache_dir: Path, supplied: Path | None) -> Path:
    if supplied is not None:
        candidate = supplied.resolve()
        if not candidate.is_file():
            raise RuntimeError(f"SPC renderer was not found: {candidate}")
        return candidate
    tools_dir = cache_dir / "tools" / "spc2vgm-v0.8"
    existing = next(tools_dir.rglob("spc_render.exe"), None) if tools_dir.is_dir() else None
    if existing is not None:
        return existing
    print("Downloading the pinned SPC renderer build...")
    archive_bytes = _request_bytes(SPC_RENDERER_URL)
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest.casefold() != SPC_RENDERER_SHA256.casefold():
        raise RuntimeError("The downloaded SPC renderer failed its safety check.")
    tools_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temporary:
        temporary.write(archive_bytes)
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path) as archive:
            for member in archive.infolist():
                normalized = Path(member.filename.replace("\\", "/"))
                if normalized.is_absolute() or ".." in normalized.parts:
                    raise RuntimeError("The SPC renderer archive contains an unsafe path.")
                if member.is_dir():
                    continue
                destination = tools_dir.joinpath(*normalized.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)
    finally:
        temporary_path.unlink(missing_ok=True)
    renderer = next(tools_dir.rglob("spc_render.exe"), None)
    if renderer is None:
        raise RuntimeError("The SPC renderer package did not contain spc_render.exe.")
    return renderer


def _chromaprint_executable(cache_dir: Path, supplied: Path | None) -> Path:
    if supplied is not None:
        candidate = supplied.resolve()
        if not candidate.is_file():
            raise RuntimeError(f"Chromaprint fpcalc was not found: {candidate}")
        return candidate
    tools_dir = cache_dir / "tools" / "chromaprint-1.6.1"
    existing = next(tools_dir.rglob("fpcalc.exe"), None) if tools_dir.is_dir() else None
    if existing is not None:
        return existing
    print("Downloading the pinned Chromaprint matcher build...")
    archive_bytes = _request_bytes(CHROMAPRINT_URL)
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest.casefold() != CHROMAPRINT_SHA256.casefold():
        raise RuntimeError("The downloaded Chromaprint tool failed its safety check.")
    tools_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temporary:
        temporary.write(archive_bytes)
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path) as archive:
            for member in archive.infolist():
                normalized = Path(member.filename.replace("\\", "/"))
                if normalized.is_absolute() or ".." in normalized.parts:
                    raise RuntimeError(
                        "The Chromaprint archive contains an unsafe path."
                    )
                if member.is_dir():
                    continue
                destination = tools_dir.joinpath(*normalized.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)
    finally:
        temporary_path.unlink(missing_ok=True)
    executable = next(tools_dir.rglob("fpcalc.exe"), None)
    if executable is None:
        raise RuntimeError("The Chromaprint package did not contain fpcalc.exe.")
    return executable


def _archive_path(cache_dir: Path, submission: dict[str, Any]) -> Path:
    submission_id = str(submission.get("id", "")).strip()
    updated_at = str(submission.get("time", "0") or "0")
    return cache_dir / "archives" / f"{submission_id}-{updated_at}.zip"


def _download_archive(cache_dir: Path, submission: dict[str, Any]) -> Path:
    destination = _archive_path(cache_dir, submission)
    if destination.is_file() and destination.stat().st_size > 0:
        return destination
    url = str(submission.get("download_url", "")).strip()
    if not url.startswith("https://"):
        raise RuntimeError("Submission has no safe download URL.")
    payload = _request_bytes(url)
    _atomic_bytes(destination, payload)
    time.sleep(DOWNLOAD_DELAY_SECONDS)
    return destination


def _spc_members(archive_path: Path) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(archive_path) as archive:
        members = [
            member
            for member in archive.infolist()
            if not member.is_dir()
            and member.filename.casefold().endswith(".spc")
            and 0 < member.file_size <= MAX_SPC_BYTES
        ]
    amk_members = [
        member
        for member in members
        if member.filename.casefold().endswith(".amk.spc")
    ]
    # Old submissions commonly bundle a legacy Addmusic preview alongside the
    # AddmusicK preview that is actually used by current hacks. When AMK
    # previews are present, index all of those variants and skip their obsolete
    # legacy counterparts. Modern packages without AMK suffixes are unchanged.
    return amk_members or members


def _remove_superseded_legacy_previews(database: Path) -> int:
    """Remove legacy previews when that submission already has AMK previews."""
    with closing(sqlite3.connect(database, timeout=60)) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        cursor = connection.execute(
            """
            DELETE FROM tracks
            WHERE LOWER(spc_filename) NOT LIKE '%.amk.spc'
              AND submission_id IN (
                  SELECT submission_id FROM tracks
                  WHERE LOWER(spc_filename) LIKE '%.amk.spc'
              )
            """
        )
        connection.commit()
        return max(0, int(cursor.rowcount))


def _duration_seconds(submission: dict[str, Any]) -> int:
    fields = submission.get("raw_fields", {})
    if not isinstance(fields, dict):
        fields = {}
    value = str(fields.get("duration", ""))
    try:
        minutes, seconds = value.split(":", 1)
        declared = int(minutes) * 60 + int(seconds)
    except (ValueError, TypeError):
        declared = DEFAULT_RENDER_SECONDS
    return max(30, min(180, declared + 12))


def _submission_authors(submission: dict[str, Any]) -> str:
    authors = submission.get("authors", [])
    if not isinstance(authors, list):
        return ""
    return ", ".join(
        str(author.get("name", "")).strip()
        for author in authors
        if isinstance(author, dict) and str(author.get("name", "")).strip()
    )


def _render_submission(
    cache_dir: Path,
    renderer: Path,
    chromaprint: Path,
    submission: dict[str, Any],
) -> list[
    tuple[dict[str, Any], list[tuple[int, int]], list[int]]
]:
    archive_path = _download_archive(cache_dir, submission)
    members = _spc_members(archive_path)
    if not members:
        raise RuntimeError("archive contains no SPC preview")
    submission_id = str(submission.get("id", ""))
    submission_title = " ".join(str(submission.get("name", "")).split())
    duration = _duration_seconds(submission)
    rendered_tracks: list[
        tuple[dict[str, Any], list[tuple[int, int]], list[int]]
    ] = []
    member_errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="smwc-spc-") as temporary_folder:
        work = Path(temporary_folder)
        with zipfile.ZipFile(archive_path) as archive:
            for position, member in enumerate(members, start=1):
                safe_name = Path(member.filename.replace("\\", "/")).name
                spc_path = work / f"{position:03d}-{safe_name}"
                wav_path = work / f"{position:03d}.wav"
                try:
                    with (
                        archive.open(member) as source,
                        spc_path.open("wb") as destination,
                    ):
                        shutil.copyfileobj(source, destination)
                    completed = subprocess.run(
                        [str(renderer), str(spc_path), str(duration), str(wav_path)],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=max(90, duration * 3),
                    )
                    if completed.returncode != 0 or not wav_path.is_file():
                        raise RuntimeError(
                            "SPC rendering failed: "
                            + completed.stdout.strip()[-600:]
                        )
                    title = submission_title
                    if len(members) > 1:
                        title = f"{submission_title} — {Path(safe_name).stem}"
                    rendered_tracks.append(
                        (
                            {
                                "submission_id": submission_id,
                                "submission_updated_at": str(
                                    submission.get("time", "")
                                ),
                                "spc_filename": member.filename,
                                "title": title,
                                "author": _submission_authors(submission),
                                "submission_url": SMWC_DETAILS_URL.format(
                                    submission_id
                                ),
                                "download_url": str(
                                    submission.get("download_url", "")
                                ),
                                "duration_seconds": duration,
                            },
                            [],
                            music_index.chromaprint_fingerprint_wav(
                                wav_path,
                                chromaprint,
                            ),
                        )
                    )
                except Exception as error:
                    member_errors.append(f"{safe_name}: {error}")
    if not rendered_tracks:
        raise RuntimeError(
            "; ".join(member_errors[-3:])
            or "archive contains no usable SPC preview"
        )
    return rendered_tracks


def _apply_rendered_submission(
    database: Path,
    submission_id: str,
    rendered_tracks: list[
        tuple[dict[str, Any], list[tuple[int, int]], list[int]]
    ],
) -> int:
    # Leave a previously working version intact until every replacement SPC
    # has rendered and fingerprinted successfully. This function is called
    # only by the coordinator thread, keeping SQLite writes serialized while
    # downloads, SPC rendering, and fingerprint calculation run in parallel.
    music_index.remove_submission_tracks(database, submission_id)
    for metadata, fingerprints, chromaprint_values in rendered_tracks:
        music_index.add_track_fingerprints(
            database,
            metadata,
            fingerprints,
            chromaprint_values,
        )
    return len(rendered_tracks)


def _render_and_index_submission(
    database: Path,
    cache_dir: Path,
    renderer: Path,
    chromaprint: Path,
    submission: dict[str, Any],
) -> int:
    rendered_tracks = _render_submission(
        cache_dir,
        renderer,
        chromaprint,
        submission,
    )
    return _apply_rendered_submission(
        database,
        str(submission.get("id", "")),
        rendered_tracks,
    )


def _checkpoint_database(database: Path) -> None:
    with closing(sqlite3.connect(database, timeout=60)) as connection:
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("PRAGMA optimize")


def build_index(arguments: argparse.Namespace) -> dict[str, Any]:
    output = Path(arguments.output).resolve()
    cache_dir = Path(arguments.cache_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = cache_dir / "catalog.json"
    submissions, catalog_complete = fetch_catalog(
        catalog_path,
        full=bool(arguments.full_catalog),
        maximum_submissions=max(0, int(arguments.max_submissions)),
    )
    renderer = _renderer_executable(
        cache_dir,
        Path(arguments.renderer) if arguments.renderer else None,
    )
    chromaprint = _chromaprint_executable(
        cache_dir,
        Path(arguments.fpcalc) if arguments.fpcalc else None,
    )
    if not output.is_file():
        music_index.initialize_music_index(output)
    removed_legacy_previews = _remove_superseded_legacy_previews(output)
    if removed_legacy_previews:
        print(
            f"Removed {removed_legacy_previews:,} superseded legacy SPC "
            "previews."
        )
    previous_index_metadata = music_index.music_index_metadata(output)
    indexed_versions = music_index.indexed_submission_versions(output)
    changed = [
        submission
        for submission in submissions
        if str(submission.get("time", ""))
        != indexed_versions.get(str(submission.get("id", "")), "")
    ]
    changed.sort(key=lambda item: int(item.get("time", 0) or 0))
    failures: list[dict[str, str]] = []
    successful_changes = 0
    print(
        f"Catalog has {len(submissions):,} entries; "
        f"{len(changed):,} are new or changed."
    )
    worker_count = max(1, min(16, int(arguments.workers)))
    changed_iterator = iter(changed)
    pending: dict[Future, dict[str, Any]] = {}
    completed_count = 0
    executor = ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="SMWCMusicIndex",
    )

    def submit_next() -> bool:
        try:
            submission = next(changed_iterator)
        except StopIteration:
            return False
        pending[
            executor.submit(
                _render_submission,
                cache_dir,
                renderer,
                chromaprint,
                submission,
            )
        ] = submission
        return True

    try:
        for _unused in range(min(len(changed), worker_count * 2)):
            submit_next()
        while pending:
            finished, _still_pending = wait(
                tuple(pending),
                return_when=FIRST_COMPLETED,
            )
            for future in finished:
                submission = pending.pop(future)
                completed_count += 1
                submission_id = str(submission.get("id", ""))
                title = " ".join(str(submission.get("name", "")).split())
                print(f"[{completed_count:,}/{len(changed):,}] {title}")
                try:
                    rendered_tracks = future.result()
                    count = _apply_rendered_submission(
                        output,
                        submission_id,
                        rendered_tracks,
                    )
                    successful_changes += 1
                    print(
                        f"  Added {count} SPC preview"
                        f"{'s' if count != 1 else ''}."
                    )
                except Exception as error:
                    failures.append(
                        {
                            "submission_id": submission_id,
                            "title": title,
                            "error": str(error),
                        }
                    )
                    print(f"  Skipped: {error}")
                    if arguments.strict:
                        raise
                if completed_count % 25 == 0:
                    _checkpoint_database(output)
                submit_next()
    except BaseException:
        for future in pending:
            future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        raise
    else:
        executor.shutdown(wait=True)
    index_version = str(
        arguments.index_version
        or (
            _utc_version()
            if successful_changes
            else previous_index_metadata.get("index_version", "") or _utc_version()
        )
    )
    catalog_updated_at = max(
        (int(item.get("time", 0) or 0) for item in submissions), default=0
    )
    music_index.update_music_index_metadata(
        output,
        {
            "schema_version": music_index.INDEX_SCHEMA_VERSION,
            "fingerprint_algorithm": music_index.FINGERPRINT_ALGORITHM,
            "index_version": index_version,
            "catalog_updated_at": str(catalog_updated_at),
            "catalog_complete": "1" if catalog_complete else "0",
        },
    )
    _checkpoint_database(output)
    manifest = music_index.write_index_manifest(
        output,
        Path(arguments.manifest).resolve(),
        download_url=str(arguments.download_url),
        index_version=index_version,
    )
    if arguments.base_index or arguments.incremental_output:
        if not all(
            (
                arguments.base_index,
                arguments.incremental_output,
                arguments.incremental_download_url,
            )
        ):
            raise RuntimeError(
                "--base-index, --incremental-output, and "
                "--incremental-download-url must be used together."
            )
        incremental_output = Path(arguments.incremental_output).resolve()
        try:
            incremental = music_index.create_incremental_music_update(
                Path(arguments.base_index).resolve(),
                output,
                incremental_output,
            )
        except music_index.MusicIndexError as error:
            if "no new or changed songs" not in str(error).casefold():
                raise
            incremental_output.unlink(missing_ok=True)
        else:
            manifest["incremental_update"] = {
                "base_index_version": str(
                    incremental["base_index_version"]
                ),
                "index_version": str(incremental["index_version"]),
                "catalog_updated_at": str(
                    incremental.get("catalog_updated_at", "")
                ),
                "submission_count": int(incremental["submission_count"]),
                "deleted_submission_count": int(
                    incremental["deleted_submission_count"]
                ),
                "track_count": int(incremental["track_count"]),
                "size_bytes": int(incremental["size_bytes"]),
                "sha256": str(incremental["sha256"]),
                "download_url": str(arguments.incremental_download_url),
            }
            _atomic_bytes(
                Path(arguments.manifest).resolve(),
                (
                    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
                ).encode("utf-8"),
            )
            print(
                "Incremental update: "
                f"{incremental['submission_count']:,} changed submission(s), "
                f"{incremental['track_count']:,} track(s), "
                f"{incremental['size_bytes'] / (1024 * 1024):.1f} MB."
            )
    if failures:
        failure_path = cache_dir / "last-failures.json"
        _atomic_bytes(
            failure_path,
            (json.dumps(failures, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
    print(
        f"Finished: {manifest['track_count']:,} tracks, "
        f"{manifest['size_bytes'] / (1024 * 1024):.1f} MB, "
        f"{len(failures):,} skipped."
    )
    return manifest


def parse_arguments(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--renderer")
    parser.add_argument("--fpcalc")
    parser.add_argument("--index-version")
    parser.add_argument("--download-url", required=True)
    parser.add_argument("--base-index")
    parser.add_argument("--incremental-output")
    parser.add_argument("--incremental-download-url")
    parser.add_argument("--full-catalog", action="store_true")
    parser.add_argument("--max-submissions", type=int, default=0)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    # Historical SMW Central titles include characters outside the active
    # Windows console code page. Progress reporting must never stop a valid,
    # resumable index build just because one title cannot be displayed.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass
    try:
        build_index(parse_arguments(argv))
    except KeyboardInterrupt:
        print("Index build stopped; completed submissions are safely cached.")
        return 130
    except Exception as error:
        print(f"Index build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
