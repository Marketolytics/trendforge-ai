import { useEffect, useRef, useState } from "react";
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
import { CommandPalette } from "@/components/command/CommandPalette";
import { UpdateBanner } from "@/components/common/UpdateBanner";
import { OnboardingWizard } from "@/components/common/OnboardingWizard";
import { toggleTheme } from "@/lib/theme";
import { getAppState, patchAppState } from "@/lib/appState";

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
  "/export": {
    title: "Export Center",
    subtitle: "Export packages, back up your data and move projects.",
  },
  "/settings": { title: "Settings", subtitle: "AI keys, appearance, data, notifications, developer." },
};

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [devOpen, setDevOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);

  // Global shortcuts: Ctrl/Cmd+K palette, "/" search, Ctrl/Cmd+Shift+D dev panel.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const typing = target.tagName === "INPUT" || target.tagName === "TEXTAREA";
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "d") {
        e.preventDefault();
        setDevOpen((o) => !o);
      } else if (e.key === "/" && !typing) {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  const prefixMeta = ["/studio", "/research"].find((p) => location.pathname.startsWith(p));
  const meta =
    PAGE_META[location.pathname] ??
    (prefixMeta ? PAGE_META[prefixMeta] : { title: "TrendForge AI", subtitle: "" });

  // Restore the last visited route once, on first launch.
  const restored = useRef(false);
  useEffect(() => {
    if (restored.current) return;
    restored.current = true;
    const last = getAppState().lastRoute;
    if (last && last !== "/" && location.pathname === "/") navigate(last);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist the current route for next launch.
  useEffect(() => {
    patchAppState({ lastRoute: location.pathname });
  }, [location.pathname]);

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
            <UpdateBanner />
            <Header title={meta.title} subtitle={meta.subtitle} onSearch={() => setPaletteOpen(true)} />
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
          <OnboardingWizard />
          <DeveloperPanel open={devOpen} onClose={() => setDevOpen(false)} />
          <CommandPalette
            open={paletteOpen}
            onClose={() => setPaletteOpen(false)}
            onToggleTheme={toggleTheme}
            onToggleDev={() => setDevOpen((o) => !o)}
          />
        </div>
      </JobsProvider>
    </TrendsProvider>
  );
}
