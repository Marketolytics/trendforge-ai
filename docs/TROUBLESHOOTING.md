# Troubleshooting

## The UI says "Couldn't reach the backend"

The backend isn't running or is on a different port.
- Make sure the backend is started (`scripts\backend.ps1`) and listening on
  http://localhost:8000 — open http://localhost:8000/api/health to confirm.
- Click **Retry connection** on the startup screen.
- Check the logs at `backend/data/logs/trendforge.log`.
- If you changed the backend port, set `VITE_API_PROXY_TARGET` (dev) or
  `VITE_API_BASE_URL` (build) so the frontend targets the right origin.

## Port already in use

Another process holds port 8000 or 5173. Stop it, or run the backend on a
different port (`uvicorn app.main:app --reload --port 8010`) and update
`VITE_API_PROXY_TARGET` accordingly.

## "No AI provider configured" / AI tabs are locked

Open **Settings → AI Provider**, add an API key, and **Test connection**.
Collection and research work without a key; only AI generation requires one.

## Connection test fails with "API key not valid"

Double-check the key and that the selected provider matches it (a Gemini key
won't work under the OpenAI provider). For local providers (Ollama, LM Studio),
make sure the local server is running on its default port.

## Trends don't refresh / a source fails

Some sources rate-limit or change feeds. Open the **Developer panel**
(`Ctrl+Shift+D`) → logs, or check `backend/data/logs/trendforge.log`. Individual
source failures don't stop a refresh; other sources still return results.

## Nothing happens after generating a workflow

Watch the **Job Monitor** (bottom-right). If a job fails, it shows the error and
a **Retry** button. Without an AI key, jobs fail fast with an "add key" message.

## Reset the application

Stop the backend and either delete `backend/data/` (removes ALL local data) or
just `backend/data/trendforge.db` (keeps exports/backups but clears data).

## Where are the logs?

`backend/data/logs/` — `trendforge.log` (all) and `errors.log` (warnings and
errors). The **Developer panel** shows the live tail and the exact workspace/log
paths.
