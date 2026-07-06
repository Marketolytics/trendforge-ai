# Troubleshooting

## The app opens but says "Couldn't reach the backend"

The bundled backend didn't start or another process holds its port.
- Click **Retry connection** on the startup screen.
- Check the logs at `%LOCALAPPDATA%\TrendForge AI\logs\trendforge.log`.
- If another TrendForge instance is running, close it (the launcher reuses an
  existing backend, but a stuck process can block the port). End
  `trendforge-backend.exe` in Task Manager and relaunch.

## "No AI provider configured" / AI tabs are locked

Open **Settings → AI Provider**, add an API key, and **Test connection**.
Collection and research work without a key; only AI generation requires one.

## Connection test fails with "API key not valid"

Double-check the key and that the selected provider matches it (a Gemini key
won't work under the OpenAI provider). For local providers (Ollama, LM Studio),
make sure the local server is running on its default port.

## Trends don't refresh / a source fails

Some sources rate-limit or change feeds. Open the **Developer panel**
(`Ctrl+Shift+D`) → logs, or check `logs\trendforge.log`. Individual source
failures don't stop a refresh; other sources still return results.

## Nothing happens after generating a workflow

Watch the **Job Monitor** (bottom-right). If a job fails, it shows the error and
a **Retry** button. Without an AI key, jobs fail fast with an "add key" message.

## Reset the application

Close the app and either delete `%LOCALAPPDATA%\TrendForge AI` (removes ALL user
data) or just `trendforge.db` inside it (keeps exports/backups but clears data).

## Where are the logs?

`%LOCALAPPDATA%\TrendForge AI\logs\` — `trendforge.log` (all) and `errors.log`
(warnings and errors). The **Developer panel** shows the live tail and the exact
workspace/log paths.
