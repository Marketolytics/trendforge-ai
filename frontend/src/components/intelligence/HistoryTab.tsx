import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { History as HistoryIcon, Search, ArrowUpRight } from "lucide-react";
import { intelligenceApi, type ProjectItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/EmptyState";
import { relativeTime } from "@/lib/format";
import { VirtualTable } from "./VirtualTable";

type Sort = "recent" | "modules" | "title";

export function HistoryTab() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<Sort>("recent");

  const load = useCallback(async () => {
    const list = await intelligenceApi.projects(q || undefined, sort);
    setProjects(list);
  }, [q, sort]);

  useEffect(() => {
    const id = setTimeout(load, 200);
    return () => clearTimeout(id);
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-9 min-w-56 flex-1 items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-[var(--muted-foreground)] focus-within:border-[var(--ring)]">
          <Search className="h-4 w-4" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search projects…"
            className="w-full bg-transparent text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as Sort)}
          className="h-9 rounded-md border border-[var(--border)] bg-[var(--card)] px-2 text-sm outline-none focus:border-[var(--ring)]"
        >
          <option value="recent">Most recent</option>
          <option value="modules">Most modules</option>
          <option value="title">Title A–Z</option>
        </select>
      </div>

      <VirtualTable
        rows={projects}
        rowHeight={64}
        height={520}
        empty={
          <EmptyState
            icon={HistoryIcon}
            title="No projects yet"
            description="Generate a content package in the Studio and it will appear here for reopening."
          />
        }
        renderRow={(p) => (
          <div className="flex h-16 items-center gap-3 border-b border-[var(--border)] px-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{p.title}</p>
              <div className="mt-1 flex items-center gap-2 text-[11px] text-[var(--muted-foreground)]">
                <Badge variant="muted">{p.variant || "—"}</Badge>
                <span>{p.module_count} modules</span>
                <span>· updated {relativeTime(p.updated_at)}</span>
              </div>
            </div>
            {p.trend_id != null && (
              <Button size="sm" variant="outline" onClick={() => navigate(`/studio/${p.trend_id}`)}>
                <ArrowUpRight className="h-4 w-4" /> Open
              </Button>
            )}
          </div>
        )}
      />
    </div>
  );
}
