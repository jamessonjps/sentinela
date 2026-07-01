import React from "react";
import { Shield, AlertTriangle, AlertCircle } from "lucide-react";
import { Badge } from "./Badge";

interface SourceQualityCardProps {
  fonte: "NEAC" | "IML" | "DAAS";
  percentualPreenchido: number;
  camposFaltantes: string[];
  metricValue: number;
  metricLabel: string;
}

export function SourceQualityCard({
  fonte,
  percentualPreenchido,
  camposFaltantes,
  metricValue,
  metricLabel,
}: SourceQualityCardProps) {
  const configs = {
    NEAC: {
      title: "NEAC - Controle Morte",
      icon: Shield,
      status: "Ativo" as const,
      badgeVariant: "ok" as const,
      color: "var(--color-focus)",
      description: "Qualidade dos dados integrados da base mestra.",
    },
    IML: {
      title: "Polícia Científica - IML",
      icon: AlertTriangle,
      status: "Fase Futura" as const,
      badgeVariant: "neutral" as const,
      color: "var(--color-critical)",
      description: "Registros com Declaração de Óbito preenchida.",
    },
    DAAS: {
      title: "DAAS - Polícia Civil",
      icon: AlertCircle,
      status: "Fase Futura" as const,
      badgeVariant: "neutral" as const,
      color: "var(--color-warning)",
      description: "Integração de Boletins de Ocorrência consumados.",
    },
  };

  const config = configs[fonte];
  const Icon = config.icon;

  return (
    <div className="bg-surface border border-border rounded-md p-4 flex flex-col justify-between min-h-0">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5 text-paper">
            <Icon className="w-3.5 h-3.5 text-slate" />
            <span className="text-label text-paper">{config.title}</span>
          </div>
          <Badge variant={config.badgeVariant}>{config.status}</Badge>
        </div>

        {/* Métrica Principal */}
        <div className="flex items-baseline gap-2 mb-1.5">
          <span className="text-kpi leading-none">{metricValue}</span>
          <span className="text-xs text-slate font-semibold">{metricLabel}</span>
        </div>
        <p className="text-[11px] text-slate leading-relaxed mb-3">
          {config.description}
        </p>
      </div>

      <div className="pt-3 border-t border-border">
        {/* Barra de Progresso Fina e Sólida */}
        <div className="flex items-center justify-between text-[11px] font-semibold mb-2">
          <span className="text-slate text-xs">Preenchimento / Consistência</span>
          <span className="text-data text-[12px]" style={{ color: config.color }}>
            {percentualPreenchido}%
          </span>
        </div>
        <div className="h-1 bg-ink rounded-sm overflow-hidden border border-border/50">
          <div
            className="h-full rounded-sm transition-all duration-500"
            style={{
              width: `${percentualPreenchido}%`,
              backgroundColor: config.color,
            }}
          />
        </div>

        {/* Campos Faltantes */}
        {camposFaltantes.length > 0 && (
          <div className="mt-3">
            <span className="text-[9px] uppercase tracking-wider text-slate font-bold block mb-1">
              Campos Críticos / Pendências:
            </span>
            <div className="flex flex-wrap gap-1">
              {camposFaltantes.map((campo, index) => (
                <span
                  key={index}
                  className="text-[9px] font-mono px-1.5 py-0.5 bg-ink border border-border text-slate rounded-sm"
                >
                  {campo}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
