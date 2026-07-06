import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Clapperboard, ChevronRight, RefreshCw } from "lucide-react";
import { api, type Trend } from "@/lib/api";
import { useTrends } from "@/store/trends";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { ScoreRing } from "@/components/trends/ScoreRing";
import { Workspace } from "@/components/studio/Workspace";

function TrendPicker() {
  const navigate = useNavigate();
  const { trends, status, refresh } = useTrends();

  if (status === "loading") {
    return (
      <div className="space-y-2.5">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (trends.length === 0) {
    return (
      <EmptyState
        icon={Clapperboard}
        title="No trends to build from"
        description="Refresh trends first, then pick one to open the production studio."
        action={
          <Button onClick={() => refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh Trends
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Production Studio</h2>
        <p className="text-sm text-[var(--muted-foreground)]">
          Pick a trend to generate a full production package.
        </p>
      </div>
      <div className="space-y-2.5">
        {trends.slice(0, 30).map((t) => (
          <button
            key={t.id}
            onClick={() => navigate(`/studio/${t.id}`)}
            className="group surface flex w-full items-center gap-4 p-3.5 text-left transition-colors hover:border-[var(--ring)]"
          >
            <ScoreRing score={t.score} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{t.title}</p>
              <p className="text-xs text-[var(--muted-foreground)]">
                {t.source} · {t.category}
              </p>
            </div>
            <ChevronRight className="h-4 w-4 text-[var(--muted-foreground)] transition-transform group-hover:translate-x-0.5" />
          </button>
        ))}
      </div>
    </div>
  );
}

export function Studio() {
  const { trendId } = useParams<{ trendId?: string }>();
  const { trends } = useTrends();
  const [fetched, setFetched] = useState<Trend | null>(null);
  const [loading, setLoading] = useState(false);

  const id = trendId ? Number(trendId) : null;
  const fromStore = id != null ? trends.find((t) => t.id === id) : undefined;
  const trend = fromStore ?? fetched;

  useEffect(() => {
    if (id == null || fromStore) return;
    setLoading(true);
    api
      .getTrend(id)
      .then(setFetched)
      .catch(() => setFetched(null))
      .finally(() => setLoading(false));
  }, [id, fromStore]);

  if (id == null) return <TrendPicker />;

  if (loading && !trend) {
    return <Skeleton className="h-[70vh] w-full" />;
  }

  if (!trend) {
    return (
      <EmptyState
        icon={Clapperboard}
        title="Trend not found"
        description="This trend may have been removed. Head back and pick another."
      />
    );
  }

  return <Workspace trend={trend} />;
}
