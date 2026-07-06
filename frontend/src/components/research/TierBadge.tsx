import { cn } from "@/lib/utils";

const TIER_STYLE: Record<string, string> = {
  official: "text-[var(--success)] border-[var(--success)]/30 bg-[var(--success)]/10",
  developer: "text-[var(--success)] border-[var(--success)]/30 bg-[var(--success)]/10",
  industry: "text-[var(--accent)] border-[var(--accent)]/30 bg-[var(--accent)]/10",
  community: "text-[var(--warning)] border-[var(--warning)]/30 bg-[var(--warning)]/10",
  forum: "text-[var(--warning)] border-[var(--warning)]/30 bg-[var(--warning)]/10",
  social: "text-[#c084fc] border-[#c084fc]/30 bg-[#c084fc]/10",
  signal: "text-[var(--muted-foreground)] border-[var(--border)] bg-[var(--muted)]",
  unknown: "text-[var(--muted-foreground)] border-[var(--border)] bg-[var(--muted)]",
};

export function TierBadge({ tier, label }: { tier: string; label?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium",
        TIER_STYLE[tier] ?? TIER_STYLE.unknown,
      )}
    >
      {label ?? tier}
    </span>
  );
}
