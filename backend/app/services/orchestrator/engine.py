"""Orchestration engine + persistent background job queue.

A single async worker processes jobs one at a time; within a job, agent groups
run in parallel. Jobs persist to the ``jobs`` table so they survive restarts
(interrupted jobs are re-queued and resume cheaply — already-generated stages
return from cache instead of re-calling Gemini).
"""

from __future__ import annotations

import asyncio
import itertools
import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.logging import get_logger, log_event
from app.db.models import Job
from app.db.session import engine as db_engine
from app.services.orchestrator.agents import AGENTS, JobContext, agent_label, get_agent
from app.services.orchestrator.workflows import get_workflow

log = get_logger("trendforge.orchestrator")

MAX_STAGE_ATTEMPTS = 2

_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
_seq = itertools.count()
_worker_task: asyncio.Task | None = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- job persistence ------------------------------------------------------

def _get(job_id: str) -> Job | None:
    with Session(db_engine) as s:
        return s.get(Job, job_id)


def _status(job_id: str) -> str | None:
    with Session(db_engine) as s:
        job = s.get(Job, job_id)
        return job.status if job else None


def _update(job_id: str, **fields) -> None:
    with Session(db_engine) as s:
        job = s.get(Job, job_id)
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)
        job.updated_at = _now()
        s.add(job)
        s.commit()


def create_job(
    workflow: str,
    trend_id: int,
    *,
    format: str = "60s",
    voice_style: str = "Professional",
    force: bool = False,
    priority: int = 5,
) -> dict:
    wf = get_workflow(workflow)
    if wf is None:
        raise ValueError(f"unknown workflow: {workflow}")
    fmt = format or wf.default_format or "60s"
    steps = [
        {"key": key, "label": agent_label(key), "status": "pending", "attempts": 0,
         "duration_ms": 0, "error": None}
        for key in wf.agent_keys
    ]
    job = Job(
        id=uuid.uuid4().hex,
        workflow=workflow,
        trend_id=trend_id,
        variant=fmt,
        params={"format": fmt, "voice_style": voice_style, "force": force},
        priority=priority,
        status="queued",
        steps=steps,
    )
    with Session(db_engine) as s:
        s.add(job)
        s.commit()
        s.refresh(job)
    return job.model_dump()


# --- execution ------------------------------------------------------------

async def _run_stage(ctx: JobContext, key: str, steps: list[dict]) -> None:
    step = next((st for st in steps if st["key"] == key), None)
    if step is None:
        return
    agent = get_agent(key)
    if agent is None:
        step.update(status="failed", error="no agent registered")
        return

    step["status"] = "running"
    started = _now()
    ok = False
    issues: list[str] = []
    for attempt in range(1, MAX_STAGE_ATTEMPTS + 1):
        step["attempts"] = attempt
        await agent.initialize(ctx)
        result = await agent.execute(ctx)
        ok, issues = agent.validate(result)
        if ok:
            break
    step["status"] = "done" if ok else "failed"
    step["error"] = None if ok else "; ".join(issues)
    step["duration_ms"] = int((_now() - started).total_seconds() * 1000)
    log_event(
        "ai",
        f"stage {key} {'ok' if ok else 'failed'}",
        job_id=ctx.job_id,
        stage=key,
        attempts=step["attempts"],
        duration_ms=step["duration_ms"],
    )


async def run_job(job_id: str) -> None:
    job = _get(job_id)
    if job is None or job.status in ("cancelled", "completed"):
        return
    wf = get_workflow(job.workflow)
    if wf is None:
        _update(job_id, status="failed", error="unknown workflow", finished_at=_now())
        return

    steps = list(job.steps)
    total = max(len(steps), 1)
    ctx = JobContext(
        trend_id=job.trend_id or 0,
        variant=job.variant,
        params=dict(job.params),
        job_id=job.id,
        force=bool(job.params.get("force")),
        is_cancelled=lambda: _status(job_id) == "cancelled",
    )
    _update(job_id, status="running", started_at=job.started_at or _now(), error=None)
    log_event("ai", "job started", job_id=job_id, workflow=job.workflow)

    for group in wf.groups:
        st = _status(job_id)
        if st == "cancelled":
            _update(job_id, steps=steps, finished_at=_now())
            log_event("ai", "job cancelled", job_id=job_id)
            return
        if st == "paused":
            _update(job_id, steps=steps)
            log_event("ai", "job paused", job_id=job_id)
            return

        # Skip stages already completed (cheap resume).
        pending = [k for k in group if next((s for s in steps if s["key"] == k), {}).get("status") != "done"]
        _update(job_id, current_step=", ".join(agent_label(k) for k in group))
        await asyncio.gather(*(_run_stage(ctx, k, steps) for k in pending))

        done = sum(1 for s in steps if s["status"] == "done")
        durations = [s["duration_ms"] for s in steps if s["status"] == "done" and s["duration_ms"]]
        avg = sum(durations) / len(durations) if durations else 0
        remaining = total - done
        eta = int((avg * remaining) / 1000) if avg else None
        _update(job_id, steps=steps, progress=round(done / total, 3), eta_seconds=eta)

    failed = [s["key"] for s in steps if s["status"] == "failed"]
    done = sum(1 for s in steps if s["status"] == "done")
    status = "completed" if done > 0 and not failed else ("failed" if done == 0 else "completed")
    _update(
        job_id,
        status=status,
        progress=round(done / total, 3),
        current_step="Done",
        eta_seconds=0,
        finished_at=_now(),
        error=("; ".join(failed) + " failed") if failed else None,
        result={"completed": done, "failed": failed, "total": total},
    )
    log_event("ai", "job finished", job_id=job_id, status=status, completed=done, failed=len(failed))


# --- queue + worker -------------------------------------------------------

def enqueue(job_id: str, priority: int = 5) -> None:
    _queue.put_nowait((priority, next(_seq), job_id))


async def _worker() -> None:
    log.info("orchestrator worker started", extra={"category": "ai"})
    while True:
        _, _, job_id = await _queue.get()
        try:
            st = _status(job_id)
            if st in ("cancelled", "paused", "completed"):
                continue
            await run_job(job_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("job crashed", extra={"category": "ai", "job_id": job_id, "error": str(exc)})
            _update(job_id, status="failed", error=str(exc), finished_at=_now())
        finally:
            _queue.task_done()


def start_worker() -> None:
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker())


def resume_pending() -> int:
    """Re-enqueue jobs left queued/running by a previous run."""
    resumed = 0
    with Session(db_engine) as s:
        jobs = list(s.exec(select(Job).where(Job.status.in_(["queued", "running"]))).all())
        for job in jobs:
            job.status = "queued"
            job.updated_at = _now()
            s.add(job)
            resumed += 1
        s.commit()
        ids = [(j.priority, j.id) for j in jobs]
    for priority, jid in ids:
        enqueue(jid, priority)
    if resumed:
        log.info("resumed pending jobs", extra={"category": "ai", "count": resumed})
    return resumed


# --- control --------------------------------------------------------------

def cancel(job_id: str) -> bool:
    job = _get(job_id)
    if job is None or job.status in ("completed", "failed", "cancelled"):
        return False
    _update(job_id, status="cancelled", finished_at=_now())
    return True


def pause(job_id: str) -> bool:
    job = _get(job_id)
    if job is None or job.status not in ("queued", "running"):
        return False
    _update(job_id, status="paused")
    return True


def resume(job_id: str) -> bool:
    job = _get(job_id)
    if job is None or job.status != "paused":
        return False
    _update(job_id, status="queued")
    enqueue(job_id, job.priority)
    return True


def retry(job_id: str) -> bool:
    job = _get(job_id)
    if job is None:
        return False
    has_failed = any(st.get("status") == "failed" for st in job.steps)
    # Retry failed/cancelled jobs, or completed jobs that had partial failures.
    if job.status not in ("failed", "cancelled") and not (job.status == "completed" and has_failed):
        return False
    steps = list(job.steps)
    for st in steps:
        if st["status"] in ("failed", "running"):
            st["status"] = "pending"
            st["error"] = None
    _update(job_id, status="queued", steps=steps, error=None, finished_at=None)
    enqueue(job_id, job.priority)
    return True


def queue_stats() -> dict:
    with Session(db_engine) as s:
        rows = list(s.exec(select(Job)).all())
    by_status: dict[str, int] = {}
    for j in rows:
        by_status[j.status] = by_status.get(j.status, 0) + 1
    return {
        "queue_size": _queue.qsize(),
        "worker_running": bool(_worker_task and not _worker_task.done()),
        "by_status": by_status,
        "total": len(rows),
    }
