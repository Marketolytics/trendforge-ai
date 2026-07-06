import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, type AiEnvelope } from "@/lib/api";

type AiStatus = "idle" | "loading" | "ready" | "error";

export interface AiResource<T> {
  status: AiStatus;
  data: T | null;
  error: string | null;
  notConfigured: boolean;
  cached: boolean;
  version: string | null;
  generatedAt: string | null;
  load: () => Promise<void>;
  regenerate: () => Promise<void>;
}

/**
 * Loads a single AI resource for a trend. `auto` triggers a load once when the
 * trend id becomes available. `regenerate` re-runs with force=true.
 */
export function useAi<T>(
  trendId: number | null,
  call: (id: number, force: boolean) => Promise<AiEnvelope<T>>,
  auto = false,
): AiResource<T> {
  const [status, setStatus] = useState<AiStatus>("idle");
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notConfigured, setNotConfigured] = useState(false);
  const [cached, setCached] = useState(false);
  const [version, setVersion] = useState<string | null>(null);
  const [generatedAt, setGeneratedAt] = useState<string | null>(null);

  // Guard against overlapping / stale requests when switching trends.
  const activeId = useRef<number | null>(null);

  const run = useCallback(
    async (force: boolean) => {
      if (trendId == null) return;
      const requestId = trendId;
      activeId.current = requestId;
      setStatus("loading");
      setError(null);
      setNotConfigured(false);
      try {
        const res = await call(requestId, force);
        if (activeId.current !== requestId) return; // stale
        setData(res.data);
        setCached(res.cached);
        setVersion(res.prompt_version);
        setGeneratedAt(res.generated_at);
        setStatus("ready");
      } catch (err) {
        if (activeId.current !== requestId) return;
        if (err instanceof ApiError && err.status === 409) {
          setNotConfigured(true);
        }
        setError(err instanceof ApiError ? err.message : "Generation failed");
        setStatus("error");
      }
    },
    [trendId, call],
  );

  const load = useCallback(() => run(false), [run]);
  const regenerate = useCallback(() => run(true), [run]);

  // Reset + optional auto-load when the trend changes.
  useEffect(() => {
    setStatus("idle");
    setData(null);
    setError(null);
    setNotConfigured(false);
    if (auto && trendId != null) {
      run(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trendId]);

  return {
    status,
    data,
    error,
    notConfigured,
    cached,
    version,
    generatedAt,
    load,
    regenerate,
  };
}
