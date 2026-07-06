import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, KeyRound, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AiLoading } from "@/components/trends/analysis/AiLoading";

type State = "idle" | "loading" | "ready" | "error";

interface StudioSectionProps {
  status: State | undefined;
  notConfigured: boolean;
  onGenerate: () => void;
  emptyLabel: string;
  loadingLabel?: string;
  children: ReactNode;
}

export function StudioSection({
  status,
  notConfigured,
  onGenerate,
  emptyLabel,
  loadingLabel,
  children,
}: StudioSectionProps) {
  const navigate = useNavigate();

  if (notConfigured) {
    return (
      <div className="surface flex flex-col items-center gap-3 px-6 py-12 text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--muted)] text-[var(--accent)]">
          <KeyRound className="h-5 w-5" />
        </div>
        <p className="max-w-xs text-sm text-[var(--muted-foreground)]">
          Add your Gemini API key in Settings to generate content.
        </p>
        <Button size="sm" onClick={() => navigate("/settings")}>
          Open Settings
        </Button>
      </div>
    );
  }

  if (!status || status === "idle") {
    return (
      <div className="flex justify-center py-12">
        <Button onClick={onGenerate}>
          <Sparkles className="h-4 w-4" />
          {emptyLabel}
        </Button>
      </div>
    );
  }

  if (status === "loading") return <AiLoading label={loadingLabel} />;

  if (status === "error") {
    return (
      <div className="surface flex flex-col items-center gap-3 px-6 py-10 text-center">
        <AlertTriangle className="h-6 w-6 text-[var(--danger)]" />
        <p className="text-sm text-[var(--muted-foreground)]">Generation failed.</p>
        <Button size="sm" variant="outline" onClick={onGenerate}>
          Try again
        </Button>
      </div>
    );
  }

  return <>{children}</>;
}
