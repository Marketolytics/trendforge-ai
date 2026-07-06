import { Download, RefreshCw } from "lucide-react";
import { studioApi, type ModuleKind } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { CopyButton } from "./primitives";
import { StudioSection } from "./StudioSection";
import { MODULE_VIEWS, copyTextFor } from "./ModuleViews";
import { MODULE_LABELS, type Workspace } from "./useWorkspace";

export function ModulePanel({
  kind,
  ws,
  trendId,
}: {
  kind: ModuleKind;
  ws: Workspace;
  trendId: number;
}) {
  const status = ws.moduleStatus[kind];
  const data = ws.modules[kind]?.data as any;
  const view = MODULE_VIEWS[kind];
  const ready = status === "ready" && data;

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">{MODULE_LABELS[kind]}</h3>
        {ready && (
          <div className="flex items-center gap-1.5">
            <CopyButton text={copyTextFor(kind, data)} />
            <a
              href={studioApi.exportModuleUrl(trendId, kind, ws.format, "md")}
              className="inline-flex items-center gap-1 rounded-md border border-[var(--border)] px-2 py-1 text-xs text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
              title="Export Markdown"
            >
              <Download className="h-3.5 w-3.5" />
              .md
            </a>
            <a
              href={studioApi.exportModuleUrl(trendId, kind, ws.format, "json")}
              className="inline-flex items-center gap-1 rounded-md border border-[var(--border)] px-2 py-1 text-xs text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
              title="Export JSON"
            >
              .json
            </a>
            <Button size="sm" variant="ghost" onClick={() => ws.generateModule(kind, true)}>
              <RefreshCw className="h-3.5 w-3.5" />
              Regenerate
            </Button>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto pr-1">
        <StudioSection
          status={status}
          notConfigured={ws.notConfigured}
          onGenerate={() => ws.generateModule(kind)}
          emptyLabel={`Generate ${MODULE_LABELS[kind].toLowerCase()}`}
        >
          {ready && view ? view(data) : null}
        </StudioSection>
      </div>
    </div>
  );
}
