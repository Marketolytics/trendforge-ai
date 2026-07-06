import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, LineChart } from "lucide-react";
import { insightApi, type TrendForecast, type UploadAdvice } from "@/lib/api";
import { EmptyState } from "@/components/common/EmptyState";
import { useAi } from "@/components/trends/analysis/useAi";
import { AiSection } from "@/components/trends/analysis/AiSection";
import { TrendSelect } from "./TrendSelect";

const DIR_ICON: Record<string, typeof TrendingUp> = {
  rising: TrendingUp,
  declining: TrendingDown,
  flat: Minus,
};
const DIR_TONE: Record<string, string> = {
  rising: "text-[var(--success)]",
  declining: "text-[var(--danger)]",
  flat: "text-[var(--muted-foreground)]",
};

export function ForecastTab() {
  const [trendId, setTrendId] = useState<number | null>(null);
  const forecast = useAi<TrendForecast>(trendId, insightApi.forecast);
  const advice = useAi<UploadAdvice>(trendId, insightApi.uploadAdvisor);

  return (
    <div className="space-y-5">
      <div>
        <p className="mb-2 text-sm text-[var(--muted-foreground)]">
          Forecast how a trend will evolve and get upload timing advice.
        </p>
        <TrendSelect value={trendId} onChange={setTrendId} />
      </div>

      {trendId == null ? (
        <EmptyState
          icon={LineChart}
          title="Select a trend"
          description="Choose a trend above to forecast its momentum and get an upload plan."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-2 text-sm font-semibold">Trend Forecast</h3>
            <AiSection resource={forecast} emptyLabel="Forecast this trend">
              {(d) => (
                <div className="space-y-4">
                  <div className="surface flex items-center gap-5 p-4">
                    <div className="text-center">
                      <p className="text-3xl font-semibold text-[var(--accent)]">{d.forecast_score}</p>
                      <p className="text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                        forecast
                      </p>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-[var(--muted-foreground)]">{d.reasoning}</p>
                      <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                        {d.confidence}% confidence
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {d.horizons?.map((h) => {
                      const Icon = DIR_ICON[h.direction] ?? Minus;
                      return (
                        <div key={h.horizon} className="surface p-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium">{h.horizon}</span>
                            <Icon className={`h-4 w-4 ${DIR_TONE[h.direction] ?? ""}`} />
                          </div>
                          <p className="mt-1 text-lg font-semibold">{h.likelihood}%</p>
                          <p className="text-[11px] text-[var(--muted-foreground)]">{h.note}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </AiSection>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold">Upload Advisor</h3>
            <AiSection resource={advice} emptyLabel="Get upload plan">
              {(d) => (
                <div className="surface grid grid-cols-2 gap-4 p-4">
                  {(
                    [
                      ["Best day", d.best_day],
                      ["Best time", d.best_time],
                      ["Ideal length", d.ideal_length],
                      ["Frequency", d.posting_frequency],
                      ["Best format", d.best_format],
                      ["Audience", d.target_audience],
                    ] as const
                  ).map(([label, value]) =>
                    value ? (
                      <div key={label}>
                        <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                          {label}
                        </p>
                        <p className="mt-0.5 text-sm">{value}</p>
                      </div>
                    ) : null,
                  )}
                  {d.reasoning && (
                    <p className="col-span-2 border-t border-[var(--border)] pt-3 text-sm text-[var(--muted-foreground)]">
                      {d.reasoning}
                    </p>
                  )}
                </div>
              )}
            </AiSection>
          </div>
        </div>
      )}
    </div>
  );
}
