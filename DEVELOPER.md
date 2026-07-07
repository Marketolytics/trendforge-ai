# TrendForge AI — Developer Guide

Practical reference for working on and releasing TrendForge AI v1.0.

## Architecture

```
Browser
  └── Frontend (React + Vite + TS)  ──HTTP /api──►  Backend (FastAPI)  ──►  SQLite
```

In development the Vite dev server (`:5173`) proxies `/api` to the FastAPI
backend (`:8000`), so the app uses same-origin relative URLs. In production the
built frontend can be served from any static host pointed at the API via
`VITE_API_BASE_URL`.

- **Backend** owns all logic: collectors, research, AI orchestration, persistence.
- **Frontend** is a typed client (`src/lib/api.ts` is the only place that talks to the backend).
- **AI** flows through one analyzer (`services/ai/analyzer.py`) that every generator, agent and workflow reuses — render prompt → call Gemini → parse → persist → log.

## Folder structure

```
backend/app/
  api/routes/        HTTP endpoints (one file per domain)
  core/              logging
  db/                models, session, migrations, seed
  services/
    collectors/      trend sources (RSS, Reddit, Steam, YouTube, ...)
    intelligence/    scoring, competitors, patterns, analytics
    research/        confidence, clustering, timeline, keywords, entities
    ai/              gemini_service, prompt_manager, analyzer, prompt_library/
    orchestrator/    agents, workflows, engine (queue)
    *_service.py     settings, favorites, projects, backup, search
frontend/src/
  components/        layout, ui, trends, studio, intelligence, research, jobs, dev, command
  pages/             one per route
  store/             React contexts (trends, jobs)
  lib/               api client, theme, notifications, format
```

## Configuration & environment

Settings live in `backend/.env` (prefix `TRENDFORGE_`) — see `.env.example`.
User-editable preferences are persisted in the `settings` table and edited in
the app's Settings Center. Key env vars:

| Variable | Purpose |
|----------|---------|
| `TRENDFORGE_PORT` | Backend port (default 8000) |
| `TRENDFORGE_DATA_DIR` | Where the DB, logs, exports and backups live |
| `TRENDFORGE_GEMINI_API_KEY` | Enables AI features |
| `TRENDFORGE_GEMINI_MODEL` | Gemini model (default `gemini-2.5-flash`) |

## How to add a new collector

1. Create `services/collectors/mysource.py` subclassing `BaseCollector`, implement `async collect() -> list[StandardTrend]`.
2. Register it in `services/collectors/registry.py` (`COLLECTOR_TYPES`).
3. Seed a source row (type = your key) in `db/seed.py` or add via `POST /api/sources`.

No other code changes needed — the aggregation engine dispatches by source type.

## How to add a new AI generator/agent

1. Add a prompt template `services/ai/prompt_library/<name>.md` (front-matter `version`, `temperature`).
2. Add a typed output schema in `schemas/ai.py`.
3. Register a `GenSpec` in `analyzer.GENERATORS` (with an optional context builder).
4. Expose an endpoint in `api/routes/ai.py`.
5. (Optional) register a `GeneratorAgent` in `orchestrator/agents.py` to use it in workflows.

## How to add a new AI provider

1. Implement `AIProvider` in `services/ai/providers/` (or reuse
   `OpenAICompatibleProvider` for any OpenAI-style endpoint): `validate`,
   `list_models`, `generate`, optional `stream`.
2. Register it in `services/ai/providers/registry.py` (`PROVIDERS`).
3. That's it — the model router, service facade, settings UI and usage tracking
   pick it up automatically. Keys go to the OS credential store via
   `services/ai/credentials.py`; never store them in the DB or config.

## How to add a new workflow

Add an entry to `WORKFLOWS` in `services/orchestrator/workflows.py`:

```python
"my_flow": Workflow(
    name="my_flow", label="My Flow", description="…",
    groups=[["script"], ["storyboard", "continuity"]],  # sequential groups of parallel agents
    default_format="60s",
)
```

The engine reads the registry generically — no core changes required.

## Running locally

```powershell
# backend
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000
# frontend
cd frontend; npm run dev
```

Or use the helper scripts: `scripts\setup.ps1` (once), then `scripts\backend.ps1`
and `scripts\frontend.ps1` in separate terminals.

## Testing & linting

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest      # unit + integration tests
.\.venv\Scripts\python.exe -m ruff check . # lint
cd ..\frontend
npm run build                              # type-check + production build
```

## Startup & first run

On startup the UI shows a splash until `/api/health` responds (`StartupGate`),
with a friendly retry screen if the backend can't be reached. The workspace
folders and database are created and migrated automatically on first run;
route / theme / last-trend UI state persists via `localStorage`.

## Building for production

```powershell
# 1. Build the frontend (type-check + Vite production build -> frontend/dist)
cd frontend; npm run build

# 2. Serve the API with a production ASGI server (co-hosts frontend/dist)
cd ..\backend; .\.venv\Scripts\python.exe run_server.py --host 0.0.0.0 --port 8000
```

When the built frontend is present, the backend serves it directly (index.html,
`/assets`, and an SPA fallback so nested-route refresh works), so the whole app
runs from one origin with no CORS setup. To host the UI separately, point it at
the API via `VITE_API_BASE_URL` at build time.

### Database: SQLite ↔ MySQL

Development defaults to SQLite. For production set `DATABASE_URL` to a MySQL URL
(`mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4`) — no code changes.
The engine is dialect-aware (connection pooling + pre-ping for MySQL) and
migrations are additive and non-destructive. Manage the schema with:

```powershell
python manage.py check     # verify connectivity + show config
python manage.py initdb    # create tables + seed (first deploy)
python manage.py migrate   # additive column migrations (updates)
python manage.py backup / restore
```

### Hostinger shared hosting (Passenger)

`backend/passenger_wsgi.py` bridges the ASGI app to WSGI (via `a2wsgi`) and runs
the idempotent `initialize()` at import (WSGI has no lifespan). Point the
Hostinger Python App at `passenger_wsgi.py` / `application`. Full guide:
[docs/DEPLOYMENT_HOSTINGER.md](docs/DEPLOYMENT_HOSTINGER.md).

Environment variables (standard names; legacy `TRENDFORGE_` names still work):
`APP_ENV`, `SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`, `ALLOWED_ORIGINS`,
`DATA_DIR`, `CACHE_DIRECTORY`, `EXPORT_DIRECTORY`, `LOG_DIRECTORY`,
`FRONTEND_DIST`, `LOG_LEVEL`. See `backend/.env.example`.

A deployment/CI pipeline may write `backend/build_info.json`
(`{name, version, build_date, commit, channel}`); `/api/version` surfaces it.
