# Deploying TrendForge AI to Vercel

TrendForge deploys to Vercel as **one project**: the React + Vite frontend is
built to static files and the FastAPI backend runs as a Python serverless
function. No desktop code, no Docker.

```
Browser ──► Vercel static (frontend/dist)         # UI
        └─► /api/*  ──► api/index.py (FastAPI)     # serverless function
                            └─► PostgreSQL (managed) + Gemini API
```

Routing and the combined build are defined in `vercel.json`.

---

## Fastest path (minimum steps)

The repo is already configured, so the shortest route is:

1. **Import** the GitHub repo at [vercel.com/new](https://vercel.com/new) and click **Deploy**.
   With no environment variables the app still deploys and runs — it falls back
   to an ephemeral SQLite DB under `/tmp` (data resets between invocations) and
   AI features stay locked until a key is added. Nothing to configure to see it live.
2. **To make it real**, add two env vars and redeploy:
   - `DATABASE_URL` → a PostgreSQL URL (persists data)
   - `GEMINI_API_KEY` → enables AI features

Everything below is the detailed version of these steps.

---

## 1. How it fits together

| Piece | File |
|-------|------|
| Serverless entry (exports the ASGI `app`) | `api/index.py` |
| Build + routing config | `vercel.json` |
| Python dependencies (Vercel reads root) | `requirements.txt` → `backend/requirements.txt` |
| Backend app (bundled via `includeFiles`) | `backend/app/**` |
| Frontend build output | `frontend/dist` |

`vercel.json` builds the frontend, serves it statically, rewrites `/api/*` to the
FastAPI function (which keeps the original path so its `/api/...` routes match),
and falls back to `index.html` for client-side routes.

---

## 2. Run locally (unchanged)

```powershell
# backend
cd backend
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal) — proxies /api to the backend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Local development uses SQLite automatically.

---

## 3. Create a PostgreSQL database

Serverless functions have an ephemeral, read-only filesystem, so **production
must use PostgreSQL** (SQLite cannot persist). Any managed provider works:

- **Vercel Postgres** (Storage tab) — exposes `POSTGRES_URL`, picked up
  automatically.
- **Neon** / **Supabase** — copy the connection string.

The app accepts `DATABASE_URL` (or Vercel's `POSTGRES_URL`) and normalizes
`postgres://` / `postgresql://` to the psycopg driver automatically. Use a
**pooled** connection string and keep `?sslmode=require`, e.g.:

```
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
```

---

## 4. Set environment variables (Vercel → Project → Settings → Environment Variables)

| Variable | Value |
|----------|-------|
| `APP_ENV` | `production` |
| `DATABASE_URL` | your PostgreSQL URL (skip if using Vercel Postgres's `POSTGRES_URL`) |
| `GEMINI_API_KEY` | your Google Gemini key |
| `SECRET_KEY` | a random string (`python -c "import secrets;print(secrets.token_urlsafe(48))"`) |
| `ALLOWED_ORIGINS` | usually unnecessary (UI is same-origin); set to your domain if calling the API cross-origin |

Never commit secrets. `GEMINI_API_KEY` is read from the environment (there is no
OS credential store on serverless).

---

## 5. Deploy

1. Push the repo to GitHub/GitLab/Bitbucket.
2. In Vercel: **Add New → Project → Import** the repo.
3. Vercel reads `vercel.json` — leave the build settings as detected.
4. Add the environment variables from step 4.
5. **Deploy.**

---

## 6. Initialize the database schema

Tables + default sources are created automatically on the first request (the
serverless function runs an idempotent initializer on cold start). To provision
explicitly before going live, run the schema step locally against the production
database:

```powershell
cd backend
$env:DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
.\.venv\Scripts\python.exe manage.py initdb
```

Migrations are additive and non-destructive, so this is always safe to re-run.

---

## 7. Verify

- `https://<project>.vercel.app/api/health` → `{"status":"ok","database":"connected"}`
- `https://<project>.vercel.app/docs` → Swagger UI
- `https://<project>.vercel.app/` → the app loads; refreshing `/studio` works
- **Settings → AI Provider → Test connection** → confirms Gemini works

---

## 8. Serverless limitations (by design)

- **Background job queue is disabled** on serverless (no persistent event loop
  across invocations). Direct AI actions — trend analysis, content generation,
  research — run per request and work normally; the orchestrator "jobs" workflow
  is the only feature that needs a long-running host.
- **Function duration:** AI generation can take 10–30s. `vercel.json` sets
  `maxDuration: 60`; ensure your plan allows it (Hobby caps lower than Pro). If
  requests time out, generate individual modules rather than a full package, or
  run the backend on a long-running host (see `DEPLOYMENT_HOSTINGER.md`).
- **Ephemeral filesystem:** logs go to stdout (visible in Vercel logs); exports
  are generated in-memory and streamed; nothing is written to disk permanently.
- **Cold starts:** the first request after idle is slower while the function and
  DB connection warm up.

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `500` on `/api/*` | Check the function logs in the Vercel dashboard. Usually a bad `DATABASE_URL` or a missing env var. |
| `database "connected"` false / connection errors | Verify `DATABASE_URL`, that it's the **pooled** URL with `?sslmode=require`, and the DB allows external connections. |
| Build fails on frontend | Confirm `npm run build` works locally; Vercel runs `npm --prefix frontend install && npm --prefix frontend run build`. |
| `ModuleNotFoundError: app` | Ensure `vercel.json`'s `functions.includeFiles` is `backend/**` and `api/index.py` is present. |
| API calls 404 | Confirm the `/api/(.*)` rewrite in `vercel.json` and that FastAPI routes are under `/api`. |
| Blank page on refresh of a route | The `index.html` fallback rewrite handles this; redeploy if `vercel.json` changed. |
| AI request times out | Increase `maxDuration` (plan permitting) or generate smaller units of work. |
| "API key can't be stored" when saving in Settings | Expected on serverless — there's no OS credential store. Set `GEMINI_API_KEY` as an environment variable and redeploy instead of saving from the UI. Not a database issue. |
