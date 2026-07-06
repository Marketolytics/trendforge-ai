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

## Content (placeholder — Sprint 3+)

- `GET /api/content/status`
