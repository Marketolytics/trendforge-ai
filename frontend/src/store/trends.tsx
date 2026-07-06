import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { toast } from "sonner";
import { api, ApiError, type Trend } from "@/lib/api";

type Status = "idle" | "loading" | "refreshing" | "error";

interface TrendsState {
  trends: Trend[];
  status: Status;
  error: string | null;
  lastRefresh: string | null;
  loadTrends: () => Promise<void>;
  refresh: (force?: boolean) => Promise<void>;
}

const TrendsContext = createContext<TrendsState | null>(null);

export function TrendsProvider({ children }: { children: ReactNode }) {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<string | null>(null);

  const loadTrends = useCallback(async () => {
    try {
      const res = await api.getTrends({ limit: 100 });
      setTrends(res.trends);
      setError(null);
      if (res.trends.length > 0) {
        setLastRefresh(res.trends[0].collection_timestamp);
      }
      setStatus("idle");
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to load trends";
      setError(message);
      setStatus("error");
    }
  }, []);

  const refresh = useCallback(
    async (force = false) => {
      setStatus("refreshing");
      const loading = toast.loading("Collecting live trends…");
      try {
        const result = await api.refreshTrends(force);
        await loadTrends();
        toast.success(
          `Collected ${result.trends_collected} trends from ${result.sources_ok} sources`,
          {
            id: loading,
            description:
              result.sources_failed > 0
                ? `${result.sources_failed} source(s) failed`
                : `in ${(result.duration_ms / 1000).toFixed(1)}s`,
          },
        );
        setLastRefresh(new Date().toISOString());
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "Refresh failed";
        setError(message);
        setStatus("error");
        toast.error("Refresh failed", { id: loading, description: message });
      }
    },
    [loadTrends],
  );

  // Initial load of any previously collected trends.
  useEffect(() => {
    loadTrends();
  }, [loadTrends]);

  const value = useMemo(
    () => ({ trends, status, error, lastRefresh, loadTrends, refresh }),
    [trends, status, error, lastRefresh, loadTrends, refresh],
  );

  return <TrendsContext.Provider value={value}>{children}</TrendsContext.Provider>;
}

export function useTrends(): TrendsState {
  const ctx = useContext(TrendsContext);
  if (!ctx) throw new Error("useTrends must be used within a TrendsProvider");
  return ctx;
}
