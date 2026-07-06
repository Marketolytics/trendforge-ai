/**
 * Backend auto-discovery and readiness.
 *
 * In the browser we use the default local URL. Inside the Tauri desktop shell
 * the Rust launcher spawns the backend on a free port and exposes it via the
 * `get_backend_url` command, so the UI never needs a manually-entered URL.
 */

import { getApiBaseUrl, setApiBaseUrl } from "@/lib/api";

export function isTauri(): boolean {
  return typeof window !== "undefined" && "__TAURI__" in window;
}

/** Ask the desktop launcher which URL the backend bound to (Tauri only). */
export async function resolveBackendUrl(): Promise<string> {
  if (isTauri()) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      const url = await invoke<string>("get_backend_url");
      if (url) setApiBaseUrl(url);
    } catch {
      /* fall back to the default URL */
    }
  }
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
