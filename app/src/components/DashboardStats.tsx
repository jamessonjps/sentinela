import React from "react";
import { Shield, ShieldAlert, Compass, FileText } from "lucide-react";
import { StatBlock } from "./ui/StatBlock";

interface DashboardStatsProps {
  stats: {
    mvi_total: number;
    active_alerts: number;
    critical_alerts: number;
    resolved_alerts: number;
  };
  radarStats: {
    total: number;
    novos: number;
    validados: number;
    descartados: number;
    alta_prioridade: number;
  };
  imlSemDo: number;
}

export function DashboardStats({ stats, radarStats, imlSemDo }: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
      <StatBlock
        label="Consolidação MVI"
        value={stats.mvi_total}
        description="Casos MVI no Gold Standard"
        change={{
          value: `${stats.resolved_alerts} resolvidos`,
          type: "positive"
        }}
        icon={Shield}
      />
      <StatBlock
        label="Alertas Ativos (Auditoria)"
        value={stats.active_alerts}
        description="Inconsistências de chaves pendentes"
        change={{
          value: `${stats.critical_alerts} críticos`,
          type: stats.critical_alerts > 0 ? "negative" : "neutral"
        }}
        icon={ShieldAlert}
      />
    </div>
  );
}
