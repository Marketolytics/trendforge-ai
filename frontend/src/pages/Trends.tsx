import { useMemo, useState } from "react";
import { RefreshCw, Search, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { TrendCard } from "@/components/trends/TrendCard";
import { cn } from "@/lib/utils";
import { useTrends } from "@/store/trends";

export function Trends() {
  const { trends, status, refresh } = useTrends();
  const [category, setCategory] = useState<string>("all");
  const [q, setQ] = useState("");

  const loading = status === "loading";
  const refreshing = status === "refreshing";

  const categories = useMemo(() => {
    const set = new Set(trends.map((t) => t.category));
    return ["all", ...Array.from(set).sort()];
  }, [trends]);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return trends.filter((t) => {
      if (category !== "all" && t.category !== category) return false;
      if (needle && !t.title.toLowerCase().includes(needle)) return false;
      return true;
    });
  }, [trends, category, q]);

  return (
    <div className="space-y-5">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-9 min-w-56 flex-1 items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-[var(--muted-foreground)] focus-within:border-[var(--ring)]">
          <Search className="h-4 w-4" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Filter trends…"
            className="w-full bg-transparent text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]"
          />
        </div>
        <Button variant="outline" size="sm" onClick={() => refresh()} disabled={refreshing}>
          <RefreshCw className={refreshing ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
          Refresh
        </Button>
      </div>

      {/* Category filters */}
      <div className="flex flex-wrap gap-2">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium capitalize transition-colors",
              category === c
                ? "border-transparent bg-[var(--accent)] text-[var(--accent-foreground)]"
                : "border-[var(--border)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]",
            )}
          >
            {c}
          </button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-2.5">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="space-y-2.5">
          {filtered.map((trend, i) => (
            <TrendCard key={trend.id} trend={trend} rank={i + 1} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={TrendingUp}
          title={trends.length === 0 ? "No trends collected yet" : "No matches"}
          description={
            trends.length === 0
              ? "Refresh to pull live trending topics from Google Trends, Reddit, Steam, YouTube and gaming news."
              : "Try a different category or search term."
          }
          action={
            trends.length === 0 ? (
              <Button onClick={() => refresh()} disabled={refreshing}>
                <RefreshCw className={refreshing ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
                Refresh Trends
              </Button>
            ) : undefined
          }
        />
      )}
    </div>
  );
}
