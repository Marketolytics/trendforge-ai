# Known Issues

## v1.0

- **Reddit metrics are limited.** Reddit's public JSON API blocks unauthenticated
  clients, so Reddit is collected via RSS. Exact upvote/comment counts aren't
  available; hot-rank is used as the popularity signal. Full metrics would require
  Reddit OAuth (a future optional credentialed source).

- **YouTube competitor metrics.** Competitor tracking uses YouTube's public RSS
  feeds — views are available, but likes/comments/duration are not (they need the
  official YouTube Data API). Those fields display as unavailable.

- **First AI request latency.** The first Gemini/OpenAI call after launch may take
  a few seconds while the provider client initializes. Results are cached, so
  repeats are instant.

- **Light theme.** The UI is dark-theme-first. A light theme is available in
  Settings but has received less visual polish than dark mode.

- **Update checker is opt-in.** Update checks only run if you set an update URL in
  Settings → Advanced. TrendForge never auto-updates and needs no online account.

- **Workspace must be writable.** The backend writes its workspace to
  `backend/data/` (or `TRENDFORGE_DATA_DIR`). If that path isn't writable the
  backend fails to start — check the Developer panel / logs for the resolved path.
