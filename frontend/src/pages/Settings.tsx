import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Save, Trash2, CheckCircle2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api, aiApi, type AppSettings, type Source } from "@/lib/api";

const inputClass =
  "h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none placeholder:text-[var(--muted-foreground)] focus:border-[var(--ring)]";

const labelClass =
  "mb-1.5 block text-xs font-medium text-[var(--muted-foreground)]";

export function Settings() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [aiConfigured, setAiConfigured] = useState(false);
  const [saving, setSaving] = useState(false);

  // Editable fields
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("");
  const [refreshInterval, setRefreshInterval] = useState(0);
  const [cacheDuration, setCacheDuration] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const [s, srcs, status] = await Promise.all([
          api.getSettings(),
          api.getSources(),
          aiApi.status(),
        ]);
        setSettings(s);
        setSources(srcs);
        setAiConfigured(status.configured);
        setModel(s.gemini_model);
        setRefreshInterval(s.refresh_interval);
        setCacheDuration(s.cache_duration);
      } catch {
        toast.error("Failed to load settings");
      }
    })();
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const payload: Partial<AppSettings> = {
        gemini_model: model,
        refresh_interval: refreshInterval,
        cache_duration: cacheDuration,
      };
      if (apiKey.trim()) payload.gemini_api_key = apiKey.trim();
      const updated = await api.updateSettings(payload);
      setSettings(updated);
      setApiKey("");
      const status = await aiApi.status();
      setAiConfigured(status.configured);
      toast.success("Settings saved");
    } catch {
      toast.error("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const clearCache = async () => {
    try {
      const res = await api.clearCache();
      toast.success(`Cleared ${res.cleared} cached requests`);
    } catch {
      toast.error("Failed to clear cache");
    }
  };

  if (!settings) {
    return (
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-56 w-full" />
        <Skeleton className="h-56 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        {/* Gemini */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Gemini AI</CardTitle>
              {aiConfigured ? (
                <Badge variant="success">
                  <CheckCircle2 className="h-3 w-3" /> Connected
                </Badge>
              ) : (
                <Badge variant="warning">Not configured</Badge>
              )}
            </div>
            <CardDescription>
              Your key is stored locally and never leaves this machine.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className={labelClass}>
                API Key {settings.gemini_api_key_set && "(a key is already saved)"}
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={
                  settings.gemini_api_key_set ? "•••••••• (enter to replace)" : "Paste your Gemini API key"
                }
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Model</label>
              <input
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="gemini-2.5-flash"
                className={inputClass}
              />
            </div>
          </CardContent>
        </Card>

        {/* Collection */}
        <Card>
          <CardHeader>
            <CardTitle>Collection & Cache</CardTitle>
            <CardDescription>How often to refresh and cache requests.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className={labelClass}>Refresh interval (seconds)</label>
              <input
                type="number"
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Cache duration (seconds)</label>
              <input
                type="number"
                value={cacheDuration}
                onChange={(e) => setCacheDuration(Number(e.target.value))}
                className={inputClass}
              />
            </div>
            <Button variant="outline" size="sm" onClick={clearCache}>
              <Trash2 className="h-4 w-4" />
              Clear cache
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Sources */}
      <Card>
        <CardHeader>
          <CardTitle>Trend Sources</CardTitle>
          <CardDescription>{sources.length} configured collection sources.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {sources.map((s) => (
            <Badge key={s.id} variant={s.enabled ? "default" : "muted"}>
              {s.name}
            </Badge>
          ))}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={save} disabled={saving}>
          <Save className="h-4 w-4" />
          {saving ? "Saving…" : "Save settings"}
        </Button>
      </div>
    </div>
  );
}
