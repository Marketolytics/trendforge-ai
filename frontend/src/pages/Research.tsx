import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Microscope, ChevronRight, RefreshCw } from "lucide-react";
import { api, type Trend } from "@/lib/api";
import { useTrends } from "@/store/trends";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { ScoreRing } from "@/components/trends/ScoreRing";
import { ResearchWorkspace } from "@/components/research/ResearchWorkspace";

function Picker() {
  const navigate = useNavigate();
  const { trends, status, refresh } = useTrends();

  if (status === "loading") {
    return (
      <div className="space-y-2.5">
        {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}
      </div>
    );
  }
  if (trends.length === 0) {
    return (
      <EmptyState
        icon={Microscope}
        title="No trends to research"
        description="Refresh trends first, then pick one to assemble a research package."
        action={<Button onClick={() => refresh()}><RefreshCw className="h-4 w-4" /> Refresh Trends</Button>}
      />
    );
  }
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Research a story</h2>
        <p className="text-sm text-[var(--muted-foreground)]">
          Pick a trend to gather multi-source intelligence, build a timeline and verify facts.
        </p>
      </div>
      <div className="space-y-2.5">
        {trends.slice(0, 40).map((t) => (
          <button
            key={t.id}
            onClick={() => navigate(`/research/${t.id}`)}
            className="group surface flex w-full items-center gap-4 p-3.5 text-left transition-colors hover:border-[var(--ring)]"
          >
            <ScoreRing score={t.score} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{t.title}</p>
              <p className="text-xs text-[var(--muted-foreground)]">{t.source} · {t.category}</p>
            </div>
            <ChevronRight className="h-4 w-4 text-[var(--muted-foreground)] transition-transform group-hover:translate-x-0.5" />
          </button>
        ))}
      </div>
    </div>
  );
}

export function Research() {
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
    api.getTrend(id).then(setFetched).catch(() => setFetched(null)).finally(() => setLoading(false));
  }, [id, fromStore]);

  if (id == null) return <Picker />;
  if (loading && !trend) return <Skeleton className="h-[70vh] w-full" />;
  if (!trend)
    return <EmptyState icon={Microscope} title="Trend not found" description="Pick another trend to research." />;

  return <ResearchWorkspace trend={trend} />;
}
