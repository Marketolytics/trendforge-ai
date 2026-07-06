import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { RefreshCw, X, Database, Layers, HardDrive, FileCode } from "lucide-react";
import { devApi, type DevStats } from "@/lib/api";
import { cn } from "@/lib/utils";

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-[var(--border)] p-3">
      <p className="text-[11px] uppercase tracking-wide text-[var(--muted-foreground)]">{label}</p>
      <p className="mt-0.5 text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}

export function DeveloperPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [stats, setStats] = useState<DevStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [tab, setTab] = useState<"stats" | "logs" | "prompts">("stats");

  const load = useCallback(async () => {
    try {
      const [s, l] = await Promise.all([devApi.stats(), devApi.logs(150)]);
      setStats(s);
      setLogs(l.lines);
    } catch {
      /* offline */
    }
  }, []);

  useEffect(() => {
    if (open) load();
  }, [open, load]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-xl flex-col border-l border-[var(--border)] bg-[var(--background)] shadow-2xl"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 34 }}
          >
            <div className="flex items-center justify-between border-b border-[var(--border)] p-4">
              <div className="flex items-center gap-2">
                <FileCode className="h-4 w-4 text-[var(--accent)]" />
                <h2 className="text-sm font-semibold">Developer Panel</h2>
                <span className="rounded bg-[var(--muted)] px-1.5 py-0.5 text-[10px] text-[var(--muted-foreground)]">
                  ⌃⇧D
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <button onClick={load} className="rounded-md p-1.5 hover:bg-[var(--muted)]" title="Refresh">
                  <RefreshCw className="h-4 w-4" />
                </button>
                <button onClick={onClose} className="rounded-md p-1.5 hover:bg-[var(--muted)]" title="Close">
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="flex gap-1 border-b border-[var(--border)] px-3">
              {(["stats", "logs", "prompts"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={cn(
                    "px-3 py-2.5 text-sm font-medium capitalize transition-colors",
                    tab === t ? "text-[var(--foreground)]" : "text-[var(--muted-foreground)]",
                  )}
                >
                  {t}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {!stats ? (
                <p className="text-sm text-[var(--muted-foreground)]">Loading…</p>
              ) : tab === "stats" ? (
                <div className="space-y-5">
                  <section>
                    <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                      <Layers className="h-4 w-4" /> Queue
                    </h3>
                    <div className="grid grid-cols-3 gap-2">
                      <Metric label="Queue size" value={stats.queue.queue_size} />
                      <Metric label="Worker" value={stats.queue.worker_running ? "on" : "off"} />
                      <Metric label="Jobs" value={stats.queue.total} />
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {Object.entries(stats.queue.by_status).map(([k, v]) => (
                        <span key={k} className="rounded-full border border-[var(--border)] bg-[var(--muted)] px-2.5 py-0.5 text-xs">
                          {k}: {v}
                        </span>
                      ))}
                    </div>
                  </section>

                  <section>
                    <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                      <HardDrive className="h-4 w-4" /> Cache
                    </h3>
                    <div className="grid grid-cols-3 gap-2">
                      <Metric label="Total" value={stats.cache.total} />
                      <Metric label="Fresh" value={stats.cache.fresh} />
                      <Metric label="Expired" value={stats.cache.expired} />
                    </div>
                  </section>

                  <section>
                    <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                      <Database className="h-4 w-4" /> Database
                    </h3>
                    <div className="grid grid-cols-3 gap-2">
                      {Object.entries(stats.db).map(([k, v]) => (
                        <Metric key={k} label={k.replace(/_/g, " ")} value={v} />
                      ))}
                    </div>
                  </section>
                </div>
              ) : tab === "logs" ? (
                <pre className="whitespace-pre-wrap break-all rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 font-mono text-[11px] leading-relaxed text-[var(--muted-foreground)]">
                  {logs.length ? logs.join("\n") : "No logs."}
                </pre>
              ) : (
                <div className="space-y-1.5">
                  {stats.prompts.map((p) => (
                    <div key={p.name} className="flex items-center justify-between rounded-md border border-[var(--border)] px-3 py-2">
                      <div className="min-w-0">
                        <p className="text-sm font-medium">{p.name}</p>
                        <p className="truncate text-xs text-[var(--muted-foreground)]">{p.description}</p>
                      </div>
                      <span className="shrink-0 rounded bg-[var(--muted)] px-2 py-0.5 text-[11px] tabular-nums">
                        v{p.version}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
