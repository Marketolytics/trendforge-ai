import { useNavigate } from "react-router-dom";
import { RefreshCw, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTrends } from "@/store/trends";
import { BackendStatus } from "./BackendStatus";

interface HeaderProps {
  title: string;
  subtitle?: string;
  onSearch?: () => void;
}

export function Header({ title, subtitle, onSearch }: HeaderProps) {
  const navigate = useNavigate();
  const { refresh, status } = useTrends();
  const refreshing = status === "refreshing";

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-[var(--border)] bg-[var(--background)]/80 px-6 backdrop-blur">
      <div className="min-w-0">
        <h1 className="truncate text-sm font-semibold tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="truncate text-xs text-[var(--muted-foreground)]">
            {subtitle}
          </p>
        )}
      </div>

      {/* Search (opens command palette) */}
      <div className="ml-auto hidden items-center md:flex">
        <button
          onClick={onSearch}
          className="flex h-9 w-64 items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-[var(--muted-foreground)] transition-colors hover:border-[var(--ring)]"
        >
          <Search className="h-4 w-4" />
          <span className="flex-1 text-left text-sm">Search everything…</span>
          <kbd className="rounded border border-[var(--border)] bg-[var(--background)] px-1.5 text-[10px]">
            ⌘K
          </kbd>
        </button>
      </div>

      <div className="flex items-center gap-2">
        <BackendStatus />
        <Button
          variant="outline"
          size="sm"
          onClick={() => refresh()}
          disabled={refreshing}
        >
          <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
          {refreshing ? "Refreshing" : "Refresh"}
        </Button>
        <Button size="sm" onClick={() => navigate("/studio")}>
          <Sparkles className="h-4 w-4" />
          Studio
        </Button>
      </div>
    </header>
  );
}
