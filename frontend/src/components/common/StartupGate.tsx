import { useCallback, useEffect, useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { Flame, AlertTriangle, RefreshCw } from "lucide-react";
import { resolveBackendUrl, waitForBackend } from "@/lib/backend";
import { getApiBaseUrl } from "@/lib/api";

type Phase = "connecting" | "ready" | "error";

/** Blocks the app until the local backend is reachable; recovers gracefully. */
export function StartupGate({ children }: { children: ReactNode }) {
  const [phase, setPhase] = useState<Phase>("connecting");

  const connect = useCallback(async () => {
    setPhase("connecting");
    await resolveBackendUrl();
    const ok = await waitForBackend();
    setPhase(ok ? "ready" : "error");
  }, []);

  useEffect(() => {
    connect();
  }, [connect]);

  if (phase === "ready") return <>{children}</>;

  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center gap-5 bg-[var(--background)] text-[var(--foreground)]">
      {phase === "connecting" ? (
        <>
          <motion.div
            className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--accent)] text-[var(--accent-foreground)] shadow-lg"
            animate={{ scale: [1, 1.08, 1] }}
            transition={{ duration: 1.3, repeat: Infinity, ease: "easeInOut" }}
          >
            <Flame className="h-7 w-7" />
          </motion.div>
          <div className="text-center">
            <p className="text-sm font-semibold">Starting TrendForge…</p>
            <p className="mt-1 text-xs text-[var(--muted-foreground)]">Connecting to the local engine</p>
          </div>
        </>
      ) : (
        <div className="flex max-w-md flex-col items-center gap-4 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--danger)]/15 text-[var(--danger)]">
            <AlertTriangle className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Couldn't reach the backend</h1>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              The local engine didn't respond at <code>{getApiBaseUrl()}</code>. It may still be
              starting, or another instance may be using the port. Check the logs in your workspace
              <code> logs/</code> folder.
            </p>
          </div>
          <button
            onClick={connect}
            className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--accent-foreground)]"
          >
            <RefreshCw className="h-4 w-4" /> Retry connection
          </button>
        </div>
      )}
    </div>
  );
}
