import { useState } from "react";
import { Lightbulb } from "lucide-react";
import { insightApi, type CompetitorGap, type GapItem, type MultiIdeas } from "@/lib/api";
import { EmptyState } from "@/components/common/EmptyState";
import { useAi } from "@/components/trends/analysis/useAi";
import { AiSection } from "@/components/trends/analysis/AiSection";
import { TrendSelect } from "./TrendSelect";

function GapList({ title, items }: { title: string; items: GapItem[] }) {
  if (!items || items.length === 0) return null;
  const sorted = [...items].sort((a, b) => (a.rank || 99) - (b.rank || 99));
  return (
    <div className="surface p-4">
      <h4 className="mb-2 text-sm font-semibold">{title}</h4>
      <div className="space-y-2">
        {sorted.map((it, i) => (
          <div key={i} className="flex gap-2">
            <span className="mt-0.5 text-xs font-semibold text-[var(--accent)]">{it.rank || i + 1}</span>
            <div>
              <p className="text-sm">{it.text}</p>
              {it.why && <p className="text-xs text-[var(--muted-foreground)]">{it.why}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function IdeaGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="surface p-4">
      <h4 className="mb-2 text-sm font-semibold">{title}</h4>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

export function OpportunitiesTab() {
  const [trendId, setTrendId] = useState<number | null>(null);
  const gap = useAi<CompetitorGap>(trendId, insightApi.competitorGap);
  const ideas = useAi<MultiIdeas>(trendId, insightApi.multiIdeas);

  return (
    <div className="space-y-5">
      <div>
        <p className="mb-2 text-sm text-[var(--muted-foreground)]">
          Pick a trend to find gaps competitors are missing and generate a full connected idea slate.
        </p>
        <TrendSelect value={trendId} onChange={setTrendId} />
      </div>

      {trendId == null ? (
        <EmptyState
          icon={Lightbulb}
          title="Select a trend"
          description="Choose a trend above to analyze competitor gaps and generate ideas."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-2 text-sm font-semibold">Content Gap Finder</h3>
            <AiSection resource={gap} emptyLabel="Find content gaps">
              {(d) => (
                <div className="space-y-3">
                  <GapList title="Untapped angles" items={d.untapped_angles} />
                  <GapList title="Under-explored questions" items={d.under_explored_questions} />
                  <GapList title="New perspectives" items={d.new_perspectives} />
                  <GapList title="Emerging discussions" items={d.emerging_discussions} />
                </div>
              )}
            </AiSection>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold">Multi-Idea Generator</h3>
            <AiSection resource={ideas} emptyLabel="Generate idea slate">
              {(d) => (
                <div className="space-y-3">
                  <IdeaGroup title={`Shorts (${d.shorts?.length ?? 0})`}>
                    {d.shorts?.map((s, i) => (
                      <p key={i} className="text-sm">
                        {s.idea}
                      </p>
                    ))}
                  </IdeaGroup>
                  <IdeaGroup title={`Long videos (${d.long_videos?.length ?? 0})`}>
                    {d.long_videos?.map((s, i) => (
                      <p key={i} className="text-sm">
                        {s.idea}
                      </p>
                    ))}
                  </IdeaGroup>
                  <IdeaGroup title="Reels">
                    {d.reels?.map((s, i) => (
                      <p key={i} className="text-sm">
                        {s.idea}
                      </p>
                    ))}
                  </IdeaGroup>
                  <IdeaGroup title="Community & X posts">
                    {[...(d.community_posts ?? []), ...(d.x_posts ?? [])].map((s, i) => (
                      <p key={i} className="text-sm">
                        {s.text}
                      </p>
                    ))}
                  </IdeaGroup>
                  <IdeaGroup title="Carousels & livestreams">
                    {d.carousels?.map((s, i) => (
                      <p key={`c${i}`} className="text-sm">
                        📸 {s.concept}
                      </p>
                    ))}
                    {d.livestreams?.map((s, i) => (
                      <p key={`l${i}`} className="text-sm">
                        🔴 {s.concept}
                      </p>
                    ))}
                  </IdeaGroup>
                </div>
              )}
            </AiSection>
          </div>
        </div>
      )}
    </div>
  );
}
