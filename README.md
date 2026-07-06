# TrendForge AI

AI-powered Content Intelligence Desktop Application.

> Answers one question: **"What content should I create today that has the highest probability of performing well?"**

TrendForge collects trending topics from multiple sources, analyzes them with AI, ranks them, and generates everything needed for content production — locally, on your machine.

## Stack

| Layer     | Tech                                                      |
|-----------|-----------------------------------------------------------|
| Backend   | Python 3.12+, FastAPI, SQLite, SQLModel, HTTPX, Feedparser |
| Frontend  | React, TypeScript, Vite, Tailwind CSS, shadcn/ui          |
| Desktop   | Tauri v2                                                   |
| AI        | Google Gemini API                                         |

## Repository layout

```
TrendForge AI/
├── backend/            FastAPI service (API, services, AI, db)
├── frontend/           React + Vite UI
│   └── src-tauri/      Tauri v2 desktop shell
└── README.md
```

## Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Git
- (For the native desktop window) Rust toolchain + Microsoft C++ Build Tools + WebView2

## Running locally (development)

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8756
```

Backend runs at http://127.0.0.1:8756 — health check at `/api/health`.

### 2. Frontend (browser)

```powershell
cd frontend
npm install
npm run dev
```

UI runs at http://localhost:5173.

### 3. Desktop window (optional, requires Rust)

```powershell
cd frontend
npm run tauri dev
```

## Status

- **Sprint 1** — application shell + local frontend/backend communication.
- **Sprint 2** — core infrastructure & trend collection: config, SQLite schema,
  structured rotating logs, TTL request cache, modular collectors (RSS, Google
  Trends, Reddit, Steam, YouTube, gaming news, Rockstar), aggregation engine
  (dedupe + cluster + preliminary scoring), documented API, and a live
  dashboard. See `backend/API.md` for the API reference.

- **Sprint 3** — AI intelligence engine: a modular AI service layer (versioned
  markdown prompt library, Gemini client with retries + logging, robust JSON
  parsing) that turns each trend into an actionable content opportunity —
  intelligence, timeline, audience, a 0-100 opportunity score, content-gap
  analysis, ranked hooks/titles/strategy, and thumbnail direction. Results are
  persisted and regenerable. A slide-over analysis panel surfaces it all in the
  UI, and Settings lets you add your Gemini key.

The backend stores data under `backend/data/` (SQLite DB, logs, exports).
The default backend port is **8756**.

- **Sprint 4** — AI Content Factory: one click turns a trend into a full,
  export-ready production package — retention script (9 durations),
  scene-by-scene storyboard, a scene-continuity engine, per-scene Nano Banana
  image prompts and Veo/Runway/Pika/Luma video prompts (with character
  continuity), voice-over, B-roll, thumbnail blueprint, SEO package and
  production checklist. Everything is independently regenerable, cached, and
  exportable individually (MD/JSON) or as one ZIP. The **Production Studio**
  workspace (left: trend + format; center: storyboard timeline; right: module
  tabs; bottom: export) drives it all.

- **Sprint 5** — Creator Intelligence & Competitive Analysis: track competitor
  YouTube channels (via RSS, no API key), compute viral patterns (views, upload
  timing, title keywords, frequency), AI content-gap finder, trend forecast,
  upload advisor and a duplicate-protected multi-idea generator, plus favorites,
  a projects/history browser and a local analytics dashboard. Surfaced in a new
  **Intelligence** workspace with tabs (Overview, Competitors, Opportunities,
  Forecast, History, Favorites, Analytics) and virtualized tables.

- **Sprint 6** — AI Orchestrator & Background Processing: a workflow engine that
  coordinates every AI stage through independent agents (common interface), a
  persistent background job queue (priority, progress, ETA, pause/resume/cancel/
  retry, resume-after-restart), reusable workflow templates, a Quality Review
  agent, append-only generation logging (view prompt used, compare responses),
  and robust per-stage retry. The UI adds a live **Job Monitor** and a
  **Developer panel** (⌃⇧D) showing queue/cache/DB stats, logs and prompt tools.

- **Sprint 7** — Smart Research Engine & Multi-Source Intelligence: assembles the
  single *story* behind many articles. A deterministic layer scores every source
  by confidence tier, clusters duplicate coverage, builds an event timeline, and
  extracts keywords, entities and a research graph — all offline, no key needed.
  An AI verification layer then extracts confirmed facts vs rumors, flags possible
  misinformation, and writes executive/creator/technical/timeline/community
  summaries. A **Research** workspace (Overview, Timeline, Sources, Facts,
  Entities, Community, Keywords, Verification) surfaces it with source badges,
  confidence indicators and MD/JSON/print export.

- **Sprint 8 — v1.0** — Production readiness: route code-splitting (smaller,
  faster startup), a global search + **command palette (Ctrl/⌘+K)**, an Export
  Center with backup/restore and project import/export, an expanded validated
  Settings Center, friendly error handling (backend handler + UI error
  boundary), desktop notifications, an optional update checker, a **24-test**
  automated suite (collectors, prompts, DB, exports, queue, workflow engine,
  settings, research, backup), light/dark theme toggle, linting (ruff), and
  finalized Tauri packaging config. See `DEVELOPER.md`.

To enable AI: open **Settings** in the app and paste your Gemini API key
(or set `TRENDFORGE_GEMINI_API_KEY` in `backend/.env`).

- **Sprint 9** — AI Provider & Model Management: a vendor-agnostic provider
  interface (`connect/validate/list_models/generate/stream`) with Gemini plus
  OpenAI-compatible providers (OpenAI, OpenRouter, Ollama, LM Studio); API keys
  stored in the **OS credential store** (never in SQLite/plaintext); connection
  testing (latency, models, errors); per-task **model routing**
  (research / content / quality); and a usage dashboard — all in a new Settings
  **AI Provider** panel. The rest of the app no longer depends on Gemini-specific
  code.

- **Sprint 10 — Desktop integration** — one-click app: the Tauri shell launches
  the backend automatically as a bundled sidecar (auto port selection + duplicate
  detection), the UI auto-discovers it (no manual URL) and shows a startup splash
  with a friendly retry screen, the full workspace tree + database initialize on
  first run, health-report and diagnostics endpoints back a system view in the
  developer panel, an onboarding wizard appears when no AI provider is set, and
  window/route/theme/last-trend state persist across launches. Includes a
  PyInstaller backend spec + `scripts/build_release.ps1` for a portable Windows
  build (backend runs cleanly on any local port via `run_server.py`).

- **Sprint 11 — Windows installer & distribution** — packaging only: Tauri NSIS/MSI
  installer config (install dir choice, desktop + Start Menu shortcuts, license
  screen, uninstaller with an opt-in "remove user data" prompt), embedded Python
  backend via PyInstaller (no Python needed by users), user data isolated in
  `%LOCALAPPDATA%\TrendForge AI` so upgrades preserve everything, build/version
  metadata (`/api/version` reports version + build date + commit + channel),
  `scripts/build_release.ps1` (installer + portable ZIP + SHA-256 checksums),
  `scripts/validate_release.ps1`, and distribution docs in `docs/`
  (install / upgrade / troubleshooting / known issues).

**TrendForge AI v1.0 is feature complete.** See `DEVELOPER.md` for architecture,
adding collectors/agents/workflows/providers, desktop integration, and the
portable release + installer process.
