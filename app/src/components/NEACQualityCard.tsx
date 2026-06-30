"use client";

import { motion } from "framer-motion";
import { Shield, AlertTriangle, Database } from "lucide-react";

interface NEACQualityCardProps {
  divergenciasCount: number;
  totalMvi: number;
}

export function NEACQualityCard({ divergenciasCount, totalMvi }: NEACQualityCardProps) {
  const percentDivergencia = totalMvi > 0 
    ? parseFloat(((divergenciasCount / totalMvi) * 100).toFixed(1)) 
    : 0;

  return (
    <div className="glass-card p-4 w-full rounded-xl relative overflow-hidden flex flex-col justify-between border border-primary/20 bg-primary/5 hover:border-primary/35 transition-all duration-300">
      {/* Background Glow */}
      <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-primary/10 blur-2xl"></div>

      <div>
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-primary flex items-center gap-1.5 bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
            <Shield className="w-3 h-3" />
            NEAC - Controle Morte
          </span>
          <span className="text-[9px] bg-success/15 border border-success/30 px-2 py-0.5 rounded-md text-success font-bold uppercase tracking-wider">
            Ativo
          </span>
        </div>

        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-extrabold text-white tracking-tight leading-none text-glow">
            {divergenciasCount}
          </span>
          <span className="text-xs text-muted-foreground font-semibold">divergências</span>
        </div>

        <h3 className="font-bold text-white text-xs mb-1">Auditoria IML × Controle Morte</h3>
        <p className="text-[10px] text-muted-foreground leading-relaxed">
          Inconsistências de nomes entre a base mestra (NEAC) e os registros do necrotério (SGOU/IML) identificadas pelo cruzamento automatizado.
        </p>
      </div>

      <div className="mt-3 pt-2.5 border-t border-white/5">
        {/* Barra de Progresso Analítica */}
        <div className="flex items-center justify-between text-[9px] text-muted-foreground font-semibold mb-1.5">
          <span>Taxa de Divergência</span>
          <span className="text-primary font-bold">{percentDivergencia}%</span>
        </div>
        <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/5">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${percentDivergencia}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="h-full bg-primary rounded-full"
          />
        </div>
        <div className="mt-2 flex items-center gap-1 text-[9px] text-muted-foreground/80 leading-snug">
          <Database className="w-3 h-3 text-primary shrink-0" />
          <span>Fila prioritária — Fase Inicial do SENTINELA.</span>
        </div>
      </div>
    </div>
  );
}
