import { ExternalLink, Layers, Sparkles } from "lucide-react";
import type { Trend } from "@/lib/api";
import { relativeTime } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { useTrends } from "@/store/trends";
import { ScoreRing } from "./ScoreRing";

interface TrendCardProps {
  trend: Trend;
  rank?: number;
}

export function TrendCard({ trend, rank }: TrendCardProps) {
  const { openTrend } = useTrends();

  const openSource = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (trend.url) window.open(trend.url, "_blank", "noopener,noreferrer");
  };

  return (
    <div
      onClick={() => openTrend(trend)}
      className="group surface flex cursor-pointer items-center gap-4 p-3.5 transition-colors hover:border-[var(--ring)]"
    >
      {typeof rank === "number" && (
        <span className="w-5 shrink-0 text-center text-sm font-semibold text-[var(--muted-foreground)]">
          {rank}
        </span>
      )}

      <ScoreRing score={trend.score} />

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h3 className="truncate text-sm font-medium leading-tight">
            {trend.title}
          </h3>
          <Sparkles className="h-3.5 w-3.5 shrink-0 text-[var(--accent)] opacity-0 transition-opacity group-hover:opacity-100" />
        </div>
        <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-[var(--muted-foreground)]">
          <span className="font-medium text-[var(--foreground)]/80">
            {trend.source}
          </span>
          <span>·</span>
          <span>{relativeTime(trend.published_time ?? trend.collection_timestamp)}</span>
          <Badge variant="muted" className="ml-1">
            {trend.category}
          </Badge>
          {trend.cluster_size > 1 && (
            <span className="inline-flex items-center gap-1 text-[var(--accent)]">
              <Layers className="h-3 w-3" />
              {trend.cluster_size} sources
            </span>
          )}
          {trend.url && (
            <button
              onClick={openSource}
              className="inline-flex items-center gap-1 text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
              title="Open source"
            >
              <ExternalLink className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
