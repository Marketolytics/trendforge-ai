import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function Field({ label, value }: { label: string; value?: string | number | null }) {
  if (value === "" || value === null || value === undefined) return null;
  return (
    <div>
      <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
        {label}
      </p>
      <p className="mt-0.5 whitespace-pre-wrap text-sm leading-relaxed">{value}</p>
    </div>
  );
}

export function Pills({ items }: { items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((it, i) => (
        <span
          key={i}
          className="rounded-full border border-[var(--border)] bg-[var(--muted)] px-2.5 py-0.5 text-xs text-[var(--foreground)]/85"
        >
          {it}
        </span>
      ))}
    </div>
  );
}

export function BulletList({ items }: { items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <ul className="space-y-1">
      {items.map((it, i) => (
        <li key={i} className="flex gap-2 text-sm text-[var(--foreground)]/90">
          <span className="text-[var(--muted-foreground)]">•</span>
          {it}
        </li>
      ))}
    </ul>
  );
}

export function CopyButton({ text, className }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success("Copied to clipboard");
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast.error("Copy failed");
    }
  };
  return (
    <button
      onClick={copy}
      className={cn(
        "inline-flex items-center gap-1 rounded-md border border-[var(--border)] px-2 py-1 text-xs text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]",
        className,
      )}
      title="Copy"
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export function Card({ children }: { children: React.ReactNode }) {
  return <div className="surface space-y-3 p-4">{children}</div>;
}
