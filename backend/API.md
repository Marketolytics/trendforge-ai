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

## Creator Intelligence (Sprint 5)

Competitor tracking (YouTube RSS, no API key), viral pattern analysis, analytics
and favorites — all local.

- `GET    /api/competitors` — saved channels
- `POST   /api/competitors` — add `{ handle, category }` (@handle, URL, or UC… id)
- `POST   /api/competitors/refresh` — refresh all channels
- `POST   /api/competitors/{pk}/refresh` — refresh one
- `DELETE /api/competitors/{pk}` — remove a channel
- `GET    /api/competitors/videos` — all collected videos
- `GET    /api/competitors/{pk}/videos` — videos for one channel
- `GET    /api/competitors/patterns?channel_pk=` — computed viral patterns

- `GET    /api/intelligence/analytics` — local analytics dashboard data
- `GET    /api/intelligence/projects?q=&sort=recent|modules|title` — generated projects

- `GET    /api/favorites?type=&q=` · `POST /api/favorites` · `DELETE /api/favorites/{id}`

Intelligence AI generators (trend-scoped, `?force=true` to regenerate):
- `POST /api/ai/forecast/{id}` — growth forecast (tomorrow / 3d / 1w / 1m)
- `POST /api/ai/upload-advisor/{id}` — best day/time/length/frequency/format/audience
- `POST /api/ai/competitor-gap/{id}` — what competitors aren't covering, ranked
- `POST /api/ai/multi-ideas/{id}` — full idea slate with duplicate protection

## Orchestrator & Background Jobs (Sprint 6)

Workflows are ordered groups of agents (parallel within a group, sequential
across groups). Jobs run on a persistent background queue (single worker; jobs
survive restart and resume from cache). Each stage retries on failure.

- `GET  /api/workflows` — workflow templates (complete, quick_short, long_video, research_only, storyboard_only, prompt_only, seo_only)
- `POST /api/jobs` — enqueue `{ workflow, trend_id, format, voice_style, force, priority }`
- `GET  /api/jobs?status=&limit=` — recent jobs
- `GET  /api/jobs/{id}` — job status (progress, steps, current_step, eta)
- `POST /api/jobs/{id}/cancel|pause|resume|retry`

- `POST /api/ai/quality/{id}?format=` — Quality Review Agent (recommendations only)

Developer panel + prompt engine tools:
- `GET  /api/dev/stats` — cache, queue, DB and prompt stats
- `GET  /api/dev/logs?lines=` — tail of the structured log
- `GET  /api/dev/prompts/{name}` — raw template, version, variables
- `POST /api/dev/prompts/{name}/preview?trend_id=&format=` — render + validate a prompt
- `GET  /api/dev/generations?trend_id=&kind=` — AI generation history (for compare)
- `GET  /api/dev/generations/{id}` — the exact prompt used + response

## Content (placeholder)

- `GET /api/content/status`
