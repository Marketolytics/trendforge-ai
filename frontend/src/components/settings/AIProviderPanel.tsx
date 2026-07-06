import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { KeyRound, Plug, Trash2, CheckCircle2, XCircle, Activity } from "lucide-react";
import {
  providersApi,
  type ConnectionTest,
  type ProviderConfig,
  type ProviderInfo,
  type ProviderUsageRow,
} from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { relativeTime, compactNumber } from "@/lib/format";

const input =
  "h-9 w-full rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none focus:border-[var(--ring)]";
const label = "mb-1.5 block text-xs font-medium text-[var(--muted-foreground)]";

export function AIProviderPanel() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [config, setConfig] = useState<ProviderConfig | null>(null);
  const [usage, setUsage] = useState<ProviderUsageRow[]>([]);
  const [selected, setSelected] = useState<string>("gemini");
  const [keyInput, setKeyInput] = useState("");
  const [testing, setTesting] = useState(false);
  const [test, setTest] = useState<ConnectionTest | null>(null);

  const load = useCallback(async () => {
    const [list, cfg, use] = await Promise.all([
      providersApi.list(),
      providersApi.getConfig(),
      providersApi.usage(),
    ]);
    setProviders(list.providers);
    setConfig(cfg);
    setSelected(cfg.provider);
    setUsage(use.usage);
  }, []);

  useEffect(() => {
    load().catch(() => toast.error("Failed to load providers"));
  }, [load]);

  const current = providers.find((p) => p.name === selected);

  const chooseProvider = async (name: string) => {
    setSelected(name);
    setTest(null);
    await providersApi.setConfig({ provider: name });
    await load();
  };

  const saveKey = async () => {
    if (!keyInput.trim()) return;
    try {
      await providersApi.setKey(selected, keyInput.trim());
      setKeyInput("");
      await load();
      toast.success("API key stored securely");
    } catch {
      toast.error("Could not store key");
    }
  };

  const resetKey = async () => {
    await providersApi.deleteKey(selected);
    await load();
    toast.success("Credentials reset");
  };

  const runTest = async () => {
    setTesting(true);
    setTest(null);
    try {
      setTest(await providersApi.test(selected));
    } catch {
      setTest({ ok: false, latency_ms: 0, models: [], error: "Request failed" });
    } finally {
      setTesting(false);
    }
  };

  const setModel = async (cat: "research" | "content" | "quality", value: string) => {
    await providersApi.setConfig({ [`model_${cat}`]: value });
    await load();
    toast.success(`${cat} model set`);
  };

  const modelOptions = () => {
    const fromTest = test?.models.map((m) => m.id) ?? [];
    const defaults = current?.default_models ?? [];
    const chosen = config ? Object.values(config.models) : [];
    return Array.from(new Set([...fromTest, ...defaults, ...chosen])).filter(Boolean);
  };

  return (
    <div className="space-y-6">
      {/* Provider + key */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>AI Provider</CardTitle>
            {current?.configured ? (
              <Badge variant="success"><CheckCircle2 className="h-3 w-3" /> Configured</Badge>
            ) : (
              <Badge variant="warning">Not configured</Badge>
            )}
          </div>
          <CardDescription>
            Keys are stored in your OS credential store — never in the database or plaintext.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className={label}>Provider</label>
              <select value={selected} onChange={(e) => chooseProvider(e.target.value)} className={input}>
                {providers.map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.label}
                    {p.active ? " (active)" : ""}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <p className="text-xs text-[var(--muted-foreground)]">
                {current?.requires_key
                  ? current?.key_set
                    ? "A key is saved for this provider."
                    : "This provider needs an API key."
                  : "Local provider — no key required."}
              </p>
            </div>
          </div>

          {current?.requires_key && (
            <div>
              <label className={label}>
                API Key {current?.key_set && <span className="text-[var(--success)]">• saved</span>}
              </label>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  placeholder={current?.key_set ? "•••••••• (enter to replace)" : "Paste API key"}
                  className={input}
                />
                <Button size="sm" onClick={saveKey} disabled={!keyInput.trim()}>
                  <KeyRound className="h-4 w-4" /> Save
                </Button>
                {current?.key_set && (
                  <Button size="sm" variant="outline" onClick={resetKey} title="Reset credentials">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center gap-3">
            <Button size="sm" variant="outline" onClick={runTest} disabled={testing}>
              <Plug className="h-4 w-4" /> {testing ? "Testing…" : "Test connection"}
            </Button>
            {test && (
              <div className="flex items-center gap-2 text-sm">
                {test.ok ? (
                  <span className="flex items-center gap-1 text-[var(--success)]">
                    <CheckCircle2 className="h-4 w-4" /> Connected · {test.latency_ms}ms · {test.models.length} models
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[var(--danger)]">
                    <XCircle className="h-4 w-4" /> {test.error}
                  </span>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Model routing */}
      <Card>
        <CardHeader>
          <CardTitle>Model routing</CardTitle>
          <CardDescription>Route each task type to a specific model.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {(["research", "content", "quality"] as const).map((cat) => (
            <div key={cat}>
              <label className={`${label} capitalize`}>{cat}</label>
              <select
                value={config?.models[cat] ?? ""}
                onChange={(e) => setModel(cat, e.target.value)}
                className={input}
              >
                {modelOptions().map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
                {config && !modelOptions().includes(config.models[cat]) && (
                  <option value={config.models[cat]}>{config.models[cat]}</option>
                )}
              </select>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Usage dashboard */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-[var(--accent)]" />
            <CardTitle>Usage</CardTitle>
          </div>
          <CardDescription>Local request counts and estimated token usage.</CardDescription>
        </CardHeader>
        <CardContent>
          {usage.length === 0 ? (
            <p className="text-sm text-[var(--muted-foreground)]">No AI requests yet.</p>
          ) : (
            <div className="space-y-2">
              {usage.map((u) => (
                <div key={u.provider} className="flex items-center gap-3 rounded-md border border-[var(--border)] p-3">
                  <span className="w-24 shrink-0 text-sm font-medium capitalize">{u.provider}</span>
                  <span className="text-xs text-[var(--muted-foreground)]">{u.requests} requests</span>
                  <span className="text-xs text-[var(--muted-foreground)]">
                    ~{compactNumber(u.total_tokens)} tokens
                  </span>
                  <span className="ml-auto text-xs text-[var(--muted-foreground)]">
                    last {relativeTime(u.last_success)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
