import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

const PHASES = [
  "Reading the trend…",
  "Sizing up the competition…",
  "Finding the untapped angle…",
  "Scoring the opportunity…",
  "Writing it up…",
];

export function AiLoading({ label }: { label?: string }) {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setPhase((p) => (p + 1) % PHASES.length), 1400);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-14 text-center">
      <div className="relative">
        <motion.div
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--accent)]/15 text-[var(--accent)]"
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
        >
          <Sparkles className="h-6 w-6" />
        </motion.div>
        <motion.span
          className="absolute inset-0 rounded-xl border border-[var(--accent)]/40"
          animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "easeOut" }}
        />
      </div>
      <motion.p
        key={phase}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-sm text-[var(--muted-foreground)]"
      >
        {label ?? PHASES[phase]}
      </motion.p>
    </div>
  );
}
