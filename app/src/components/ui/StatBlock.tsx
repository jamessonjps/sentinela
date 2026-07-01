import React from "react";

interface StatBlockProps {
  label: string;
  value: string | number;
  change?: {
    value: string | number;
    type: "positive" | "negative" | "neutral";
  };
  description?: string;
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  className?: string;
}

export function StatBlock({ label, value, change, description, icon: Icon, className = "" }: StatBlockProps) {
  const changeColor = change
    ? change.type === "positive"
      ? "text-[var(--color-ok)]"
      : change.type === "negative"
      ? "text-[var(--color-critical)]"
      : "text-[var(--color-slate)]"
    : "";

  return (
    <div className={`bg-surface border border-border rounded-md p-4 flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-label truncate">{label}</span>
        {Icon && <Icon className="w-4 h-4 text-[var(--color-slate)] shrink-0" />}
      </div>
      <div className="flex items-baseline gap-2 mt-2">
        <span className="text-kpi leading-none">{value}</span>
        {change && (
          <span className={`text-data font-semibold text-[11px] leading-none ${changeColor}`}>
            {change.value}
          </span>
        )}
      </div>
      {description && (
        <div className="mt-2.5 pt-2 border-t border-border/30 text-[10px] text-[var(--color-slate)] font-medium">
          {description}
        </div>
      )}
    </div>
  );
}
