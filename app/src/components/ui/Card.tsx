import React from "react";

interface CardProps {
  title?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, action, children, className = "" }: CardProps) {
  return (
    <div className={`bg-surface border border-border rounded-md flex flex-col min-h-0 overflow-hidden ${className}`}>
      {title && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0 bg-surface">
          <h3 className="text-section-title leading-none">{title}</h3>
          {action && <div className="flex items-center">{action}</div>}
        </div>
      )}
      <div className="flex-1 p-4 min-h-0 overflow-hidden flex flex-col">
        {children}
      </div>
    </div>
  );
}
