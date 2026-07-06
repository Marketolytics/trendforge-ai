import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { ApiError, researchApi, type ResearchAI, type ResearchBase } from "@/lib/api";

interface ResearchState {
  base: ResearchBase | null;
  ai: ResearchAI | null;
  loading: boolean;
  enriching: boolean;
  notConfigured: boolean;
  build: () => Promise<void>;
  enrich: (force?: boolean) => Promise<void>;
}

export function useResearch(trendId: number): ResearchState {
  const [base, setBase] = useState<ResearchBase | null>(null);
  const [ai, setAi] = useState<ResearchAI | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [notConfigured, setNotConfigured] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await researchApi.get(trendId);
      setBase(res.base);
      setAi(res.ai);
    } catch {
      setBase(null);
    } finally {
      setLoading(false);
    }
  }, [trendId]);

  useEffect(() => {
    load();
  }, [load]);

  const build = useCallback(async () => {
    setLoading(true);
    try {
      const res = await researchApi.build(trendId);
      setBase(res.base);
      setAi(res.ai);
      toast.success("Research rebuilt");
    } finally {
      setLoading(false);
    }
  }, [trendId]);

  const enrich = useCallback(
    async (force = false) => {
      setEnriching(true);
      setNotConfigured(false);
      const t = toast.loading("Running AI verification…");
      try {
        const env = await researchApi.enrich(trendId, force);
        setAi(env.data);
        toast.success("Research verified", { id: t });
      } catch (err) {
        if (err instanceof ApiError && err.status === 409) setNotConfigured(true);
        toast.error("Verification failed", {
          id: t,
          description: err instanceof ApiError ? err.message : undefined,
        });
      } finally {
        setEnriching(false);
      }
    },
    [trendId],
  );

  return { base, ai, loading, enriching, notConfigured, build, enrich };
}
