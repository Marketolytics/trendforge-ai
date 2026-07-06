import { useEffect } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { NAV_ITEMS } from "./navigation";
import { TrendsProvider } from "@/store/trends";
import { AnalysisPanel } from "@/components/trends/analysis/AnalysisPanel";

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
  "/intelligence": {
    title: "Creator Intelligence",
    subtitle: "Competitors, gaps, forecasts, history, favorites and analytics.",
  },
  "/settings": { title: "Settings", subtitle: "Sources, AI keys, preferences." },
};

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const meta =
    PAGE_META[location.pathname] ??
    (location.pathname.startsWith("/studio")
      ? PAGE_META["/studio"]
      : { title: "TrendForge AI", subtitle: "" });

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
      </div>
    </TrendsProvider>
  );
}
