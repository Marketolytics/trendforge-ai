import { useEffect, useState } from "react";
import { ArrowUpCircle, X } from "lucide-react";
import { systemApi } from "@/lib/api";

/** Passive, optional update notice — never auto-updates, no account needed. */
export function UpdateBanner() {
  const [latest, setLatest] = useState<string | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    systemApi
      .updateCheck()
      .then((info) => {
        if (info.update_available) setLatest(info.latest);
      })
      .catch(() => void 0);
  }, []);

  if (!latest || dismissed) return null;

  return (
    <div className="flex items-center gap-2 border-b border-[var(--border)] bg-[var(--accent)]/10 px-4 py-1.5 text-xs text-[var(--foreground)]">
      <ArrowUpCircle className="h-3.5 w-3.5 text-[var(--accent)]" />
      <span>
        A newer version (<strong>{latest}</strong>) is available.
      </span>
      <button onClick={() => setDismissed(true)} className="ml-auto p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
