import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { NAV_ITEMS } from "./navigation";
import { TrendsProvider } from "@/store/trends";
import { JobsProvider } from "@/store/jobs";
import { AnalysisPanel } from "@/components/trends/analysis/AnalysisPanel";
import { JobMonitor } from "@/components/jobs/JobMonitor";
import { DeveloperPanel } from "@/components/dev/DeveloperPanel";

const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  "/": {
    title: "Dashboard",
    subtitle: "Today's highest-opportunity content, ranked.",
  },
  "/trends": {
    title: "Trends",
    subtitle: "Collected topics from every source.",
  },
  "/studio": {
    title: "Production Studio",
    subtitle: "Turn a trend into a full, export-ready content package.",
  },
  "/research": {
    title: "Research Workspace",
    subtitle: "Multi-source intelligence: sources, timeline, facts and verification.",
  },
  "/intelligence": {
    title: "Creator Intelligence",
    subtitle: "Competitors, gaps, forecasts, history, favorites and analytics.",
  },
  "/settings": { title: "Settings", subtitle: "Sources, AI keys, preferences." },
};

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [devOpen, setDevOpen] = useState(false);

  // Developer mode toggle: Ctrl/Cmd + Shift + D.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "d") {
        e.preventDefault();
        setDevOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  const prefixMeta = ["/studio", "/research"].find((p) => location.pathname.startsWith(p));
  const meta =
    PAGE_META[location.pathname] ??
    (prefixMeta ? PAGE_META[prefixMeta] : { title: "TrendForge AI", subtitle: "" });

  // Keyboard shortcuts: 1-5 jump between modules.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;
      const item = NAV_ITEMS.find((n) => n.shortcut === e.key);
      if (item && !e.metaKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        navigate(item.to);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navigate]);

  return (
    <TrendsProvider>
      <JobsProvider>
        <div className="flex h-screen w-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)]">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <Header title={meta.title} subtitle={meta.subtitle} />
            <main className="flex-1 overflow-y-auto">
              <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: "easeOut" }}
                  className="mx-auto max-w-6xl px-6 py-6"
                >
                  <Outlet />
                </motion.div>
              </AnimatePresence>
            </main>
          </div>
          <AnalysisPanel />
          <JobMonitor />
          <DeveloperPanel open={devOpen} onClose={() => setDevOpen(false)} />
        </div>
      </JobsProvider>
    </TrendsProvider>
  );
}
