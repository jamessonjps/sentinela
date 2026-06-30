"use client";

import { motion } from "framer-motion";
import { Shield, ShieldAlert, Compass, FileText, TrendingUp, CheckCircle2 } from "lucide-react";

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
  const cards = [
    {
      title: "Consolidação MVI",
      value: stats.mvi_total,
      description: "Casos MVI no Gold Standard",
      icon: Shield,
      color: "text-primary",
      bgGlow: "rgba(59, 130, 246, 0.15)",
      borderColor: "border-primary/20",
      detail: `${stats.resolved_alerts} alertas auditados/resolvidos`
    },
    {
      title: "Alertas Ativos (Auditoria)",
      value: stats.active_alerts,
      description: "Inconsistências de chaves pendentes",
      icon: ShieldAlert,
      color: "text-warning",
      bgGlow: "rgba(245, 158, 11, 0.15)",
      borderColor: "border-warning/20",
      detail: `${stats.critical_alerts} com criticidade ALTA`
    },
    {
      title: "Radar CAD (190 PM)",
      value: radarStats.novos,
      description: "Eventos sem vínculo na Mestra",
      icon: Compass,
      color: "text-indigo-400",
      bgGlow: "rgba(99, 102, 241, 0.15)",
      borderColor: "border-indigo-500/25",
      detail: `${radarStats.alta_prioridade} classificados como CVLI`
    },
    {
      title: "Qualidade do Dado (IML)",
      value: imlSemDo,
      description: "Corpos sem DO no necrotério",
      icon: FileText,
      color: "text-purple-400",
      bgGlow: "rgba(168, 85, 247, 0.15)",
      borderColor: "border-purple-500/25",
      detail: `De um total de ${stats.mvi_total} óbitos`
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.08 }}
            whileHover={{ y: -3, transition: { duration: 0.2 } }}
            className={`glass-card p-3.5 rounded-xl flex flex-col justify-between border ${card.borderColor} relative overflow-hidden`}
            style={{
              boxShadow: `0 4px 30px rgba(0, 0, 0, 0.2), inset 0 0 20px ${card.bgGlow}`
            }}
          >
            {/* Ambient Background Light */}
            <div 
              className="absolute -right-4 -top-4 w-20 h-20 rounded-full filter blur-xl opacity-20"
              style={{ backgroundColor: card.color.includes("primary") ? "#3b82f6" : card.color.includes("warning") ? "#f59e0b" : card.color.includes("indigo") ? "#6366f1" : "#a855f7" }}
            />

            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">
                  {card.title}
                </span>
                <h3 className="text-xl font-black text-white mt-0.5 tracking-tight text-glow">
                  {card.value}
                </h3>
              </div>
              <div className={`p-2 rounded-lg bg-white/5 border border-white/10 ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between text-[9px]">
              <span className="text-muted-foreground font-medium">
                {card.description}
              </span>
              <span className="text-white font-semibold">
                {card.detail}
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
