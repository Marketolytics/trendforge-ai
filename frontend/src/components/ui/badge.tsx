import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[var(--accent)]/15 text-[var(--accent)]",
        muted:
          "border-[var(--border)] bg-[var(--muted)] text-[var(--muted-foreground)]",
        success:
          "border-transparent bg-[var(--success)]/15 text-[var(--success)]",
        warning:
          "border-transparent bg-[var(--warning)]/15 text-[var(--warning)]",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
