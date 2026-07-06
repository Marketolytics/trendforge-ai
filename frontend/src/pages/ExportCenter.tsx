import { useRef, useState } from "react";
import { toast } from "sonner";
import { Download, Upload, Package, DatabaseBackup, FolderInput, FolderOutput } from "lucide-react";
import { backupApi, studioApi } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTrends } from "@/store/trends";

const FORMATS = ["15s", "20s", "30s", "45s", "60s", "3min", "5min", "8min", "10min"];

export function ExportCenter() {
  const { trends } = useTrends();
  const [trendId, setTrendId] = useState<number | null>(null);
  const [format, setFormat] = useState("60s");
  const restoreRef = useRef<HTMLInputElement>(null);
  const importRef = useRef<HTMLInputElement>(null);

  const restore = async (file: File) => {
    try {
      const r = await backupApi.restore(file);
      toast.success("Backup restored", {
        description: r.restart_recommended ? "Restart the app to finish." : undefined,
      });
    } catch {
      toast.error("Restore failed");
    }
  };

  const importProject = async (file: File) => {
    try {
      const bundle = JSON.parse(await file.text());
      const r = await backupApi.importProject(bundle);
      toast.success("Project imported", { description: `New trend #${r.trend_id}` });
    } catch {
      toast.error("Import failed — invalid project file");
    }
  };

  return (
    <div className="space-y-6">
      {/* Package export */}
      <Card>
        <CardHeader>
          <CardTitle>Export a production package</CardTitle>
          <CardDescription>Download every generated module for a trend/format as a ZIP.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2">
          <select
            value={trendId ?? ""}
            onChange={(e) => setTrendId(Number(e.target.value))}
            className="h-9 min-w-56 flex-1 rounded-md border border-[var(--border)] bg-[var(--card)] px-2 text-sm outline-none focus:border-[var(--ring)]"
          >
            <option value="" disabled>Select a trend…</option>
            {trends.slice(0, 100).map((t) => (
              <option key={t.id} value={t.id}>{t.title.slice(0, 70)}</option>
            ))}
          </select>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            className="h-9 rounded-md border border-[var(--border)] bg-[var(--card)] px-2 text-sm outline-none focus:border-[var(--ring)]"
          >
            {FORMATS.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
          <a
            href={trendId != null ? studioApi.exportPackageUrl(trendId, format) : undefined}
            className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium ${
              trendId != null
                ? "bg-[var(--accent)] text-[var(--accent-foreground)] hover:brightness-110"
                : "pointer-events-none bg-[var(--muted)] text-[var(--muted-foreground)]"
            }`}
          >
            <Package className="h-4 w-4" /> Export ZIP
          </a>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Backup */}
        <Card>
          <CardHeader>
            <CardTitle>Backup & Restore</CardTitle>
            <CardDescription>Full local database backup — prevents data loss.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <a href={backupApi.downloadUrl()} className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--accent-foreground)] hover:brightness-110">
              <DatabaseBackup className="h-4 w-4" /> Download backup
            </a>
            <Button variant="outline" size="sm" onClick={() => restoreRef.current?.click()}>
              <Upload className="h-4 w-4" /> Restore
            </Button>
            <input
              ref={restoreRef}
              type="file"
              accept=".zip"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && restore(e.target.files[0])}
            />
          </CardContent>
        </Card>

        {/* Project import/export */}
        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
            <CardDescription>Move a single project between machines.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <a
              href={trendId != null ? backupApi.exportProjectUrl(trendId) : undefined}
              className={`inline-flex items-center gap-2 rounded-md border border-[var(--border)] px-4 py-2 text-sm ${
                trendId != null ? "hover:bg-[var(--muted)]" : "pointer-events-none opacity-50"
              }`}
            >
              <FolderOutput className="h-4 w-4" /> Export project
            </a>
            <Button variant="outline" size="sm" onClick={() => importRef.current?.click()}>
              <FolderInput className="h-4 w-4" /> Import project
            </Button>
            <input
              ref={importRef}
              type="file"
              accept=".json"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && importProject(e.target.files[0])}
            />
          </CardContent>
        </Card>
      </div>

      <p className="flex items-center justify-center gap-1.5 text-center text-xs text-[var(--muted-foreground)]">
        <Download className="h-3.5 w-3.5" /> Individual modules also export as MD/JSON from the Studio and Research workspaces.
      </p>
    </div>
  );
}
