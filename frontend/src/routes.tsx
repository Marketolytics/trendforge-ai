import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { Dashboard } from "@/pages/Dashboard";
import { Trends } from "@/pages/Trends";
import { Studio } from "@/pages/Studio";
import { Intelligence } from "@/pages/Intelligence";
import { Settings } from "@/pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "trends", element: <Trends /> },
      { path: "studio", element: <Studio /> },
      { path: "studio/:trendId", element: <Studio /> },
      { path: "intelligence", element: <Intelligence /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);
