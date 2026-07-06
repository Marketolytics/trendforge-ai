import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import {
  ApiError,
  studioApi,
  type AiEnvelope,
  type FormatInfo,
  type ModuleKind,
} from "@/lib/api";

export const MODULE_ORDER: ModuleKind[] = [
  "script",
  "storyboard",
  "continuity",
  "image_prompts",
  "video_prompts",
  "voiceover",
  "broll",
  "thumbnail_blueprint",
  "seo_package",
  "checklist",
];

type ModuleState = "idle" | "loading" | "ready" | "error";

export interface Workspace {
  formats: FormatInfo[];
  voiceStyles: string[];
  format: string;
  voiceStyle: string;
  setFormat: (f: string) => void;
  setVoiceStyle: (v: string) => void;

  modules: Partial<Record<ModuleKind, AiEnvelope<unknown>>>;
  moduleStatus: Partial<Record<ModuleKind, ModuleState>>;
  packageStatus: "idle" | "generating";
  notConfigured: boolean;

  generatePackage: (force?: boolean) => Promise<void>;
  generateModule: (kind: ModuleKind, force?: boolean) => Promise<void>;
  reload: () => Promise<void>;
}

export function useWorkspace(trendId: number): Workspace {
  const [formats, setFormats] = useState<FormatInfo[]>([]);
  const [voiceStyles, setVoiceStyles] = useState<string[]>([]);
  const [format, setFormat] = useState("60s");
  const [voiceStyle, setVoiceStyle] = useState("Professional");

  const [modules, setModules] = useState<Partial<Record<ModuleKind, AiEnvelope<unknown>>>>({});
  const [moduleStatus, setModuleStatus] = useState<Partial<Record<ModuleKind, ModuleState>>>({});
  const [packageStatus, setPackageStatus] = useState<"idle" | "generating">("idle");
  const [notConfigured, setNotConfigured] = useState(false);

  // Load format options once.
  useEffect(() => {
    studioApi
      .formats()
      .then((f) => {
        setFormats(f.formats);
        setVoiceStyles(f.voice_styles);
        setFormat(f.default);
      })
      .catch(() => void 0);
  }, []);

  // Load any already-generated modules for this trend/format.
  const loadExisting = useCallback(async () => {
    try {
      const pkg = await studioApi.getPackage(trendId, format);
      setModules(pkg.modules);
      const status: Partial<Record<ModuleKind, ModuleState>> = {};
      (Object.keys(pkg.modules) as ModuleKind[]).forEach((k) => (status[k] = "ready"));
      setModuleStatus(status);
    } catch {
      setModules({});
      setModuleStatus({});
    }
  }, [trendId, format]);

  useEffect(() => {
    loadExisting();
  }, [loadExisting]);

  const generatePackage = useCallback(
    async (force = false) => {
      setPackageStatus("generating");
      setNotConfigured(false);
      const t = toast.loading("Generating full production package… this can take a minute.");
      try {
        const pkg = await studioApi.generatePackage(trendId, { format, voiceStyle, force });
        setModules(pkg.modules);
        const status: Partial<Record<ModuleKind, ModuleState>> = {};
        (Object.keys(pkg.modules) as ModuleKind[]).forEach((k) => (status[k] = "ready"));
        setModuleStatus(status);
        if (pkg.failures.length > 0) {
          toast.warning(`Package ready with ${pkg.failures.length} module(s) failed`, {
            id: t,
            description: pkg.failures.map((f) => f.kind).join(", "),
          });
        } else {
          toast.success("Production package ready", {
            id: t,
            description: `${Object.keys(pkg.modules).length} modules · ${pkg.format}`,
          });
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 409) setNotConfigured(true);
        toast.error("Package generation failed", {
          id: t,
          description: err instanceof ApiError ? err.message : "Unknown error",
        });
      } finally {
        setPackageStatus("idle");
      }
    },
    [trendId, format, voiceStyle],
  );

  const generateModule = useCallback(
    async (kind: ModuleKind, force = false) => {
      setModuleStatus((s) => ({ ...s, [kind]: "loading" }));
      setNotConfigured(false);
      try {
        const env = await studioApi.generateModule(kind, trendId, { format, voiceStyle, force });
        setModules((m) => ({ ...m, [kind]: env }));
        setModuleStatus((s) => ({ ...s, [kind]: "ready" }));
        toast.success(`${label(kind)} ${force ? "regenerated" : "generated"}`);
      } catch (err) {
        if (err instanceof ApiError && err.status === 409) setNotConfigured(true);
        setModuleStatus((s) => ({ ...s, [kind]: "error" }));
        toast.error(`${label(kind)} failed`, {
          description: err instanceof ApiError ? err.message : "Unknown error",
        });
      }
    },
    [trendId, format, voiceStyle],
  );

  return {
    formats,
    voiceStyles,
    format,
    voiceStyle,
    setFormat,
    setVoiceStyle,
    modules,
    moduleStatus,
    packageStatus,
    notConfigured,
    generatePackage,
    generateModule,
    reload: loadExisting,
  };
}

export const MODULE_LABELS: Record<ModuleKind, string> = {
  script: "Script",
  storyboard: "Storyboard",
  continuity: "Continuity",
  image_prompts: "Image Prompts",
  video_prompts: "Video Prompts",
  voiceover: "Voice Over",
  broll: "B-Roll",
  thumbnail_blueprint: "Thumbnail",
  seo_package: "SEO",
  checklist: "Checklist",
};

function label(kind: ModuleKind): string {
  return MODULE_LABELS[kind] ?? kind;
}
