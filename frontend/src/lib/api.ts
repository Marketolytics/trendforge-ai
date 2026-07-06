/**
 * Single typed client for the local FastAPI backend.
 * All backend communication funnels through here.
 */

const DEFAULT_BASE_URL = "http://127.0.0.1:8756";

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE_URL;

// --- Types ----------------------------------------------------------------

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  database: string;
  timestamp: string;
}

export interface Trend {
  id: number;
  title: string;
  summary: string | null;
  url: string | null;
  source: string;
  source_type: string;
  published_time: string | null;
  category: string;
  keywords: string[];
  popularity_score: number;
  image_url: string | null;
  language: string;
  region: string;
  cluster_size: number;
  score: number;
  collection_timestamp: string;
}

export interface TrendListResponse {
  trends: Trend[];
  count: number;
  generated_at: string;
}

export interface RefreshResponse {
  status: "success" | "partial" | "error";
  trends_collected: number;
  raw_items: number;
  sources_ok: number;
  sources_failed: number;
  duration_ms: number;
  failures: { source: string; error: string }[];
}

export interface Source {
  id: number;
  name: string;
  type: string;
  category: string;
  config: Record<string, unknown>;
  enabled: boolean;
  created_at: string;
}

export interface HistoryEntry {
  id: number;
  event: string;
  status: string;
  trends_collected: number;
  sources_ok: number;
  sources_failed: number;
  duration_ms: number;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface AppSettings {
  refresh_interval: number;
  cache_duration: number;
  theme: string;
  output_folder: string;
  log_level: string;
  gemini_api_key: string;
  gemini_api_key_set: boolean;
}

// --- Error + request helper ----------------------------------------------

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(
      "Cannot reach the backend. Is the TrendForge service running?",
    );
  }

  if (!res.ok) {
    throw new ApiError(`Request failed (${res.status})`, res.status);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

function query(params: Record<string, string | number | undefined>): string {
  const usable = Object.entries(params).filter(([, v]) => v !== undefined);
  if (usable.length === 0) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of usable) sp.set(k, String(v));
  return `?${sp.toString()}`;
}

// --- API surface ----------------------------------------------------------

export const api = {
  health: () => request<HealthResponse>("/api/health"),

  getTrends: (params: { limit?: number; category?: string; source?: string } = {}) =>
    request<TrendListResponse>(`/api/trends${query(params)}`),

  getTrend: (id: number) => request<Trend>(`/api/trends/${id}`),

  refreshTrends: (force = false) =>
    request<RefreshResponse>(`/api/trends/refresh${query({ force: force ? "true" : undefined })}`, {
      method: "POST",
    }),

  getSources: () => request<Source[]>("/api/sources"),

  getHistory: (limit = 25) => request<HistoryEntry[]>(`/api/history${query({ limit })}`),

  getSettings: () => request<AppSettings>("/api/settings"),

  clearCache: () => request<{ cleared: number }>("/api/cache/clear", { method: "POST" }),
};
