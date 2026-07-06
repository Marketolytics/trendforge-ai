import { Sunrise, TrendingUp, TrendingDown, Infinity as InfinityIcon } from "lucide-react";
import { cn } from "@/lib/utils";

const STAGES = [
  { key: "starting", label: "Starting", icon: Sunrise },
  { key: "peaking", label: "Peaking", icon: TrendingUp },
  { key: "declining", label: "Declining", icon: TrendingDown },
  { key: "evergreen", label: "Evergreen", icon: InfinityIcon },
];

export function TimelineBar({
  stage,
  confidence,
  explanation,
}: {
  stage: string;
  confidence: number;
  explanation: string;
}) {
  const activeIndex = STAGES.findIndex((s) => s.key === stage.toLowerCase());

  return (
    <div className="surface p-5">
      <div className="mb-4 flex items-center justify-between">
        <h4 className="text-sm font-semibold">Trend Timeline</h4>
        <span className="text-xs text-[var(--muted-foreground)]">
          {confidence}% confidence
        </span>
      </div>

      <div className="flex items-center">
        {STAGES.map((s, i) => {
          const active = i === activeIndex;
          const passed = activeIndex >= 0 && i < activeIndex;
          const Icon = s.icon;
          return (
            <div key={s.key} className="flex flex-1 items-center">
              <div className="flex flex-col items-center gap-1.5">
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-full border transition-colors",
                    active
                      ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--accent-foreground)]"
                      : passed
                        ? "border-[var(--accent)]/40 text-[var(--accent)]"
                        : "border-[var(--border)] text-[var(--muted-foreground)]",
                  )}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <span
                  className={cn(
                    "text-[11px] font-medium",
                    active ? "text-[var(--foreground)]" : "text-[var(--muted-foreground)]",
                  )}
                >
                  {s.label}
                </span>
              </div>
              {i < STAGES.length - 1 && (
                <div
                  className={cn(
                    "mx-1 h-0.5 flex-1 rounded-full",
                    passed ? "bg-[var(--accent)]/40" : "bg-[var(--border)]",
                  )}
                />
              )}
            </div>
          );
        })}
      </div>

      {explanation && (
        <p className="mt-4 text-sm text-[var(--muted-foreground)]">{explanation}</p>
      )}
    </div>
  );
}
