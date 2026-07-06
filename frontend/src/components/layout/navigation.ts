import {
  LayoutDashboard,
  TrendingUp,
  Sparkles,
  History,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
  shortcut?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard, shortcut: "1" },
  { label: "Trends", to: "/trends", icon: TrendingUp, shortcut: "2" },
  { label: "Generator", to: "/generator", icon: Sparkles, shortcut: "3" },
  { label: "History", to: "/history", icon: History, shortcut: "4" },
  { label: "Settings", to: "/settings", icon: Settings, shortcut: "5" },
];
