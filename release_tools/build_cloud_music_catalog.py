"""Export the complete local SMW Central fingerprint catalog for D1.

The generated SQL contains no audio. Each reference fingerprint is a sequence
of 32-bit Chromaprint values, and each token posting is a packed little-endian
``(track_id, frame)`` pair used for Shazam-style inverted lookup.
"""

from __future__ import annotations

import argparse
from array import array
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import struct
import sys
import time
import zlib


MAXIMUM_SQL_BLOB_BYTES = 2 * 1024

def _sql_text(value: object) -> str:
    return "'" + str(value or "").replace("'", "''") + "'"


def _blob_literal(payload: bytes) -> str:
    return "X'" + bytes(payload).hex() + "'"


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


def export_catalog(index_path: Path, sql_path: Path) -> dict[str, object]:
    index_path = Path(index_path).resolve()
    sql_path = Path(sql_path).resolve()
    sql_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(index_path)) as connection:
        connection.row_factory = sqlite3.Row
        metadata = {
            str(row["key"]): str(row["value"])
            for row in connection.execute("SELECT key, value FROM metadata")
        }
        tracks = connection.execute(
            """
            SELECT tracks.id, tracks.track_key, tracks.submission_id,
                   tracks.spc_filename, tracks.title, tracks.author,
                   tracks.submission_url, tracks.download_url,
                   chromaprint_data.value_count, chromaprint_data.fingerprint
            FROM tracks
            JOIN chromaprint_data ON chromaprint_data.track_id = tracks.id
            ORDER BY tracks.id
            """
        ).fetchall()
        if not tracks:
            raise RuntimeError("The source index has no Chromaprint tracks.")
        maximum_track_id = max(int(row["id"]) for row in tracks)
        maximum_frame = int(
            connection.execute(
                "SELECT COALESCE(MAX(frame), 0) FROM chromaprint_tokens"
            ).fetchone()[0]
        )
        if maximum_track_id > 0xFFFF or maximum_frame > 0xFFFF:
            raise RuntimeError(
                "The compact cloud posting format needs wider identifiers."
            )

        raw_fingerprint_bytes = 0
        posting_count = 0
        token_count = 0
        with sql_path.open("w", encoding="utf-8", newline="\n") as output:
            output.write("DELETE FROM music_token_overlay_entries;\n")
            output.write("DELETE FROM music_replaced_tracks;\n")
            output.write("DELETE FROM music_token_posting_chunks;\n")
            output.write("DELETE FROM music_reference_fingerprint_chunks;\n")
            output.write("DELETE FROM music_reference_tracks;\n")
            output.write("DELETE FROM music_catalog_metadata;\n")
            for key, value in (
                ("schema_version", "1"),
                ("catalog", "smwcentral"),
                ("index_version", metadata.get("index_version", "")),
                ("catalog_updated_at", metadata.get("catalog_updated_at", "")),
                ("track_count", str(len(tracks))),
            ):
                output.write(
                    "INSERT INTO music_catalog_metadata(key,value) VALUES("
                    f"{_sql_text(key)},{_sql_text(value)});\n"
                )
            for row in tracks:
                raw = _raw_fingerprint(
                    bytes(row["fingerprint"]),
                    int(row["value_count"]),
                )
                raw_fingerprint_bytes += len(raw)
                fields = (
                    str(int(row["id"])),
                    _sql_text(row["track_key"]),
                    _sql_text(row["submission_id"]),
                    _sql_text(row["spc_filename"]),
                    _sql_text(row["title"]),
                    _sql_text(row["author"]),
                    _sql_text(row["submission_url"]),
                    _sql_text(row["download_url"]),
                    str(int(row["value_count"])),
                    "X''",
                )
                output.write(
                    "INSERT INTO music_reference_tracks("
                    "track_id,track_key,submission_id,spc_filename,title,artist,"
                    "submission_url,download_url,value_count,fingerprint) VALUES("
                    + ",".join(fields)
                    + ");\n"
                )
                for chunk_id, start in enumerate(
                    range(0, len(raw), MAXIMUM_SQL_BLOB_BYTES)
                ):
                    output.write(
                        "INSERT INTO music_reference_fingerprint_chunks("
                        "track_id,chunk_id,fingerprint) VALUES("
                        f"{int(row['id'])},{chunk_id},"
                        f"{_blob_literal(raw[start:start + MAXIMUM_SQL_BLOB_BYTES])});\n"
                    )

            token_rows = connection.execute(
                "SELECT DISTINCT token FROM chromaprint_tokens ORDER BY token"
            ).fetchall()
            for token_row in token_rows:
                token = int(token_row[0])
                packed = bytearray()
                for posting in connection.execute(
                    "SELECT track_id, frame FROM chromaprint_tokens "
                    "WHERE token = ? ORDER BY track_id, frame",
                    (token,),
                ):
                    packed.extend(
                        struct.pack("<HH", int(posting[0]), int(posting[1]))
                    )
                count = len(packed) // 4
                posting_count += count
                token_count += 1
                for chunk_id, start in enumerate(
                    range(0, len(packed), MAXIMUM_SQL_BLOB_BYTES)
                ):
                    chunk = packed[start : start + MAXIMUM_SQL_BLOB_BYTES]
                    chunk_count = len(chunk) // 4
                    output.write(
                        "INSERT INTO music_token_posting_chunks("
                        "token,chunk_id,posting_count,total_posting_count,postings) "
                        f"VALUES({token},{chunk_id},{chunk_count},{count},"
                        f"{_blob_literal(chunk)});\n"
                    )
            output.write("PRAGMA optimize;\n")

    return {
        "schema_version": 1,
        "catalog": "smwcentral",
        "index_version": metadata.get("index_version", ""),
        "track_count": len(tracks),
        "token_count": token_count,
        "posting_count": posting_count,
        "fingerprint_bytes": raw_fingerprint_bytes,
        "sql_bytes": sql_path.stat().st_size,
        "generated_at": int(time.time()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    arguments = parser.parse_args()
    details = export_catalog(arguments.index, arguments.output)
    if arguments.manifest:
        arguments.manifest.parent.mkdir(parents=True, exist_ok=True)
        arguments.manifest.write_text(
            json.dumps(details, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(details, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
