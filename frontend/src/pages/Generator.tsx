import { Sparkles } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";

export function Generator() {
  return (
    <EmptyState
      icon={Sparkles}
      title="Content generator coming soon"
      description="Pick a trend and generate video ideas, hooks, scripts, storyboards, image and video prompts, thumbnails and full SEO — powered by Gemini."
    />
  );
}
