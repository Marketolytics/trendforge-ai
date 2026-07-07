# Upgrading TrendForge AI

Your data lives in `backend/data/` (or `TRENDFORGE_DATA_DIR`), separate from the
application code, so pulling new code preserves it automatically.

## How to upgrade

```powershell
git pull

# refresh backend dependencies
cd backend; .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# refresh frontend dependencies
cd ..\frontend; npm install
```

Restart the backend and frontend. On the next backend start, any pending
database migrations are applied automatically.

## What is preserved

- Projects and generated content
- The SQLite database (trends, research, jobs, favorites, history)
- Settings and model routing
- Backups

Nothing in `backend/data/` is removed or overwritten by an upgrade.

## Before a major upgrade (recommended)

Create a backup from **Export Center → Download backup**. To roll back, restore
that `.zip` via **Export Center → Restore**. Migrations are additive and
forward-only.
