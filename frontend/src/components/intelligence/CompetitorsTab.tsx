import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Plus, RefreshCw, Trash2, Users, ExternalLink } from "lucide-react";
import {
  competitorsApi,
  type CompetitorChannel,
  type CompetitorVideo,
  type Patterns,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/EmptyState";
import { cn } from "@/lib/utils";
import { compactNumber, relativeTime } from "@/lib/format";
import { VirtualTable } from "./VirtualTable";

export function CompetitorsTab() {
  const [channels, setChannels] = useState<CompetitorChannel[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [videos, setVideos] = useState<CompetitorVideo[]>([]);
  const [patterns, setPatterns] = useState<Patterns | null>(null);
  const [handle, setHandle] = useState("");
  const [busy, setBusy] = useState(false);

  const loadChannels = useCallback(async () => {
    const list = await competitorsApi.list();
    setChannels(list);
  }, []);

  const loadData = useCallback(async (pk: number | null) => {
    const [v, p] = await Promise.all([
      competitorsApi.videos(pk ?? undefined),
      competitorsApi.patterns(pk ?? undefined),
    ]);
    setVideos(v);
    setPatterns(p);
  }, []);

  useEffect(() => {
    loadChannels();
  }, [loadChannels]);

  useEffect(() => {
    loadData(selected);
  }, [selected, loadData]);

  const add = async () => {
    if (!handle.trim()) return;
    setBusy(true);
    try {
      await competitorsApi.add(handle.trim());
      setHandle("");
      await loadChannels();
      await loadData(selected);
      toast.success("Channel added");
    } catch (err) {
      toast.error("Could not add channel", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setBusy(false);
    }
  };

  const refreshAll = async () => {
    setBusy(true);
    const t = toast.loading("Refreshing competitors…");
    try {
      const r = await competitorsApi.refreshAll();
      await loadChannels();
      await loadData(selected);
      toast.success(`Refreshed ${r.channels} channels`, { id: t, description: `${r.new_videos} new videos` });
    } catch {
      toast.error("Refresh failed", { id: t });
    } finally {
      setBusy(false);
    }
  };

  const remove = async (pk: number) => {
    await competitorsApi.remove(pk);
    if (selected === pk) setSelected(null);
    await loadChannels();
    await loadData(selected === pk ? null : selected);
    toast.success("Channel removed");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      {/* Channels column */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Add competitor</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <input
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && add()}
              placeholder="@handle, channel URL, or UC… id"
              className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none focus:border-[var(--ring)]"
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={add} disabled={busy || !handle.trim()} className="flex-1">
                <Plus className="h-4 w-4" /> Add
              </Button>
              <Button size="sm" variant="outline" onClick={refreshAll} disabled={busy}>
                <RefreshCw className={cn("h-4 w-4", busy && "animate-spin")} />
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-1.5">
          <button
            onClick={() => setSelected(null)}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors",
              selected === null ? "bg-[var(--muted)]" : "hover:bg-[var(--muted)]",
            )}
          >
            <Users className="h-4 w-4 text-[var(--accent)]" />
            All channels
          </button>
          {channels.map((c) => (
            <div
              key={c.id}
              onClick={() => setSelected(c.id)}
              className={cn(
                "group flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                selected === c.id ? "bg-[var(--muted)]" : "hover:bg-[var(--muted)]",
              )}
            >
              {c.thumbnail ? (
                <img src={c.thumbnail} alt="" className="h-6 w-6 rounded-full object-cover" />
              ) : (
                <div className="h-6 w-6 rounded-full bg-[var(--muted)]" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate">{c.name}</p>
                <p className="text-[11px] text-[var(--muted-foreground)]">{c.video_count} videos</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  remove(c.id);
                }}
                className="opacity-0 transition-opacity group-hover:opacity-100"
                title="Remove"
              >
                <Trash2 className="h-3.5 w-3.5 text-[var(--muted-foreground)] hover:text-[var(--danger)]" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main column */}
      <div className="space-y-6">
        {channels.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No competitors yet"
            description="Add a YouTube channel by handle, URL, or channel id to start tracking their videos and patterns."
          />
        ) : (
          <>
            {patterns && patterns.total_videos > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Viral patterns</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                    <Stat label="Avg views" value={compactNumber(patterns.avg_views)} />
                    <Stat label="Max views" value={compactNumber(patterns.max_views)} />
                    <Stat label="Best day" value={patterns.best_day ?? "—"} />
                    <Stat label="Uploads/wk" value={String(patterns.frequency_per_week ?? "—")} />
                  </div>
                  {patterns.title_keywords && patterns.title_keywords.length > 0 && (
                    <div className="mt-4">
                      <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
                        Common title keywords
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {patterns.title_keywords.slice(0, 12).map((k) => (
                          <span
                            key={k.word}
                            className="rounded-full border border-[var(--border)] bg-[var(--muted)] px-2.5 py-0.5 text-xs"
                          >
                            {k.word} · {k.count}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            <VirtualTable
              rows={videos}
              rowHeight={56}
              height={460}
              header={
                <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2.5">
                  <span className="text-sm font-semibold">Videos ({videos.length})</span>
                  <span className="text-xs text-[var(--muted-foreground)]">sorted by recency</span>
                </div>
              }
              empty={
                <EmptyState
                  icon={Users}
                  title="No videos collected"
                  description="Refresh this channel to pull its latest videos."
                />
              }
              renderRow={(v) => (
                <div className="flex h-14 items-center gap-3 border-b border-[var(--border)] px-4">
                  {v.thumbnail && (
                    <img src={v.thumbnail} alt="" className="h-9 w-16 shrink-0 rounded object-cover" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm">{v.title}</p>
                    <p className="text-[11px] text-[var(--muted-foreground)]">
                      {relativeTime(v.published)}
                    </p>
                  </div>
                  <Badge variant="muted">{compactNumber(v.views)} views</Badge>
                  {v.url && (
                    <a href={v.url} target="_blank" rel="noopener noreferrer" title="Open">
                      <ExternalLink className="h-3.5 w-3.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]" />
                    </a>
                  )}
                </div>
              )}
            />
          </>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
        {label}
      </p>
      <p className="mt-0.5 text-lg font-semibold">{value}</p>
    </div>
  );
}
