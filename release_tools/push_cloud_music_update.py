"""Publish only new, changed, or deleted SMW Central fingerprints to D1.

The updater never uploads SPC files or recorded audio. It sends the same
non-reconstructive Chromaprint values and lookup tokens used by the desktop
application's local index.
"""

from __future__ import annotations

import argparse
from array import array
import base64
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import struct
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zlib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import smwc_music_index as music_index


DEFAULT_ENDPOINT = (
    "https://smw-stream-tracker-community-learning."
    "smw-stream-tracker-community-learning.workers.dev/v1/admin/music/catalog"
)
USER_AGENT = "SMW-Stream-Tracker-Catalog-Publisher/1.0"


def _metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return {
        str(row[0]): str(row[1])
        for row in connection.execute("SELECT key, value FROM metadata")
    }


def _raw_fingerprint(payload: bytes, expected_count: int) -> bytes:
    raw = zlib.decompress(bytes(payload))
    if len(raw) != int(expected_count) * 4:
        raise RuntimeError("A reference fingerprint has an invalid length.")
    if sys.byteorder == "little":
        return raw
    values = array("I")
    values.frombytes(raw)
    values.byteswap()
    return values.tobytes()


def _postings(connection: sqlite3.Connection, track_id: int) -> bytes:
    payload = bytearray()
    for row in connection.execute(
        "SELECT token, frame FROM chromaprint_tokens "
        "WHERE track_id = ? ORDER BY frame, token",
        (int(track_id),),
    ):
        payload.extend(struct.pack("<II", int(row[0]), int(row[1])))
    if not payload:
        raise RuntimeError(f"Track {track_id} has no Chromaprint token postings.")
    return bytes(payload)


def _request(endpoint: str, token: str, document: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(document, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(5):
        request = Request(
            endpoint,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=90) as response:
                result = json.loads(response.read(1024 * 1024).decode("utf-8"))
            if not isinstance(result, dict) or result.get("ok") is not True:
                raise RuntimeError("The cloud catalog rejected an update operation.")
            return result
        except HTTPError as error:
            message = error.read(16 * 1024).decode("utf-8", "replace")
            if error.code not in {429, 500, 502, 503, 504}:
                raise RuntimeError(
                    f"The cloud catalog returned HTTP {error.code}: {message}"
                ) from error
            last_error = error
        except (URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as error:
            last_error = error
        if attempt < 4:
            time.sleep(2 ** attempt)
    raise RuntimeError("The cloud catalog update did not complete after retries.") from last_error


def _track_document(
    connection: sqlite3.Connection,
    track: sqlite3.Row,
) -> dict[str, Any]:
    chromaprint = connection.execute(
        "SELECT value_count, fingerprint FROM chromaprint_data WHERE track_id = ?",
        (int(track["id"]),),
    ).fetchone()
    if chromaprint is None:
        raise RuntimeError(f"Track {track['id']} has no Chromaprint fingerprint.")
    fingerprint = _raw_fingerprint(
        bytes(chromaprint["fingerprint"]),
        int(chromaprint["value_count"]),
    )
    postings = _postings(connection, int(track["id"]))
    return {
        "track_id": int(track["id"]),
        "track_key": str(track["track_key"]),
        "submission_id": str(track["submission_id"]),
        "spc_filename": str(track["spc_filename"] or ""),
        "title": str(track["title"] or ""),
        "artist": str(track["author"] or ""),
        "submission_url": str(track["submission_url"] or ""),
        "download_url": str(track["download_url"] or ""),
        "fingerprint_base64": base64.b64encode(fingerprint).decode("ascii"),
        "token_postings_base64": base64.b64encode(postings).decode("ascii"),
    }


def publish(
    index_path: Path,
    *,
    endpoint: str,
    token: str,
    submission_ids: list[str],
    deleted_submission_ids: list[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    endpoint = str(endpoint).strip()
    if not endpoint.lower().startswith("https://"):
        raise RuntimeError("The cloud catalog endpoint must use HTTPS.")
    updated_tracks = 0
    with closing(sqlite3.connect(index_path)) as connection:
        connection.row_factory = sqlite3.Row
        metadata = _metadata(connection)
        for submission_id in submission_ids:
            tracks = connection.execute(
                "SELECT * FROM tracks WHERE submission_id = ? ORDER BY id",
                (str(submission_id),),
            ).fetchall()
            if not tracks:
                raise RuntimeError(f"Changed submission {submission_id} has no tracks.")
            if not dry_run:
                _request(endpoint, token, {
                    "schema_version": 1,
                    "catalog": "smwcentral",
                    "operation": "begin_submission",
                    "submission_id": str(submission_id),
                    "track_ids": [int(track["id"]) for track in tracks],
                })
            for track in tracks:
                document = _track_document(connection, track)
                if not dry_run:
                    _request(endpoint, token, {
                        "schema_version": 1,
                        "catalog": "smwcentral",
                        "operation": "upsert_track",
                        "submission_id": str(submission_id),
                        "track": document,
                    })
                updated_tracks += 1
        for submission_id in deleted_submission_ids:
            if not dry_run:
                _request(endpoint, token, {
                    "schema_version": 1,
                    "catalog": "smwcentral",
                    "operation": "delete_submission",
                    "submission_id": str(submission_id),
                })
        if not dry_run:
            _request(endpoint, token, {
                "schema_version": 1,
                "catalog": "smwcentral",
                "operation": "finish",
                "index_version": metadata.get("index_version", ""),
                "catalog_updated_at": metadata.get("catalog_updated_at", ""),
            })
    return {
        "ok": True,
        "index_version": metadata.get("index_version", ""),
        "updated_submissions": len(submission_ids),
        "updated_tracks": updated_tracks,
        "deleted_submissions": len(deleted_submission_ids),
        "fingerprints_only": True,
        "raw_audio_uploaded": False,
        "dry_run": bool(dry_run),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--update", type=Path)
    source.add_argument("--index", type=Path)
    parser.add_argument("--submission-id", action="append", default=[])
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--token-env", default="MUSIC_CATALOG_UPDATE_TOKEN")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()

    deleted_submission_ids: list[str] = []
    if arguments.update:
        details = music_index.validate_incremental_music_update(arguments.update)
        index_path = arguments.update
        submission_ids = list(details["changed_submission_ids"])
        deleted_submission_ids = list(details["deleted_submission_ids"])
    else:
        music_index.validate_music_index(arguments.index, require_tracks=True)
        index_path = arguments.index
        submission_ids = [str(value).strip() for value in arguments.submission_id if str(value).strip()]
        if not submission_ids:
            parser.error("--index requires at least one --submission-id")

    token = str(os.environ.get(arguments.token_env, "")).strip()
    if not token and not arguments.dry_run:
        raise RuntimeError(f"The {arguments.token_env} secret is not available.")
    result = publish(
        index_path,
        endpoint=arguments.endpoint,
        token=token,
        submission_ids=submission_ids,
        deleted_submission_ids=deleted_submission_ids,
        dry_run=arguments.dry_run,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
