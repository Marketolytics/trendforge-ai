import { TrendingUp } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";

export function Trends() {
  return (
    <EmptyState
      icon={TrendingUp}
      title="Trend collection coming next"
      description="This view will list every collected topic from Google Trends, YouTube, Reddit, Steam, RSS feeds and more — normalized and scored."
    />
  );
}
