"use client";

import { motion } from "framer-motion";
import { FileX, AlertTriangle, ShieldCheck, ArrowUpRight } from "lucide-react";

interface IMLQualityCardProps {
  corposSemDo: number;
  totalMvi: number;
}

export function IMLQualityCard({ corposSemDo, totalMvi }: IMLQualityCardProps) {
  // Calcula o percentual de não preenchimento
  const percentIncompleteness = totalMvi > 0 
    ? parseFloat(((corposSemDo / totalMvi) * 100).toFixed(1)) 
    : 0;

  return (
    <div className="glass-card p-5 w-full rounded-2xl relative overflow-hidden flex flex-col justify-between border border-destructive/20 bg-destructive/5 hover:border-destructive/30 transition-all duration-300">
      {/* Background Glow */}
      <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-destructive/10 blur-2xl"></div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-[10px] font-bold uppercase tracking-widest text-destructive flex items-center gap-1.5 bg-destructive/10 px-2 py-0.5 rounded border border-destructive/20">
            <AlertTriangle className="w-3 h-3" />
            IML - Alerta Forense
          </span>
          <span className="text-[9px] bg-success/15 border border-success/30 px-2 py-0.5 rounded-md text-success font-bold uppercase tracking-wider">
            Ativo / Inicial
          </span>
        </div>

        <div className="flex items-baseline gap-2 mb-1.5">
          <span className="text-3xl font-extrabold text-white tracking-tight leading-none text-glow">
            {corposSemDo}
          </span>
          <span className="text-xs text-muted-foreground font-semibold">óbitos</span>
        </div>

        <h3 className="font-bold text-white text-xs mb-1">Declaração de Óbito (DO) Vazia</h3>
        <p className="text-[10px] text-muted-foreground leading-relaxed">
          Corpos que deram entrada no necrotério, mas não possuem o número da guia DO registrado no sistema cadavérico.
        </p>
      </div>

      <div className="mt-4 pt-3.5 border-t border-white/5">
        {/* Barra de Progresso Analítica */}
        <div className="flex items-center justify-between text-[9px] text-muted-foreground font-semibold mb-1.5">
          <span>Taxa de Ausência de DO</span>
          <span className="text-destructive font-bold">{percentIncompleteness}%</span>
        </div>
        <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/5">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${percentIncompleteness}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="h-full bg-destructive rounded-full"
          />
        </div>
        <div className="mt-3 flex items-center gap-1 text-[9px] text-muted-foreground/80 leading-snug">
          <FileX className="w-3 h-3 text-destructive shrink-0" />
          <span>Fila dedicada para analistas da Polícia Científica / IML.</span>
        </div>
      </div>
    </div>
  );
}
