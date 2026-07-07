# TrendForge AI

AI-powered Content Intelligence web application.

> Answers one question: **"What content should I create today that has the highest probability of performing well?"**

TrendForge collects trending topics from multiple sources, analyzes them with AI, ranks them, and generates everything needed for content production — running entirely on your machine in the browser.

## Stack

| Layer     | Tech                                                              |
|-----------|-------------------------------------------------------------------|
| Backend   | Python 3.12+, FastAPI, SQLModel, HTTPX, Feedparser                 |
| Database  | SQLite (dev) · PostgreSQL / MySQL (prod) — switch via `DATABASE_URL` |
| Frontend  | React, TypeScript, Vite, Tailwind CSS                             |
| AI        | Google Gemini API (plus OpenAI-compatible providers)              |

Runs on localhost with no desktop runtime, no Docker, and no cloud required.
Deploys with only configuration changes to:
- **Render** (single always-on service, all features incl. background jobs,
  PostgreSQL) — see [docs/DEPLOYMENT_RENDER.md](docs/DEPLOYMENT_RENDER.md) *(recommended for full functionality)*
- **Vercel** (static frontend + FastAPI serverless function, PostgreSQL) — see
  [docs/DEPLOYMENT_VERCEL.md](docs/DEPLOYMENT_VERCEL.md)
- **Hostinger shared hosting** (Passenger, MySQL) — see
  [docs/DEPLOYMENT_HOSTINGER.md](docs/DEPLOYMENT_HOSTINGER.md)

## Repository layout

```
TrendForge AI/
├── backend/            FastAPI service (API, services, AI, db)
├── frontend/           React + Vite UI
├── scripts/            Development helper scripts
├── docs/               Additional documentation
└── README.md
```

## Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Git

## Running locally (development)

The quickest path on Windows:

```powershell
# one-time: install backend + frontend dependencies
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

# terminal 1 — backend API
powershell -ExecutionPolicy Bypass -File scripts\backend.ps1

# terminal 2 — frontend UI
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1
```

Or manually:

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger / OpenAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

- UI: http://localhost:5173

The Vite dev server proxies `/api` to the backend, so no CORS setup or manual
URL entry is needed. To point the UI at a backend on a different origin, set
`VITE_API_BASE_URL` (frontend) and/or `VITE_API_PROXY_TARGET` (dev proxy).

## Authentication

V1 has no authentication — everything runs locally for a single user. The
architecture keeps auth concerns out of the data layer so JWT-based auth can be
added later without restructuring.

## Data & storage

The backend stores everything under `backend/data/` (SQLite DB, logs, exports,
projects, cache, backups). The full workspace tree and database are created and
migrated automatically on first launch. Set `TRENDFORGE_DATA_DIR` to relocate it.

To enable AI: open **Settings** in the app and paste your Gemini API key
(or set `TRENDFORGE_GEMINI_API_KEY` in `backend/.env`). API keys are stored in
the operating system credential store, never in the database or exposed to the
frontend.

## Features

- **Trend collection** — modular collectors (RSS, Google Trends, Reddit, Steam,
  YouTube, gaming news) with an aggregation engine (dedupe, cluster, scoring).
- **AI intelligence** — per-trend intelligence, timeline, audience, a 0-100
  opportunity score, content-gap analysis, ranked hooks/titles/strategy, and
  thumbnail direction.
- **AI Content Factory** — one click turns a trend into an export-ready package:
  retention script, storyboard, scene continuity, image/video prompts,
  voice-over, B-roll, thumbnail blueprint, SEO package, and production checklist.
- **Creator Intelligence** — competitor tracking, viral pattern analysis, content
  gap finder, trend forecast, upload advisor, favorites, projects/history, and a
  local analytics dashboard.
- **AI Orchestrator** — workflow engine with a persistent background job queue
  (priority, progress, ETA, pause/resume/cancel/retry), plus a live job monitor.
- **Smart Research Engine** — assembles the single story behind many articles:
  confidence tiers, clustering, event timeline, keywords, entities, and an AI
  verification layer (facts vs rumors, misinformation flags, summaries).
- **Provider management** — vendor-agnostic AI provider interface (Gemini plus
  OpenAI-compatible providers), per-task model routing, and usage tracking.
- **Production readiness** — route code-splitting, global search + command
  palette (Ctrl/⌘+K), Export Center with backup/restore, friendly error
  handling, browser notifications, health checks, and an automated test suite.

See `DEVELOPER.md` for architecture and extension guides, and `backend/API.md`
for the full API reference.
