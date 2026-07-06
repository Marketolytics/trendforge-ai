# TrendForge AI — Backend API

Base URL: `http://127.0.0.1:8756`
Interactive docs (OpenAPI/Swagger): `http://127.0.0.1:8756/docs`

All endpoints are local, unauthenticated, and JSON.

## Health

### `GET /api/health`
Liveness + database connectivity.
```json
{ "status": "ok", "app": "TrendForge AI", "version": "0.2.0", "database": "connected", "timestamp": "..." }
```

## Trends

### `POST /api/trends/refresh?force=false`
Collects from all enabled sources, aggregates (dedupe + cluster), scores, and stores.
`force=true` bypasses the request cache.
```json
{ "status": "success", "trends_collected": 223, "raw_items": 268,
  "sources_ok": 11, "sources_failed": 0, "duration_ms": 3600, "failures": [] }
```

### `GET /api/trends?limit=50&category=&source=&window_hours=48`
Highest-scoring recent trends. Returns `{ trends: Trend[], count, generated_at }`.

**Trend object**
```
id, title, summary, url, source, source_type, published_time, category,
keywords[], popularity_score, image_url, language, region,
cluster_size, score, collection_timestamp
```

### `GET /api/trends/{id}`
Full trend detail (adds `raw_content`, `content_hash`, `cluster_id`, `source_id`, `created_at`).

## Sources

- `GET /api/sources` — list all configured sources
- `POST /api/sources` — create `{ name, type, category?, config?, enabled? }`
- `PATCH /api/sources/{id}` — update any of `{ name, category, config, enabled }`
- `DELETE /api/sources/{id}` — remove a source

`type` ∈ `rss | gaming_news | google_trends | reddit | steam | youtube | rockstar`.

## History

### `GET /api/history?limit=25`
Recent refresh runs: counts, duration, status, per-run detail.

## Settings

- `GET /api/settings` — current settings (secret keys masked; adds `gemini_api_key_set`)
- `PUT /api/settings` — update any of `{ gemini_api_key, refresh_interval, cache_duration, theme, output_folder, log_level }`

## Cache

- `GET /api/cache/stats` — `{ total, fresh, expired }`
- `POST /api/cache/clear?namespace=` — clear all or one namespace; returns `{ cleared }`
- `POST /api/cache/clear-expired` — drop expired entries only

## AI Intelligence (Sprint 3)

Every AI endpoint returns a standard envelope:
```json
{ "kind": "analysis", "trend_id": 12, "prompt_version": "1.0.0",
  "cached": false, "generated_at": "...", "data": { ... } }
```
Results are persisted to `generated_content` (one row per trend+kind) so repeat
requests are free. Pass `?force=true` to regenerate. Requires a Gemini API key
(set via `PUT /api/settings`), otherwise endpoints return **409**.

- `GET  /api/ai/status` — `{ configured, model }`
- `GET  /api/ai/prompts` — versioned prompt templates in the library
- `POST /api/ai/analyze/{trend_id}` — intelligence, timeline, audience, opportunity score, content gap
- `POST /api/ai/summary/{trend_id}` — short/detailed/creator summary + facts, cautions, misinfo, sources
- `POST /api/ai/opportunity/{trend_id}` — opportunity score + 9 factors + explanation
- `POST /api/ai/strategy/{trend_id}` — 10 shorts, 5 long, 5 community, 5 X, 3 carousels, 3 livestreams
- `POST /api/ai/hooks/{trend_id}` — 25+ ranked hooks across 7 types
- `POST /api/ai/titles/{trend_id}` — title variants + predicted CTR
- `POST /api/ai/thumbnail/{trend_id}` — thumbnail creative direction (no image generation)

Prompts live in `app/services/ai/prompt_library/*.md` — versioned and editable
without code changes (hot-reloaded on file change).

## AI Content Factory (Sprint 4)

A "package" is all modules sharing a (trend, format) — e.g. `60s`. Modules
persist in `generated_content` (keyed by trend + kind + variant) so repeats are
free; `?force=true` regenerates. Dependencies are auto-loaded (storyboard reads
the script; image/video prompts read the storyboard + continuity bible).

- `GET  /api/ai/formats` — supported formats + voice styles
- `POST /api/ai/script/{id}?format=` — retention script (hook/body/climax/CTA)
- `POST /api/ai/storyboard/{id}?format=` — scene-by-scene storyboard
- `POST /api/ai/continuity/{id}?format=` — scene-continuity bible
- `POST /api/ai/image-prompts/{id}?format=` — per-scene Nano Banana prompts
- `POST /api/ai/video-prompts/{id}?format=` — per-scene Veo/Runway/Pika/Luma prompts
- `POST /api/ai/voiceover/{id}?format=&voice_style=` — AI-voice narration
- `POST /api/ai/broll/{id}?format=` — B-roll shot list
- `POST /api/ai/thumbnail-blueprint/{id}?format=` — thumbnail blueprint + CTR
- `POST /api/ai/seo/{id}?format=` — SEO package
- `POST /api/ai/checklist/{id}?format=` — production checklist

Package + export:
- `POST /api/ai/package/{id}?format=&voice_style=` — generate every module (409 if no key)
- `GET  /api/ai/package/{id}?format=` — fetch stored modules for a format
- `GET  /api/ai/export/{id}/{kind}?format=&fmt=md|json` — export one module
- `GET  /api/ai/export/{id}?format=` — export the whole package as a ZIP

## Content (placeholder)

- `GET /api/content/status`
