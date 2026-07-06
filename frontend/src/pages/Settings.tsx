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
import { api, aiApi, ApiError, type AppSettings } from "@/lib/api";
import { applyTheme, type Theme } from "@/lib/theme";
import { setNotificationsEnabled } from "@/lib/notifications";

const input =
  "h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none placeholder:text-[var(--muted-foreground)] focus:border-[var(--ring)]";
const label = "mb-1.5 block text-xs font-medium text-[var(--muted-foreground)]";

function Toggle({ checked, onChange, text }: { checked: boolean; onChange: (v: boolean) => void; text: string }) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-3 py-1.5">
      <span className="text-sm">{text}</span>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative h-5 w-9 rounded-full transition-colors ${checked ? "bg-[var(--accent)]" : "bg-[var(--muted)]"}`}
      >
        <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${checked ? "translate-x-4" : "translate-x-0.5"}`} />
      </button>
    </label>
  );
}

export function Settings() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [aiConfigured, setAiConfigured] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Partial<AppSettings>>({});
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [s, status] = await Promise.all([api.getSettings(), aiApi.status()]);
        setSettings(s);
        setForm(s);
        setAiConfigured(status.configured);
      } catch {
        toast.error("Failed to load settings");
      }
    })();
  }, []);

  const set = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const save = async () => {
    setSaving(true);
    try {
      const payload: Partial<AppSettings> = {
        gemini_model: form.gemini_model,
        refresh_interval: form.refresh_interval,
        cache_duration: form.cache_duration,
        theme: form.theme,
        language: form.language,
        log_level: form.log_level,
        notifications: form.notifications,
        developer_mode: form.developer_mode,
        experimental: form.experimental,
        auto_backup: form.auto_backup,
        update_url: form.update_url,
      };
      if (apiKey.trim()) payload.gemini_api_key = apiKey.trim();
      const updated = await api.updateSettings(payload);
      setSettings(updated);
      setApiKey("");
      if (form.theme) applyTheme(form.theme as Theme);
      setNotificationsEnabled(!!form.notifications);
      setAiConfigured((await aiApi.status()).configured);
      toast.success("Settings saved");
    } catch (err) {
      toast.error("Failed to save settings", {
        description: err instanceof ApiError ? err.message : undefined,
      });
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
                <Badge variant="success"><CheckCircle2 className="h-3 w-3" /> Connected</Badge>
              ) : (
                <Badge variant="warning">Not configured</Badge>
              )}
            </div>
            <CardDescription>Stored locally, never leaves this machine.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className={label}>API Key {settings.gemini_api_key_set && "(saved)"}</label>
              <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
                placeholder={settings.gemini_api_key_set ? "•••••••• (enter to replace)" : "Paste your Gemini API key"}
                className={input} />
            </div>
            <div>
              <label className={label}>Model</label>
              <input value={form.gemini_model ?? ""} onChange={(e) => set("gemini_model", e.target.value)} className={input} />
            </div>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card>
          <CardHeader><CardTitle>Appearance</CardTitle><CardDescription>Theme and language.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className={label}>Theme</label>
              <select value={form.theme ?? "dark"} onChange={(e) => { set("theme", e.target.value); applyTheme(e.target.value as Theme); }} className={input}>
                <option value="dark">Dark</option>
                <option value="light">Light</option>
              </select>
            </div>
            <div>
              <label className={label}>Language</label>
              <select value={form.language ?? "en"} onChange={(e) => set("language", e.target.value)} className={input}>
                <option value="en">English</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Collection & cache */}
        <Card>
          <CardHeader><CardTitle>Collection & Cache</CardTitle><CardDescription>Refresh cadence and caching.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className={label}>Refresh interval (seconds)</label>
              <input type="number" value={form.refresh_interval ?? 0} onChange={(e) => set("refresh_interval", Number(e.target.value))} className={input} />
            </div>
            <div>
              <label className={label}>Cache duration (seconds)</label>
              <input type="number" value={form.cache_duration ?? 0} onChange={(e) => set("cache_duration", Number(e.target.value))} className={input} />
            </div>
            <Button variant="outline" size="sm" onClick={clearCache}><Trash2 className="h-4 w-4" /> Clear cache</Button>
          </CardContent>
        </Card>

        {/* Data & notifications */}
        <Card>
          <CardHeader><CardTitle>Data & Notifications</CardTitle><CardDescription>Local storage and alerts.</CardDescription></CardHeader>
          <CardContent className="space-y-1">
            <div className="mb-3">
              <label className={label}>Output folder</label>
              <input value={form.output_folder ?? ""} onChange={(e) => set("output_folder", e.target.value)} className={input} />
            </div>
            <Toggle text="Desktop notifications" checked={!!form.notifications} onChange={(v) => set("notifications", v)} />
            <Toggle text="Automatic backups" checked={!!form.auto_backup} onChange={(v) => set("auto_backup", v)} />
          </CardContent>
        </Card>

        {/* Advanced / developer */}
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Advanced</CardTitle><CardDescription>Logging, updates and developer options.</CardDescription></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div>
              <label className={label}>Log level</label>
              <select value={form.log_level ?? "INFO"} onChange={(e) => set("log_level", e.target.value)} className={input}>
                {["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className={label}>Update check URL (optional)</label>
              <input value={form.update_url ?? ""} onChange={(e) => set("update_url", e.target.value)} placeholder="https://…/version.json" className={input} />
            </div>
            <div className="md:col-span-2">
              <Toggle text="Developer mode (⌃⇧D panel)" checked={!!form.developer_mode} onChange={(v) => set("developer_mode", v)} />
              <Toggle text="Experimental features" checked={!!form.experimental} onChange={(v) => set("experimental", v)} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button onClick={save} disabled={saving}>
          <Save className="h-4 w-4" /> {saving ? "Saving…" : "Save settings"}
        </Button>
      </div>
    </div>
  );
}
