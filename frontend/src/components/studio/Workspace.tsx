import { useEffect, useRef, useState } from "react";
import { Download, Sparkles, RefreshCw, ExternalLink, Workflow as WorkflowIcon } from "lucide-react";
import { orchestratorApi, studioApi, type ModuleKind, type Trend, type WorkflowTemplate } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScoreRing } from "@/components/trends/ScoreRing";
import { useJobs } from "@/store/jobs";
import { StoryboardTimeline } from "./StoryboardTimeline";
import { ModulePanel } from "./ModulePanel";
import { MODULE_LABELS, MODULE_ORDER, useWorkspace } from "./useWorkspace";

// Right-panel tabs (storyboard lives in the center timeline).
const TAB_KINDS: ModuleKind[] = MODULE_ORDER.filter((k) => k !== "storyboard");

export function Workspace({ trend }: { trend: Trend }) {
  const ws = useWorkspace(trend.id);
  const { jobs, enqueue } = useJobs();
  const [tab, setTab] = useState<ModuleKind>("script");
  const [workflows, setWorkflows] = useState<WorkflowTemplate[]>([]);
  const [workflow, setWorkflow] = useState("complete");
  const generating = ws.packageStatus === "generating";
  const moduleCount = Object.keys(ws.modules).length;

  useEffect(() => {
    orchestratorApi.workflows().then(setWorkflows).catch(() => void 0);
  }, []);

  // Reload the package when a background workflow for this trend completes.
  const processed = useRef<Set<string>>(new Set());
  useEffect(() => {
    for (const j of jobs) {
      if (j.trend_id === trend.id && j.status === "completed" && !processed.current.has(j.id)) {
        processed.current.add(j.id);
        ws.reload();
      }
    }
  }, [jobs, trend.id, ws]);

  const runWorkflow = () =>
    enqueue({ workflow, trend_id: trend.id, format: ws.format, voice_style: ws.voiceStyle });

  const statusDot = (kind: ModuleKind) => {
    const s = ws.moduleStatus[kind];
    if (s === "ready") return "bg-[var(--success)]";
    if (s === "loading") return "bg-[var(--warning)] animate-pulse";
    if (s === "error") return "bg-[var(--danger)]";
    return "bg-[var(--border)]";
  };

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-4">
      <div className="flex min-h-0 flex-1 gap-4">
        {/* LEFT — trend + controls */}
        <aside className="flex w-60 shrink-0 flex-col gap-4 overflow-y-auto pr-1">
          <div className="surface p-4">
            <div className="flex items-start gap-3">
              <ScoreRing score={trend.score} />
              <div className="min-w-0">
                <h2 className="text-sm font-semibold leading-tight">{trend.title}</h2>
                <p className="mt-1 truncate text-xs text-[var(--muted-foreground)]">
                  {trend.source}
                </p>
              </div>
            </div>
            {trend.url && (
              <a
                href={trend.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex items-center gap-1 text-xs text-[var(--accent)] hover:underline"
              >
                <ExternalLink className="h-3 w-3" /> Source
              </a>
            )}
          </div>

          <div className="surface p-4">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              Format
            </p>
            <div className="flex flex-wrap gap-1.5">
              {ws.formats.map((f) => (
                <button
                  key={f.key}
                  onClick={() => ws.setFormat(f.key)}
                  className={cn(
                    "rounded-md border px-2 py-1 text-xs transition-colors",
                    ws.format === f.key
                      ? "border-transparent bg-[var(--accent)] text-[var(--accent-foreground)]"
                      : "border-[var(--border)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]",
                  )}
                >
                  {f.label.replace(" Video", "").replace(" Short", "")}
                </button>
              ))}
            </div>

            <p className="mb-2 mt-4 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              Voice style
            </p>
            <select
              value={ws.voiceStyle}
              onChange={(e) => ws.setVoiceStyle(e.target.value)}
              className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-2 text-sm outline-none focus:border-[var(--ring)]"
            >
              {ws.voiceStyles.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>

            <Button
              className="mt-4 w-full"
              onClick={() => ws.generatePackage(false)}
              disabled={generating}
            >
              <Sparkles className={generating ? "h-4 w-4 animate-pulse" : "h-4 w-4"} />
              {generating ? "Generating…" : "Generate Package"}
            </Button>
            {moduleCount > 0 && (
              <Button
                variant="ghost"
                className="mt-1.5 w-full"
                onClick={() => ws.generatePackage(true)}
                disabled={generating}
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Regenerate all
              </Button>
            )}
          </div>

          {/* Background workflow runner */}
          <div className="surface p-4">
            <p className="mb-2 flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              <WorkflowIcon className="h-3.5 w-3.5" /> Run as workflow
            </p>
            <select
              value={workflow}
              onChange={(e) => setWorkflow(e.target.value)}
              className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-2 text-sm outline-none focus:border-[var(--ring)]"
            >
              {workflows.map((w) => (
                <option key={w.name} value={w.name}>
                  {w.label}
                </option>
              ))}
            </select>
            <Button variant="outline" className="mt-2 w-full" onClick={runWorkflow}>
              <WorkflowIcon className="h-4 w-4" />
              Queue workflow
            </Button>
            <p className="mt-1.5 text-[11px] text-[var(--muted-foreground)]">
              Runs in the background — track it in the monitor.
            </p>
          </div>

          {/* Module completion */}
          <div className="surface p-4">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              Modules
            </p>
            <ul className="space-y-1">
              {MODULE_ORDER.map((kind) => (
                <li key={kind}>
                  <button
                    onClick={() => kind !== "storyboard" && setTab(kind)}
                    className="flex w-full items-center gap-2 rounded-md px-2 py-1 text-left text-sm text-[var(--foreground)]/85 transition-colors hover:bg-[var(--muted)]"
                  >
                    <span className={cn("h-2 w-2 shrink-0 rounded-full", statusDot(kind))} />
                    {MODULE_LABELS[kind]}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* CENTER — storyboard */}
        <section className="min-w-0 flex-1">
          <StoryboardTimeline ws={ws} />
        </section>

        {/* RIGHT — module tabs */}
        <section className="flex w-[26rem] shrink-0 flex-col">
          <div className="mb-3 flex gap-1 overflow-x-auto">
            {TAB_KINDS.map((k) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                className={cn(
                  "shrink-0 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                  tab === k
                    ? "bg-[var(--muted)] text-[var(--foreground)]"
                    : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]",
                )}
              >
                {MODULE_LABELS[k]}
              </button>
            ))}
          </div>
          <div className="min-h-0 flex-1">
            <ModulePanel kind={tab} ws={ws} trendId={trend.id} />
          </div>
        </section>
      </div>

      {/* BOTTOM — export bar */}
      <div className="flex items-center justify-between rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2.5">
        <p className="text-xs text-[var(--muted-foreground)]">
          {moduleCount} / {MODULE_ORDER.length} modules generated · {ws.format}
        </p>
        <a
          href={moduleCount > 0 ? studioApi.exportPackageUrl(trend.id, ws.format) : undefined}
          className={cn(
            "inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-all",
            moduleCount > 0
              ? "bg-[var(--accent)] text-[var(--accent-foreground)] hover:brightness-110"
              : "pointer-events-none bg-[var(--muted)] text-[var(--muted-foreground)]",
          )}
        >
          <Download className="h-4 w-4" />
          Export ZIP
        </a>
      </div>
    </div>
  );
}
