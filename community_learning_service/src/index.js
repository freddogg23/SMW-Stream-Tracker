const API_SCHEMA_VERSION = 1;
const MINIMUM_INDEPENDENT_CONFIRMERS = 3;
const MINIMUM_LOCAL_CONFIDENCE = 78;
const MAXIMUM_BODY_BYTES = 192 * 1024;
const MAXIMUM_FINGERPRINT_BASE64 = 160 * 1024;
const DEFAULT_PAGE_SIZE = 200;
const MAXIMUM_PAGE_SIZE = 400;
const MAXIMUM_MATCH_BODY_BYTES = 64 * 1024;
const MAXIMUM_CATALOG_UPDATE_BODY_BYTES = 512 * 1024;
const MAXIMUM_CATALOG_FINGERPRINT_BASE64 = 256 * 1024;
const MAXIMUM_CATALOG_POSTINGS_BASE64 = 256 * 1024;
const MINIMUM_MATCH_VALUES = 40;
const MAXIMUM_MATCH_VALUES = 4096;
const CHROMAPRINT_TOKEN_SHIFT = 20;
const CHROMAPRINT_MAXIMUM_DISTANCE = 0.24;
const CHROMAPRINT_RUNNER_SEPARATION = 0.025;
const CHROMAPRINT_FRAME_SECONDS = 4096 / 3 / 11025;
const MATCH_TOKEN_QUERY_CHUNK = 70;
const MATCH_INFORMATIVE_TOKEN_LIMIT = 24;
const MATCH_MAXIMUM_POSTINGS_PER_TOKEN = 12000;
const MATCH_CANDIDATE_LIMIT = 48;

const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, authorization",
  "access-control-allow-methods": "GET, POST, OPTIONS",
};

function jsonResponse(value, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { ...jsonHeaders, ...extraHeaders },
  });
}

function text(value) {
  return String(value ?? "").trim();
}

export function cloudCatalogUpdatedAt(catalog) {
  const recorded = text(catalog?.cloud_updated_at);
  if (recorded) {
    return recorded;
  }
  const version = text(catalog?.index_version);
  if (!/^\d{14}$/.test(version)) {
    return "";
  }
  return (
    `${version.slice(0, 4)}-${version.slice(4, 6)}-${version.slice(6, 8)}`
    + `T${version.slice(8, 10)}:${version.slice(10, 12)}:${version.slice(12, 14)}Z`
  );
}

function isHex(value, length) {
  return new RegExp(`^[0-9a-f]{${length}}$`, "i").test(text(value));
}

function validBase64(value) {
  const normalized = text(value);
  return (
    normalized.length > 0 &&
    normalized.length <= MAXIMUM_FINGERPRINT_BASE64 &&
    normalized.length % 4 === 0 &&
    /^[A-Za-z0-9+/]+={0,2}$/.test(normalized)
  );
}

function validBoundedBase64(value, maximumLength) {
  const normalized = text(value);
  return (
    normalized.length > 0
    && normalized.length <= maximumLength
    && normalized.length % 4 === 0
    && /^[A-Za-z0-9+/]+={0,2}$/.test(normalized)
  );
}

function decodeBase64(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function hexDigest(bytes) {
  return crypto.subtle.digest("SHA-256", bytes).then((digest) =>
    Array.from(new Uint8Array(digest), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join(""),
  );
}

function boundedInteger(value, minimum, maximum, fallback) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed)) return fallback;
  return Math.max(minimum, Math.min(maximum, parsed));
}

function chunks(values, size) {
  const result = [];
  for (let index = 0; index < values.length; index += size) {
    result.push(values.slice(index, index + size));
  }
  return result;
}

function blobBytes(value) {
  if (value instanceof Uint8Array) return value;
  if (value instanceof ArrayBuffer) return new Uint8Array(value);
  if (Array.isArray(value)) return Uint8Array.from(value);
  if (value?.buffer instanceof ArrayBuffer) {
    return new Uint8Array(value.buffer, value.byteOffset ?? 0, value.byteLength);
  }
  return new Uint8Array();
}

function decodeUint32Fingerprint(value) {
  const bytes = blobBytes(value);
  if (!bytes.length || bytes.length % 4 !== 0) return [];
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const values = new Array(bytes.length / 4);
  for (let index = 0; index < values.length; index += 1) {
    values[index] = view.getUint32(index * 4, true);
  }
  return values;
}

function popcount32(value) {
  let bits = value >>> 0;
  bits -= (bits >>> 1) & 0x55555555;
  bits = (bits & 0x33333333) + ((bits >>> 2) & 0x33333333);
  return (((bits + (bits >>> 4)) & 0x0f0f0f0f) * 0x01010101) >>> 24;
}

export function chromaprintAlignedDistance(query, reference, offset) {
  const queryStart = Math.max(0, -Number(offset));
  const referenceStart = Math.max(0, Number(offset));
  const overlap = Math.min(
    query.length - queryStart,
    reference.length - referenceStart,
  );
  const minimumOverlap = Math.max(
    MINIMUM_MATCH_VALUES,
    Math.ceil(query.length * 0.68),
  );
  if (overlap < minimumOverlap) return null;

  // A 33-bin histogram produces the same 15%-trimmed Hamming distance as
  // sorting every frame, with predictable CPU usage in a Worker.
  const histogram = new Uint32Array(33);
  for (let position = 0; position < overlap; position += 1) {
    const difference = (
      (query[queryStart + position] >>> 0)
      ^ (reference[referenceStart + position] >>> 0)
    ) >>> 0;
    histogram[popcount32(difference)] += 1;
  }
  let remaining = Math.max(minimumOverlap, Math.round(overlap * 0.85));
  const keptCount = remaining;
  let totalBits = 0;
  for (let distance = 0; distance <= 32 && remaining > 0; distance += 1) {
    const take = Math.min(remaining, histogram[distance]);
    totalBits += take * distance;
    remaining -= take;
  }
  return { distance: totalBits / (32 * keptCount), overlap };
}

export function validateMusicMatchDocument(document) {
  if (!document || typeof document !== "object" || Array.isArray(document)) {
    return "The match request must be a JSON object.";
  }
  if (document.schema_version !== API_SCHEMA_VERSION) {
    return "Unsupported match schema.";
  }
  if (document.catalog !== "smwcentral") {
    return "Only the SMW Central music catalog is supported.";
  }
  if (!Array.isArray(document.fingerprint_values)) {
    return "The acoustic fingerprint is missing.";
  }
  if (
    document.fingerprint_values.length < MINIMUM_MATCH_VALUES
    || document.fingerprint_values.length > MAXIMUM_MATCH_VALUES
  ) {
    return "The acoustic fingerprint length is invalid.";
  }
  if (document.fingerprint_values.some((value) => (
    !Number.isInteger(value) || value < 0 || value > 0xffffffff
  ))) {
    return "The acoustic fingerprint contains invalid values.";
  }
  return "";
}

async function secureTokenEqual(expected, provided) {
  if (!expected || !provided) return false;
  const encoder = new TextEncoder();
  const [expectedHash, providedHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(expected)),
    crypto.subtle.digest("SHA-256", encoder.encode(provided)),
  ]);
  const left = new Uint8Array(expectedHash);
  const right = new Uint8Array(providedHash);
  let difference = 0;
  for (let index = 0; index < left.length; index += 1) {
    difference |= left[index] ^ right[index];
  }
  return difference === 0;
}

async function executeStatementBatches(database, statements, batchSize = 80) {
  const results = [];
  for (const statementChunk of chunks(statements, batchSize)) {
    results.push(...await database.batch(statementChunk));
  }
  return results;
}

async function readBoundedJson(request, maximumBytes, label) {
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > maximumBytes) {
    throw new RangeError(`${label} is too large.`);
  }
  const body = await request.arrayBuffer();
  if (body.byteLength > maximumBytes) {
    throw new RangeError(`${label} is too large.`);
  }
  try {
    return JSON.parse(new TextDecoder().decode(body));
  } catch {
    throw new SyntaxError(`${label} JSON is invalid.`);
  }
}

export function validateCatalogUpdateDocument(document) {
  if (!document || typeof document !== "object" || Array.isArray(document)) {
    return "The catalog update must be a JSON object.";
  }
  if (document.schema_version !== API_SCHEMA_VERSION || document.catalog !== "smwcentral") {
    return "Unsupported catalog update schema.";
  }
  const operation = text(document.operation);
  if (!["begin_submission", "upsert_track", "delete_submission", "finish"].includes(operation)) {
    return "The catalog update operation is invalid.";
  }
  if (operation === "finish") {
    if (!text(document.index_version) || text(document.index_version).length > 80) {
      return "The catalog version is invalid.";
    }
    if (text(document.catalog_updated_at).length > 80) {
      return "The catalog update time is invalid.";
    }
    return "";
  }
  if (!text(document.submission_id) || text(document.submission_id).length > 80) {
    return "The SMW Central submission ID is invalid.";
  }
  if (operation === "begin_submission") {
    if (!Array.isArray(document.track_ids) || document.track_ids.length > 2048) {
      return "The replacement track list is invalid.";
    }
    if (document.track_ids.some((value) => !Number.isInteger(value) || value < 1 || value > 0x7fffffff)) {
      return "The replacement track list contains an invalid ID.";
    }
    return "";
  }
  if (operation === "delete_submission") return "";
  const track = document.track;
  if (!track || typeof track !== "object" || Array.isArray(track)) {
    return "The replacement track is missing.";
  }
  if (!Number.isInteger(track.track_id) || track.track_id < 1 || track.track_id > 0x7fffffff) {
    return "The replacement track ID is invalid.";
  }
  if (!isHex(track.track_key, 64) || text(track.submission_id) !== text(document.submission_id)) {
    return "The replacement track identity is invalid.";
  }
  for (const [field, maximum] of [
    ["spc_filename", 512], ["title", 1024], ["artist", 1024],
    ["submission_url", 2048], ["download_url", 2048],
  ]) {
    if (text(track[field]).length > maximum) return `The replacement track ${field} is invalid.`;
  }
  if (!text(track.title)) return "The replacement track title is missing.";
  if (!validBoundedBase64(track.fingerprint_base64, MAXIMUM_CATALOG_FINGERPRINT_BASE64)) {
    return "The replacement fingerprint is invalid.";
  }
  if (!validBoundedBase64(track.token_postings_base64, MAXIMUM_CATALOG_POSTINGS_BASE64)) {
    return "The replacement token postings are invalid.";
  }
  return "";
}

export function validateContribution(document) {
  if (!document || typeof document !== "object" || Array.isArray(document)) {
    return "The contribution must be a JSON object.";
  }
  if (document.schema_version !== API_SCHEMA_VERSION) {
    return "Unsupported contribution schema.";
  }
  if (document.user_confirmed !== true) {
    return "Only explicitly confirmed matches may be contributed.";
  }
  if (!isHex(document.track_key, 64)) {
    return "The track key is invalid.";
  }
  if (!text(document.submission_id) || text(document.submission_id).length > 80) {
    return "The SMW Central submission ID is invalid.";
  }
  if (!isHex(document.client_id_hash, 64)) {
    return "The anonymous installation identifier is invalid.";
  }
  if (!isHex(document.fingerprint_sha256, 64)) {
    return "The fingerprint checksum is invalid.";
  }
  if (!validBase64(document.fingerprint_base64)) {
    return "The fingerprint payload is invalid.";
  }
  const valueCount = Number(document.value_count);
  if (!Number.isInteger(valueCount) || valueCount < 40 || valueCount > 4096) {
    return "The fingerprint length is invalid.";
  }
  const confidence = Number(document.local_confidence);
  if (!Number.isFinite(confidence) || confidence < MINIMUM_LOCAL_CONFIDENCE || confidence > 100) {
    return "The local match was not confident enough to contribute.";
  }
  if (text(document.catalog_version).length > 80 || text(document.app_version).length > 40) {
    return "Version information is invalid.";
  }
  return "";
}

async function currentRevision(env) {
  const row = await env.DB.prepare(
    "SELECT value FROM service_metadata WHERE key = 'model_revision'",
  ).first();
  return Number.parseInt(row?.value ?? "0", 10) || 0;
}

async function acceptedModelCount(env) {
  const row = await env.DB.prepare(
    `WITH eligible_tracks AS (
       SELECT track_key
       FROM contributions
       WHERE revoked = 0 AND local_confidence >= ?
       GROUP BY track_key
       HAVING COUNT(DISTINCT client_id_hash) >= ?
     )
     SELECT COUNT(*) AS count
     FROM contributions c
     JOIN eligible_tracks e ON e.track_key = c.track_key
     LEFT JOIN revoked_tracks r ON r.track_key = c.track_key
     WHERE c.revoked = 0 AND c.local_confidence >= ? AND r.track_key IS NULL`,
  ).bind(
    MINIMUM_LOCAL_CONFIDENCE,
    MINIMUM_INDEPENDENT_CONFIRMERS,
    MINIMUM_LOCAL_CONFIDENCE,
  ).first();
  return Number(row?.count ?? 0);
}

async function handleContribution(request, env) {
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAXIMUM_BODY_BYTES) {
    return jsonResponse({ ok: false, error: "Contribution is too large." }, 413);
  }
  const rateKey = request.headers.get("cf-connecting-ip") || "unknown";
  if (env.LEARNING_RATE_LIMITER) {
    const allowance = await env.LEARNING_RATE_LIMITER.limit({ key: rateKey });
    if (!allowance.success) {
      return jsonResponse({ ok: false, error: "Too many contributions. Try again later." }, 429);
    }
  }
  let document;
  try {
    document = await request.json();
  } catch {
    return jsonResponse({ ok: false, error: "Contribution JSON is invalid." }, 400);
  }
  const validationError = validateContribution(document);
  if (validationError) {
    return jsonResponse({ ok: false, error: validationError }, 400);
  }
  let fingerprintBytes;
  try {
    fingerprintBytes = decodeBase64(document.fingerprint_base64);
  } catch {
    return jsonResponse({ ok: false, error: "Fingerprint encoding is invalid." }, 400);
  }
  const actualDigest = await hexDigest(fingerprintBytes);
  if (actualDigest !== text(document.fingerprint_sha256).toLowerCase()) {
    return jsonResponse({ ok: false, error: "Fingerprint checksum does not match." }, 400);
  }
  const now = new Date().toISOString();
  const insert = await env.DB.prepare(
    `INSERT OR IGNORE INTO contributions(
       track_key, submission_id, fingerprint_sha256, fingerprint_base64,
       value_count, client_id_hash, catalog_version, app_version,
       local_confidence, created_at
     ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).bind(
    text(document.track_key).toLowerCase(),
    text(document.submission_id),
    text(document.fingerprint_sha256).toLowerCase(),
    text(document.fingerprint_base64),
    Number(document.value_count),
    text(document.client_id_hash).toLowerCase(),
    text(document.catalog_version),
    text(document.app_version),
    Number(document.local_confidence),
    now,
  ).run();
  if (Number(insert.meta?.changes ?? 0) > 0) {
    await env.DB.prepare(
      "UPDATE service_metadata SET value = CAST(value AS INTEGER) + 1 WHERE key = 'model_revision'",
    ).run();
  }
  const quorum = await env.DB.prepare(
    `SELECT COUNT(DISTINCT client_id_hash) AS confirmers
     FROM contributions
     WHERE track_key = ? AND revoked = 0 AND local_confidence >= ?`,
  ).bind(text(document.track_key).toLowerCase(), MINIMUM_LOCAL_CONFIDENCE).first();
  const confirmers = Number(quorum?.confirmers ?? 0);
  return jsonResponse({
    ok: true,
    duplicate: Number(insert.meta?.changes ?? 0) === 0,
    confirmers,
    promoted: confirmers >= MINIMUM_INDEPENDENT_CONFIRMERS,
    required_confirmers: MINIMUM_INDEPENDENT_CONFIRMERS,
    model_revision: await currentRevision(env),
  }, 202);
}

async function handleManifest(env) {
  const revision = await currentRevision(env);
  const totalExamples = await acceptedModelCount(env);
  return jsonResponse({
    schema_version: API_SCHEMA_VERSION,
    model_revision: revision,
    total_examples: totalExamples,
    page_size: DEFAULT_PAGE_SIZE,
    minimum_independent_confirmers: MINIMUM_INDEPENDENT_CONFIRMERS,
    fingerprints_only: true,
    raw_audio_collected: false,
  }, 200, {
    etag: `"community-model-${revision}"`,
    "cache-control": "public, max-age=300",
  });
}

async function handleModelPage(url, env) {
  const cursor = Math.max(0, Number.parseInt(url.searchParams.get("cursor") || "0", 10) || 0);
  const requestedLimit = Number.parseInt(url.searchParams.get("limit") || String(DEFAULT_PAGE_SIZE), 10);
  const limit = Math.max(1, Math.min(MAXIMUM_PAGE_SIZE, requestedLimit || DEFAULT_PAGE_SIZE));
  const result = await env.DB.prepare(
    `WITH eligible_tracks AS (
       SELECT track_key
       FROM contributions
       WHERE revoked = 0 AND local_confidence >= ?
       GROUP BY track_key
       HAVING COUNT(DISTINCT client_id_hash) >= ?
     )
     SELECT c.id, c.track_key, c.submission_id, c.fingerprint_sha256,
            c.fingerprint_base64, c.value_count, c.catalog_version,
            c.local_confidence
     FROM contributions c
     JOIN eligible_tracks e ON e.track_key = c.track_key
     LEFT JOIN revoked_tracks r ON r.track_key = c.track_key
     WHERE c.id > ? AND c.revoked = 0 AND c.local_confidence >= ?
           AND r.track_key IS NULL
     ORDER BY c.id
     LIMIT ?`,
  ).bind(
    MINIMUM_LOCAL_CONFIDENCE,
    MINIMUM_INDEPENDENT_CONFIRMERS,
    cursor,
    MINIMUM_LOCAL_CONFIDENCE,
    limit + 1,
  ).all();
  const rows = Array.isArray(result.results) ? result.results : [];
  const hasMore = rows.length > limit;
  const examples = rows.slice(0, limit);
  const nextCursor = hasMore && examples.length ? Number(examples[examples.length - 1].id) : null;
  return jsonResponse({
    schema_version: API_SCHEMA_VERSION,
    model_revision: await currentRevision(env),
    examples,
    next_cursor: nextCursor,
  }, 200, { "cache-control": "public, max-age=300" });
}

async function readBoundedMatchDocument(request) {
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAXIMUM_MATCH_BODY_BYTES) {
    throw new RangeError("The match request is too large.");
  }
  const body = await request.arrayBuffer();
  if (body.byteLength > MAXIMUM_MATCH_BODY_BYTES) {
    throw new RangeError("The match request is too large.");
  }
  try {
    return JSON.parse(new TextDecoder().decode(body));
  } catch {
    throw new SyntaxError("The match request JSON is invalid.");
  }
}

function strongestCandidateOffsets(offsetVotes) {
  const byTrack = new Map();
  for (const [key, votes] of offsetVotes.entries()) {
    const separator = key.indexOf(":");
    const trackId = Number(key.slice(0, separator));
    const offset = Number(key.slice(separator + 1));
    if (!byTrack.has(trackId)) byTrack.set(trackId, []);
    byTrack.get(trackId).push({ votes, offset });
  }
  for (const candidates of byTrack.values()) {
    candidates.sort((left, right) => right.votes - left.votes);
    const selected = [];
    for (const candidate of candidates) {
      if (selected.some((existing) => Math.abs(existing.offset - candidate.offset) <= 2)) {
        continue;
      }
      selected.push(candidate);
      if (selected.length >= 5) break;
    }
    candidates.splice(0, candidates.length, ...selected);
  }
  return new Map(
    Array.from(byTrack.entries())
      .filter(([, candidates]) => candidates.length)
      .sort((left, right) => right[1][0].votes - left[1][0].votes)
      .slice(0, MATCH_CANDIDATE_LIMIT),
  );
}

function scoreReferenceTracks(query, trackRows, candidateOffsets) {
  const scored = [];
  for (const row of trackRows) {
    const trackId = Number(row.track_id);
    const reference = decodeUint32Fingerprint(row.fingerprint);
    if (reference.length !== Number(row.value_count)) continue;
    let best = null;
    for (const suggested of candidateOffsets.get(trackId) ?? []) {
      for (let adjustment = -4; adjustment <= 4; adjustment += 1) {
        const offset = suggested.offset + adjustment;
        const measured = chromaprintAlignedDistance(query, reference, offset);
        if (!measured) continue;
        const candidate = {
          distance: measured.distance,
          overlap: measured.overlap,
          offset,
          row,
        };
        if (
          !best
          || candidate.distance < best.distance
          || (
            candidate.distance === best.distance
            && candidate.overlap > best.overlap
          )
        ) {
          best = candidate;
        }
      }
    }
    if (best) scored.push(best);
  }
  scored.sort((left, right) => (
    left.distance - right.distance || right.overlap - left.overlap
  ));
  return scored;
}

function responseMatches(scored, requestedLimit) {
  if (!scored.length || scored[0].distance > CHROMAPRINT_MAXIMUM_DISTANCE) {
    return [];
  }
  const winnerSubmission = text(scored[0].row.submission_id);
  const distinctRunner = scored.find((candidate, index) => (
    index > 0 && text(candidate.row.submission_id) !== winnerSubmission
  ));
  if (
    distinctRunner
    && distinctRunner.distance <= CHROMAPRINT_MAXIMUM_DISTANCE
    && distinctRunner.distance - scored[0].distance < CHROMAPRINT_RUNNER_SEPARATION
  ) {
    return [];
  }
  const winnerDistance = scored[0].distance;
  const winnerSeparation = (
    !distinctRunner || distinctRunner.distance > CHROMAPRINT_MAXIMUM_DISTANCE
      ? 1
      : Math.max(0, Math.min(
        1,
        (distinctRunner.distance - winnerDistance)
          / Math.max(0.001, CHROMAPRINT_MAXIMUM_DISTANCE - winnerDistance),
      ))
  );
  const returnedSubmissions = new Set();
  const matches = [];
  for (const candidate of scored) {
    if (candidate.distance > CHROMAPRINT_MAXIMUM_DISTANCE) continue;
    const row = candidate.row;
    const submissionId = text(row.submission_id);
    if (!submissionId || returnedSubmissions.has(submissionId)) continue;
    const similarity = Math.max(
      0,
      Math.min(1, 1 - candidate.distance / CHROMAPRINT_MAXIMUM_DISTANCE),
    );
    const separation = submissionId === winnerSubmission ? winnerSeparation : 0;
    const confidence = Math.max(
      0,
      Math.min(100, 50 + 40 * Math.sqrt(similarity) + 10 * separation),
    );
    matches.push({
      track_id: Number(row.track_id),
      track_key: text(row.track_key),
      submission_id: submissionId,
      spc_filename: text(row.spc_filename),
      title: text(row.title),
      artist: text(row.artist),
      submission_url: text(row.submission_url),
      download_url: text(row.download_url),
      confidence: Math.round(confidence * 10) / 10,
      audio_distance: Math.round(candidate.distance * 10000) / 10000,
      matching_frames: candidate.overlap,
      offset_seconds: Math.round(
        candidate.offset * CHROMAPRINT_FRAME_SECONDS * 100,
      ) / 100,
    });
    returnedSubmissions.add(submissionId);
    if (matches.length >= requestedLimit) break;
  }
  return matches;
}

async function handleMusicMatch(request, env) {
  const rateKey = request.headers.get("cf-connecting-ip") || "unknown";
  if (env.LEARNING_RATE_LIMITER) {
    const allowance = await env.LEARNING_RATE_LIMITER.limit({
      key: `music:${rateKey}`,
    });
    if (!allowance.success) {
      return jsonResponse({ ok: false, error: "Too many match requests. Try again shortly." }, 429);
    }
  }
  let document;
  try {
    document = await readBoundedMatchDocument(request);
  } catch (error) {
    const tooLarge = error instanceof RangeError;
    return jsonResponse({ ok: false, error: error.message }, tooLarge ? 413 : 400);
  }
  const validationError = validateMusicMatchDocument(document);
  if (validationError) {
    return jsonResponse({ ok: false, error: validationError }, 400);
  }
  const query = document.fingerprint_values.map((value) => Number(value) >>> 0);
  const requestedLimit = boundedInteger(document.limit, 1, 5, 3);
  const queryTimes = new Map();
  for (let frame = 0; frame < query.length; frame += 1) {
    const token = query[frame] >>> CHROMAPRINT_TOKEN_SHIFT;
    if (!queryTimes.has(token)) queryTimes.set(token, []);
    queryTimes.get(token).push(frame);
  }

  const queryTokenChunks = chunks(Array.from(queryTimes.keys()), MATCH_TOKEN_QUERY_CHUNK);
  const baseCountStatements = queryTokenChunks.map((tokenChunk) => env.DB.prepare(
    `SELECT token, total_posting_count
     FROM music_token_posting_chunks
     WHERE token IN (${tokenChunk.map(() => "?").join(",")}) AND chunk_id = 0`,
  ).bind(...tokenChunk));
  const overlayCountStatements = queryTokenChunks.map((tokenChunk) => env.DB.prepare(
    `SELECT token, COUNT(*) AS total_posting_count
     FROM music_token_overlay_entries
     WHERE token IN (${tokenChunk.map(() => "?").join(",")})
     GROUP BY token`,
  ).bind(...tokenChunk));
  const [baseCountResults, overlayCountResults, replacedResult] = await Promise.all([
    executeStatementBatches(env.DB, baseCountStatements),
    executeStatementBatches(env.DB, overlayCountStatements),
    env.DB.prepare("SELECT track_id FROM music_replaced_tracks").all(),
  ]);
  const postingCounts = new Map();
  for (const row of [baseCountResults, overlayCountResults].flatMap((results) => (
    results.flatMap((result) => Array.isArray(result.results) ? result.results : [])
  ))) {
    const token = Number(row.token);
    postingCounts.set(token, (postingCounts.get(token) ?? 0) + Number(row.total_posting_count));
  }
  const informativeTokens = Array.from(postingCounts.entries())
    .filter((entry) => entry[1] <= MATCH_MAXIMUM_POSTINGS_PER_TOKEN)
    .sort((left, right) => left[1] - right[1])
    .slice(0, MATCH_INFORMATIVE_TOKEN_LIMIT)
    .map((entry) => entry[0]);
  const basePostingRows = informativeTokens.length
    ? (await env.DB.prepare(
      `SELECT token, postings
       FROM music_token_posting_chunks
       WHERE token IN (${informativeTokens.map(() => "?").join(",")})
       ORDER BY token, chunk_id`,
    ).bind(...informativeTokens).all()).results ?? []
    : [];
  const overlayPostingRows = informativeTokens.length
    ? (await env.DB.prepare(
      `SELECT token, track_id, frame
       FROM music_token_overlay_entries
       WHERE token IN (${informativeTokens.map(() => "?").join(",")})
       ORDER BY token, track_id, frame`,
    ).bind(...informativeTokens).all()).results ?? []
    : [];
  const replacedTrackIds = new Set(
    (replacedResult.results ?? []).map((row) => Number(row.track_id)),
  );
  const offsetVotes = new Map();
  const addVote = (token, trackId, referenceFrame) => {
    const queryFrames = queryTimes.get(token) ?? [];
    for (const queryFrame of queryFrames) {
      const offset = referenceFrame - queryFrame;
      const key = `${trackId}:${offset}`;
      offsetVotes.set(key, (offsetVotes.get(key) ?? 0) + 1);
    }
  };
  for (const row of basePostingRows) {
    const token = Number(row.token);
    const postings = blobBytes(row.postings);
    if (postings.length % 4 !== 0) continue;
    const view = new DataView(
      postings.buffer,
      postings.byteOffset,
      postings.byteLength,
    );
    for (let index = 0; index < postings.length; index += 4) {
      const trackId = view.getUint16(index, true);
      const referenceFrame = view.getUint16(index + 2, true);
      if (!replacedTrackIds.has(trackId)) addVote(token, trackId, referenceFrame);
    }
  }
  for (const row of overlayPostingRows) {
    addVote(Number(row.token), Number(row.track_id), Number(row.frame));
  }
  const candidateOffsets = strongestCandidateOffsets(offsetVotes);
  const candidateIds = Array.from(candidateOffsets.keys());
  if (!candidateIds.length) {
    return jsonResponse({ ok: true, matches: [], strategy: "time-aligned-landmarks" });
  }
  const trackStatements = chunks(candidateIds, MATCH_TOKEN_QUERY_CHUNK).map(
    (idChunk) => env.DB.prepare(
      `SELECT track_id, track_key, submission_id, spc_filename, title, artist,
              submission_url, download_url, value_count
       FROM music_reference_tracks
       WHERE track_id IN (${idChunk.map(() => "?").join(",")})`,
    ).bind(...idChunk),
  );
  const trackResults = await env.DB.batch(trackStatements);
  const trackRows = trackResults.flatMap(
    (result) => Array.isArray(result.results) ? result.results : [],
  );
  const fingerprintStatements = chunks(candidateIds, MATCH_TOKEN_QUERY_CHUNK).map(
    (idChunk) => env.DB.prepare(
      `SELECT track_id, chunk_id, fingerprint
       FROM music_reference_fingerprint_chunks
       WHERE track_id IN (${idChunk.map(() => "?").join(",")})
       ORDER BY track_id, chunk_id`,
    ).bind(...idChunk),
  );
  const fingerprintResults = await env.DB.batch(fingerprintStatements);
  const fingerprintPieces = new Map();
  for (const row of fingerprintResults.flatMap(
    (result) => Array.isArray(result.results) ? result.results : [],
  )) {
    const trackId = Number(row.track_id);
    if (!fingerprintPieces.has(trackId)) fingerprintPieces.set(trackId, []);
    fingerprintPieces.get(trackId).push(blobBytes(row.fingerprint));
  }
  for (const row of trackRows) {
    const pieces = fingerprintPieces.get(Number(row.track_id)) ?? [];
    const totalBytes = pieces.reduce((total, piece) => total + piece.length, 0);
    const fingerprint = new Uint8Array(totalBytes);
    let writeOffset = 0;
    for (const piece of pieces) {
      fingerprint.set(piece, writeOffset);
      writeOffset += piece.length;
    }
    row.fingerprint = fingerprint;
  }
  const scored = scoreReferenceTracks(query, trackRows, candidateOffsets);
  return jsonResponse({
    ok: true,
    matches: responseMatches(scored, requestedLimit),
    strategy: "time-aligned-landmarks",
    raw_audio_collected: false,
  });
}

async function replaceCatalogSubmission(env, submissionId, incomingTrackIds) {
  const existing = await env.DB.prepare(
    "SELECT track_id FROM music_reference_tracks WHERE submission_id = ?",
  ).bind(submissionId).all();
  const trackIds = Array.from(new Set([
    ...(existing.results ?? []).map((row) => Number(row.track_id)),
    ...incomingTrackIds.map((value) => Number(value)),
  ])).filter((value) => Number.isInteger(value) && value > 0);
  const statements = [];
  for (const idChunk of chunks(trackIds, 70)) {
    const placeholders = idChunk.map(() => "?").join(",");
    statements.push(
      env.DB.prepare(
        `DELETE FROM music_token_overlay_entries WHERE track_id IN (${placeholders})`,
      ).bind(...idChunk),
      env.DB.prepare(
        `DELETE FROM music_reference_fingerprint_chunks WHERE track_id IN (${placeholders})`,
      ).bind(...idChunk),
    );
  }
  statements.push(
    env.DB.prepare("DELETE FROM music_reference_tracks WHERE submission_id = ?").bind(submissionId),
  );
  const replacedAt = new Date().toISOString();
  for (const idChunk of chunks(trackIds, 24)) {
    statements.push(env.DB.prepare(
      `INSERT OR REPLACE INTO music_replaced_tracks(track_id, submission_id, replaced_at) VALUES ${
        idChunk.map(() => "(?, ?, ?)").join(",")
      }`,
    ).bind(...idChunk.flatMap((trackId) => [trackId, submissionId, replacedAt])));
  }
  await executeStatementBatches(env.DB, statements);
  return trackIds.length;
}

async function upsertCatalogTrack(env, document) {
  const track = document.track;
  const fingerprint = decodeBase64(track.fingerprint_base64);
  const postings = decodeBase64(track.token_postings_base64);
  if (!fingerprint.length || fingerprint.length % 4 !== 0 || postings.length % 8 !== 0) {
    throw new SyntaxError("The replacement fingerprint payload is malformed.");
  }
  const valueCount = fingerprint.length / 4;
  if (valueCount < MINIMUM_MATCH_VALUES || valueCount > 65535) {
    throw new SyntaxError("The replacement fingerprint length is invalid.");
  }
  const postingView = new DataView(postings.buffer, postings.byteOffset, postings.byteLength);
  const tokenEntries = [];
  for (let offset = 0; offset < postings.length; offset += 8) {
    const token = postingView.getUint32(offset, true);
    const frame = postingView.getUint32(offset + 4, true);
    if (token > 0xfff || frame > 0xffff) {
      throw new SyntaxError("The replacement token postings are malformed.");
    }
    tokenEntries.push([token, Number(track.track_id), frame]);
  }
  if (!tokenEntries.length) {
    throw new SyntaxError("The replacement track has no searchable token postings.");
  }
  const trackId = Number(track.track_id);
  const trackKey = text(track.track_key).toLowerCase();
  const statements = [
    env.DB.prepare("DELETE FROM music_token_overlay_entries WHERE track_id = ?").bind(trackId),
    env.DB.prepare("DELETE FROM music_reference_fingerprint_chunks WHERE track_id = ?").bind(trackId),
    env.DB.prepare("DELETE FROM music_reference_tracks WHERE track_id = ? OR track_key = ?").bind(trackId, trackKey),
    env.DB.prepare(
      `INSERT INTO music_reference_tracks(
         track_id, track_key, submission_id, spc_filename, title, artist,
         submission_url, download_url, value_count, fingerprint
       ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)` ,
    ).bind(
      trackId,
      trackKey,
      text(document.submission_id),
      text(track.spc_filename),
      text(track.title),
      text(track.artist),
      text(track.submission_url),
      text(track.download_url),
      valueCount,
      new Uint8Array(),
    ),
  ];
  const fingerprintChunkBytes = 2048;
  for (let offset = 0, chunkId = 0; offset < fingerprint.length; offset += fingerprintChunkBytes, chunkId += 1) {
    statements.push(env.DB.prepare(
      "INSERT INTO music_reference_fingerprint_chunks(track_id, chunk_id, fingerprint) VALUES(?, ?, ?)",
    ).bind(trackId, chunkId, fingerprint.slice(offset, offset + fingerprintChunkBytes)));
  }
  for (const entryChunk of chunks(tokenEntries, 24)) {
    statements.push(env.DB.prepare(
      `INSERT OR REPLACE INTO music_token_overlay_entries(token, track_id, frame) VALUES ${
        entryChunk.map(() => "(?, ?, ?)").join(",")
      }`,
    ).bind(...entryChunk.flat()));
  }
  await executeStatementBatches(env.DB, statements);
  return { track_id: trackId, value_count: valueCount, posting_count: tokenEntries.length };
}

async function finishCatalogUpdate(env, document) {
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS count FROM music_reference_tracks",
  ).first();
  const values = [
    ["schema_version", String(API_SCHEMA_VERSION)],
    ["catalog", "smwcentral"],
    ["index_version", text(document.index_version)],
    ["catalog_updated_at", text(document.catalog_updated_at)],
    ["cloud_updated_at", new Date().toISOString()],
    ["track_count", String(Number(countRow?.count ?? 0))],
  ];
  await env.DB.batch(values.map(([key, value]) => env.DB.prepare(
    "INSERT INTO music_catalog_metadata(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
  ).bind(key, value)));
  return Number(countRow?.count ?? 0);
}

async function handleCatalogUpdate(request, env) {
  const expectedToken = text(env.MUSIC_CATALOG_UPDATE_TOKEN);
  const providedToken = text(request.headers.get("authorization")).replace(/^Bearer\s+/i, "");
  if (!await secureTokenEqual(expectedToken, providedToken)) {
    return jsonResponse({ ok: false, error: "Unauthorized." }, 401);
  }
  let document;
  try {
    document = await readBoundedJson(
      request,
      MAXIMUM_CATALOG_UPDATE_BODY_BYTES,
      "The catalog update",
    );
  } catch (error) {
    return jsonResponse(
      { ok: false, error: error.message },
      error instanceof RangeError ? 413 : 400,
    );
  }
  const validationError = validateCatalogUpdateDocument(document);
  if (validationError) {
    return jsonResponse({ ok: false, error: validationError }, 400);
  }
  try {
    const operation = text(document.operation);
    if (operation === "begin_submission") {
      const replaced = await replaceCatalogSubmission(
        env,
        text(document.submission_id),
        document.track_ids,
      );
      return jsonResponse({ ok: true, operation, replaced });
    }
    if (operation === "delete_submission") {
      const replaced = await replaceCatalogSubmission(env, text(document.submission_id), []);
      return jsonResponse({ ok: true, operation, replaced });
    }
    if (operation === "upsert_track") {
      return jsonResponse({ ok: true, operation, ...(await upsertCatalogTrack(env, document)) });
    }
    const trackCount = await finishCatalogUpdate(env, document);
    return jsonResponse({
      ok: true,
      operation,
      index_version: text(document.index_version),
      track_count: trackCount,
    });
  } catch (error) {
    const isBadPayload = error instanceof SyntaxError;
    console.error(JSON.stringify({
      event: "music-catalog-update-failed",
      operation: text(document.operation),
      submission_id: text(document.submission_id),
      error: String(error?.message ?? error),
    }));
    return jsonResponse(
      { ok: false, error: isBadPayload ? error.message : "The catalog update could not be applied." },
      isBadPayload ? 400 : 503,
    );
  }
}

async function handleCatalogStatus(env) {
  const result = await env.DB.prepare(
    "SELECT key, value FROM music_catalog_metadata",
  ).all();
  const catalog = Object.fromEntries(
    (result.results ?? []).map((row) => [text(row.key), text(row.value)]),
  );
  return jsonResponse({
    ok: true,
    ...catalog,
    cloud_updated_at: cloudCatalogUpdatedAt(catalog),
    fingerprints_only: true,
    raw_audio_collected: false,
  });
}

async function handleAdminRevoke(request, env) {
  const expectedToken = text(env.ADMIN_TOKEN);
  const providedToken = text(request.headers.get("authorization")).replace(/^Bearer\s+/i, "");
  if (!await secureTokenEqual(expectedToken, providedToken)) {
    return jsonResponse({ ok: false, error: "Unauthorized." }, 401);
  }
  let document;
  try {
    document = await request.json();
  } catch {
    return jsonResponse({ ok: false, error: "Invalid JSON." }, 400);
  }
  if (!isHex(document?.track_key, 64)) {
    return jsonResponse({ ok: false, error: "Invalid track key." }, 400);
  }
  const trackKey = text(document.track_key).toLowerCase();
  await env.DB.batch([
    env.DB.prepare(
      "INSERT OR REPLACE INTO revoked_tracks(track_key, reason, revoked_at) VALUES(?, ?, ?)",
    ).bind(trackKey, text(document.reason).slice(0, 500), new Date().toISOString()),
    env.DB.prepare(
      "UPDATE service_metadata SET value = CAST(value AS INTEGER) + 1 WHERE key = 'model_revision'",
    ),
  ]);
  return jsonResponse({ ok: true, track_key: trackKey });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: jsonHeaders });
    }
    const url = new URL(request.url);
    try {
      if (request.method === "GET" && url.pathname === "/v1/health") {
        return jsonResponse({ ok: true, schema_version: API_SCHEMA_VERSION });
      }
      if (request.method === "POST" && url.pathname === "/v1/contributions") {
        return await handleContribution(request, env);
      }
      if (request.method === "GET" && url.pathname === "/v1/model/manifest") {
        return await handleManifest(env);
      }
      if (request.method === "GET" && url.pathname === "/v1/model") {
        return await handleModelPage(url, env);
      }
      if (request.method === "POST" && url.pathname === "/v1/music/match") {
        return await handleMusicMatch(request, env);
      }
      if (request.method === "GET" && url.pathname === "/v1/music/catalog") {
        return await handleCatalogStatus(env);
      }
      if (request.method === "POST" && url.pathname === "/v1/admin/music/catalog") {
        return await handleCatalogUpdate(request, env);
      }
      if (request.method === "POST" && url.pathname === "/v1/admin/revoke") {
        return await handleAdminRevoke(request, env);
      }
      return jsonResponse({ ok: false, error: "Not found." }, 404);
    } catch (error) {
      console.error(JSON.stringify({
        event: "community-learning-request-failed",
        path: url.pathname,
        method: request.method,
        error: String(error?.message ?? error),
      }));
      return jsonResponse({ ok: false, error: "Service temporarily unavailable." }, 503);
    }
  },
};
