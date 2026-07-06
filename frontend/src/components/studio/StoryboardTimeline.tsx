import { RefreshCw, Film } from "lucide-react";
import type { Storyboard } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StudioSection } from "./StudioSection";
import type { Workspace } from "./useWorkspace";

export function StoryboardTimeline({ ws }: { ws: Workspace }) {
  const status = ws.moduleStatus.storyboard;
  const data = ws.modules.storyboard?.data as Storyboard | undefined;

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Film className="h-4 w-4 text-[var(--accent)]" />
          <h3 className="text-sm font-semibold">Storyboard</h3>
          {data?.scenes?.length ? (
            <Badge variant="muted">{data.scenes.length} scenes</Badge>
          ) : null}
        </div>
        {status === "ready" && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => ws.generateModule("storyboard", true)}
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate
          </Button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto pr-1">
        <StudioSection
          status={status}
          notConfigured={ws.notConfigured}
          onGenerate={() => ws.generateModule("storyboard")}
          emptyLabel="Generate storyboard"
          loadingLabel="Directing the storyboard…"
        >
          {data && data.scenes?.length > 0 ? (
            <ol className="relative space-y-3 border-l border-[var(--border)] pl-5">
              {data.scenes.map((scene) => (
                <li key={scene.number} className="relative">
                  <span className="absolute -left-[26px] flex h-5 w-5 items-center justify-center rounded-full bg-[var(--accent)] text-[10px] font-semibold text-[var(--accent-foreground)]">
                    {scene.number}
                  </span>
                  <div className="surface space-y-2 p-3.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {scene.emotion && <Badge>{scene.emotion}</Badge>}
                        {scene.camera_angle && (
                          <span className="text-xs text-[var(--muted-foreground)]">
                            {scene.camera_angle}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-[var(--muted-foreground)]">
                        {scene.duration_seconds}s
                      </span>
                    </div>
                    {scene.visual && <p className="text-sm">{scene.visual}</p>}
                    {scene.narration && (
                      <p className="text-xs italic text-[var(--muted-foreground)]">
                        “{scene.narration}”
                      </p>
                    )}
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-[var(--muted-foreground)]">
                      {scene.transition && <span>→ {scene.transition}</span>}
                      {scene.sound_effect && <span>♪ {scene.sound_effect}</span>}
                      {scene.animation_notes && <span>⚙ {scene.animation_notes}</span>}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <p className="py-8 text-center text-sm text-[var(--muted-foreground)]">
              No scenes yet.
            </p>
          )}
        </StudioSection>
      </div>
    </div>
  );
}
