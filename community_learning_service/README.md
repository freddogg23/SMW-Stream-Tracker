# SMW Stream Tracker Community Learning Service

This Cloudflare Worker provides the shared SMW Central music-recognition
catalog and accepts **explicitly confirmed** learning fingerprints. It never
accepts or stores WAV files, usernames, Twitch data, or reconstructive audio.

## Music recognition

`POST /v1/music/match` accepts a short sequence of non-reconstructive
Chromaprint values. The service selects rare fingerprint landmarks with an
inverted index, votes for a consistent time offset, then verifies the best
candidates across one continuous timeline. This is the same core architecture
used by Shazam-style recognition: compact landmarks, fast lookup, and temporal
alignment instead of comparing uploaded recordings.

The production catalog contains every rendered SPC preview in the published
SMW Central index. `release_tools/build_cloud_music_catalog.py` turns that
index into a D1 import containing only fingerprints and metadata. The Windows
app keeps the complete local index as an offline fallback and checks for new
or changed submissions every 30 minutes while open.

The scheduled index workflow also calls the authenticated incremental catalog
endpoint after it finds new, changed, or deleted submissions. Only those
tracks' fingerprints and public SMW Central metadata are sent, so routine
cloud refreshes do not rebuild or re-upload the complete catalog.

## Safety model

- Contributions below 78% local confidence are rejected.
- A track is not published until three independent anonymous installations
  confirm it.
- Uploads are rate limited and deduplicated.
- A private admin endpoint can revoke a poisoned or incorrect track.
- The Windows app keeps its local matcher and full SMW Central index as an
  offline fallback.
- Music-match requests contain only unsigned 32-bit fingerprint values; raw
  audio remains on the user's computer.

## Deployment

1. Create a Cloudflare D1 database named
   `smw-stream-tracker-community-learning`.
2. Put its database ID in `wrangler.jsonc`.
3. Apply `schema.sql` to the remote database.
4. Export the published index with `release_tools/build_cloud_music_catalog.py`
   and import the generated SQL into D1.
5. Add strong `ADMIN_TOKEN` and `MUSIC_CATALOG_UPDATE_TOKEN` Worker secrets.
6. Deploy the Worker and copy its HTTPS URL into the Windows app's recognition
   endpoint constant.

Set the same `MUSIC_CATALOG_UPDATE_TOKEN` as a GitHub Actions secret. The daily
music-index workflow will then call `release_tools/push_cloud_music_update.py`
for only the cumulative incremental update. The GitHub repository never needs
a general Cloudflare deployment credential.

The production deployment is intentionally separate from application builds;
an app must never ship with an administrative credential.
