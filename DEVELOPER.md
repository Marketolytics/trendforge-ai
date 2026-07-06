# TrendForge AI — Developer Guide

Practical reference for working on and releasing TrendForge AI v1.0.

## Architecture

```
Tauri (native window)
  └── Frontend (React + Vite + TS)  ──HTTP──►  Backend (FastAPI)  ──►  SQLite
```

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
| `TRENDFORGE_PORT` | Backend port (default 8756) |
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
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8756
# frontend
cd frontend; npm run dev
```

## Testing & linting

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest      # unit + integration tests
.\.venv\Scripts\python.exe -m ruff check . # lint
cd ..\frontend
npm run build                              # type-check + production build
```

## Creating a release

1. Bump the version in `backend/app/config.py`, `frontend/package.json`, `frontend/src-tauri/{tauri.conf.json,Cargo.toml}`.
2. Install the Tauri prerequisites on Windows: Rust toolchain, Microsoft C++ Build Tools, WebView2.
3. Generate icons: `cd frontend && npx tauri icon path/to/icon.png`.
4. Build the desktop app + installer: `npm run tauri build`.
   - Output: `frontend/src-tauri/target/release/bundle/` (`.msi` installer + `.exe`).
5. The backend runs as a local sidecar; ensure Python and dependencies are available, or bundle it (see Tauri sidecar docs).

> Note: producing the Windows `.exe`/installer requires the Rust toolchain, which
> must be installed on the build machine. In development the UI runs in the
> browser via Vite and the backend via uvicorn.
