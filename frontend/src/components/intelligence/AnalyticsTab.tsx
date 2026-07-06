import { useEffect, useState } from "react";
import { Sparkles, TrendingUp, Users, Package } from "lucide-react";
import { intelligenceApi, type Analytics } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { compactNumber } from "@/lib/format";

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: any }) {
  return (
    <Card>
      <CardContent className="flex items-center justify-between p-4">
        <div>
          <p className="text-xs font-medium text-[var(--muted-foreground)]">{label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--muted)] text-[var(--accent)]">
          <Icon className="h-4.5 w-4.5" />
        </div>
      </CardContent>
    </Card>
  );
}

function BarRow({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="w-24 shrink-0 truncate text-xs capitalize text-[var(--muted-foreground)]">
        {label}
      </span>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-[var(--muted)]">
        <div className="h-full rounded-full bg-[var(--accent)]" style={{ width: `${pct}%` }} />
      </div>
      <span className="w-8 text-right text-xs tabular-nums">{value}</span>
    </div>
  );
}

export function AnalyticsTab() {
  const [data, setData] = useState<Analytics | null>(null);

  useEffect(() => {
    intelligenceApi.analytics().then(setData).catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }

  const maxWeekly = Math.max(1, ...data.weekly_activity.map((d) => d.count));
  const maxCat = Math.max(1, ...data.top_categories.map((c) => c.count));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Trends today" value={data.trends_today} icon={TrendingUp} />
        <StatCard label="AI generations" value={data.ai_generations} icon={Sparkles} />
        <StatCard label="Competitors" value={data.competitors} icon={Users} />
        <StatCard label="Content packages" value={data.content_packages} icon={Package} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Weekly activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex h-40 items-end gap-2">
              {data.weekly_activity.map((d) => (
                <div key={d.day} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t bg-[var(--accent)]"
                    style={{ height: `${(d.count / maxWeekly) * 100}%`, minHeight: 2 }}
                    title={`${d.count} events`}
                  />
                  <span className="text-[10px] text-[var(--muted-foreground)]">
                    {d.day.slice(5)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top categories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.top_categories.map((c) => (
              <BarRow key={c.category} label={c.category} value={c.count} max={maxCat} />
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top opportunity scores</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.top_opportunities.map((o) => (
              <div key={o.id} className="flex items-center gap-3">
                <span className="w-9 shrink-0 text-center text-sm font-semibold text-[var(--accent)]">
                  {Math.round(o.score)}
                </span>
                <span className="min-w-0 flex-1 truncate text-sm">{o.title}</span>
                <span className="shrink-0 text-xs text-[var(--muted-foreground)]">{o.source}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generations & hooks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                By module
              </p>
              {data.generations_by_kind.length === 0 ? (
                <p className="text-sm text-[var(--muted-foreground)]">No generations yet.</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {data.generations_by_kind.map((g) => (
                    <span
                      key={g.kind}
                      className="rounded-full border border-[var(--border)] bg-[var(--muted)] px-2.5 py-0.5 text-xs"
                    >
                      {g.kind} · {g.count}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div>
              <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                Most used hook types
              </p>
              {data.most_used_hooks.length === 0 ? (
                <p className="text-sm text-[var(--muted-foreground)]">No hooks generated yet.</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {data.most_used_hooks.map((h) => (
                    <span
                      key={h.type}
                      className="rounded-full border border-[var(--border)] bg-[var(--muted)] px-2.5 py-0.5 text-xs capitalize"
                    >
                      {h.type} · {h.count}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      <p className="text-center text-xs text-[var(--muted-foreground)]">
        {compactNumber(data.total_trends)} total trends tracked · local only, no cloud sync
      </p>
    </div>
  );
}
