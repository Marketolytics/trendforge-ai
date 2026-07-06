import { useMemo } from "react";
import { RefreshCw, TrendingUp, Flame, Target, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { TrendCard } from "@/components/trends/TrendCard";
import { useTrends } from "@/store/trends";
import { relativeTime, formatScore } from "@/lib/format";

export function Dashboard() {
  const { trends, status, lastRefresh, refresh } = useTrends();
  const loading = status === "loading";
  const refreshing = status === "refreshing";

  const stats = useMemo(() => {
    const topScore = trends.reduce((max, t) => Math.max(max, t.score), 0);
    const opportunities = trends.filter((t) => t.score >= 70).length;
    return [
      { label: "Trends tracked", value: trends.length || "—", icon: TrendingUp },
      { label: "Top score", value: trends.length ? formatScore(topScore) : "—", icon: Flame },
      { label: "Opportunities", value: trends.length ? opportunities : "—", icon: Target },
      {
        label: "Last refresh",
        value: lastRefresh ? relativeTime(lastRefresh) : "Never",
        icon: Clock,
      },
    ];
  }, [trends, lastRefresh]);

  const topTrends = trends.slice(0, 6);
  const latestNews = useMemo(
    () =>
      [...trends]
        .filter((t) => t.published_time)
        .sort(
          (a, b) =>
            new Date(b.published_time!).getTime() -
            new Date(a.published_time!).getTime(),
        )
        .slice(0, 6),
    [trends],
  );

  return (
    <div className="space-y-6">
      {/* Stat row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="text-xs font-medium text-[var(--muted-foreground)]">
                  {label}
                </p>
                <p className="mt-1 text-2xl font-semibold tracking-tight">
                  {loading ? <Skeleton className="h-7 w-12" /> : value}
                </p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--muted)] text-[var(--accent)]">
                <Icon className="h-4.5 w-4.5" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>Today's Top Trends</CardTitle>
              <Badge variant="muted">ranked by score</Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refresh()}
              disabled={refreshing}
            >
              <RefreshCw className={refreshing ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
              Refresh
            </Button>
          </CardHeader>
          <CardContent className="space-y-2.5">
            {loading || (refreshing && trends.length === 0) ? (
              Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))
            ) : topTrends.length > 0 ? (
              topTrends.map((trend, i) => (
                <TrendCard key={trend.id} trend={trend} rank={i + 1} />
              ))
            ) : (
              <EmptyState
                icon={TrendingUp}
                title="No trends yet"
                description="Hit refresh to collect live trending topics from all your sources."
                action={
                  <Button onClick={() => refresh()} disabled={refreshing}>
                    <RefreshCw className={refreshing ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
                    Refresh Trends
                  </Button>
                }
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest News</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : latestNews.length > 0 ? (
              <ul className="space-y-3">
                {latestNews.map((t) => (
                  <li key={t.id}>
                    <a
                      href={t.url ?? "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block rounded-md p-1 transition-colors hover:bg-[var(--muted)]"
                    >
                      <p className="line-clamp-2 text-sm leading-snug">{t.title}</p>
                      <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                        {t.source} · {relativeTime(t.published_time)}
                      </p>
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                icon={Clock}
                title="Nothing here yet"
                description="Fresh headlines from your sources will show up here."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
