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
  gemini_model: string;
}

// --- AI types -------------------------------------------------------------

export interface AiEnvelope<T> {
  kind: string;
  trend_id: number;
  prompt_version: string;
  cached: boolean;
  generated_at: string;
  data: T;
}

export interface AiStatus {
  configured: boolean;
  model: string;
}

export interface RelevanceHorizon {
  horizon: string;
  level: "high" | "medium" | "low" | string;
  note: string;
}

export interface FormatRecommendation {
  format: string;
  recommended: boolean;
  confidence: number;
  reason: string;
}

export interface OpportunityFactors {
  freshness: number;
  search_interest: number;
  competition: number;
  viewer_curiosity: number;
  shareability: number;
  emotional_impact: number;
  replay_potential: number;
  monetization_potential: number;
  evergreen_value: number;
}

export interface Opportunity {
  score: number;
  factors: OpportunityFactors;
  explanation: string;
}

export interface UniqueIdea {
  idea: string;
  angle: string;
  why: string;
}

export interface TrendAnalysis {
  intelligence: {
    what_happened: string;
    why_important: string;
    who_cares: string;
    is_growing: boolean;
    growth_reason: string;
  };
  relevance: RelevanceHorizon[];
  timeline: { stage: string; confidence: number; explanation: string };
  audience: {
    age_range: string;
    gaming_knowledge: string;
    intensity: string;
    region: string;
    search_intent: string;
    expected_emotion: string;
    presentation_style: string;
  };
  formats: FormatRecommendation[];
  opportunity: Opportunity;
  content_gap: {
    common_angles: string[];
    saturated_angles: string[];
    undercovered_angles: string[];
    unique_ideas: UniqueIdea[];
  };
}

export interface TrendSummary {
  short: string;
  detailed: string;
  creator: string;
  key_facts: string[];
  things_to_avoid: string[];
  potential_misinformation: string[];
  verified_sources: string[];
}

export interface Hook {
  text: string;
  type: string;
  click_potential: number;
}
export interface HooksData {
  hooks: Hook[];
}

export interface TitleItem {
  text: string;
  type: string;
  predicted_ctr: number;
}
export interface TitlesData {
  titles: TitleItem[];
}

export interface ThumbnailStrategy {
  concept: string;
  text: string;
  emotion: string;
  composition: string;
  background: string;
  subject_placement: string;
  color_direction: string;
  visual_hierarchy: string;
  alternates: { concept: string; text: string }[];
}

export interface ContentStrategy {
  shorts: { idea: string; hook_angle: string; rank: number }[];
  long_videos: { idea: string; angle: string; rank: number }[];
  community_posts: { text: string; rank: number }[];
  x_posts: { text: string; rank: number }[];
  instagram_carousels: { concept: string; slides: string[]; rank: number }[];
  livestreams: { concept: string; rank: number }[];
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

  updateSettings: (values: Partial<AppSettings>) =>
    request<AppSettings>("/api/settings", {
      method: "PUT",
      body: JSON.stringify(values),
    }),

  clearCache: () => request<{ cleared: number }>("/api/cache/clear", { method: "POST" }),
};

// --- AI API ---------------------------------------------------------------

function aiPost<T>(kind: string, trendId: number, force: boolean) {
  return request<AiEnvelope<T>>(
    `/api/ai/${kind}/${trendId}${query({ force: force ? "true" : undefined })}`,
    { method: "POST" },
  );
}

export const aiApi = {
  status: () => request<AiStatus>("/api/ai/status"),
  analyze: (id: number, force = false) => aiPost<TrendAnalysis>("analyze", id, force),
  summary: (id: number, force = false) => aiPost<TrendSummary>("summary", id, force),
  opportunity: (id: number, force = false) => aiPost<Opportunity>("opportunity", id, force),
  strategy: (id: number, force = false) => aiPost<ContentStrategy>("strategy", id, force),
  hooks: (id: number, force = false) => aiPost<HooksData>("hooks", id, force),
  titles: (id: number, force = false) => aiPost<TitlesData>("titles", id, force),
  thumbnail: (id: number, force = false) => aiPost<ThumbnailStrategy>("thumbnail", id, force),
};
