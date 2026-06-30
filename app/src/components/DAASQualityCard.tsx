"use client";

import { motion } from "framer-motion";
import { AlertCircle, ShieldAlert, ArrowUpRight, FileSpreadsheet } from "lucide-react";

interface DAASQualityCardProps {
  boInexistenteCount: number;
  totalMvi: number;
}

export function DAASQualityCard({ boInexistenteCount, totalMvi }: DAASQualityCardProps) {
  // Calcula o percentual de não preenchimento
  const percentIncompleteness = totalMvi > 0 
    ? parseFloat(((boInexistenteCount / totalMvi) * 100).toFixed(1)) 
    : 0;

  return (
    <div className="glass-card p-4 w-full rounded-xl relative overflow-hidden flex flex-col justify-between border border-indigo-500/20 bg-indigo-500/5 hover:border-indigo-500/35 transition-all duration-300">
      {/* Background Glow */}
      <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-indigo-500/10 blur-2xl"></div>

      <div>
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400 flex items-center gap-1.5 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
            <AlertCircle className="w-3 h-3" />
            DAAS - Polícia Civil
          </span>
          <span className="text-[9px] bg-white/5 border border-white/10 px-2 py-0.5 rounded-md text-muted-foreground font-bold uppercase tracking-wider">
            Fase Futura
          </span>
        </div>

        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-extrabold text-white tracking-tight leading-none text-glow">
            {boInexistenteCount}
          </span>
          <span className="text-xs text-muted-foreground font-semibold">casos</span>
        </div>

        <h3 className="font-bold text-white text-xs mb-1">Boletins (BO PC) Não Localizados</h3>
        <p className="text-[10px] text-muted-foreground leading-relaxed">
          Ocorrências registradas como óbito pelo NEAC, mas cujas chaves do Boletim de Ocorrência não estão consolidadas ou integradas no DAAS.
        </p>
      </div>

      <div className="mt-3 pt-2.5 border-t border-white/5">
        {/* Barra de Progresso Analítica */}
        <div className="flex items-center justify-between text-[9px] text-muted-foreground font-semibold mb-1.5">
          <span>Taxa de Ausência de BO</span>
          <span className="text-indigo-400 font-bold">{percentIncompleteness}%</span>
        </div>
        <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/5">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${percentIncompleteness}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="h-full bg-indigo-500 rounded-full"
          />
        </div>
        <div className="mt-2 flex items-center gap-1 text-[9px] text-muted-foreground/80 leading-snug">
          <FileSpreadsheet className="w-3 h-3 text-indigo-400 shrink-0" />
          <span>Fila de auditoria e validação da Polícia Civil (Em breve).</span>
        </div>
      </div>
    </div>
  );
}
