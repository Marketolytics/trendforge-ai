import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type Status = "checking" | "online" | "offline";

const LABEL: Record<Status, string> = {
  checking: "Connecting",
  online: "Connected",
  offline: "Offline",
};

const DOT: Record<Status, string> = {
  checking: "bg-[var(--warning)] animate-pulse",
  online: "bg-[var(--success)]",
  offline: "bg-[var(--danger)]",
};

/** Polls the backend health endpoint and shows a live connection pill. */
export function BackendStatus() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let active = true;

    const check = async () => {
      try {
        await api.health();
        if (active) setStatus("online");
      } catch {
        if (active) setStatus("offline");
      }
    };

    check();
    const id = setInterval(check, 10_000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--card)] px-3 py-1.5">
      <span className={cn("h-2 w-2 rounded-full", DOT[status])} />
      <span className="text-xs font-medium text-[var(--muted-foreground)]">
        {LABEL[status]}
      </span>
    </div>
  );
}
