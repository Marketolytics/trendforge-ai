import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { toast } from "sonner";
import { orchestratorApi, isActiveJob, type Job, type JobCreate } from "@/lib/api";
import { notify } from "@/lib/notifications";

interface JobsState {
  jobs: Job[];
  activeCount: number;
  enqueue: (payload: JobCreate) => Promise<Job | null>;
  cancel: (id: string) => Promise<void>;
  pause: (id: string) => Promise<void>;
  resume: (id: string) => Promise<void>;
  retry: (id: string) => Promise<void>;
  refresh: () => Promise<void>;
}

const JobsContext = createContext<JobsState | null>(null);

export function JobsProvider({ children }: { children: ReactNode }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const timer = useRef<number | null>(null);
  const notified = useRef<Set<string>>(new Set());

  // Desktop notification when a job finishes.
  useEffect(() => {
    for (const j of jobs) {
      if ((j.status === "completed" || j.status === "failed") && j.finished_at && !notified.current.has(j.id)) {
        notified.current.add(j.id);
        notify(
          j.status === "completed" ? "Workflow complete" : "Workflow failed",
          `${j.workflow.replace("_", " ")} · ${j.status}`,
        );
      }
    }
  }, [jobs]);

  const refresh = useCallback(async () => {
    try {
      setJobs(await orchestratorApi.listJobs(undefined, 20));
    } catch {
      /* backend offline — ignore */
    }
  }, []);

  const activeCount = jobs.filter(isActiveJob).length;

  // Adaptive polling: fast while jobs are active, slow otherwise.
  useEffect(() => {
    const tick = async () => {
      await refresh();
    };
    tick();
    const interval = activeCount > 0 ? 1200 : 6000;
    timer.current = window.setInterval(tick, interval);
    return () => {
      if (timer.current) window.clearInterval(timer.current);
    };
  }, [refresh, activeCount]);

  const enqueue = useCallback(
    async (payload: JobCreate) => {
      try {
        const job = await orchestratorApi.createJob(payload);
        await refresh();
        toast.success("Workflow queued", { description: payload.workflow });
        return job;
      } catch {
        toast.error("Could not queue workflow");
        return null;
      }
    },
    [refresh],
  );

  const control = useCallback(
    (fn: (id: string) => Promise<unknown>) => async (id: string) => {
      try {
        await fn(id);
      } catch {
        /* ignore */
      }
      await refresh();
    },
    [refresh],
  );

  const value = useMemo<JobsState>(
    () => ({
      jobs,
      activeCount,
      enqueue,
      cancel: control(orchestratorApi.cancel),
      pause: control(orchestratorApi.pause),
      resume: control(orchestratorApi.resume),
      retry: control(orchestratorApi.retry),
      refresh,
    }),
    [jobs, activeCount, enqueue, control, refresh],
  );

  return <JobsContext.Provider value={value}>{children}</JobsContext.Provider>;
}

export function useJobs(): JobsState {
  const ctx = useContext(JobsContext);
  if (!ctx) throw new Error("useJobs must be used within a JobsProvider");
  return ctx;
}
