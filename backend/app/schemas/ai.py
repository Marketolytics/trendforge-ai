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


class AIEnvelope(BaseModel):
    """Standard wrapper for every AI endpoint response."""

    kind: str
    trend_id: int
    prompt_version: str
    cached: bool
    generated_at: str
    data: dict


class AIStatus(BaseModel):
    configured: bool
    model: str


class PromptInfo(BaseModel):
    name: str
    version: str
    description: str
