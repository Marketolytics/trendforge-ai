/**
 * Backend readiness.
 *
 * This is a pure web application: the frontend talks to the FastAPI backend
 * over HTTP. In development the Vite dev server proxies `/api` to the backend,
 * and in production both can be served from the same origin. The API base URL
 * can be overridden via the `VITE_API_BASE_URL` environment variable.
 */

import { getApiBaseUrl } from "@/lib/api";

/**
 * Resolve the backend base URL. Kept for API compatibility with the startup
 * flow; the URL is configured statically via the environment / dev proxy.
 */
export async function resolveBackendUrl(): Promise<string> {
  return getApiBaseUrl();
}

/** Poll the backend health endpoint until it responds or attempts run out. */
export async function waitForBackend(attempts = 40, delayMs = 500): Promise<boolean> {
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/health`, {
        signal: AbortSignal.timeout(2000),
      });
      if (res.ok) return true;
    } catch {
      /* not up yet */
    }
    await new Promise((r) => setTimeout(r, delayMs));
  }
  return false;
}
