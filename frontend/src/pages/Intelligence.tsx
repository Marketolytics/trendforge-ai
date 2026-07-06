import { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { OverviewTab, type IntelTab } from "@/components/intelligence/OverviewTab";
import { CompetitorsTab } from "@/components/intelligence/CompetitorsTab";
import { OpportunitiesTab } from "@/components/intelligence/OpportunitiesTab";
import { ForecastTab } from "@/components/intelligence/ForecastTab";
import { HistoryTab } from "@/components/intelligence/HistoryTab";
import { FavoritesTab } from "@/components/intelligence/FavoritesTab";
import { AnalyticsTab } from "@/components/intelligence/AnalyticsTab";

const TABS: { key: IntelTab; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "competitors", label: "Competitors" },
  { key: "opportunities", label: "Opportunities" },
  { key: "forecast", label: "Forecast" },
  { key: "history", label: "History" },
  { key: "favorites", label: "Favorites" },
  { key: "analytics", label: "Analytics" },
];

export function Intelligence() {
  const [tab, setTab] = useState<IntelTab>("overview");

  return (
    <div className="space-y-5">
      <div className="flex gap-1 overflow-x-auto border-b border-[var(--border)]">
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
                layoutId="intel-tab-underline"
                className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-[var(--accent)]"
              />
            )}
          </button>
        ))}
      </div>

      {tab === "overview" && <OverviewTab onNavigate={setTab} />}
      {tab === "competitors" && <CompetitorsTab />}
      {tab === "opportunities" && <OpportunitiesTab />}
      {tab === "forecast" && <ForecastTab />}
      {tab === "history" && <HistoryTab />}
      {tab === "favorites" && <FavoritesTab />}
      {tab === "analytics" && <AnalyticsTab />}
    </div>
  );
}
