import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  ChevronDown,
  ChevronUp,
  Pause,
  Play,
  RotateCcw,
  X,
  Check,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { isActiveJob, type Job, type JobStep } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useJobs } from "@/store/jobs";

const STATUS_TONE: Record<string, string> = {
  running: "text-[var(--accent)]",
  queued: "text-[var(--warning)]",
  paused: "text-[var(--warning)]",
  completed: "text-[var(--success)]",
  failed: "text-[var(--danger)]",
  cancelled: "text-[var(--muted-foreground)]",
};

function StepDot({ step }: { step: JobStep }) {
  const tone =
    step.status === "done"
      ? "bg-[var(--success)]"
      : step.status === "running"
        ? "bg-[var(--accent)] animate-pulse"
        : step.status === "failed"
          ? "bg-[var(--danger)]"
          : "bg-[var(--border)]";
  return <span className={cn("h-1.5 w-1.5 rounded-full", tone)} title={`${step.label}: ${step.status}`} />;
}

function JobRow({ job }: { job: Job }) {
  const { cancel, pause, resume, retry } = useJobs();
  const active = isActiveJob(job);
  const pct = Math.round(job.progress * 100);

  return (
    <div className="border-t border-[var(--border)] p-3 first:border-t-0">
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          {job.status === "running" && <Loader2 className="h-3.5 w-3.5 animate-spin text-[var(--accent)]" />}
          {job.status === "completed" && <Check className="h-3.5 w-3.5 text-[var(--success)]" />}
          {job.status === "failed" && <AlertCircle className="h-3.5 w-3.5 text-[var(--danger)]" />}
          <span className="truncate text-xs font-medium capitalize">{job.workflow.replace("_", " ")}</span>
        </div>
        <span className={cn("text-[11px] font-medium capitalize", STATUS_TONE[job.status])}>
          {job.status}
        </span>
      </div>

      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--muted)]">
        <div
          className="h-full rounded-full bg-[var(--accent)] transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="mt-1.5 flex items-center justify-between text-[11px] text-[var(--muted-foreground)]">
        <span className="truncate">{job.current_step || "—"}</span>
        <span>
          {pct}%{job.eta_seconds ? ` · ~${job.eta_seconds}s` : ""}
        </span>
      </div>

      <div className="mt-2 flex flex-wrap gap-1">
        {job.steps.map((s) => (
          <StepDot key={s.key} step={s} />
        ))}
      </div>

      <div className="mt-2 flex items-center gap-1.5">
        {job.status === "running" || job.status === "queued" ? (
          <>
            <button onClick={() => pause(job.id)} className="monitor-btn" title="Pause">
              <Pause className="h-3.5 w-3.5" />
            </button>
            <button onClick={() => cancel(job.id)} className="monitor-btn" title="Cancel">
              <X className="h-3.5 w-3.5" />
            </button>
          </>
        ) : null}
        {job.status === "paused" && (
          <button onClick={() => resume(job.id)} className="monitor-btn" title="Resume">
            <Play className="h-3.5 w-3.5" />
          </button>
        )}
        {(job.status === "failed" || job.status === "cancelled" || (job.status === "completed" && job.error)) && (
          <button onClick={() => retry(job.id)} className="monitor-btn" title="Retry">
            <RotateCcw className="h-3.5 w-3.5" /> Retry
          </button>
        )}
        {job.error && !active && (
          <span className="truncate text-[11px] text-[var(--danger)]">{job.error}</span>
        )}
      </div>
    </div>
  );
}

export function JobMonitor() {
  const { jobs, activeCount } = useJobs();
  const [open, setOpen] = useState(true);

  const visible = jobs.filter(
    (j) => isActiveJob(j) || (j.finished_at && Date.now() - new Date(j.finished_at).getTime() < 30_000),
  );

  if (visible.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-30 w-80">
      <style>{`.monitor-btn{display:inline-flex;align-items:center;gap:4px;border:1px solid var(--border);border-radius:6px;padding:2px 8px;font-size:11px;color:var(--muted-foreground);transition:all .15s}.monitor-btn:hover{background:var(--muted);color:var(--foreground)}`}</style>
      <div className="surface overflow-hidden shadow-2xl">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex w-full items-center justify-between px-3 py-2.5"
        >
          <span className="flex items-center gap-2 text-sm font-semibold">
            <Activity className="h-4 w-4 text-[var(--accent)]" />
            Workflows
            {activeCount > 0 && (
              <span className="rounded-full bg-[var(--accent)] px-1.5 text-[10px] text-[var(--accent-foreground)]">
                {activeCount}
              </span>
            )}
          </span>
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
        </button>
        <AnimatePresence initial={false}>
          {open && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: "auto" }}
              exit={{ height: 0 }}
              className="max-h-96 overflow-y-auto"
            >
              {visible.map((job) => (
                <JobRow key={job.id} job={job} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
