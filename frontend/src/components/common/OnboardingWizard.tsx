import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Flame, KeyRound, Sparkles } from "lucide-react";
import { providersApi } from "@/lib/api";
import { getAppState, patchAppState } from "@/lib/appState";
import { Button } from "@/components/ui/button";

/** First-run welcome shown when no AI provider is configured yet. */
export function OnboardingWizard() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (getAppState().onboardingDismissed) return;
    providersApi
      .list()
      .then((r) => {
        if (!r.providers.some((p) => p.configured)) setOpen(true);
      })
      .catch(() => void 0);
  }, []);

  const dismiss = () => {
    patchAppState({ onboardingDismissed: true });
    setOpen(false);
  };

  const goSettings = () => {
    dismiss();
    navigate("/settings");
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-[70] bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
          <motion.div
            className="fixed left-1/2 top-1/2 z-[71] w-full max-w-md -translate-x-1/2 -translate-y-1/2 px-4"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
          >
            <div className="surface p-6 text-center shadow-2xl">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--accent)] text-[var(--accent-foreground)]">
                <Flame className="h-6 w-6" />
              </div>
              <h2 className="text-lg font-semibold">Welcome to TrendForge</h2>
              <p className="mx-auto mt-1 max-w-sm text-sm text-[var(--muted-foreground)]">
                You can already collect and research trends. To unlock AI analysis and content
                generation, connect an AI provider — your key is stored securely in your OS
                credential store.
              </p>
              <div className="mt-5 space-y-2 text-left">
                <div className="flex items-center gap-3 rounded-md border border-[var(--border)] p-3">
                  <KeyRound className="h-4 w-4 text-[var(--accent)]" />
                  <span className="text-sm">Add an API key (Gemini, OpenAI, or a local model)</span>
                </div>
                <div className="flex items-center gap-3 rounded-md border border-[var(--border)] p-3">
                  <Sparkles className="h-4 w-4 text-[var(--accent)]" />
                  <span className="text-sm">Analyze trends and generate full content packages</span>
                </div>
              </div>
              <div className="mt-6 flex justify-center gap-2">
                <Button variant="outline" size="sm" onClick={dismiss}>
                  I'll do it later
                </Button>
                <Button size="sm" onClick={goSettings}>
                  Set up AI provider
                </Button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
