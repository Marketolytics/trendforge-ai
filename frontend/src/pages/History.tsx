import { History as HistoryIcon } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";

export function History() {
  return (
    <EmptyState
      icon={HistoryIcon}
      title="No history yet"
      description="Every generated content package is saved locally and will appear here for quick reuse and duplicate detection."
    />
  );
}
