/**
 * Single typed client for the local FastAPI backend.
 * All backend communication funnels through here.
 */

const DEFAULT_BASE_URL = "http://127.0.0.1:8756";

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE_URL;

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  database: string;
  timestamp: string;
}

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
  } catch (err) {
    throw new ApiError(
      "Cannot reach the backend. Is the TrendForge service running?",
    );
  }

  if (!res.ok) {
    throw new ApiError(`Request failed (${res.status})`, res.status);
  }

  return (await res.json()) as T;
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),
};
