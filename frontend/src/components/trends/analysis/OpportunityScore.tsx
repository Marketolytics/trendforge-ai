import { motion } from "framer-motion";
import type { Opportunity } from "@/lib/api";

const FACTOR_LABELS: Record<string, string> = {
  freshness: "Freshness",
  search_interest: "Search Interest",
  competition: "Competition",
  viewer_curiosity: "Viewer Curiosity",
  shareability: "Shareability",
  emotional_impact: "Emotional Impact",
  replay_potential: "Replay Potential",
  monetization_potential: "Monetization",
  evergreen_value: "Evergreen Value",
};

function toneFor(score: number): string {
  if (score >= 70) return "var(--success)";
  if (score >= 45) return "var(--warning)";
  return "var(--muted-foreground)";
}

export function OpportunityScore({ opportunity }: { opportunity: Opportunity }) {
  const score = Math.max(0, Math.min(100, opportunity.score));
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);
  const color = toneFor(score);

  return (
    <div className="surface p-5">
      <div className="flex items-center gap-5">
        <div className="relative h-28 w-28 shrink-0">
          <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke="var(--muted)"
              strokeWidth="8"
            />
            <motion.circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 0.9, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-semibold tracking-tight" style={{ color }}>
              {score}
            </span>
            <span className="text-[10px] font-medium uppercase tracking-widest text-[var(--muted-foreground)]">
              opportunity
            </span>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-[var(--muted-foreground)]">
          {opportunity.explanation}
        </p>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-x-6 gap-y-2.5 sm:grid-cols-2">
        {Object.entries(opportunity.factors).map(([key, value]) => (
          <div key={key} className="flex items-center gap-3">
            <span className="w-28 shrink-0 text-xs text-[var(--muted-foreground)]">
              {FACTOR_LABELS[key] ?? key}
            </span>
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[var(--muted)]">
              <motion.div
                className="h-full rounded-full"
                style={{ background: toneFor(value) }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.max(0, Math.min(100, value))}%` }}
                transition={{ duration: 0.7, ease: "easeOut" }}
              />
            </div>
            <span className="w-7 text-right text-xs font-medium tabular-nums">
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
