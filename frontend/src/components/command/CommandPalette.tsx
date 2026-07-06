import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  Search,
  RefreshCw,
  LayoutDashboard,
  TrendingUp,
  Microscope,
  Clapperboard,
  Radar,
  Download,
  Settings as SettingsIcon,
  SunMoon,
  Terminal,
  CornerDownLeft,
} from "lucide-react";
import { searchApi, type SearchResult } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useTrends } from "@/store/trends";

interface Item {
  id: string;
  label: string;
  sublabel?: string;
  icon: any;
  run: () => void;
}

interface Props {
  open: boolean;
  onClose: () => void;
  onToggleTheme: () => void;
  onToggleDev: () => void;
}

export function CommandPalette({ open, onClose, onToggleTheme, onToggleDev }: Props) {
  const navigate = useNavigate();
  const { refresh } = useTrends();
  const [q, setQ] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setQ("");
      setResults([]);
      setSelected(0);
      setTimeout(() => inputRef.current?.focus(), 40);
    }
  }, [open]);

  // Debounced global search.
  useEffect(() => {
    if (!q.trim()) {
      setResults([]);
      return;
    }
    const t = setTimeout(() => {
      searchApi.search(q).then((r) => setResults(r.results)).catch(() => setResults([]));
    }, 180);
    return () => clearTimeout(t);
  }, [q]);

  const go = (path: string) => {
    onClose();
    navigate(path);
  };

  const commands: Item[] = useMemo(
    () => [
      { id: "refresh", label: "Refresh Trends", icon: RefreshCw, run: () => { onClose(); refresh(); } },
      { id: "nav-dash", label: "Go to Dashboard", icon: LayoutDashboard, run: () => go("/") },
      { id: "nav-trends", label: "Go to Trends", icon: TrendingUp, run: () => go("/trends") },
      { id: "nav-research", label: "Go to Research", icon: Microscope, run: () => go("/research") },
      { id: "nav-studio", label: "Go to Studio", icon: Clapperboard, run: () => go("/studio") },
      { id: "nav-intel", label: "Go to Intelligence", icon: Radar, run: () => go("/intelligence") },
      { id: "nav-export", label: "Open Export Center", icon: Download, run: () => go("/export") },
      { id: "nav-settings", label: "Open Settings", icon: SettingsIcon, run: () => go("/settings") },
      { id: "theme", label: "Toggle Theme", icon: SunMoon, run: () => { onClose(); onToggleTheme(); } },
      { id: "dev", label: "Toggle Developer Mode", icon: Terminal, run: () => { onClose(); onToggleDev(); } },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const resultPath = (r: SearchResult): string => {
    if (r.type === "content") return `/studio/${r.id}`;
    if (r.type === "favorite") return "/intelligence";
    return `/research/${r.id}`; // trend + research
  };

  const filteredCommands = commands.filter((c) => c.label.toLowerCase().includes(q.toLowerCase()));
  const resultItems: Item[] = results.map((r, i) => ({
    id: `res-${i}`,
    label: r.title,
    sublabel: `${r.type} · ${r.subtitle}`,
    icon: Search,
    run: () => go(resultPath(r)),
  }));
  const items = [...filteredCommands, ...resultItems];

  useEffect(() => {
    if (selected >= items.length) setSelected(0);
  }, [items.length, selected]);

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelected((s) => Math.min(s + 1, items.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelected((s) => Math.max(s - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      items[selected]?.run();
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed left-1/2 top-24 z-[61] w-full max-w-xl -translate-x-1/2 px-4"
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
          >
            <div className="surface overflow-hidden shadow-2xl">
              <div className="flex items-center gap-2 border-b border-[var(--border)] px-4">
                <Search className="h-4 w-4 text-[var(--muted-foreground)]" />
                <input
                  ref={inputRef}
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  onKeyDown={onKey}
                  placeholder="Search or run a command…"
                  className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-[var(--muted-foreground)]"
                />
                <kbd className="rounded border border-[var(--border)] bg-[var(--background)] px-1.5 text-[10px] text-[var(--muted-foreground)]">
                  esc
                </kbd>
              </div>
              <div className="max-h-80 overflow-y-auto py-1.5">
                {items.length === 0 && (
                  <p className="px-4 py-6 text-center text-sm text-[var(--muted-foreground)]">No matches.</p>
                )}
                {items.map((item, i) => (
                  <button
                    key={item.id}
                    onMouseEnter={() => setSelected(i)}
                    onClick={item.run}
                    className={cn(
                      "flex w-full items-center gap-3 px-4 py-2 text-left text-sm",
                      i === selected ? "bg-[var(--muted)]" : "",
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0 text-[var(--muted-foreground)]" />
                    <span className="min-w-0 flex-1 truncate">{item.label}</span>
                    {item.sublabel && (
                      <span className="shrink-0 truncate text-xs text-[var(--muted-foreground)]">
                        {item.sublabel}
                      </span>
                    )}
                    {i === selected && <CornerDownLeft className="h-3.5 w-3.5 text-[var(--muted-foreground)]" />}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
