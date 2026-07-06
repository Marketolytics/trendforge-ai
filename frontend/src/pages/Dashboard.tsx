import { RefreshCw, TrendingUp, Flame, Target, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/EmptyState";

const STATS = [
  { label: "Trends tracked", value: "—", icon: TrendingUp },
  { label: "Top score today", value: "—", icon: Flame },
  { label: "Opportunities", value: "—", icon: Target },
  { label: "Last refresh", value: "Never", icon: Clock },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Stat row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {STATS.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="text-xs font-medium text-[var(--muted-foreground)]">
                  {label}
                </p>
                <p className="mt-1 text-2xl font-semibold tracking-tight">
                  {value}
                </p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--muted)] text-[var(--accent)]">
                <Icon className="h-4.5 w-4.5" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>Today's Top Trends</CardTitle>
              <Badge variant="muted">ranked by score</Badge>
            </div>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={TrendingUp}
              title="No trends yet"
              description="Collectors and the intelligence engine arrive in the next milestone. Refresh will pull and rank live topics."
              action={
                <Button>
                  <RefreshCw className="h-4 w-4" />
                  Refresh Trends
                </Button>
              }
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest News</CardTitle>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={Clock}
              title="Nothing here yet"
              description="Fresh headlines from your sources will show up here."
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
