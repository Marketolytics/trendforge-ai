import {
  LayoutDashboard,
  TrendingUp,
  Microscope,
  Clapperboard,
  Radar,
  Download,
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
  { label: "Research", to: "/research", icon: Microscope, shortcut: "3" },
  { label: "Studio", to: "/studio", icon: Clapperboard, shortcut: "4" },
  { label: "Intelligence", to: "/intelligence", icon: Radar, shortcut: "5" },
  { label: "Export", to: "/export", icon: Download, shortcut: "6" },
  { label: "Settings", to: "/settings", icon: Settings, shortcut: "7" },
];
