import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { RefreshCw, KeyRound, AlertTriangle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { relativeTime } from "@/lib/format";
import { AiLoading } from "./AiLoading";
import type { AiResource } from "./useAi";

interface AiSectionProps<T> {
  resource: AiResource<T>;
  /** Called to trigger the first generation when idle. */
  emptyLabel?: string;
  loadingLabel?: string;
  children: (data: T) => ReactNode;
}

export function AiSection<T>({
  resource,
  emptyLabel = "Generate",
  loadingLabel,
  children,
}: AiSectionProps<T>) {
  const navigate = useNavigate();
  const { status, data, error, notConfigured, cached, generatedAt, load, regenerate } =
    resource;

  if (notConfigured) {
    return (
      <div className="surface flex flex-col items-center gap-3 px-6 py-12 text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--muted)] text-[var(--accent)]">
          <KeyRound className="h-5 w-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold">Gemini API key required</h4>
          <p className="mt-1 max-w-xs text-sm text-[var(--muted-foreground)]">
            Add your Gemini API key in Settings to unlock AI analysis.
          </p>
        </div>
        <Button size="sm" onClick={() => navigate("/settings")}>
          Open Settings
        </Button>
      </div>
    );
  }

  if (status === "idle") {
    return (
      <div className="flex justify-center py-10">
        <Button onClick={load}>
          <Sparkles className="h-4 w-4" />
          {emptyLabel}
        </Button>
      </div>
    );
  }

  if (status === "loading") {
    return <AiLoading label={loadingLabel} />;
  }

  if (status === "error") {
    return (
      <div className="surface flex flex-col items-center gap-3 px-6 py-10 text-center">
        <AlertTriangle className="h-6 w-6 text-[var(--danger)]" />
        <p className="max-w-sm text-sm text-[var(--muted-foreground)]">{error}</p>
        <Button size="sm" variant="outline" onClick={load}>
          <RefreshCw className="h-4 w-4" />
          Try again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-[var(--muted-foreground)]">
          {cached && <Badge variant="muted">saved</Badge>}
          <span>updated {relativeTime(generatedAt)}</span>
        </div>
        <Button size="sm" variant="ghost" onClick={regenerate}>
          <RefreshCw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
      </div>
      {data != null && children(data)}
    </div>
  );
}
