import test from "node:test";
import assert from "node:assert/strict";

import {
  chromaprintAlignedDistance,
  cloudCatalogUpdatedAt,
  validateCatalogUpdateDocument,
  validateContribution,
  validateMusicMatchDocument,
} from "../src/index.js";

test("catalog status derives a UTC cloud time for catalogs uploaded before tracking", () => {
  assert.equal(
    cloudCatalogUpdatedAt({ index_version: "20260831012233" }),
    "2026-08-31T01:22:33Z",
  );
  assert.equal(
    cloudCatalogUpdatedAt({
      index_version: "20260831012233",
      cloud_updated_at: "2026-08-31T01:25:10.000Z",
    }),
    "2026-08-31T01:25:10.000Z",
  );
});

function validContribution() {
  return {
    schema_version: 1,
    user_confirmed: true,
    track_key: "a".repeat(64),
    submission_id: "12345",
    client_id_hash: "b".repeat(64),
    fingerprint_sha256: "c".repeat(64),
    fingerprint_base64: "AQIDBA==",
    value_count: 80,
    local_confidence: 94,
    catalog_version: "20260827",
    app_version: "2.2.0",
  };
}

test("accepts an explicitly confirmed, bounded fingerprint", () => {
  assert.equal(validateContribution(validContribution()), "");
});

test("rejects automatic matches that the user did not confirm", () => {
  const contribution = validContribution();
  contribution.user_confirmed = false;
  assert.match(validateContribution(contribution), /explicitly confirmed/i);
});

test("rejects weak local matches and oversized fingerprints", () => {
  const weak = validContribution();
  weak.local_confidence = 52;
  assert.match(validateContribution(weak), /not confident enough/i);

  const oversized = validContribution();
  oversized.fingerprint_base64 = "A".repeat(160 * 1024 + 4);
  assert.match(validateContribution(oversized), /fingerprint payload/i);
});

test("accepts a bounded SMW Central acoustic match request", () => {
  const document = {
    schema_version: 1,
    catalog: "smwcentral",
    fingerprint_values: Array.from({ length: 80 }, (_, index) => index >>> 0),
    limit: 3,
  };
  assert.equal(validateMusicMatchDocument(document), "");
  document.catalog = "other";
  assert.match(validateMusicMatchDocument(document), /SMW Central/i);
});

test("requires one continuous time alignment while trimming brief noise", () => {
  const reference = Array.from(
    { length: 180 },
    (_, index) => ((index * 2654435761) ^ (index << 11)) >>> 0,
  );
  const query = reference.slice(52, 142);
  for (let index = 10; index < 18; index += 1) {
    query[index] = (~query[index]) >>> 0;
  }
  const measured = chromaprintAlignedDistance(query, reference, 52);
  assert.ok(measured);
  assert.equal(measured.overlap, query.length);
  assert.ok(measured.distance < 0.02);
  assert.equal(chromaprintAlignedDistance(query, reference, -120), null);
});

test("accepts bounded fingerprint-only catalog refresh operations", () => {
  const begin = {
    schema_version: 1,
    catalog: "smwcentral",
    operation: "begin_submission",
    submission_id: "7303",
    track_ids: [25],
  };
  assert.equal(validateCatalogUpdateDocument(begin), "");
  const track = {
    ...begin,
    operation: "upsert_track",
    track: {
      track_id: 25,
      track_key: "d".repeat(64),
      submission_id: "7303",
      spc_filename: "song.spc",
      title: "Song",
      artist: "Porter",
      submission_url: "https://www.smwcentral.net/",
      download_url: "https://www.smwcentral.net/",
      fingerprint_base64: "AQIDBA==",
      token_postings_base64: "AQAAAAAAAAA=",
    },
  };
  assert.equal(validateCatalogUpdateDocument(track), "");
  track.track.submission_id = "different";
  assert.match(validateCatalogUpdateDocument(track), /identity/i);
});
