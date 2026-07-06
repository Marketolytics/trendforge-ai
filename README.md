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

To enable AI: open **Settings** in the app and paste your Gemini API key
(or set `TRENDFORGE_GEMINI_API_KEY` in `backend/.env`).
