import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ExternalLink, X } from "lucide-react";
import type { Trend } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useTrends } from "@/store/trends";
import { ScoreRing } from "../ScoreRing";
import { OverviewTab } from "./OverviewTab";
import {
  HooksTab,
  StrategyTab,
  SummaryTab,
  ThumbnailTab,
  TitlesTab,
} from "./GeneratorTabs";

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "summary", label: "Summary" },
  { key: "strategy", label: "Strategy" },
  { key: "hooks", label: "Hooks" },
  { key: "titles", label: "Titles" },
  { key: "thumbnail", label: "Thumbnail" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

function TabContent({ tab, trend }: { tab: TabKey; trend: Trend }) {
  switch (tab) {
    case "overview":
      return <OverviewTab trendId={trend.id} />;
    case "summary":
      return <SummaryTab trendId={trend.id} />;
    case "strategy":
      return <StrategyTab trendId={trend.id} />;
    case "hooks":
      return <HooksTab trendId={trend.id} />;
    case "titles":
      return <TitlesTab trendId={trend.id} />;
    case "thumbnail":
      return <ThumbnailTab trendId={trend.id} />;
  }
}

function PanelInner({ trend }: { trend: Trend }) {
  const { closeTrend } = useTrends();
  const [tab, setTab] = useState<TabKey>("overview");

  // Reset to overview whenever a different trend opens.
  useEffect(() => setTab("overview"), [trend.id]);

  return (
    <motion.aside
      className="fixed right-0 top-0 z-50 flex h-full w-full max-w-2xl flex-col border-l border-[var(--border)] bg-[var(--background)] shadow-2xl"
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ type: "spring", stiffness: 320, damping: 34 }}
    >
      {/* Header */}
      <div className="flex items-start gap-3 border-b border-[var(--border)] p-5">
        <ScoreRing score={trend.score} />
        <div className="min-w-0 flex-1">
          <h2 className="text-base font-semibold leading-tight">{trend.title}</h2>
          <div className="mt-1 flex items-center gap-2 text-xs text-[var(--muted-foreground)]">
            <span className="font-medium text-[var(--foreground)]/80">{trend.source}</span>
            <span>·</span>
            <span className="capitalize">{trend.category}</span>
            {trend.url && (
              <a
                href={trend.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[var(--accent)] hover:underline"
              >
                <ExternalLink className="h-3 w-3" />
                Source
              </a>
            )}
          </div>
        </div>
        <button
          onClick={closeTrend}
          className="rounded-md p-1.5 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto border-b border-[var(--border)] px-3">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={cn(
              "relative shrink-0 px-3 py-2.5 text-sm font-medium transition-colors",
              tab === t.key
                ? "text-[var(--foreground)]"
                : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]",
            )}
          >
            {t.label}
            {tab === t.key && (
              <motion.span
                layoutId="tab-underline"
                className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-[var(--accent)]"
              />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        <TabContent tab={tab} trend={trend} />
      </div>
    </motion.aside>
  );
}

export function AnalysisPanel() {
  const { selected, closeTrend } = useTrends();

  // Close on Escape.
  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeTrend();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selected, closeTrend]);

  return (
    <AnimatePresence>
      {selected && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeTrend}
          />
          <PanelInner trend={selected} />
        </>
      )}
    </AnimatePresence>
  );
}
