"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Search, Bell, Menu, ShieldAlert, Compass, Eye, CheckCircle2, Lock } from "lucide-react";
import { AlertQueue } from "@/components/AlertQueue";
import { CaseTimeline } from "@/components/CaseTimeline";
import { IMLQualityCard } from "@/components/IMLQualityCard";
import { DAASQualityCard } from "@/components/DAASQualityCard";
import { NEACQualityCard } from "@/components/NEACQualityCard";
import { DashboardStats } from "@/components/DashboardStats";
import { RadarCAD } from "@/components/RadarCAD";

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"auditoria" | "radar">("auditoria");
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  
  const [stats, setStats] = useState<any>({
    status: { novos: 0, em_tratativa: 0, resolvidos: 0, total: 0 },
    prioridade: { baixa: 0, media: 0, alta: 0 },
    mvi_total: 0,
    corpos_sem_do: 0
  });

  const [radarStats, setRadarStats] = useState<any>({
    total: 0,
    status: { novos: 0, validados: 0, descartados: 0 },
    prioridade: { alta: 0, media: 0, baixa: 0 }
  });

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/alertas/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Erro ao buscar estatísticas de auditoria:", err);
    }
  };

  const fetchRadarStats = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/radar/stats`);
      if (res.ok) {
        const data = await res.json();
        setRadarStats(data);
      }
    } catch (err) {
      console.error("Erro ao buscar estatísticas do radar:", err);
    }
  };

  const handleAlertStatusChanged = () => {
    fetchStats();
    if (selectedAlert) {
      setSelectedAlert((prev: any) => prev ? { ...prev, status_alerta: "Resolvido" } : null);
    }
  };

  const handleRadarStatusChanged = () => {
    fetchRadarStats();
  };

  useEffect(() => {
    fetchStats();
    fetchRadarStats();
    const interval = setInterval(() => {
      fetchStats();
      fetchRadarStats();
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen lg:h-screen lg:max-h-screen p-3 flex flex-col gap-2.5 max-w-[1920px] mx-auto lg:overflow-hidden">
      {/* Header Premium */}
      <header className="glass-panel px-5 py-2 rounded-xl flex items-center justify-between z-50 transition-all shrink-0">
        <div className="flex items-center gap-3">
          <motion.div 
            whileHover={{ scale: 1.02 }}
            className="flex items-center gap-3"
          >
            {/* Bloco Logomarca NEAC (Imagem Limpa + Subtexto HTML para máxima nitidez) */}
            <div className="flex flex-col items-center gap-0.5">
              <img 
                src="/logo_neac_white.png" 
                alt="Logo NEAC" 
                className="h-6 w-auto opacity-95 filter drop-shadow-[0_0_6px_rgba(59,130,246,0.3)]" 
              />
              <span className="text-[5px] text-white/50 font-bold uppercase tracking-wider text-center block max-w-[130px] leading-tight">
                NÚCLEO DE ESTATÍSTICA E ANÁLISE CRIMINAL
              </span>
            </div>

            {/* Divisor */}
            <div className="w-[1px] h-8 bg-white/10 hidden sm:block" />

            {/* Brasão de Alagoas */}
            <img 
              src="/brasao_alagoas.png" 
              alt="Brasão de Alagoas" 
              className="h-8 w-auto opacity-90 filter drop-shadow-[0_0_8px_rgba(255,255,255,0.1)] hidden sm:block" />

            {/* Título do Sistema */}
            <div className="hidden sm:block">
              <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5 leading-none">
                SENTINELA 
                <span className="px-1.5 py-0.5 rounded bg-accent/85 text-[8px] text-primary font-bold uppercase tracking-widest border border-primary/20 shadow-[0_0_10px_rgba(59,130,246,0.15)]">
                  CHENEAC
                </span>
              </h1>
              <p className="text-[8px] text-muted-foreground font-medium uppercase tracking-wider mt-1">SSP - Estado de Alagoas</p>
            </div>
          </motion.div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden md:block group">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <input 
              type="text" 
              placeholder="Pesquisar boletim, CAD ou NIC..." 
              className="glass-button pl-10 pr-4 py-2 rounded-lg text-xs w-64 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all bg-black/20"
            />
          </div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="glass-button w-9 h-9 rounded-lg flex items-center justify-center relative hover:bg-white/10"
          >
            <Bell className="w-5 h-5 text-foreground" />
            <span className="absolute top-2.5 right-2.5 w-2.5 h-2.5 bg-destructive rounded-full shadow-[0_0_10px_rgba(220,38,38,1)] border border-background"></span>
          </motion.button>
        </div>
      </header>

      {/* Grid de KPIs Consolidados */}
      <DashboardStats 
        stats={{
          mvi_total: stats.mvi_total || 0,
          active_alerts: (stats.status?.novos || 0) + (stats.status?.em_tratativa || 0),
          critical_alerts: stats.prioridade?.alta || 0,
          resolved_alerts: stats.status?.resolvidos || 0
        }}
        radarStats={{
          total: radarStats.total || 0,
          novos: radarStats.status?.novos || 0,
          validados: radarStats.status?.validados || 0,
          descartados: radarStats.status?.descartados || 0,
          alta_prioridade: radarStats.prioridade?.alta || 0
        }}
        imlSemDo={stats.corpos_sem_do || 0}
      />

      {/* Seletor de Abas Principal */}
      <div className="flex justify-start shrink-0">
        <div className="flex gap-1.5 p-0.5 bg-black/20 border border-white/5 rounded-lg text-xs font-bold">
          <button
            onClick={() => setActiveTab("auditoria")}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all cursor-pointer text-[11px] ${
              activeTab === "auditoria"
                ? "bg-primary/20 text-white border border-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]"
                : "text-muted-foreground hover:text-white"
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            Fila de Auditoria (NEAC)
          </button>
          
          <button
            onClick={() => setActiveTab("radar")}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all cursor-pointer text-[11px] ${
              activeTab === "radar"
                ? "bg-white/5 text-muted-foreground border border-white/10"
                : "text-muted-foreground/50"
            }`}
          >
            <Compass className="w-4 h-4 opacity-50" />
            Radar de Ocorrências (CAD/190)
            <span className="text-[8px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-muted-foreground font-bold uppercase tracking-wider ml-1 flex items-center gap-1">
              <Lock className="w-2.5 h-2.5" />
              Fase Futura
            </span>
          </button>
        </div>
      </div>

      {/* Conteúdo das Abas com Animação */}
      <main className="flex-1 min-h-0 flex flex-col overflow-hidden">
        <AnimatePresence mode="wait">
          {activeTab === "auditoria" ? (
            <motion.div
              key="auditoria-tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0 overflow-hidden"
            >
              {/* Fila de Auditoria */}
              <div className="lg:col-span-4 min-h-0 overflow-hidden">
                <AlertQueue 
                  onSelectAlert={setSelectedAlert} 
                  selectedAlertId={selectedAlert?.id_alerta} 
                />
              </div>

              {/* Detalhe do Caso / Timeline */}
              <div className="lg:col-span-5 min-h-0 overflow-hidden">
                <CaseTimeline 
                  selectedAlert={selectedAlert} 
                  onStatusChanged={handleAlertStatusChanged}
                />
              </div>

              {/* Quality Cards: NEAC (Ativo) + Polícia Científica + Polícia Civil (Fase Futura) */}
              <div className="lg:col-span-3 min-h-0 flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1">
                <NEACQualityCard 
                  divergenciasCount={(stats.status?.novos || 0) + (stats.status?.em_tratativa || 0)} 
                  totalMvi={stats.mvi_total || 0} 
                />
                <IMLQualityCard 
                  corposSemDo={stats.corpos_sem_do || 0} 
                  totalMvi={stats.mvi_total || 0} 
                />
                <DAASQualityCard 
                  boInexistenteCount={21}
                  totalMvi={stats.mvi_total || 0}
                />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="radar-tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25 }}
              className="h-full flex-1 flex items-center justify-center"
            >
              <div className="glass-card p-8 rounded-2xl flex flex-col items-center justify-center text-center max-w-md">
                <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-muted-foreground mb-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                  <Lock className="w-8 h-8 opacity-40" />
                </div>
                <h3 className="text-sm font-bold text-white mb-2">Radar de Ocorrências — Fase Futura</h3>
                <p className="text-xs text-muted-foreground leading-relaxed max-w-[300px]">
                  O cruzamento das ocorrências do CAD/190 (PM) com a base mestra será habilitado após a consolidação da auditoria IML × Controle Morte.
                </p>
                <span className="mt-4 text-[9px] bg-white/5 border border-white/10 px-3 py-1 rounded-full text-muted-foreground font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <Compass className="w-3 h-3" />
                  Em Planejamento
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
