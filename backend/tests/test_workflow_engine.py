"""Workflow templates + orchestration engine (stubbed agents)."""

from __future__ import annotations

import pytest

from app.services.ai import analyzer
from app.services.orchestrator import engine as orchestrator
from app.services.orchestrator.workflows import WORKFLOWS, get_workflow


def test_workflow_registry():
    assert "complete" in WORKFLOWS
    wf = get_workflow("research_only")
    assert wf is not None
    assert "analysis" in wf.agent_keys


def test_create_job_builds_steps():
    job = orchestrator.create_job("storyboard_only", trend_id=1, format="60s")
    assert job["status"] == "queued"
    assert len(job["steps"]) == len(get_workflow("storyboard_only").agent_keys)


@pytest.mark.asyncio
async def test_run_job_completes_with_stubbed_agents(monkeypatch):
    async def fake_generate(trend_id, kind, *, params=None, force=False, job_id=None):
        return {"kind": kind, "data": {"ok": kind}}

    async def fake_opp(trend_id, *, force=False):
        return {"kind": "opportunity", "data": {"score": 1}}

    monkeypatch.setattr(analyzer, "generate", fake_generate)
    monkeypatch.setattr(analyzer, "get_opportunity", fake_opp)

    job = orchestrator.create_job("research_only", trend_id=1, format="60s")
    await orchestrator.run_job(job["id"])

    final = orchestrator._get(job["id"])
    assert final.status == "completed"
    assert final.progress == 1.0
    assert all(s["status"] == "done" for s in final.steps)


@pytest.mark.asyncio
async def test_failed_stage_marks_failure_and_retries(monkeypatch):
    async def failing(trend_id, kind, *, params=None, force=False, job_id=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(analyzer, "generate", failing)
    job = orchestrator.create_job("seo_only", trend_id=1, format="60s")
    await orchestrator.run_job(job["id"])
    final = orchestrator._get(job["id"])
    assert final.status == "failed"
    assert final.steps[0]["attempts"] == orchestrator.MAX_STAGE_ATTEMPTS
