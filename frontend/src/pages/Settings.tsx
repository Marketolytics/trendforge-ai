import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function Settings() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Gemini API</CardTitle>
          <CardDescription>
            Your key is stored locally and never leaves this machine.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <label className="mb-1.5 block text-xs font-medium text-[var(--muted-foreground)]">
            API Key
          </label>
          <input
            type="password"
            disabled
            placeholder="Configured in a later milestone"
            className="h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none placeholder:text-[var(--muted-foreground)] focus:border-[var(--ring)] disabled:opacity-60"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Trend Sources</CardTitle>
          <CardDescription>Toggle where trends are collected from.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {[
            "Google Trends",
            "YouTube",
            "Reddit",
            "Steam News",
            "Rockstar Newswire",
            "RSS Feeds",
          ].map((s) => (
            <Badge key={s} variant="muted">
              {s}
            </Badge>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
