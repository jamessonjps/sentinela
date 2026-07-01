/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Search, Bell, ShieldAlert, Compass, Lock } from "lucide-react";
import { AlertQueue } from "@/components/AlertQueue";
import { CaseTimeline } from "@/components/CaseTimeline";
import { SourceQualityCard } from "@/components/ui/SourceQualityCard";
import { DashboardStats } from "@/components/DashboardStats";

// Carregamento dinâmico para evitar problemas de SSR com o Leaflet
const CrimeMap = dynamic(() => import("@/components/CrimeMap"), { ssr: false });

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

interface Alert {
  id_alerta: number;
  id_controle_morte: number;
  tipo_alerta: string;
  subjetividade: string;
  prioridade: number;
  cidade: string;
  bairro?: string;
  bo_pc?: string;
  cad?: string;
  nic?: string;
  declaracao_obito?: string;
  tipo_morte_iml?: string;
  natureza_cad?: string;
  natureza_daas?: string;
  aisp?: string;
  risp?: string;
  data_hora_fato?: string;
  nome_vitima_cm?: string;
  nome_vitima_iml?: string;
  latitude?: number;
  longitude?: number;
  status_alerta?: string;
}

interface DashboardStatsData {
  status: { novos: number; em_tratativa: number; resolvidos: number; total: number };
  prioridade: { baixa: number; media: number; alta: number };
  mvi_total: number;
  corpos_sem_do: number;
}

interface RadarStatsData {
  total: number;
  status: { novos: number; validados: number; descartados: number };
  prioridade: { alta: number; media: number; baixa: number };
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"auditoria" | "radar">("auditoria");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  
  const [stats, setStats] = useState<DashboardStatsData>({
    status: { novos: 0, em_tratativa: 0, resolvidos: 0, total: 0 },
    prioridade: { baixa: 0, media: 0, alta: 0 },
    mvi_total: 0,
    corpos_sem_do: 0
  });

  const [radarStats, setRadarStats] = useState<RadarStatsData>({
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
      setSelectedAlert((prev) => prev ? { ...prev, status_alerta: "Resolvido" } : null);
    }
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
    <div className="min-h-screen lg:h-screen lg:max-h-screen p-3 flex flex-col gap-3 max-w-[1920px] mx-auto lg:overflow-hidden bg-ink text-paper">
      {/* Header Compacto e Sólido (Console de Inteligência) */}
      <header className="bg-surface border border-border px-5 py-3 rounded-md flex items-center justify-between z-50 shrink-0">
        <div className="flex items-center gap-4">
          {/* 1. Identidade Institucional (Brasão + Hierarquia Governamental) */}
          <div className="flex items-center gap-3 shrink-0">
            <img 
              src="/brasao_alagoas.png" 
              alt="Brasão do Estado de Alagoas" 
              className="h-9 w-auto opacity-95" 
            />
            <div className="flex flex-col justify-center leading-none">
              <span className="text-[10px] font-bold text-paper uppercase tracking-wider">
                Estado de Alagoas
              </span>
              <span className="text-[8px] font-bold text-slate uppercase tracking-wider mt-0.5">
                Secretaria de Estado da Segurança Pública
              </span>
              <span className="text-[8px] font-medium text-slate-dim uppercase tracking-wider mt-0.5">
                Chefia Especial do Núcleo de Estatística e Análise Criminal (CHENEAC)
              </span>
            </div>
          </div>

          {/* Divisor vertical sutil */}
          <div className="w-[1px] h-8 bg-border hidden lg:block shrink-0" />

          {/* 2. Nome do Sistema e Badge Operacional */}
          <div className="hidden sm:flex items-center gap-2 shrink-0">
            <h1 className="text-sm font-bold text-paper tracking-tight font-display uppercase leading-none">
              SENTINELA
            </h1>
            <span className="px-2 py-0.5 rounded-sm bg-focus-bg text-[8px] text-focus font-mono font-bold uppercase tracking-widest border border-focus/20">
              AUDITORIA MVI
            </span>
          </div>
        </div>

        {/* 3. Ações e Logo NEAC à Direita */}
        <div className="flex items-center gap-4">
          <div className="relative hidden xl:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-dim" />
            <input 
              type="text" 
              placeholder="Pesquisar boletim, CAD ou NIC..." 
              className="bg-ink border border-border pl-9 pr-3 py-1.5 rounded-sm text-xs w-64 text-paper placeholder:text-slate-dim focus:outline-none focus:border-focus transition-all"
            />
          </div>

          {/* Logomarca NEAC Branding */}
          <div className="flex items-center shrink-0">
            <img 
              src="/logo_neac_white.png" 
              alt="Logo NEAC" 
              className="h-5.5 w-auto opacity-90" 
            />
          </div>

          <button 
            className="bg-surface border border-border w-9 h-9 rounded-sm flex items-center justify-center relative hover:bg-surface-raised transition-colors cursor-pointer shrink-0"
          >
            <Bell className="w-4.5 h-4.5 text-slate" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-critical rounded-full border border-surface"></span>
          </button>
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

      {/* Seletor de Abas Sólido */}
      <div className="flex justify-start shrink-0">
        <div className="flex gap-1.5 p-0.5 bg-surface border border-border rounded-sm text-xs font-semibold">
          <button
            onClick={() => setActiveTab("auditoria")}
            className={`px-3 py-1 rounded-sm flex items-center gap-1.5 transition-all cursor-pointer text-[10px] font-bold uppercase tracking-wider ${
              activeTab === "auditoria"
                ? "bg-surface-raised text-paper border border-border"
                : "text-slate hover:text-paper"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-focus" />
            Fila de Auditoria (NEAC)
          </button>
          
          <button
            onClick={() => setActiveTab("radar")}
            className={`px-3 py-1 rounded-sm flex items-center gap-1.5 transition-all cursor-pointer text-[10px] font-bold uppercase tracking-wider ${
              activeTab === "radar"
                ? "bg-surface-raised text-paper border border-border"
                : "text-slate hover:text-paper"
            }`}
          >
            <Compass className="w-3.5 h-3.5 text-slate-dim" />
            Radar de Ocorrências (CAD/190)
            <span className="text-[8px] bg-ink border border-border px-1.5 py-0.5 rounded-sm text-slate-dim font-bold uppercase tracking-wider ml-1.5 inline-flex items-center gap-1">
              <Lock className="w-2.5 h-2.5" />
              Fase Futura
            </span>
          </button>
        </div>
      </div>

      {/* Conteúdo das Abas */}
      <main className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {activeTab === "auditoria" ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0 overflow-hidden">
            {/* Fila de Auditoria */}
            <div className="lg:col-span-4 min-h-0 overflow-hidden flex flex-col">
              <AlertQueue 
                onSelectAlert={setSelectedAlert} 
                selectedAlertId={selectedAlert?.id_alerta} 
              />
            </div>

            {/* Detalhe do Caso / Timeline */}
            <div className="lg:col-span-4 min-h-0 overflow-hidden flex flex-col">
              <CaseTimeline 
                selectedAlert={selectedAlert} 
                onStatusChanged={handleAlertStatusChanged}
              />
            </div>

            {/* Mapa e Painéis de Qualidade de Dados */}
            <div className="lg:col-span-4 min-h-0 flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1">
              <div className="h-[280px] shrink-0">
                <CrimeMap selectedAlert={selectedAlert} />
              </div>
              
              <SourceQualityCard 
                fonte="NEAC"
                percentualPreenchido={stats.mvi_total > 0 ? parseFloat((100 - (((stats.status?.novos || 0) + (stats.status?.em_tratativa || 0)) / stats.mvi_total) * 100).toFixed(1)) : 100}
                metricValue={(stats.status?.novos || 0) + (stats.status?.em_tratativa || 0)}
                metricLabel="divergências"
                camposFaltantes={["NOME_VITIMA", "BO_PC", "CAD"]}
              />
              <SourceQualityCard 
                fonte="IML"
                percentualPreenchido={stats.mvi_total > 0 ? parseFloat((100 - ((stats.corpos_sem_do || 0) / stats.mvi_total) * 100).toFixed(1)) : 100}
                metricValue={stats.corpos_sem_do || 0}
                metricLabel="óbitos sem DO"
                camposFaltantes={["NR_DECLARACAO_OBITO"]}
              />
              <SourceQualityCard 
                fonte="DAAS"
                percentualPreenchido={stats.mvi_total > 0 ? parseFloat((100 - (21 / stats.mvi_total) * 100).toFixed(1)) : 100}
                metricValue={21}
                metricLabel="casos sem BO"
                camposFaltantes={["BO_PC", "NATUREZA_OCORRENCIA"]}
              />
            </div>
          </div>
        ) : (
          <div className="h-full flex-1 flex items-center justify-center">
            <div className="bg-surface border border-border p-8 rounded-md flex flex-col items-center justify-center text-center max-w-md">
              <div className="w-12 h-12 rounded-sm bg-ink border border-border flex items-center justify-center text-slate mb-5">
                <Lock className="w-6 h-6 opacity-45" />
              </div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-paper mb-2 font-display">
                Radar de Ocorrências — Fase Futura
              </h3>
              <p className="text-xs text-slate leading-relaxed max-w-[320px]">
                O cruzamento das ocorrências do CAD/190 (PM) com a base mestra será habilitado após a consolidação da auditoria IML × Controle Morte.
              </p>
              <span className="mt-4 text-[9px] bg-ink border border-border px-3 py-1 rounded-sm text-slate font-bold uppercase tracking-widest flex items-center gap-1.5">
                <Compass className="w-3 h-3 text-slate-dim" />
                Em Planejamento
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
