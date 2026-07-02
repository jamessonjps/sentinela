/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps, @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Search, Bell, ShieldAlert, Compass, Lock, Activity, ClipboardList, TrendingUp, X, Check, Calendar, FolderGit } from "lucide-react";
import { AlertQueue } from "@/components/AlertQueue";
import { CaseTimeline } from "@/components/CaseTimeline";
import { SourceQualityCard } from "@/components/ui/SourceQualityCard";
import { DashboardStats } from "@/components/DashboardStats";
import { RadarCAD } from "@/components/RadarCAD";

// Importação dos novos componentes operacionais do SENTINELA
import { WatchlistPanel } from "@/components/WatchlistPanel";
import { IMLNotificationFeed } from "@/components/IMLNotificationFeed";
import { EvolutionsQueue } from "@/components/EvolutionsQueue";

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
  const [activeTab, setActiveTab] = useState<"auditoria" | "futuras">("auditoria");
  const [subTab, setSubTab] = useState<"alertas" | "evolucoes">("evolucoes");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Estado para Divergências Pendentes do Mês Anterior (Consolidação)
  const [pendingPrevMonthCount, setPendingPrevMonthCount] = useState(0);

  // Mês e ano de referência para consolidação mensal (mês anterior)
  const today = new Date();
  const currentDay = today.getDate();
  const currentMonth = today.getMonth(); // 0 a 11
  const currentYear = today.getFullYear();
  
  const prevMonthDate = new Date(currentYear, currentMonth - 1, 1);
  const prevMonthNumber = prevMonthDate.getMonth();
  const prevMonthYear = prevMonthDate.getFullYear();
  const prevMonthName = prevMonthDate.toLocaleString("pt-BR", { month: "long" });
  const currentMonthName = today.toLocaleString("pt-BR", { month: "long" });
  
  const daysRemaining = 15 - currentDay;

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
    setRefreshTrigger(prev => prev + 1);
    if (selectedAlert) {
      setSelectedAlert((prev) => prev ? { ...prev, status_alerta: "Resolvido" } : null);
    }
  };

  const fetchConsolidationStats = async () => {
    try {
      const [resNovos, resTratativa] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/alertas/?status=Novo&limit=200`),
        fetch(`${API_BASE_URL}/api/v1/alertas/?status=Em%20Tratativa&limit=200`)
      ]);
      
      let allActiveAlerts: any[] = [];
      if (resNovos.ok) {
        const data = await resNovos.json();
        allActiveAlerts = [...allActiveAlerts, ...(data.data || [])];
      }
      if (resTratativa.ok) {
        const data = await resTratativa.json();
        allActiveAlerts = [...allActiveAlerts, ...(data.data || [])];
      }
      
      const count = allActiveAlerts.filter(alert => {
        if (!alert.data_hora_fato) return false;
        try {
          const alertDate = new Date(alert.data_hora_fato.replace(" ", "T"));
          return alertDate.getMonth() === prevMonthNumber && alertDate.getFullYear() === prevMonthYear;
        } catch (e) {
          return false;
        }
      }).length;
      
      setPendingPrevMonthCount(count);
    } catch (err) {
      console.error("Erro ao buscar estatísticas de consolidação:", err);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchRadarStats();
    fetchConsolidationStats();
    const interval = setInterval(() => {
      fetchStats();
      fetchRadarStats();
      fetchConsolidationStats();
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen lg:h-screen lg:max-h-screen p-3 flex flex-col gap-3 max-w-[1920px] mx-auto lg:overflow-hidden bg-ink text-paper">
      {/* Header Compacto e Sólido (Console de Inteligência) */}
      <header className="bg-surface border border-border px-5 py-3 rounded-md flex items-center justify-between z-50 shrink-0">
        <div className="flex items-center gap-4">
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

          <div className="w-[1px] h-8 bg-border hidden lg:block shrink-0" />

          <div className="hidden sm:flex items-center gap-2 shrink-0">
            <h1 className="text-sm font-bold text-paper tracking-tight font-display uppercase leading-none">
              SENTINELA
            </h1>
            <span className="px-2 py-0.5 rounded-sm bg-focus-bg text-[8px] text-focus font-mono font-bold uppercase tracking-widest border border-focus/20">
              AUDITORIA MVI
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden xl:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-dim" />
            <input 
              type="text" 
              placeholder="Pesquisar boletim, CAD ou NIC..." 
              className="bg-ink border border-border pl-9 pr-3 py-1.5 rounded-sm text-xs w-64 text-paper placeholder:text-slate-dim focus:outline-none focus:border-focus transition-all"
            />
          </div>

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

      {/* Painel de Consolidação Mensal */}
      <div className="bg-surface border border-border p-3.5 rounded-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-r from-surface to-focus-bg/5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-focus/15 border border-focus/25 text-focus rounded-sm shrink-0">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-paper font-display">
              Consolidação Mensal — Mês de Referência: <span className="text-focus">{prevMonthName} de {prevMonthYear}</span>
            </h2>
            <p className="text-[10px] text-slate mt-0.5 leading-none">
              Prazo limite para fechamento das divergências do mês anterior: <strong className="text-paper">15 de {currentMonthName}</strong> ({daysRemaining > 0 ? `${daysRemaining} dias restantes` : daysRemaining === 0 ? "Último dia do prazo!" : "Prazo excedido!"})
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 w-full md:w-auto self-stretch md:self-auto border-t md:border-t-0 md:border-l border-border pt-3 md:pt-0 md:pl-4 shrink-0">
          <div className="flex-1 md:flex-none">
            <span className="text-[9px] text-slate uppercase block tracking-wider font-mono">Divergências Pendentes (Referência)</span>
            <span className="text-xs font-mono font-bold text-warning">{pendingPrevMonthCount} alertas ativos</span>
          </div>
          <div className="flex-1 md:flex-none">
            <span className="text-[9px] text-slate uppercase block tracking-wider font-mono">Status da Consolidação</span>
            {pendingPrevMonthCount > 0 ? (
              <span className="px-2 py-0.5 rounded-sm bg-warning/10 text-warning text-[8px] font-bold uppercase tracking-wider border border-warning/20">
                Pendente
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded-sm bg-ok/10 text-ok text-[8px] font-bold uppercase tracking-wider border border-ok/20">
                Consolidado
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Seletor de Abas Principais e Sub-Abas Operacionais */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0 bg-surface border border-border p-1.5 rounded-sm">
        {/* Abas Principais */}
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab("auditoria")}
            className={`px-3 py-1 rounded-sm flex items-center gap-1.5 transition-all cursor-pointer text-[10px] font-bold uppercase tracking-wider ${
              activeTab === "auditoria"
                ? "bg-surface-raised text-paper border border-border"
                : "text-slate hover:text-paper"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-focus" />
            Console de Auditoria (NEAC)
          </button>
          
          <button
            onClick={() => setActiveTab("futuras")}
            className={`px-3 py-1 rounded-sm flex items-center gap-1.5 transition-all cursor-pointer text-[10px] font-bold uppercase tracking-wider ${
              activeTab === "futuras"
                ? "bg-surface-raised text-paper border border-border"
                : "text-slate hover:text-paper"
            }`}
          >
            <Lock className="w-3.5 h-3.5 text-slate-dim" />
            Funcionalidades Futuras
          </button>
        </div>

        {/* Sub-Abas Operacionais da Auditoria */}
        {activeTab === "auditoria" && (
          <div className="flex gap-1 p-0.5 bg-ink/60 border border-border/40 rounded-sm">
            <button
              onClick={() => setSubTab("alertas")}
              className={`px-2.5 py-1 rounded-sm text-[9px] font-bold uppercase tracking-wider transition-colors cursor-pointer flex items-center gap-1 ${
                subTab === "alertas" ? "bg-focus text-ink font-extrabold" : "text-slate hover:text-paper"
              }`}
            >
              <Activity className="w-3 h-3" />
              Divergências IML
            </button>
            <button
              onClick={() => setSubTab("evolucoes")}
              className={`px-2.5 py-1 rounded-sm text-[9px] font-bold uppercase tracking-wider transition-colors cursor-pointer flex items-center gap-1 ${
                subTab === "evolucoes" ? "bg-critical text-ink font-extrabold" : "text-slate hover:text-paper"
              }`}
            >
              <FolderGit className="w-3 h-3" />
              Fila de Evoluções
            </button>
          </div>
        )}
      </div>

      {/* Conteúdo das Abas */}
      <main className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {activeTab === "auditoria" ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0 overflow-hidden">
            
            {/* Visualização de acordo com a Sub-Aba selecionada */}
            {subTab === "alertas" && (
              <>
                {/* Fila de Alertas */}
                <div className="lg:col-span-6 min-h-0 overflow-hidden flex flex-col">
                  <AlertQueue 
                    onSelectAlert={setSelectedAlert} 
                    selectedAlertId={selectedAlert?.id_alerta} 
                  />
                </div>

                {/* Detalhe do Caso / Timeline */}
                <div className="lg:col-span-6 min-h-0 overflow-hidden flex flex-col">
                  <CaseTimeline 
                    selectedAlert={selectedAlert} 
                    onStatusChanged={handleAlertStatusChanged}
                  />
                </div>
              </>
            )}

            {/* Removed Watchlist subTab */}

            {subTab === "evolucoes" && (
              <>
                <div className="lg:col-span-12 min-h-0 overflow-hidden flex flex-col">
                  <EvolutionsQueue 
                    onRefreshTrigger={refreshTrigger}
                    onEvolutionProcessed={handleAlertStatusChanged}
                  />
                </div>
              </>
            )}

          </div>
        ) : (
          <div className="flex-1 min-h-0 overflow-hidden p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-surface border border-border rounded-md p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 border-b border-border pb-2">
                <Compass className="w-5 h-5 text-slate-dim" />
                <h2 className="text-sm font-bold text-paper font-display uppercase tracking-wider">Radar de Ocorrências (CAD)</h2>
              </div>
              <p className="text-xs text-slate-dim">Módulo de integração com o sistema CAD/190 para detecção antecipada de ocorrências MVI. Atualmente desativado para foco nas evoluções IML.</p>
              <div className="mt-4 opacity-50 pointer-events-none filter blur-[1px]">
                <RadarCAD onStatusChanged={() => {}} />
              </div>
            </div>

            <div className="bg-surface border border-border rounded-md p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 border-b border-border pb-2">
                <TrendingUp className="w-5 h-5 text-slate-dim" />
                <h2 className="text-sm font-bold text-paper font-display uppercase tracking-wider">Watchlist de Tentativas</h2>
              </div>
              <p className="text-xs text-slate-dim">Painel de acompanhamento de longo prazo de vítimas de tentativa que ainda não evoluíram a óbito. Foco transferido temporariamente para a Fila Ativa de Evoluções.</p>
              <div className="mt-4 h-64 overflow-hidden opacity-50 pointer-events-none filter blur-[1px]">
                <WatchlistPanel onRefreshTrigger={0} />
              </div>
            </div>
          </div>
        )}
      </main>

    </div>
  );
}
