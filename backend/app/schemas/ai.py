"""Typed schemas for AI outputs.

Fields carry safe defaults so a slightly incomplete model response still
validates rather than failing the whole request.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- Trend analysis -------------------------------------------------------


class Intelligence(BaseModel):
    what_happened: str = ""
    why_important: str = ""
    who_cares: str = ""
    is_growing: bool = False
    growth_reason: str = ""


class RelevanceHorizon(BaseModel):
    horizon: str
    level: str = "medium"
    note: str = ""


class Timeline(BaseModel):
    stage: str = "starting"  # starting | peaking | declining | evergreen
    confidence: int = 0
    explanation: str = ""


class Audience(BaseModel):
    age_range: str = ""
    gaming_knowledge: str = ""
    intensity: str = "mixed"  # casual | hardcore | mixed
    region: str = ""
    search_intent: str = ""
    expected_emotion: str = ""
    presentation_style: str = ""


class FormatRecommendation(BaseModel):
    format: str
    recommended: bool = False
    confidence: int = 0
    reason: str = ""


class OpportunityFactors(BaseModel):
    freshness: int = 0
    search_interest: int = 0
    competition: int = 0
    viewer_curiosity: int = 0
    shareability: int = 0
    emotional_impact: int = 0
    replay_potential: int = 0
    monetization_potential: int = 0
    evergreen_value: int = 0


class Opportunity(BaseModel):
    score: int = 0
    factors: OpportunityFactors = Field(default_factory=OpportunityFactors)
    explanation: str = ""


class UniqueIdea(BaseModel):
    idea: str
    angle: str = ""
    why: str = ""


class ContentGap(BaseModel):
    common_angles: list[str] = Field(default_factory=list)
    saturated_angles: list[str] = Field(default_factory=list)
    undercovered_angles: list[str] = Field(default_factory=list)
    unique_ideas: list[UniqueIdea] = Field(default_factory=list)


class TrendAnalysis(BaseModel):
    intelligence: Intelligence = Field(default_factory=Intelligence)
    relevance: list[RelevanceHorizon] = Field(default_factory=list)
    timeline: Timeline = Field(default_factory=Timeline)
    audience: Audience = Field(default_factory=Audience)
    formats: list[FormatRecommendation] = Field(default_factory=list)
    opportunity: Opportunity = Field(default_factory=Opportunity)
    content_gap: ContentGap = Field(default_factory=ContentGap)


# --- Summary --------------------------------------------------------------


class TrendSummary(BaseModel):
    short: str = ""
    detailed: str = ""
    creator: str = ""
    key_facts: list[str] = Field(default_factory=list)
    things_to_avoid: list[str] = Field(default_factory=list)
    potential_misinformation: list[str] = Field(default_factory=list)
    verified_sources: list[str] = Field(default_factory=list)


# --- Content strategy -----------------------------------------------------


class ShortIdea(BaseModel):
    idea: str
    hook_angle: str = ""
    rank: int = 0


class LongIdea(BaseModel):
    idea: str
    angle: str = ""
    rank: int = 0


class RankedText(BaseModel):
    text: str
    rank: int = 0


class CarouselIdea(BaseModel):
    concept: str
    slides: list[str] = Field(default_factory=list)
    rank: int = 0


class LivestreamIdea(BaseModel):
    concept: str
    rank: int = 0


class ContentStrategy(BaseModel):
    shorts: list[ShortIdea] = Field(default_factory=list)
    long_videos: list[LongIdea] = Field(default_factory=list)
    community_posts: list[RankedText] = Field(default_factory=list)
    x_posts: list[RankedText] = Field(default_factory=list)
    instagram_carousels: list[CarouselIdea] = Field(default_factory=list)
    livestreams: list[LivestreamIdea] = Field(default_factory=list)


# --- Hooks ----------------------------------------------------------------


class Hook(BaseModel):
    text: str
    type: str = "curiosity"
    click_potential: int = 0


class Hooks(BaseModel):
    hooks: list[Hook] = Field(default_factory=list)


# --- Titles ---------------------------------------------------------------


class Title(BaseModel):
    text: str
    type: str = "seo"
    predicted_ctr: float = 0.0


class Titles(BaseModel):
    titles: list[Title] = Field(default_factory=list)


# --- Thumbnail ------------------------------------------------------------


class ThumbnailAlternate(BaseModel):
    concept: str
    text: str = ""


class ThumbnailStrategy(BaseModel):
    concept: str = ""
    text: str = ""
    emotion: str = ""
    composition: str = ""
    background: str = ""
    subject_placement: str = ""
    color_direction: str = ""
    visual_hierarchy: str = ""
    alternates: list[ThumbnailAlternate] = Field(default_factory=list)


# --- API envelopes --------------------------------------------------------


# ==========================================================================
# Sprint 4 — Content Factory modules
# ==========================================================================


class ScriptSegment(BaseModel):
    label: str = "Body"
    text: str = ""
    seconds: float = 0.0
    retention_marker: str = ""


class Script(BaseModel):
    format: str = ""
    estimated_seconds: int = 0
    hook: str = ""
    segments: list[ScriptSegment] = Field(default_factory=list)
    climax: str = ""
    cta: str = ""
    full_script: str = ""
    retention_markers: list[str] = Field(default_factory=list)
    pacing_notes: str = ""


class Scene(BaseModel):
    number: int = 0
    duration_seconds: float = 0.0
    narration: str = ""
    visual: str = ""
    camera_angle: str = ""
    emotion: str = ""
    transition: str = ""
    sound_effect: str = ""
    animation_notes: str = ""


class Storyboard(BaseModel):
    scenes: list[Scene] = Field(default_factory=list)
    total_seconds: float = 0.0


class ContinuityBible(BaseModel):
    character_name: str = ""
    character_appearance: str = ""
    clothing: str = ""
    hair: str = ""
    environment: str = ""
    time_of_day: str = ""
    lighting: str = ""
    camera_lens: str = ""
    mood: str = ""
    color_palette: str = ""
    vehicle_position: str = ""
    weather: str = ""


class ImagePrompt(BaseModel):
    scene_number: int = 0
    prompt: str = ""
    subject: str = ""
    environment: str = ""
    lighting: str = ""
    lens: str = ""
    camera_position: str = ""
    composition: str = ""
    art_direction: str = ""
    style: str = ""
    mood: str = ""
    color_palette: str = ""
    textures: str = ""
    motion: str = ""
    depth_of_field: str = ""
    consistency_notes: str = ""
    negative_prompt: str = ""
    quality_settings: str = ""
    aspect_ratio: str = "9:16"


class ImagePrompts(BaseModel):
    character_reference: str = ""
    scenes: list[ImagePrompt] = Field(default_factory=list)


class VideoPrompt(BaseModel):
    scene_number: int = 0
    prompt: str = ""
    camera_motion: str = ""
    animation: str = ""
    object_motion: str = ""
    facial_expressions: str = ""
    wind: str = ""
    lighting: str = ""
    environment: str = ""
    transitions: str = ""
    physics: str = ""
    realism: str = ""
    continuity_note: str = ""
    veo: str = ""
    runway: str = ""
    pika: str = ""
    luma: str = ""


class VideoPrompts(BaseModel):
    scenes: list[VideoPrompt] = Field(default_factory=list)


class VoiceSegment(BaseModel):
    scene_number: int = 0
    text: str = ""
    direction: str = ""


class VoiceOver(BaseModel):
    style: str = ""
    full_narration: str = ""
    segments: list[VoiceSegment] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)


class BRollItem(BaseModel):
    category: str = ""
    description: str = ""
    timing: str = ""


class BRoll(BaseModel):
    suggestions: list[BRollItem] = Field(default_factory=list)


class ThumbnailBlueprint(BaseModel):
    main_subject: str = ""
    emotion: str = ""
    background: str = ""
    lighting: str = ""
    text: str = ""
    font_style: str = ""
    arrow_placement: str = ""
    highlight_objects: list[str] = Field(default_factory=list)
    color_contrast: str = ""
    ctr_prediction: float = 0.0
    notes: str = ""


class CommunityPoll(BaseModel):
    question: str = ""
    options: list[str] = Field(default_factory=list)


class SEOPackage(BaseModel):
    title_variations: list[str] = Field(default_factory=list)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    pinned_comment: str = ""
    community_poll: CommunityPoll = Field(default_factory=CommunityPoll)
    playlist_recommendation: str = ""


class ProductionChecklist(BaseModel):
    voice_over: str = ""
    visual_assets: list[str] = Field(default_factory=list)
    image_prompts: str = ""
    video_prompts: str = ""
    thumbnail: str = ""
    music_style: str = ""
    sound_effects: list[str] = Field(default_factory=list)
    editing_notes: list[str] = Field(default_factory=list)
    subtitle_style: str = ""
    final_review: list[str] = Field(default_factory=list)


# ==========================================================================
# Sprint 5 — Creator intelligence
# ==========================================================================


class ForecastHorizon(BaseModel):
    horizon: str  # Tomorrow | 3 Days | 1 Week | 1 Month
    direction: str = "flat"  # rising | flat | declining
    likelihood: int = 0  # 0-100
    note: str = ""


class TrendForecast(BaseModel):
    forecast_score: int = 0
    confidence: int = 0
    horizons: list[ForecastHorizon] = Field(default_factory=list)
    reasoning: str = ""


class UploadAdvice(BaseModel):
    best_day: str = ""
    best_time: str = ""
    ideal_length: str = ""
    posting_frequency: str = ""
    best_format: str = ""
    target_audience: str = ""
    reasoning: str = ""


class GapItem(BaseModel):
    text: str
    rank: int = 0
    why: str = ""


class CompetitorGap(BaseModel):
    untapped_angles: list[GapItem] = Field(default_factory=list)
    under_explored_questions: list[GapItem] = Field(default_factory=list)
    new_perspectives: list[GapItem] = Field(default_factory=list)
    emerging_discussions: list[GapItem] = Field(default_factory=list)


class ReelIdea(BaseModel):
    idea: str
    rank: int = 0


class MultiIdeas(BaseModel):
    shorts: list[ShortIdea] = Field(default_factory=list)
    long_videos: list[LongIdea] = Field(default_factory=list)
    community_posts: list[RankedText] = Field(default_factory=list)
    x_posts: list[RankedText] = Field(default_factory=list)
    reels: list[ReelIdea] = Field(default_factory=list)
    carousels: list[CarouselIdea] = Field(default_factory=list)
    livestreams: list[LivestreamIdea] = Field(default_factory=list)


# ==========================================================================


class AIEnvelope(BaseModel):
    """Standard wrapper for every AI endpoint response."""

    kind: str
    trend_id: int
    variant: str = ""
    prompt_version: str
    cached: bool
    generated_at: str
    generation_ms: int = 0
    data: dict


class AIStatus(BaseModel):
    configured: bool
    model: str


class PromptInfo(BaseModel):
    name: str
    version: str
    description: str
