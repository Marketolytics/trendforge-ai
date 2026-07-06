import { lazy, Suspense, type ReactNode } from "react";
import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { Dashboard } from "@/pages/Dashboard";
import { Trends } from "@/pages/Trends";
import { Skeleton } from "@/components/ui/skeleton";

// Heavy workspaces are code-split so the initial bundle stays small.
const Studio = lazy(() => import("@/pages/Studio").then((m) => ({ default: m.Studio })));
const Research = lazy(() => import("@/pages/Research").then((m) => ({ default: m.Research })));
const Intelligence = lazy(() => import("@/pages/Intelligence").then((m) => ({ default: m.Intelligence })));
const Settings = lazy(() => import("@/pages/Settings").then((m) => ({ default: m.Settings })));
const ExportCenter = lazy(() => import("@/pages/ExportCenter").then((m) => ({ default: m.ExportCenter })));

function Lazy({ children }: { children: ReactNode }) {
  return <Suspense fallback={<Skeleton className="h-[60vh] w-full" />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "trends", element: <Trends /> },
      { path: "research", element: <Lazy><Research /></Lazy> },
      { path: "research/:trendId", element: <Lazy><Research /></Lazy> },
      { path: "studio", element: <Lazy><Studio /></Lazy> },
      { path: "studio/:trendId", element: <Lazy><Studio /></Lazy> },
      { path: "intelligence", element: <Lazy><Intelligence /></Lazy> },
      { path: "export", element: <Lazy><ExportCenter /></Lazy> },
      { path: "settings", element: <Lazy><Settings /></Lazy> },
    ],
  },
]);
