import {
  aiApi,
  type ContentStrategy,
  type HooksData,
  type ThumbnailStrategy,
  type TitlesData,
  type TrendSummary,
} from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { useAi } from "./useAi";
import { AiSection } from "./AiSection";

function List({ title, items, tone }: { title: string; items: string[]; tone?: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p
        className="mb-1.5 text-[11px] font-medium uppercase tracking-wide"
        style={{ color: tone ?? "var(--muted-foreground)" }}
      >
        {title}
      </p>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-[var(--foreground)]/90">
            <span className="text-[var(--muted-foreground)]">•</span>
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Meter({ value, suffix = "" }: { value: number; suffix?: string }) {
  const pct = Math.max(0, Math.min(100, value));
  const color =
    value >= 70 ? "var(--success)" : value >= 45 ? "var(--warning)" : "var(--muted-foreground)";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-[var(--muted)]">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="w-12 text-right text-xs font-medium tabular-nums" style={{ color }}>
        {value}
        {suffix}
      </span>
    </div>
  );
}

// --- Summary --------------------------------------------------------------

export function SummaryTab({ trendId }: { trendId: number }) {
  const resource = useAi<TrendSummary>(trendId, aiApi.summary, true);
  return (
    <AiSection resource={resource} emptyLabel="Generate summary">
      {(d) => (
        <div className="space-y-4">
          <div className="surface space-y-3 p-5">
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                Short
              </p>
              <p className="mt-0.5 text-sm">{d.short}</p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                Detailed
              </p>
              <p className="mt-0.5 text-sm leading-relaxed">{d.detailed}</p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--accent)]">
                Creator angle
              </p>
              <p className="mt-0.5 text-sm leading-relaxed">{d.creator}</p>
            </div>
          </div>
          <div className="surface space-y-4 p-5">
            <List title="Key facts" items={d.key_facts} tone="var(--success)" />
            <List title="Things to avoid" items={d.things_to_avoid} tone="var(--warning)" />
            <List
              title="Potential misinformation"
              items={d.potential_misinformation}
              tone="var(--danger)"
            />
            <List title="Verify with" items={d.verified_sources} />
          </div>
        </div>
      )}
    </AiSection>
  );
}

// --- Hooks ----------------------------------------------------------------

export function HooksTab({ trendId }: { trendId: number }) {
  const resource = useAi<HooksData>(trendId, aiApi.hooks, true);
  return (
    <AiSection resource={resource} emptyLabel="Generate hooks">
      {(d) => (
        <div className="space-y-2">
          {d.hooks.map((h, i) => (
            <div key={i} className="surface flex items-center gap-3 p-3">
              <span className="w-5 text-center text-xs font-semibold text-[var(--muted-foreground)]">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm">{h.text}</p>
                <Badge variant="muted" className="mt-1 capitalize">
                  {h.type}
                </Badge>
              </div>
              <Meter value={h.click_potential} />
            </div>
          ))}
        </div>
      )}
    </AiSection>
  );
}

// --- Titles ---------------------------------------------------------------

export function TitlesTab({ trendId }: { trendId: number }) {
  const resource = useAi<TitlesData>(trendId, aiApi.titles, true);
  return (
    <AiSection resource={resource} emptyLabel="Generate titles">
      {(d) => (
        <div className="space-y-2">
          {d.titles.map((t, i) => (
            <div key={i} className="surface flex items-center gap-3 p-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">{t.text}</p>
                <Badge variant="muted" className="mt-1 capitalize">
                  {t.type.replace("_", " ")}
                </Badge>
              </div>
              <Meter value={t.predicted_ctr} suffix="%" />
            </div>
          ))}
        </div>
      )}
    </AiSection>
  );
}

// --- Thumbnail ------------------------------------------------------------

export function ThumbnailTab({ trendId }: { trendId: number }) {
  const resource = useAi<ThumbnailStrategy>(trendId, aiApi.thumbnail, true);
  return (
    <AiSection resource={resource} emptyLabel="Generate thumbnail direction">
      {(d) => (
        <div className="space-y-4">
          <div className="surface p-5">
            <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              Concept
            </p>
            <p className="mt-1 text-sm">{d.concept}</p>
            <div className="mt-3 inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--muted)] px-3 py-1.5">
              <span className="text-[11px] text-[var(--muted-foreground)]">Overlay text</span>
              <span className="text-sm font-semibold uppercase">{d.text}</span>
            </div>
          </div>
          <div className="surface grid grid-cols-2 gap-4 p-5">
            {(
              [
                ["Emotion", d.emotion],
                ["Composition", d.composition],
                ["Background", d.background],
                ["Subject placement", d.subject_placement],
                ["Color direction", d.color_direction],
                ["Visual hierarchy", d.visual_hierarchy],
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
          </div>
          {d.alternates.length > 0 && (
            <div className="surface space-y-2 p-5">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                Alternates
              </p>
              {d.alternates.map((a, i) => (
                <div key={i} className="rounded-lg border border-[var(--border)] p-3">
                  <p className="text-sm">{a.concept}</p>
                  {a.text && (
                    <span className="mt-1 inline-block text-xs font-semibold uppercase text-[var(--accent)]">
                      {a.text}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </AiSection>
  );
}

// --- Strategy -------------------------------------------------------------

function IdeaBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="surface p-5">
      <h4 className="mb-3 text-sm font-semibold">{title}</h4>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

export function StrategyTab({ trendId }: { trendId: number }) {
  const resource = useAi<ContentStrategy>(trendId, aiApi.strategy, true);
  return (
    <AiSection resource={resource} emptyLabel="Generate content strategy">
      {(d) => (
        <div className="space-y-4">
          <IdeaBlock title={`Shorts (${d.shorts.length})`}>
            {d.shorts.map((s, i) => (
              <div key={i} className="text-sm">
                <span className="font-medium">{s.idea}</span>
                {s.hook_angle && (
                  <span className="text-[var(--muted-foreground)]"> — {s.hook_angle}</span>
                )}
              </div>
            ))}
          </IdeaBlock>
          <IdeaBlock title={`Long videos (${d.long_videos.length})`}>
            {d.long_videos.map((s, i) => (
              <div key={i} className="text-sm">
                <span className="font-medium">{s.idea}</span>
                {s.angle && <span className="text-[var(--muted-foreground)]"> — {s.angle}</span>}
              </div>
            ))}
          </IdeaBlock>
          <IdeaBlock title="Community posts">
            {d.community_posts.map((s, i) => (
              <p key={i} className="text-sm">
                {s.text}
              </p>
            ))}
          </IdeaBlock>
          <IdeaBlock title="X posts">
            {d.x_posts.map((s, i) => (
              <p key={i} className="text-sm">
                {s.text}
              </p>
            ))}
          </IdeaBlock>
          <IdeaBlock title="Instagram carousels">
            {d.instagram_carousels.map((s, i) => (
              <div key={i} className="text-sm">
                <p className="font-medium">{s.concept}</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  {s.slides.join(" · ")}
                </p>
              </div>
            ))}
          </IdeaBlock>
          <IdeaBlock title="Livestreams">
            {d.livestreams.map((s, i) => (
              <p key={i} className="text-sm">
                {s.concept}
              </p>
            ))}
          </IdeaBlock>
        </div>
      )}
    </AiSection>
  );
}
