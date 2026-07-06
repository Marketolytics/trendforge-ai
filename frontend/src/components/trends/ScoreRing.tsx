import { cn } from "@/lib/utils";
import { formatScore } from "@/lib/format";

/** Compact score chip, color-coded by strength. */
export function ScoreRing({ score, className }: { score: number; className?: string }) {
  const tone =
    score >= 70
      ? "text-[var(--success)] border-[var(--success)]/30 bg-[var(--success)]/10"
      : score >= 45
        ? "text-[var(--warning)] border-[var(--warning)]/30 bg-[var(--warning)]/10"
        : "text-[var(--muted-foreground)] border-[var(--border)] bg-[var(--muted)]";

  return (
    <div
      className={cn(
        "flex h-11 w-11 shrink-0 flex-col items-center justify-center rounded-lg border font-semibold",
        tone,
        className,
      )}
      title={`Preliminary trend score: ${score}`}
    >
      <span className="text-sm leading-none">{formatScore(score)}</span>
      <span className="text-[8px] font-medium uppercase tracking-wider opacity-70">
        score
      </span>
    </div>
  );
}
