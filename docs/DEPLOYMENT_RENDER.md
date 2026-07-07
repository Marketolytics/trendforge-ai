# Deploying TrendForge AI to Render

Render runs TrendForge as a **single always-on service**, so *every* feature works
— including the background job queue and long-running AI generations that
serverless platforms can't handle. One service serves the built React frontend,
the FastAPI API, and the worker; a managed PostgreSQL database persists your data.

```
Render Web Service (Docker, always-on)
  ├─ FastAPI (uvicorn)  ── serves /api/*  + the background job worker
  └─ built frontend     ── served at /  (SPA, same origin — no CORS)
        │
        └─► Render PostgreSQL (managed)         + Gemini API
```

This repo ships a `Dockerfile` and a `render.yaml` blueprint, so deployment is
almost entirely automatic.

---

## Option A — One-click Blueprint (recommended)

1. Push the repo to GitHub (already done: `Marketolytics/trendforge-ai`).
2. In Render: **New → Blueprint**.
3. Connect your GitHub account and select the `trendforge-ai` repo.
4. Render reads `render.yaml` and shows a plan:
   - a **web service** `trendforge` (Docker)
   - a **PostgreSQL** database `trendforge-db`
5. When prompted, set the one secret it can't generate:
   - **`GEMINI_API_KEY`** = your Google Gemini key
   (`APP_ENV`, `DATABASE_URL`, and `SECRET_KEY` are wired up automatically.)
6. Click **Apply**. Render builds the Docker image (frontend build + Python
   install), provisions the database, injects `DATABASE_URL`, and starts the
   service.

First boot runs the schema creation + seed automatically. When the health check
at `/api/health` passes, you're live at `https://trendforge.onrender.com` (your
exact URL is shown in the dashboard).

---

## Option B — Manual setup (without the blueprint)

1. **Create the database:** New → PostgreSQL → name it, pick a plan, create.
   Copy its **Internal Connection String**.
2. **Create the web service:** New → Web Service → connect the repo.
   - **Runtime:** Docker (Render auto-detects the `Dockerfile`).
   - **Health Check Path:** `/api/health`
3. **Environment variables** (service → Environment):
   | Key | Value |
   |-----|-------|
   | `APP_ENV` | `production` |
   | `DATABASE_URL` | the database's Internal Connection String |
   | `SECRET_KEY` | any long random string |
   | `GEMINI_API_KEY` | your Gemini key |
4. **Create Web Service** — it builds and deploys.

---

## Environment variables reference

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | Yes (prod) | Render Postgres connection string. `postgres://…` is auto-normalized to the psycopg driver. |
| `GEMINI_API_KEY` | For AI features | Set it here — **not** in the app's Settings UI (cloud hosts have no OS credential store). |
| `APP_ENV` | Recommended | `production` (enables security headers, terse errors). |
| `SECRET_KEY` | Recommended | Random string; the blueprint generates one for you. |
| `ALLOWED_ORIGINS` | No | Not needed — the UI is same-origin. Set only if you split the frontend onto another domain. |

---

## Plans & always-on behavior

- **Free plan:** the web service **sleeps after ~15 min of inactivity** and cold-
  starts on the next request. While asleep the background job worker is paused
  (queued jobs resume when it wakes). Free PostgreSQL expires after 90 days.
- **Starter plan (paid):** the service stays **always-on**, so the job queue runs
  24/7 and there are no cold starts. Recommended for real use.

Direct AI actions (analysis, content generation, research) work on either plan —
only the long-running background **jobs** feature benefits from always-on.

---

## Updating the app

`autoDeploy` is on, so every push to the connected branch triggers a rebuild and
redeploy. Database migrations are additive and run automatically on startup, so
schema changes apply on the next deploy without data loss.

To run a migration or seed manually (rare), use Render's **Shell** tab on the
service:

```bash
cd /app/backend
python manage.py migrate     # or: initdb / seed / check
```

---

## Verify the deployment

- `https://<service>.onrender.com/api/health` → `{"status":"ok","database":"connected"}`
- `https://<service>.onrender.com/docs` → Swagger UI
- `https://<service>.onrender.com/` → app loads; refreshing `/studio` works
- **Settings → AI Provider → Test connection** → confirms Gemini works
- Run a full **content package** in the Studio — this exercises the background
  worker end to end (works fully on Render, unlike serverless).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails at `npm run build` | Confirm `npm run build` works locally in `frontend/`. |
| Build fails installing Python deps | Check the build logs; ensure `backend/requirements.txt` is intact. |
| `database` not connected | Verify `DATABASE_URL` is set from the Render DB and the DB is in the same region as the service. |
| AI features locked / "not configured" | Set `GEMINI_API_KEY` in the service's Environment and redeploy. Don't save the key in the Settings UI. |
| Service returns 502 briefly after deploy | Normal during cold start / first boot while migrations run; the health check clears once ready. |
| Jobs don't progress on Free plan | The service slept; open the app to wake it, or upgrade to Starter for always-on. |
| First request slow | Free-plan cold start — upgrade to Starter to eliminate it. |

---

## Why Render (vs Vercel)

Vercel is serverless: great for the frontend and direct API calls, but it can't
run the persistent background worker and may time out on long AI packages. Render
runs a real long-lived process, so **all** features work. Use whichever fits — the
same codebase deploys to both (`docs/DEPLOYMENT_VERCEL.md`) and to Hostinger
(`docs/DEPLOYMENT_HOSTINGER.md`).
