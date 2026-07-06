"""AI agent framework.

Every AI capability is an independent agent exposing a common interface:
``initialize`` / ``execute`` / ``validate`` (retry and cancel are coordinated by
the engine). Most agents are thin wrappers over ``analyzer.generate`` so there
is no duplicated logic — the agent layer only adds orchestration semantics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from app.services.ai import analyzer


@dataclass
class JobContext:
    """Shared context passed to every agent during a workflow run."""

    trend_id: int
    variant: str
    params: dict
    job_id: str
    force: bool = False
    is_cancelled: Callable[[], bool] = field(default=lambda: False)


@dataclass
class AgentResult:
    ok: bool
    data: dict = field(default_factory=dict)
    error: str | None = None
    issues: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Common interface for all agents."""

    key: str = "base"
    label: str = "Agent"

    async def initialize(self, ctx: JobContext) -> None:  # noqa: B027 - optional hook
        """Prepare resources before execution. Default: no-op."""

    @abstractmethod
    async def execute(self, ctx: JobContext) -> AgentResult:
        """Perform the agent's work and return a result."""

    def validate(self, result: AgentResult) -> tuple[bool, list[str]]:
        """Validate a result. Default: ok when data is non-empty."""
        if not result.ok:
            return False, [result.error or "execution failed"]
        if not result.data:
            return False, ["empty result"]
        return True, []


class GeneratorAgent(BaseAgent):
    """Wraps a single ``analyzer`` generator kind."""

    def __init__(self, kind: str, label: str) -> None:
        self.key = kind
        self.kind = kind
        self.label = label

    async def execute(self, ctx: JobContext) -> AgentResult:
        try:
            env = await analyzer.generate(
                ctx.trend_id, self.kind, params=ctx.params, force=ctx.force, job_id=ctx.job_id
            )
            return AgentResult(ok=True, data=env.get("data", {}))
        except Exception as exc:  # noqa: BLE001 - surfaced to engine for retry
            return AgentResult(ok=False, error=str(exc))


class OpportunityAgent(BaseAgent):
    """Derives the opportunity score from the (cached) analysis."""

    key = "opportunity"
    label = "Opportunity"

    async def execute(self, ctx: JobContext) -> AgentResult:
        try:
            env = await analyzer.get_opportunity(ctx.trend_id, force=ctx.force)
            return AgentResult(ok=True, data=env.get("data", {}))
        except Exception as exc:  # noqa: BLE001
            return AgentResult(ok=False, error=str(exc))


# Registry: agent key -> agent instance. Labels mirror the pipeline diagram.
_LABELS = {
    "analysis": "Trend Analysis",
    "competitor_gap": "Competition",
    "script": "Script",
    "storyboard": "Storyboard",
    "continuity": "Visual Director",
    "image_prompts": "Nano Banana Prompts",
    "video_prompts": "Video Prompts",
    "voiceover": "Voice Over",
    "broll": "B-Roll",
    "thumbnail_blueprint": "Thumbnail",
    "seo_package": "SEO",
    "checklist": "Checklist",
    "quality_review": "Quality Review",
    "forecast": "Forecast",
    "upload_advisor": "Upload Advisor",
    "multi_ideas": "Idea Slate",
}

AGENTS: dict[str, BaseAgent] = {"opportunity": OpportunityAgent()}
for _kind, _label in _LABELS.items():
    AGENTS[_kind] = GeneratorAgent(_kind, _label)


def get_agent(key: str) -> BaseAgent | None:
    return AGENTS.get(key)


def agent_label(key: str) -> str:
    agent = AGENTS.get(key)
    return agent.label if agent else key
