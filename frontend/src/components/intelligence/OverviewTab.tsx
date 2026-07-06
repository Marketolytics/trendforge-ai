import { useEffect, useState } from "react";
import { Users, Lightbulb, LineChart, BarChart3, ArrowRight } from "lucide-react";
import { intelligenceApi, type Analytics } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export type IntelTab =
  | "overview"
  | "competitors"
  | "opportunities"
  | "forecast"
  | "history"
  | "favorites"
  | "analytics";

const SHORTCUTS: { tab: IntelTab; label: string; desc: string; icon: any }[] = [
  { tab: "competitors", label: "Competitors", desc: "Track channels & patterns", icon: Users },
  { tab: "opportunities", label: "Opportunities", desc: "Find content gaps", icon: Lightbulb },
  { tab: "forecast", label: "Forecast", desc: "Predict trend momentum", icon: LineChart },
  { tab: "analytics", label: "Analytics", desc: "Local activity dashboard", icon: BarChart3 },
];

export function OverviewTab({ onNavigate }: { onNavigate: (t: IntelTab) => void }) {
  const [data, setData] = useState<Analytics | null>(null);

  useEffect(() => {
    intelligenceApi.analytics().then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          ["Trends today", data?.trends_today],
          ["AI generations", data?.ai_generations],
          ["Competitors", data?.competitors],
          ["Packages", data?.content_packages],
        ].map(([label, value]) => (
          <Card key={label as string}>
            <CardContent className="p-4">
              <p className="text-xs font-medium text-[var(--muted-foreground)]">{label}</p>
              <p className="mt-1 text-2xl font-semibold">
                {data ? (value as number) : <Skeleton className="h-7 w-10" />}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {SHORTCUTS.map((s) => (
          <button
            key={s.tab}
            onClick={() => onNavigate(s.tab)}
            className="group surface flex flex-col gap-2 p-4 text-left transition-colors hover:border-[var(--ring)]"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--muted)] text-[var(--accent)]">
              <s.icon className="h-4.5 w-4.5" />
            </div>
            <div>
              <p className="flex items-center gap-1 text-sm font-semibold">
                {s.label}
                <ArrowRight className="h-3.5 w-3.5 opacity-0 transition-all group-hover:translate-x-0.5 group-hover:opacity-100" />
              </p>
              <p className="text-xs text-[var(--muted-foreground)]">{s.desc}</p>
            </div>
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top opportunities</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {!data ? (
            <Skeleton className="h-24 w-full" />
          ) : data.top_opportunities.length === 0 ? (
            <p className="text-sm text-[var(--muted-foreground)]">Refresh trends to see opportunities.</p>
          ) : (
            data.top_opportunities.map((o) => (
              <div key={o.id} className="flex items-center gap-3">
                <span className="w-9 shrink-0 text-center text-sm font-semibold text-[var(--accent)]">
                  {Math.round(o.score)}
                </span>
                <span className="min-w-0 flex-1 truncate text-sm">{o.title}</span>
                <span className="shrink-0 text-xs text-[var(--muted-foreground)]">{o.source}</span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
