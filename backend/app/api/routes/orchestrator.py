"""Orchestrator: workflow templates + background jobs."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from app.db.models import Job
from app.db.session import engine
from app.services.orchestrator import engine as orchestrator
from app.services.orchestrator.workflows import WORKFLOWS

router = APIRouter(tags=["orchestrator"])


class WorkflowOut(BaseModel):
    name: str
    label: str
    description: str
    default_format: str | None
    agents: list[str]


class JobCreate(BaseModel):
    workflow: str
    trend_id: int
    format: str = "60s"
    voice_style: str = "Professional"
    force: bool = False
    priority: int = 5


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow: str
    trend_id: int | None
    variant: str
    status: str
    progress: float
    current_step: str
    steps: list
    result: dict
    error: str | None
    eta_seconds: int | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


@router.get("/workflows", response_model=list[WorkflowOut])
def list_workflows() -> list[WorkflowOut]:
    return [
        WorkflowOut(
            name=w.name,
            label=w.label,
            description=w.description,
            default_format=w.default_format,
            agents=w.agent_keys,
        )
        for w in WORKFLOWS.values()
    ]


@router.post("/jobs", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate) -> JobOut:
    try:
        job = orchestrator.create_job(
            payload.workflow,
            payload.trend_id,
            format=payload.format,
            voice_style=payload.voice_style,
            force=payload.force,
            priority=payload.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    orchestrator.enqueue(job["id"], payload.priority)
    return JobOut.model_validate(job)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    status: str | None = Query(None), limit: int = Query(30, ge=1, le=200)
) -> list[JobOut]:
    with Session(engine) as s:
        stmt = select(Job)
        if status:
            stmt = stmt.where(Job.status == status)
        stmt = stmt.order_by(Job.created_at.desc()).limit(limit)
        return [JobOut.model_validate(j) for j in s.exec(stmt).all()]


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str) -> JobOut:
    with Session(engine) as s:
        job = s.get(Job, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobOut.model_validate(job)


def _control(action, job_id: str) -> dict:
    ok = action(job_id)
    if not ok:
        raise HTTPException(status_code=409, detail="Action not allowed in current job state")
    return {"ok": True}


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict:
    return _control(orchestrator.cancel, job_id)


@router.post("/jobs/{job_id}/pause")
def pause_job(job_id: str) -> dict:
    return _control(orchestrator.pause, job_id)


@router.post("/jobs/{job_id}/resume")
def resume_job(job_id: str) -> dict:
    return _control(orchestrator.resume, job_id)


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str) -> dict:
    return _control(orchestrator.retry, job_id)
