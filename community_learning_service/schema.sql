CREATE TABLE IF NOT EXISTS service_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO service_metadata(key, value) VALUES('model_revision', '0');

CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_key TEXT NOT NULL,
    submission_id TEXT NOT NULL,
    fingerprint_sha256 TEXT NOT NULL,
    fingerprint_base64 TEXT NOT NULL,
    value_count INTEGER NOT NULL,
    client_id_hash TEXT NOT NULL,
    catalog_version TEXT NOT NULL,
    app_version TEXT NOT NULL,
    local_confidence REAL NOT NULL,
    created_at TEXT NOT NULL,
    revoked INTEGER NOT NULL DEFAULT 0,
    UNIQUE(track_key, fingerprint_sha256, client_id_hash)
);

CREATE INDEX IF NOT EXISTS contributions_track_idx
    ON contributions(track_key, revoked, local_confidence);
CREATE INDEX IF NOT EXISTS contributions_client_idx
    ON contributions(client_id_hash, created_at);
CREATE INDEX IF NOT EXISTS contributions_revision_idx
    ON contributions(id);

CREATE TABLE IF NOT EXISTS revoked_tracks (
    track_key TEXT PRIMARY KEY,
    reason TEXT NOT NULL DEFAULT '',
    revoked_at TEXT NOT NULL
);

-- Shared SMW Central recognition catalog. The BLOBs contain only one-way
-- acoustic fingerprints and compact (track id, frame) posting pairs. Raw SPC
-- audio and user recordings are never stored by the service.
CREATE TABLE IF NOT EXISTS music_catalog_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS music_reference_tracks (
    track_id INTEGER PRIMARY KEY,
    track_key TEXT NOT NULL UNIQUE,
    submission_id TEXT NOT NULL,
    spc_filename TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    artist TEXT NOT NULL DEFAULT '',
    submission_url TEXT NOT NULL DEFAULT '',
    download_url TEXT NOT NULL DEFAULT '',
    value_count INTEGER NOT NULL,
    fingerprint BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS music_reference_submission_idx
    ON music_reference_tracks(submission_id);

-- Fingerprints are split into small statements for reliable D1 imports. The
-- empty fingerprint column above is retained for schema compatibility with
-- the first recognition-catalog rollout.
CREATE TABLE IF NOT EXISTS music_reference_fingerprint_chunks (
    track_id INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    fingerprint BLOB NOT NULL,
    PRIMARY KEY(track_id, chunk_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS music_token_postings (
    token INTEGER PRIMARY KEY,
    posting_count INTEGER NOT NULL,
    postings BLOB NOT NULL
);

-- Chunked v2 storage keeps every D1 import statement comfortably below the
-- service limit even for silence-like tokens shared by many songs. The older
-- table remains untouched so a schema rollout never destroys a live catalog.
CREATE TABLE IF NOT EXISTS music_token_posting_chunks (
    token INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    posting_count INTEGER NOT NULL,
    total_posting_count INTEGER NOT NULL,
    postings BLOB NOT NULL,
    PRIMARY KEY(token, chunk_id)
) WITHOUT ROWID;

-- Incremental catalog refreshes leave the large immutable base posting table
-- in place. Tracks listed here have newer overlay postings (or were deleted),
-- so their old packed base postings are ignored by the matcher.
CREATE TABLE IF NOT EXISTS music_replaced_tracks (
    track_id INTEGER PRIMARY KEY,
    submission_id TEXT NOT NULL,
    replaced_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS music_replaced_submission_idx
    ON music_replaced_tracks(submission_id);

CREATE TABLE IF NOT EXISTS music_token_overlay_entries (
    token INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    frame INTEGER NOT NULL,
    PRIMARY KEY(token, track_id, frame)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS music_token_overlay_track_idx
    ON music_token_overlay_entries(track_id);
