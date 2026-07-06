import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Star, Search, Trash2 } from "lucide-react";
import { favoritesApi, type FavoriteItem } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/EmptyState";
import { cn } from "@/lib/utils";
import { relativeTime } from "@/lib/format";
import { VirtualTable } from "./VirtualTable";

const TYPES = ["all", "trend", "script", "prompt", "hook", "thumbnail", "seo"];

export function FavoritesTab() {
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [type, setType] = useState("all");
  const [q, setQ] = useState("");

  const load = useCallback(async () => {
    const list = await favoritesApi.list(type === "all" ? undefined : type, q || undefined);
    setItems(list);
  }, [type, q]);

  useEffect(() => {
    const id = setTimeout(load, 200);
    return () => clearTimeout(id);
  }, [load]);

  const remove = async (id: number) => {
    await favoritesApi.remove(id);
    setItems((prev) => prev.filter((f) => f.id !== id));
    toast.success("Removed from favorites");
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-9 min-w-56 flex-1 items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-[var(--muted-foreground)] focus-within:border-[var(--ring)]">
          <Search className="h-4 w-4" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search favorites…"
            className="w-full bg-transparent text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]"
          />
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {TYPES.map((t) => (
          <button
            key={t}
            onClick={() => setType(t)}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium capitalize transition-colors",
              type === t
                ? "border-transparent bg-[var(--accent)] text-[var(--accent-foreground)]"
                : "border-[var(--border)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]",
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <VirtualTable
        rows={items}
        rowHeight={56}
        height={480}
        empty={
          <EmptyState
            icon={Star}
            title="No favorites yet"
            description="Save trends, scripts, prompts, hooks and more to find them here."
          />
        }
        renderRow={(f) => (
          <div className="flex h-14 items-center gap-3 border-b border-[var(--border)] px-4">
            <Star className="h-4 w-4 shrink-0 text-[var(--warning)]" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm">{f.label}</p>
              <p className="text-[11px] text-[var(--muted-foreground)]">saved {relativeTime(f.created_at)}</p>
            </div>
            <Badge variant="muted">{f.type}</Badge>
            <button onClick={() => remove(f.id)} title="Remove">
              <Trash2 className="h-3.5 w-3.5 text-[var(--muted-foreground)] hover:text-[var(--danger)]" />
            </button>
          </div>
        )}
      />
    </div>
  );
}
