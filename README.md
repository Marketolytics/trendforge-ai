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

The backend stores data under `backend/data/` (SQLite DB, logs, exports).
The default backend port is **8756**.
