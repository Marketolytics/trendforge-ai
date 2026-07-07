# Installing & Running TrendForge AI

TrendForge AI is a local web application: a FastAPI backend and a React frontend
that run on your machine and open in the browser. No desktop runtime required.

## Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Git

## Setup

From the repository root (Windows / PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

This creates the backend virtualenv, installs backend and frontend dependencies,
and copies `backend/.env.example` to `backend/.env`.

Manual setup:

```powershell
# backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

# frontend
cd ..\frontend
npm install
```

## Run (development)

Two terminals:

```powershell
# terminal 1 — backend API (http://localhost:8000)
powershell -ExecutionPolicy Bypass -File scripts\backend.ps1

# terminal 2 — frontend UI (http://localhost:5173)
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1
```

Then open http://localhost:5173 in your browser.

- API base: http://localhost:8000
- Swagger / OpenAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

On first launch the backend automatically creates its workspace, initializes the
SQLite database, and applies migrations.

## Enable AI features

Collection, research, timelines and analytics work immediately. To unlock AI
analysis and content generation, open **Settings → AI Provider**, paste an API
key (Gemini, OpenAI, OpenRouter, or point at a local Ollama/LM Studio), and click
**Test connection**. Keys are stored in the operating system credential store —
never in plaintext and never exposed to the frontend.

## Where your data lives

All local data is stored under `backend/data/`:

```
backend/data/
├── trendforge.db   ├── projects\   ├── exports\
├── cache\          ├── logs\       ├── backups\   ├── settings\   └── temp\
```

Set `TRENDFORGE_DATA_DIR` in `backend/.env` to relocate the workspace.

## System requirements

- Windows, macOS, or Linux
- A modern browser (Chrome, Edge, Firefox, Safari)
- ~300 MB disk space for dependencies
