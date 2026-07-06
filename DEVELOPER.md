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

## Desktop integration (one-click app)

The Tauri shell (`frontend/src-tauri/src/lib.rs`) is a backend process manager:

- picks a local port (reusing an already-running instance to avoid duplicates),
- launches the bundled backend **sidecar** with `--port`,
- exposes the URL to the UI via the `get_backend_url` command (frontend
  auto-discovers it in `lib/backend.ts` — no manual URL),
- monitors the backend and restarts it if it crashes,
- kills it cleanly on exit.

On startup the UI shows a splash until `/api/health` responds (`StartupGate`),
with a friendly retry screen if the backend can't be reached. The workspace
folders and database are created automatically on first run; window size/
position persist via `tauri-plugin-window-state`, and route/theme/last-trend
via `localStorage`.

## Creating a portable release

Prereqs on the build machine: Python 3.12+ (backend deps + `pyinstaller`),
Node 20+, Rust toolchain + Microsoft C++ Build Tools + WebView2.

1. Bump the version in `backend/app/config.py`, `frontend/package.json`,
   `frontend/src-tauri/{tauri.conf.json,Cargo.toml}`.
2. Generate icons once: `cd frontend && npx tauri icon path/to/icon.png`.
3. Run the release script from the repo root:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
   ```
   It builds the backend into a single exe (`backend/trendforge-backend.spec`),
   copies it into `frontend/src-tauri/binaries/trendforge-backend-<triple>.exe`
   as the Tauri sidecar, then runs `npm run tauri build`.
4. Output: `dist/release/v<version>/` — the NSIS/MSI installer, the portable
   ZIP, and `SHA256SUMS.txt`. No Python runtime is required on the end-user
   machine — the backend is bundled as the sidecar.
5. Validate the build: `powershell -File scripts\validate_release.ps1` (launches
   the embedded backend, checks DB init + workspace + artifacts).

Distribution docs live in `docs/`: `INSTALL.md`, `UPGRADE.md`,
`TROUBLESHOOTING.md`, `KNOWN_ISSUES.md`. The installer configuration is in
`frontend/src-tauri/tauri.conf.json` (`bundle.windows.nsis`) with an uninstall
data-prompt hook at `src-tauri/installer/hooks.nsh`.

> The final Windows `.exe`/installer requires the Rust toolchain on the build
> machine. In development the UI runs via Vite and the backend via
> `python run_server.py` — the same entrypoint the packaged sidecar uses.
