import { aiApi, type TrendAnalysis } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { useAi } from "./useAi";
import { AiSection } from "./AiSection";
import { OpportunityScore } from "./OpportunityScore";
import { TimelineBar } from "./TimelineBar";

const LEVEL_TONE: Record<string, string> = {
  high: "text-[var(--success)] border-[var(--success)]/30 bg-[var(--success)]/10",
  medium: "text-[var(--warning)] border-[var(--warning)]/30 bg-[var(--warning)]/10",
  low: "text-[var(--muted-foreground)] border-[var(--border)] bg-[var(--muted)]",
};

function Field({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div>
      <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
        {label}
      </p>
      <p className="mt-0.5 text-sm">{value}</p>
    </div>
  );
}

function AnalysisBody({ data }: { data: TrendAnalysis }) {
  const recommendedFormats = [...data.formats]
    .filter((f) => f.recommended)
    .sort((a, b) => b.confidence - a.confidence);

  return (
    <div className="space-y-5">
      <OpportunityScore opportunity={data.opportunity} />

      <TimelineBar
        stage={data.timeline.stage}
        confidence={data.timeline.confidence}
        explanation={data.timeline.explanation}
      />

      {/* Intelligence */}
      <div className="surface space-y-3 p-5">
        <h4 className="text-sm font-semibold">What's going on</h4>
        <Field label="What happened" value={data.intelligence.what_happened} />
        <Field label="Why it matters" value={data.intelligence.why_important} />
        <Field label="Who cares" value={data.intelligence.who_cares} />
        <div className="flex items-center gap-2 pt-1">
          <Badge variant={data.intelligence.is_growing ? "success" : "muted"}>
            {data.intelligence.is_growing ? "Growing" : "Not growing"}
          </Badge>
          <span className="text-xs text-[var(--muted-foreground)]">
            {data.intelligence.growth_reason}
          </span>
        </div>
      </div>

      {/* Relevance horizons */}
      {data.relevance.length > 0 && (
        <div className="surface p-5">
          <h4 className="mb-3 text-sm font-semibold">Relevance window</h4>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {data.relevance.map((r) => (
              <div
                key={r.horizon}
                className={cn(
                  "rounded-lg border p-3 text-center",
                  LEVEL_TONE[r.level?.toLowerCase()] ?? LEVEL_TONE.low,
                )}
                title={r.note}
              >
                <p className="text-[11px] font-medium opacity-80">{r.horizon}</p>
                <p className="mt-1 text-sm font-semibold capitalize">{r.level}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Best formats */}
      {recommendedFormats.length > 0 && (
        <div className="surface p-5">
          <h4 className="mb-3 text-sm font-semibold">Best formats</h4>
          <div className="space-y-2">
            {recommendedFormats.map((f) => (
              <div key={f.format} className="flex items-start gap-3">
                <Badge className="mt-0.5 shrink-0">{f.confidence}%</Badge>
                <div>
                  <p className="text-sm font-medium">{f.format}</p>
                  <p className="text-xs text-[var(--muted-foreground)]">{f.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Audience */}
      <div className="surface grid grid-cols-2 gap-4 p-5">
        <h4 className="col-span-2 text-sm font-semibold">Suggested audience</h4>
        <Field label="Age" value={data.audience.age_range} />
        <Field label="Intensity" value={data.audience.intensity} />
        <Field label="Knowledge" value={data.audience.gaming_knowledge} />
        <Field label="Region" value={data.audience.region} />
        <Field label="Search intent" value={data.audience.search_intent} />
        <Field label="Emotion" value={data.audience.expected_emotion} />
        <div className="col-span-2">
          <Field label="Presentation style" value={data.audience.presentation_style} />
        </div>
      </div>

      {/* Content gap */}
      <div className="surface space-y-4 p-5">
        <h4 className="text-sm font-semibold">Content opportunities</h4>
        {data.content_gap.saturated_angles.length > 0 && (
          <div>
            <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-[var(--danger)]">
              Saturated — avoid
            </p>
            <div className="flex flex-wrap gap-1.5">
              {data.content_gap.saturated_angles.map((a, i) => (
                <Badge key={i} variant="muted">
                  {a}
                </Badge>
              ))}
            </div>
          </div>
        )}
        <div className="space-y-2.5">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--success)]">
            Unique angles to pursue
          </p>
          {data.content_gap.unique_ideas.map((idea, i) => (
            <div key={i} className="rounded-lg border border-[var(--border)] p-3">
              <p className="text-sm font-medium">{idea.idea}</p>
              {idea.angle && (
                <p className="mt-0.5 text-xs text-[var(--accent)]">{idea.angle}</p>
              )}
              {idea.why && (
                <p className="mt-1 text-xs text-[var(--muted-foreground)]">{idea.why}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function OverviewTab({ trendId }: { trendId: number }) {
  const resource = useAi<TrendAnalysis>(trendId, aiApi.analyze, true);
  return (
    <AiSection resource={resource} loadingLabel={undefined} emptyLabel="Analyze trend">
      {(data) => <AnalysisBody data={data} />}
    </AiSection>
  );
}
