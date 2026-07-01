import React from "react";

export type BadgeVariant = "critical" | "warning" | "ok" | "neutral";

interface BadgeProps {
  variant: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant, children, className = "" }: BadgeProps) {
  const variantClasses = {
    critical: "bg-[var(--color-critical-bg)] text-[var(--color-critical)] border border-[var(--color-critical)]/30",
    warning: "bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning)]/30",
    ok: "bg-[var(--color-ok-bg)] text-[var(--color-ok)] border border-[var(--color-ok)]/30",
    neutral: "bg-[var(--color-surface-raised)] text-[var(--color-slate)] border border-[var(--color-border)]"
  };

  return (
    <span
      className={`inline-flex items-center justify-center px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase tracking-wider ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
