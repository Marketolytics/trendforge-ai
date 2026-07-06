import { NavLink } from "react-router-dom";
import { Flame } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "./navigation";

export function Sidebar() {
  return (
    <aside className="flex h-full w-60 flex-col border-r border-[var(--border)] bg-[var(--sidebar)]">
      {/* Brand */}
      <div className="flex h-14 items-center gap-2.5 px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent)] text-[var(--accent-foreground)] shadow-sm">
          <Flame className="h-4.5 w-4.5" />
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-semibold tracking-tight">
            TrendForge
          </span>
          <span className="text-[10px] font-medium uppercase tracking-widest text-[var(--muted-foreground)]">
            AI
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-3">
        {NAV_ITEMS.map(({ label, to, icon: Icon, shortcut }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-[var(--accent)]/12 text-[var(--foreground)]"
                  : "text-[var(--sidebar-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)]",
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={cn(
                    "h-4 w-4 transition-colors",
                    isActive
                      ? "text-[var(--accent)]"
                      : "text-[var(--muted-foreground)] group-hover:text-[var(--foreground)]",
                  )}
                />
                <span className="flex-1">{label}</span>
                {shortcut && (
                  <kbd className="rounded border border-[var(--border)] bg-[var(--background)] px-1.5 text-[10px] text-[var(--muted-foreground)] opacity-0 transition-opacity group-hover:opacity-100">
                    {shortcut}
                  </kbd>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-[var(--border)] px-5 py-3">
        <p className="text-[11px] text-[var(--muted-foreground)]">
          v0.1.0 · Local
        </p>
      </div>
    </aside>
  );
}
