/**
 * Single typed client for the local FastAPI backend.
 * All backend communication funnels through here.
 */

const DEFAULT_BASE_URL = "http://127.0.0.1:8756";

// The backend URL is resolved at startup (auto-discovered under Tauri, or the
// default in the browser). It's mutable so the desktop launcher can point the
// UI at whichever local port the backend actually bound to.
let _apiBaseUrl =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE_URL;

export function getApiBaseUrl(): string {
  return _apiBaseUrl;
}

export function setApiBaseUrl(url: string): void {
  _apiBaseUrl = url.replace(/\/$/, "");
}

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
  language: string;
  output_folder: string;
  log_level: string;
  notifications: boolean;
  developer_mode: boolean;
  experimental: boolean;
  auto_backup: boolean;
  update_url: string;
  gemini_api_key: string;
  gemini_api_key_set: boolean;
  gemini_model: string;
}

// --- AI types -------------------------------------------------------------

export interface AiEnvelope<T> {
  kind: string;
  trend_id: number;
  variant?: string;
  prompt_version: string;
  cached: boolean;
  generated_at: string;
  generation_ms?: number;
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

// --- Content Factory (Sprint 4) types -------------------------------------

export interface FormatInfo {
  key: string;
  label: string;
  seconds: number;
  kind: "short" | "long" | string;
}

export interface FormatsResponse {
  formats: FormatInfo[];
  voice_styles: string[];
  default: string;
}

export interface ScriptSegment {
  label: string;
  text: string;
  seconds: number;
  retention_marker: string;
}
export interface Script {
  format: string;
  estimated_seconds: number;
  hook: string;
  segments: ScriptSegment[];
  climax: string;
  cta: string;
  full_script: string;
  retention_markers: string[];
  pacing_notes: string;
}

export interface Scene {
  number: number;
  duration_seconds: number;
  narration: string;
  visual: string;
  camera_angle: string;
  emotion: string;
  transition: string;
  sound_effect: string;
  animation_notes: string;
}
export interface Storyboard {
  scenes: Scene[];
  total_seconds: number;
}

export interface ContinuityBible {
  character_name: string;
  character_appearance: string;
  clothing: string;
  hair: string;
  environment: string;
  time_of_day: string;
  lighting: string;
  camera_lens: string;
  mood: string;
  color_palette: string;
  vehicle_position: string;
  weather: string;
}

export interface ImagePrompt {
  scene_number: number;
  prompt: string;
  [key: string]: string | number;
}
export interface ImagePrompts {
  character_reference: string;
  scenes: ImagePrompt[];
}

export interface VideoPrompt {
  scene_number: number;
  prompt: string;
  camera_motion: string;
  animation: string;
  object_motion: string;
  facial_expressions: string;
  transitions: string;
  physics: string;
  continuity_note: string;
  veo: string;
  runway: string;
  pika: string;
  luma: string;
  [key: string]: string | number;
}
export interface VideoPrompts {
  scenes: VideoPrompt[];
}

export interface VoiceOver {
  style: string;
  full_narration: string;
  segments: { scene_number: number; text: string; direction: string }[];
  tips: string[];
}

export interface BRoll {
  suggestions: { category: string; description: string; timing: string }[];
}

export interface ThumbnailBlueprint {
  main_subject: string;
  emotion: string;
  background: string;
  lighting: string;
  text: string;
  font_style: string;
  arrow_placement: string;
  highlight_objects: string[];
  color_contrast: string;
  ctr_prediction: number;
  notes: string;
}

export interface SEOPackage {
  title_variations: string[];
  description: string;
  tags: string[];
  keywords: string[];
  hashtags: string[];
  pinned_comment: string;
  community_poll: { question: string; options: string[] };
  playlist_recommendation: string;
}

export interface ProductionChecklist {
  voice_over: string;
  visual_assets: string[];
  image_prompts: string;
  video_prompts: string;
  thumbnail: string;
  music_style: string;
  sound_effects: string[];
  editing_notes: string[];
  subtitle_style: string;
  final_review: string[];
}

export type ModuleKind =
  | "script"
  | "storyboard"
  | "continuity"
  | "image_prompts"
  | "video_prompts"
  | "voiceover"
  | "broll"
  | "thumbnail_blueprint"
  | "seo_package"
  | "checklist";

export interface PackageResponse {
  trend_id: number;
  variant: string;
  format: string;
  modules: Partial<Record<ModuleKind, AiEnvelope<Record<string, unknown>>>>;
  failures: { kind: string; error: string }[];
}

const MODULE_PATHS: Record<ModuleKind, string> = {
  script: "script",
  storyboard: "storyboard",
  continuity: "continuity",
  image_prompts: "image-prompts",
  video_prompts: "video-prompts",
  voiceover: "voiceover",
  broll: "broll",
  thumbnail_blueprint: "thumbnail-blueprint",
  seo_package: "seo",
  checklist: "checklist",
};

interface ModuleOpts {
  format: string;
  voiceStyle?: string;
  force?: boolean;
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
    res = await fetch(`${getApiBaseUrl()}${path}`, {
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

// --- Studio / Content Factory API -----------------------------------------

export const studioApi = {
  formats: () => request<FormatsResponse>("/api/ai/formats"),

  getPackage: (trendId: number, format: string) =>
    request<PackageResponse>(`/api/ai/package/${trendId}${query({ format })}`),

  generatePackage: (trendId: number, opts: ModuleOpts) =>
    request<PackageResponse>(
      `/api/ai/package/${trendId}${query({
        format: opts.format,
        voice_style: opts.voiceStyle,
        force: opts.force ? "true" : undefined,
      })}`,
      { method: "POST" },
    ),

  generateModule: (kind: ModuleKind, trendId: number, opts: ModuleOpts) =>
    request<AiEnvelope<Record<string, unknown>>>(
      `/api/ai/${MODULE_PATHS[kind]}/${trendId}${query({
        format: opts.format,
        voice_style: kind === "voiceover" ? opts.voiceStyle : undefined,
        force: opts.force ? "true" : undefined,
      })}`,
      { method: "POST" },
    ),

  exportPackageUrl: (trendId: number, format: string) =>
    `${getApiBaseUrl()}/api/ai/export/${trendId}${query({ format })}`,

  exportModuleUrl: (
    trendId: number,
    kind: ModuleKind,
    format: string,
    fmt: "md" | "json" = "md",
  ) => `${getApiBaseUrl()}/api/ai/export/${trendId}/${kind}${query({ format, fmt })}`,
};

// --- Sprint 5: Creator Intelligence types --------------------------------

export interface CompetitorChannel {
  id: number;
  channel_id: string;
  name: string;
  handle: string;
  thumbnail: string | null;
  category: string;
  video_count: number;
  last_refreshed: string | null;
  created_at: string;
}

export interface CompetitorVideo {
  id: number;
  channel_pk: number;
  video_id: string;
  title: string;
  url: string | null;
  thumbnail: string | null;
  published: string | null;
  views: number;
  likes: number | null;
  comments: number | null;
  duration_seconds: number | null;
  category: string;
}

export interface Patterns {
  total_videos: number;
  avg_views?: number;
  median_views?: number;
  max_views?: number;
  top_videos?: { title: string; views: number; url: string | null; thumbnail: string | null }[];
  upload_days?: Record<string, number>;
  upload_hours?: Record<string, number>;
  best_day?: string | null;
  best_hour?: number | null;
  frequency_per_week?: number | null;
  title_keywords?: { word: string; count: number }[];
  common_caps_words?: { word: string; count: number }[];
}

export interface Analytics {
  trends_today: number;
  total_trends: number;
  ai_generations: number;
  competitors: number;
  content_packages: number;
  top_categories: { category: string; count: number }[];
  generations_by_kind: { kind: string; count: number }[];
  most_used_hooks: { type: string; count: number }[];
  weekly_activity: { day: string; count: number }[];
  top_opportunities: { id: number; title: string; score: number; source: string }[];
}

export interface FavoriteItem {
  id: number;
  type: string;
  label: string;
  ref_id: number | null;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface ProjectItem {
  trend_id: number | null;
  variant: string;
  title: string;
  modules: string[];
  module_count: number;
  updated_at: string | null;
  total_generation_ms: number;
}

export interface ForecastHorizon {
  horizon: string;
  direction: "rising" | "flat" | "declining" | string;
  likelihood: number;
  note: string;
}
export interface TrendForecast {
  forecast_score: number;
  confidence: number;
  horizons: ForecastHorizon[];
  reasoning: string;
}

export interface UploadAdvice {
  best_day: string;
  best_time: string;
  ideal_length: string;
  posting_frequency: string;
  best_format: string;
  target_audience: string;
  reasoning: string;
}

export interface GapItem {
  text: string;
  rank: number;
  why: string;
}
export interface CompetitorGap {
  untapped_angles: GapItem[];
  under_explored_questions: GapItem[];
  new_perspectives: GapItem[];
  emerging_discussions: GapItem[];
}

export interface MultiIdeas {
  shorts: { idea: string; hook_angle: string; rank: number }[];
  long_videos: { idea: string; angle: string; rank: number }[];
  community_posts: { text: string; rank: number }[];
  x_posts: { text: string; rank: number }[];
  reels: { idea: string; rank: number }[];
  carousels: { concept: string; slides: string[]; rank: number }[];
  livestreams: { concept: string; rank: number }[];
}

export const competitorsApi = {
  list: () => request<CompetitorChannel[]>("/api/competitors"),
  add: (handle: string, category = "general") =>
    request<CompetitorChannel>("/api/competitors", {
      method: "POST",
      body: JSON.stringify({ handle, category }),
    }),
  refreshAll: () => request<{ channels: number; new_videos: number }>("/api/competitors/refresh", { method: "POST" }),
  refreshOne: (pk: number) =>
    request<{ new_videos: number }>(`/api/competitors/${pk}/refresh`, { method: "POST" }),
  remove: (pk: number) => request<void>(`/api/competitors/${pk}`, { method: "DELETE" }),
  videos: (pk?: number) =>
    request<CompetitorVideo[]>(pk != null ? `/api/competitors/${pk}/videos` : "/api/competitors/videos"),
  patterns: (pk?: number) =>
    request<Patterns>(`/api/competitors/patterns${query({ channel_pk: pk })}`),
};

export const favoritesApi = {
  list: (type?: string, q?: string) =>
    request<FavoriteItem[]>(`/api/favorites${query({ type, q })}`),
  add: (fav: { type: string; label: string; ref_id?: number; payload?: Record<string, unknown> }) =>
    request<FavoriteItem>("/api/favorites", { method: "POST", body: JSON.stringify(fav) }),
  remove: (id: number) => request<void>(`/api/favorites/${id}`, { method: "DELETE" }),
};

export const intelligenceApi = {
  analytics: () => request<Analytics>("/api/intelligence/analytics"),
  projects: (q?: string, sort: "recent" | "modules" | "title" = "recent") =>
    request<ProjectItem[]>(`/api/intelligence/projects${query({ q, sort })}`),
};

export const insightApi = {
  forecast: (id: number, force = false) =>
    request<AiEnvelope<TrendForecast>>(`/api/ai/forecast/${id}${query({ force: force ? "true" : undefined })}`, { method: "POST" }),
  uploadAdvisor: (id: number, force = false) =>
    request<AiEnvelope<UploadAdvice>>(`/api/ai/upload-advisor/${id}${query({ force: force ? "true" : undefined })}`, { method: "POST" }),
  competitorGap: (id: number, force = false) =>
    request<AiEnvelope<CompetitorGap>>(`/api/ai/competitor-gap/${id}${query({ force: force ? "true" : undefined })}`, { method: "POST" }),
  multiIdeas: (id: number, force = false) =>
    request<AiEnvelope<MultiIdeas>>(`/api/ai/multi-ideas/${id}${query({ force: force ? "true" : undefined })}`, { method: "POST" }),
};

// --- Sprint 6: Orchestrator & developer types ----------------------------

export interface WorkflowTemplate {
  name: string;
  label: string;
  description: string;
  default_format: string | null;
  agents: string[];
}

export interface JobStep {
  key: string;
  label: string;
  status: "pending" | "running" | "done" | "failed" | "skipped" | string;
  attempts: number;
  duration_ms: number;
  error: string | null;
}

export interface Job {
  id: string;
  workflow: string;
  trend_id: number | null;
  variant: string;
  status: "queued" | "running" | "paused" | "completed" | "failed" | "cancelled" | string;
  progress: number;
  current_step: string;
  steps: JobStep[];
  result: Record<string, unknown>;
  error: string | null;
  eta_seconds: number | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface JobCreate {
  workflow: string;
  trend_id: number;
  format?: string;
  voice_style?: string;
  force?: boolean;
  priority?: number;
}

export interface DevStats {
  cache: { total: number; fresh: number; expired: number };
  queue: { queue_size: number; worker_running: boolean; by_status: Record<string, number>; total: number };
  db: Record<string, number>;
  prompts: { name: string; version: string; description: string }[];
  model: string;
}

const ACTIVE_JOB_STATES = ["queued", "running", "paused"];
export function isActiveJob(job: Job): boolean {
  return ACTIVE_JOB_STATES.includes(job.status);
}

export const orchestratorApi = {
  workflows: () => request<WorkflowTemplate[]>("/api/workflows"),
  createJob: (payload: JobCreate) =>
    request<Job>("/api/jobs", { method: "POST", body: JSON.stringify(payload) }),
  listJobs: (status?: string, limit = 30) =>
    request<Job[]>(`/api/jobs${query({ status, limit })}`),
  getJob: (id: string) => request<Job>(`/api/jobs/${id}`),
  cancel: (id: string) => request<{ ok: boolean }>(`/api/jobs/${id}/cancel`, { method: "POST" }),
  pause: (id: string) => request<{ ok: boolean }>(`/api/jobs/${id}/pause`, { method: "POST" }),
  resume: (id: string) => request<{ ok: boolean }>(`/api/jobs/${id}/resume`, { method: "POST" }),
  retry: (id: string) => request<{ ok: boolean }>(`/api/jobs/${id}/retry`, { method: "POST" }),
};

export const devApi = {
  stats: () => request<DevStats>("/api/dev/stats"),
  logs: (lines = 120) => request<{ lines: string[] }>(`/api/dev/logs${query({ lines })}`),
  prompt: (name: string) =>
    request<{ name: string; version: string; description: string; temperature: number; variables: string[]; body: string }>(
      `/api/dev/prompts/${name}`,
    ),
  previewPrompt: (name: string, trendId: number, format = "60s") =>
    request<{ valid: boolean; missing: string[]; variables: string[]; rendered: string }>(
      `/api/dev/prompts/${name}/preview${query({ trend_id: trendId, format })}`,
      { method: "POST" },
    ),
  generations: (params: { trend_id?: number; kind?: string; limit?: number } = {}) =>
    request<
      { id: number; trend_id: number | null; kind: string; variant: string; prompt_version: string; prompt_chars: number; response_chars: number; duration_ms: number; created_at: string }[]
    >(`/api/dev/generations${query(params)}`),
  generation: (id: number) =>
    request<{ id: number; kind: string; prompt_text: string; response: Record<string, unknown> }>(
      `/api/dev/generations/${id}`,
    ),
};

// --- Sprint 7: Research types --------------------------------------------

export interface ResearchMember {
  trend_id: number;
  title: string;
  summary: string | null;
  source: string;
  source_type: string;
  url: string | null;
  published: string | null;
  tier: string;
  tier_label: string;
  score: number;
}

export interface ResearchSource {
  source: string;
  source_type: string;
  tier: string;
  tier_label: string;
  score: number;
  count: number;
  latest: string | null;
}

export interface TimelineEvent {
  time: string | null;
  source: string;
  title: string;
  tier: string;
}

export interface ResearchBase {
  seed_trend_id: number;
  title: string;
  member_count: number;
  members: ResearchMember[];
  sources: ResearchSource[];
  timeline: TimelineEvent[];
  keywords: {
    trending: { word: string; count: number }[];
    search_phrases: string[];
    emerging: string[];
    topic_clusters: { label: string; keywords: string[] }[];
  };
  entities: {
    platforms: string[];
    companies: string[];
    topics: { name: string; count: number }[];
  };
  related_stories: { id: number; title: string; source: string }[];
  graph: { nodes: { id: string; label: string; type: string }[]; edges: { from: string; to: string }[] };
  research_confidence: number;
  built_at: string;
}

export interface ResearchAI {
  facts: {
    confirmed: string[];
    unconfirmed_claims: string[];
    rumors: string[];
    developer_statements: string[];
    quotes: string[];
    dates: string[];
    locations: string[];
  };
  entities: Record<string, string[]>;
  keywords: {
    trending: string[];
    search_phrases: string[];
    related_searches: string[];
    topic_clusters: string[];
    synonyms: string[];
    emerging: string[];
  };
  verification: {
    conflicts: string[];
    missing_information: string[];
    repeated_claims: string[];
    weak_evidence: string[];
    strong_evidence: string[];
    possible_misinformation: string[];
    confidence: number;
  };
  summaries: {
    executive: string;
    creator: string;
    technical: string;
    timeline: string;
    community: string;
  };
  outstanding_questions: string[];
  key_takeaways: string[];
  best_creator_angle: string;
  research_confidence: number;
}

export interface ResearchResponse {
  trend_id: number;
  base: ResearchBase;
  ai: ResearchAI | null;
}

export const researchApi = {
  list: () =>
    request<{ trend_id: number; title: string; confidence: number; source_count: number; updated_at: string }[]>(
      "/api/research",
    ),
  get: (trendId: number, rebuild = false) =>
    request<ResearchResponse>(`/api/research/${trendId}${query({ rebuild: rebuild ? "true" : undefined })}`),
  build: (trendId: number) =>
    request<ResearchResponse>(`/api/research/${trendId}/build`, { method: "POST" }),
  enrich: (trendId: number, force = false) =>
    request<AiEnvelope<ResearchAI>>(`/api/ai/research/${trendId}${query({ force: force ? "true" : undefined })}`, {
      method: "POST",
    }),
};

// --- Sprint 8: search, system, backup ------------------------------------

export interface SearchResult {
  type: "trend" | "research" | "favorite" | "content" | string;
  id: number | null;
  title: string;
  subtitle: string;
  variant?: string;
}

export const searchApi = {
  search: (q: string) => request<{ query: string; results: SearchResult[] }>(`/api/search${query({ q })}`),
};

export interface VersionInfo {
  name: string;
  version: string;
}
export interface UpdateInfo {
  current: string;
  latest: string;
  update_available: boolean;
  checked: boolean;
  error?: string;
}

export interface HealthReport {
  backend: string;
  database: string;
  cache: string;
  workspace: string;
  ai_provider: { configured: boolean; provider: string };
  network: string;
  first_run: boolean;
  issues: string[];
  healthy: boolean;
}

export interface Diagnostics {
  version: string;
  backend_port: number;
  workspace: Record<string, string>;
  database_path: string;
  log_dir: string;
  ai_provider: { provider: string; configured: boolean; models: Record<string, string> };
  cache: { total: number; fresh: number; expired: number };
  queue: { queue_size: number; worker_running: boolean; by_status: Record<string, number>; total: number };
  running_jobs: number;
}

export const systemApi = {
  version: () => request<VersionInfo>("/api/version"),
  updateCheck: () => request<UpdateInfo>("/api/update-check", { method: "POST" }),
  healthReport: () => request<HealthReport>("/api/system/health-report"),
  diagnostics: () => request<Diagnostics>("/api/system/diagnostics"),
};

export const backupApi = {
  downloadUrl: () => `${getApiBaseUrl()}/api/backup`,
  restore: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${getApiBaseUrl()}/api/backup/restore`, { method: "POST", body: form });
    if (!res.ok) throw new ApiError(`Restore failed (${res.status})`, res.status);
    return res.json() as Promise<{ ok: boolean; restart_recommended: boolean }>;
  },
  exportProjectUrl: (trendId: number) => `${getApiBaseUrl()}/api/backup/project/${trendId}`,
  importProject: (bundle: unknown) =>
    request<{ ok: boolean; trend_id: number }>("/api/backup/project", {
      method: "POST",
      body: JSON.stringify(bundle),
    }),
};

// --- Sprint 9: AI providers ----------------------------------------------

export interface ProviderInfo {
  name: string;
  label: string;
  requires_key: boolean;
  base_url: string;
  default_models: string[];
  key_set: boolean;
  configured: boolean;
  active: boolean;
}

export interface ProviderConfig {
  provider: string;
  models: { research: string; content: string; quality: string };
}

export interface ConnectionTest {
  ok: boolean;
  latency_ms: number;
  models: { id: string; label: string }[];
  error: string | null;
}

export interface ProviderUsageRow {
  provider: string;
  requests: number;
  prompt_tokens: number;
  response_tokens: number;
  total_tokens: number;
  last_success: string | null;
}

export const providersApi = {
  list: () => request<{ active: string; providers: ProviderInfo[] }>("/api/providers"),
  getConfig: () => request<ProviderConfig>("/api/providers/config"),
  setConfig: (cfg: Partial<{ provider: string; model_research: string; model_content: string; model_quality: string }>) =>
    request<ProviderConfig>("/api/providers/config", { method: "PUT", body: JSON.stringify(cfg) }),
  setKey: (name: string, key: string) =>
    request<{ ok: boolean; key_set: boolean }>(`/api/providers/${name}/key`, {
      method: "POST",
      body: JSON.stringify({ key }),
    }),
  deleteKey: (name: string) =>
    request<{ ok: boolean; key_set: boolean }>(`/api/providers/${name}/key`, { method: "DELETE" }),
  test: (name: string) => request<ConnectionTest>(`/api/providers/${name}/test`, { method: "POST" }),
  usage: () =>
    request<{ active_provider: string; models: Record<string, string>; usage: ProviderUsageRow[] }>(
      "/api/providers/usage",
    ),
};
