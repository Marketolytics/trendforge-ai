import { useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import {
  ExternalLink,
  RefreshCw,
  ShieldCheck,
  Download,
  Copy,
  Printer,
  KeyRound,
  Sparkles,
} from "lucide-react";
import type { ResearchAI, Trend } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { relativeTime } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Field, Pills, BulletList, Card } from "@/components/studio/primitives";
import { AiLoading } from "@/components/trends/analysis/AiLoading";
import { TierBadge } from "./TierBadge";
import { useResearch } from "./useResearch";
import { researchToMarkdown, download } from "./exportResearch";

const TABS = [
  "overview", "timeline", "sources", "facts",
  "entities", "community", "keywords", "verification",
] as const;
type Tab = (typeof TABS)[number];

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="surface p-4">
      <h4 className="mb-2 text-sm font-semibold">{title}</h4>
      {children}
    </div>
  );
}

export function ResearchWorkspace({ trend }: { trend: Trend }) {
  const r = useResearch(trend.id);
  const [tab, setTab] = useState<Tab>("overview");

  if (r.loading && !r.base) return <AiLoading label="Assembling the story…" />;
  if (!r.base) return <p className="text-sm text-[var(--muted-foreground)]">No research available.</p>;

  const base = r.base;
  const ai = r.ai;

  const AiGate = ({ children }: { children: (ai: ResearchAI) => ReactNode }) => {
    if (ai) return <>{children(ai)}</>;
    if (r.enriching) return <AiLoading label="Running AI verification…" />;
    return (
      <div className="surface flex flex-col items-center gap-3 px-6 py-12 text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--muted)] text-[var(--accent)]">
          {r.notConfigured ? <KeyRound className="h-5 w-5" /> : <ShieldCheck className="h-5 w-5" />}
        </div>
        <p className="max-w-xs text-sm text-[var(--muted-foreground)]">
          {r.notConfigured
            ? "Add your Gemini API key in Settings to run AI verification."
            : "Run AI verification to extract facts, detect misinformation and summarize."}
        </p>
        <Button size="sm" onClick={() => r.enrich()}>
          <Sparkles className="h-4 w-4" /> Run AI verification
        </Button>
      </div>
    );
  };

  const exportMd = () => download(`research-${trend.id}.md`, researchToMarkdown(base, ai), "text/markdown");
  const exportJson = () =>
    download(`research-${trend.id}.json`, JSON.stringify({ base, ai }, null, 2), "application/json");
  const copyJson = async () => {
    await navigator.clipboard.writeText(JSON.stringify({ base, ai }, null, 2));
    toast.success("Copied research JSON");
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="surface flex flex-wrap items-center gap-3 p-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-base font-semibold">{base.title}</h2>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[var(--muted-foreground)]">
            <span className="font-semibold text-[var(--accent)]">
              {base.research_confidence}/100 confidence
            </span>
            <span>· {base.sources.length} sources</span>
            <span>· {base.member_count} items clustered</span>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <Button size="sm" variant="outline" onClick={r.build}>
            <RefreshCw className="h-4 w-4" /> Rebuild
          </Button>
          <Button size="sm" onClick={() => r.enrich(!!ai)}>
            <ShieldCheck className="h-4 w-4" /> {ai ? "Re-verify" : "AI verify"}
          </Button>
          <button onClick={copyJson} className="research-btn" title="Copy JSON"><Copy className="h-4 w-4" /></button>
          <button onClick={exportMd} className="research-btn" title="Export Markdown"><Download className="h-4 w-4" /></button>
          <button onClick={exportJson} className="research-btn" title="Export JSON">.json</button>
          <button onClick={() => window.print()} className="research-btn" title="Print / PDF"><Printer className="h-4 w-4" /></button>
        </div>
      </div>
      <style>{`.research-btn{display:inline-flex;align-items:center;gap:4px;border:1px solid var(--border);border-radius:6px;padding:6px 8px;font-size:12px;color:var(--muted-foreground)}.research-btn:hover{background:var(--muted);color:var(--foreground)}`}</style>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto border-b border-[var(--border)]">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "relative shrink-0 px-3 py-2.5 text-sm font-medium capitalize transition-colors",
              tab === t ? "text-[var(--foreground)]" : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]",
            )}
          >
            {t}
            {tab === t && (
              <motion.span layoutId="research-tab" className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-[var(--accent)]" />
            )}
          </button>
        ))}
      </div>

      {/* Panels */}
      {tab === "overview" && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Card><Field label="Confidence" value={`${base.research_confidence}/100`} /></Card>
            <Card><Field label="Sources" value={base.sources.length} /></Card>
            <Card><Field label="Items clustered" value={base.member_count} /></Card>
          </div>
          <AiGate>
            {(a) => (
              <div className="space-y-4">
                <Section title="Executive summary"><p className="text-sm leading-relaxed">{a.summaries.executive}</p></Section>
                <Section title="Best creator angle"><p className="text-sm">{a.best_creator_angle}</p></Section>
                <Section title="Key takeaways"><BulletList items={a.key_takeaways} /></Section>
              </div>
            )}
          </AiGate>
        </div>
      )}

      {tab === "timeline" && (
        <ol className="relative space-y-3 border-l border-[var(--border)] pl-5">
          {base.timeline.length === 0 && <p className="text-sm text-[var(--muted-foreground)]">No timed events.</p>}
          {base.timeline.map((e, i) => (
            <li key={i} className="relative">
              <span className="absolute -left-[23px] top-1 h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
              <div className="surface p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-[var(--muted-foreground)]">
                    {e.time ? new Date(e.time).toLocaleString() : "unknown"}
                  </span>
                  <TierBadge tier={e.tier} />
                </div>
                <p className="mt-1 text-sm">{e.title}</p>
                <p className="text-xs text-[var(--muted-foreground)]">{e.source}</p>
              </div>
            </li>
          ))}
        </ol>
      )}

      {tab === "sources" && (
        <div className="space-y-2">
          {base.sources.map((s) => (
            <div key={s.source} className="surface flex items-center gap-3 p-3">
              <TierBadge tier={s.tier} label={s.tier_label} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{s.source}</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  {s.count} item(s) · latest {relativeTime(s.latest)}
                </p>
              </div>
              <span className="text-sm font-semibold text-[var(--accent)]">{s.score}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "facts" && (
        <AiGate>
          {(a) => (
            <div className="space-y-3">
              <Section title="Confirmed facts"><BulletList items={a.facts.confirmed} /></Section>
              <Section title="Unconfirmed claims"><BulletList items={a.facts.unconfirmed_claims} /></Section>
              <Section title="Rumors"><BulletList items={a.facts.rumors} /></Section>
              <Section title="Developer statements"><BulletList items={a.facts.developer_statements} /></Section>
              {a.facts.quotes.length > 0 && <Section title="Quotes"><BulletList items={a.facts.quotes} /></Section>}
              <div className="grid grid-cols-2 gap-4">
                <Section title="Dates"><Pills items={a.facts.dates} /></Section>
                <Section title="Locations"><Pills items={a.facts.locations} /></Section>
              </div>
            </div>
          )}
        </AiGate>
      )}

      {tab === "entities" && (
        <div className="space-y-3">
          <Section title="Detected (instant)">
            <div className="space-y-2">
              {base.entities.companies.length > 0 && (<div><p className="mb-1 text-[11px] uppercase text-[var(--muted-foreground)]">Companies</p><Pills items={base.entities.companies} /></div>)}
              {base.entities.platforms.length > 0 && (<div><p className="mb-1 text-[11px] uppercase text-[var(--muted-foreground)]">Platforms</p><Pills items={base.entities.platforms} /></div>)}
              {base.entities.topics.length > 0 && (<div><p className="mb-1 text-[11px] uppercase text-[var(--muted-foreground)]">Topics</p><Pills items={base.entities.topics.map((t) => t.name)} /></div>)}
            </div>
          </Section>
          {ai && (
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(ai.entities).map(([type, items]) =>
                items.length ? (
                  <Section key={type} title={type}><Pills items={items} /></Section>
                ) : null,
              )}
            </div>
          )}
        </div>
      )}

      {tab === "community" && (
        <div className="space-y-3">
          {ai && <Section title="Community reaction"><p className="text-sm leading-relaxed">{ai.summaries.community}</p></Section>}
          <Section title="Community sources">
            <div className="space-y-2">
              {base.members.filter((m) => m.tier === "community").map((m) => (
                <a key={m.trend_id} href={m.url ?? "#"} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm hover:text-[var(--accent)]">
                  <ExternalLink className="h-3.5 w-3.5 shrink-0" /> {m.title}
                </a>
              ))}
              {base.members.filter((m) => m.tier === "community").length === 0 && (
                <p className="text-sm text-[var(--muted-foreground)]">No community discussion found in the cluster.</p>
              )}
            </div>
          </Section>
        </div>
      )}

      {tab === "keywords" && (
        <div className="space-y-3">
          <Section title="Trending keywords">
            <Pills items={base.keywords.trending.map((k) => `${k.word} (${k.count})`)} />
          </Section>
          <Section title="Key phrases"><Pills items={base.keywords.search_phrases} /></Section>
          {base.keywords.emerging.length > 0 && <Section title="Emerging"><Pills items={base.keywords.emerging} /></Section>}
          {ai && (
            <>
              <Section title="Synonyms"><Pills items={ai.keywords.synonyms} /></Section>
              <Section title="Related searches"><Pills items={ai.keywords.related_searches} /></Section>
            </>
          )}
        </div>
      )}

      {tab === "verification" && (
        <AiGate>
          {(a) => (
            <div className="space-y-3">
              <div className="surface flex items-center gap-3 p-4">
                <span className="text-2xl font-semibold text-[var(--accent)]">{a.verification.confidence}</span>
                <span className="text-sm text-[var(--muted-foreground)]">verification confidence</span>
              </div>
              <Section title="Strong evidence"><BulletList items={a.verification.strong_evidence} /></Section>
              <Section title="Weak evidence"><BulletList items={a.verification.weak_evidence} /></Section>
              <Section title="Conflicts"><BulletList items={a.verification.conflicts} /></Section>
              <Section title="Repeated claims (not independent confirmation)"><BulletList items={a.verification.repeated_claims} /></Section>
              <Section title="Possible misinformation"><BulletList items={a.verification.possible_misinformation} /></Section>
              <Section title="Missing information"><BulletList items={a.verification.missing_information} /></Section>
            </div>
          )}
        </AiGate>
      )}
    </div>
  );
}
