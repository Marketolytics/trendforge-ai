"""Reusable workflow templates.

A workflow is an ordered list of *groups*; agents within a group run in
parallel, groups run sequentially. New templates are added here without
touching the engine — the engine reads this registry generically.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Workflow:
    name: str
    label: str
    description: str
    groups: list[list[str]]  # sequential groups of parallel agent keys
    default_format: str | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def agent_keys(self) -> list[str]:
        return [k for group in self.groups for k in group]


WORKFLOWS: dict[str, Workflow] = {
    "complete": Workflow(
        name="complete",
        label="Complete Production Package",
        description="Full pipeline from research to quality review.",
        groups=[
            ["analysis"],
            ["opportunity", "competitor_gap"],
            ["script"],
            ["storyboard", "continuity"],
            ["image_prompts", "video_prompts"],
            ["voiceover", "broll", "thumbnail_blueprint", "seo_package"],
            ["checklist"],
            ["quality_review"],
        ],
        default_format="60s",
    ),
    "quick_short": Workflow(
        name="quick_short",
        label="Quick Short",
        description="Fast short-form package: script, storyboard, prompts, SEO.",
        groups=[
            ["script"],
            ["storyboard", "continuity"],
            ["image_prompts"],
            ["seo_package"],
            ["quality_review"],
        ],
        default_format="30s",
    ),
    "long_video": Workflow(
        name="long_video",
        label="Long Video",
        description="Long-form package with full storyboard and prompts.",
        groups=[
            ["analysis"],
            ["script"],
            ["storyboard", "continuity"],
            ["image_prompts", "video_prompts"],
            ["voiceover", "broll", "thumbnail_blueprint", "seo_package"],
            ["checklist"],
            ["quality_review"],
        ],
        default_format="5min",
    ),
    "research_only": Workflow(
        name="research_only",
        label="Research Only",
        description="Trend analysis, opportunity and competition gap.",
        groups=[["analysis"], ["opportunity", "competitor_gap"]],
    ),
    "storyboard_only": Workflow(
        name="storyboard_only",
        label="Storyboard Only",
        description="Script then storyboard.",
        groups=[["script"], ["storyboard"]],
        default_format="60s",
    ),
    "prompt_only": Workflow(
        name="prompt_only",
        label="Prompt Only",
        description="Script, storyboard, continuity then image + video prompts.",
        groups=[
            ["script"],
            ["storyboard", "continuity"],
            ["image_prompts", "video_prompts"],
        ],
        default_format="60s",
    ),
    "seo_only": Workflow(
        name="seo_only",
        label="SEO Only",
        description="Just the SEO package.",
        groups=[["seo_package"]],
        default_format="60s",
    ),
}


def get_workflow(name: str) -> Workflow | None:
    return WORKFLOWS.get(name)
