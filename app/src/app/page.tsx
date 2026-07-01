/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps, @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Search, Bell, ShieldAlert, Compass, Lock, Activity, ClipboardList, TrendingUp, X, Check } from "lucide-react";
import { AlertQueue } from "@/components/AlertQueue";
import { CaseTimeline } from "@/components/CaseTimeline";
import { SourceQualityCard } from "@/components/ui/SourceQualityCard";
import { DashboardStats } from "@/components/DashboardStats";

// Importação dos novos componentes operacionais do SENTINELA
import { WatchlistPanel } from "@/components/WatchlistPanel";
import { EvolutionsQueue } from "@/components/EvolutionsQueue";
import { IMLNotificationFeed } from "@/components/IMLNotificationFeed";

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
  const [subTab, setSubTab] = useState<"alertas" | "watchlist" | "evolucoes">("alertas");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Estados para o Modal de Proposta de Evolução
  const [proposeModalOpen, setProposeModalOpen] = useState(false);
  const [selectedWatchlistItem, setSelectedWatchlistItem] = useState<any | null>(null);
  const [proposeMotivo, setProposeMotivo] = useState("");
  const [proposeAutor, setProposeAutor] = useState("Thais Aline");
  const [submittingPropose, setSubmittingPropose] = useState(false);

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

  const handleProposeEvolucaoOpen = (item: any) => {
    setSelectedWatchlistItem(item);
    setProposeMotivo(`Confirmada correspondência probabilística no IML com score de ${item.suspeita_evolucao?.score_similaridade}% sob o NIC ${item.suspeita_evolucao?.nic}.`);
    setProposeModalOpen(true);
  };

  const handleSubmitPropose = async () => {
    if (!selectedWatchlistItem) return;
    setSubmittingPropose(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/evolucoes-pendentes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id_controle_morte: selectedWatchlistItem.id_controle_morte,
          nic_iml: selectedWatchlistItem.suspeita_evolucao?.nic,
          bo_pc: selectedWatchlistItem.suspeita_evolucao?.bo_pc || selectedWatchlistItem.bo_pc,
          motivo: proposeMotivo,
          autor: proposeAutor
        })
      });
      if (res.ok) {
        setProposeModalOpen(false);
        setRefreshTrigger(prev => prev + 1);
        fetchStats();
      } else {
        const err = await res.json();
        alert(err.detail || "Erro ao registrar proposta.");
      }
    } catch (err) {
      console.error("Erro ao enviar proposta de evolução:", err);
    } finally {
      setSubmittingPropose(false);
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
              Fila de Alertas
            </button>
            <button
              onClick={() => setSubTab("watchlist")}
              className={`px-2.5 py-1 rounded-sm text-[9px] font-bold uppercase tracking-wider transition-colors cursor-pointer flex items-center gap-1 ${
                subTab === "watchlist" ? "bg-warning text-ink font-extrabold" : "text-slate hover:text-paper"
              }`}
            >
              <TrendingUp className="w-3 h-3" />
              Watchlist de Tentativas
            </button>
            <button
              onClick={() => setSubTab("evolucoes")}
              className={`px-2.5 py-1 rounded-sm text-[9px] font-bold uppercase tracking-wider transition-colors cursor-pointer flex items-center gap-1 ${
                subTab === "evolucoes" ? "bg-focus-bg text-focus border border-focus/30 font-extrabold" : "text-slate hover:text-paper"
              }`}
            >
              <ClipboardList className="w-3 h-3" />
              Evoluções Pendentes
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
              </>
            )}

            {subTab === "watchlist" && (
              <>
                {/* Watchlist Panel */}
                <div className="lg:col-span-4 min-h-0 overflow-hidden flex flex-col">
                  <WatchlistPanel 
                    onProposeEvolucao={handleProposeEvolucaoOpen}
                    onRefreshTrigger={refreshTrigger}
                  />
                </div>

                {/* Linha do tempo associada se houver seleção */}
                <div className="lg:col-span-4 min-h-0 overflow-hidden flex flex-col">
                  <CaseTimeline 
                    selectedAlert={selectedAlert} 
                    onStatusChanged={handleAlertStatusChanged}
                  />
                </div>
              </>
            )}

            {subTab === "evolucoes" && (
              <div className="lg:col-span-8 min-h-0 overflow-hidden flex flex-col">
                <EvolutionsQueue 
                  onRefreshTrigger={refreshTrigger}
                  onEvolutionProcessed={() => setRefreshTrigger(prev => prev + 1)}
                />
              </div>
            )}

            {/* Painel da Direita (Mapa, Notificações IML e Qualidade) */}
            <div className="lg:col-span-4 min-h-0 flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1">
              <div className="h-[240px] shrink-0">
                <CrimeMap selectedAlert={selectedAlert} />
              </div>

              {/* Feed de Notificações do IML */}
              <IMLNotificationFeed 
                onRefreshTrigger={refreshTrigger}
                onNotificationRead={() => setRefreshTrigger(prev => prev + 1)}
              />
              
              <div className="space-y-3 shrink-0">
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

      {/* Modal / Diálogo de Proposta de Evolução */}
      {proposeModalOpen && selectedWatchlistItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border w-full max-w-lg rounded-md overflow-hidden flex flex-col shadow-2xl">
            <div className="px-4 py-3 border-b border-border bg-surface-raised flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-warning" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-paper font-display">
                  Propor Evolução a Óbito
                </h3>
              </div>
              <button 
                onClick={() => setProposeModalOpen(false)}
                className="text-slate hover:text-paper cursor-pointer"
              >
                <X className="w-4.5 h-4.5" />
              </button>
            </div>

            <div className="p-4 space-y-4 text-xs">
              <div className="space-y-1">
                <span className="text-[10px] text-slate uppercase tracking-wider font-mono block">Vítima (Tentativa Mestra)</span>
                <span className="text-paper font-bold text-sm">{selectedWatchlistItem.nome_vitima}</span>
                <span className="text-slate font-mono block">ID Controle Morte: {selectedWatchlistItem.id_controle_morte} | Fato: {selectedWatchlistItem.data_hora_fato}</span>
              </div>

              <div className="p-3 rounded-sm border border-critical/30 bg-critical-bg/5 space-y-1 font-mono text-[10px]">
                <span className="text-critical font-bold uppercase tracking-wider block">Óbito Correspondente no IML</span>
                <div className="text-paper">
                  Nome IML: <span className="font-bold">{selectedWatchlistItem.suspeita_evolucao?.nome_vitima_iml || "Não Identificado"}</span>
                </div>
                <div className="text-slate">
                  NIC: <span className="text-focus font-bold">{selectedWatchlistItem.suspeita_evolucao?.nic}</span>
                  {selectedWatchlistItem.suspeita_evolucao?.data_entrada_iml && ` | Entrada: ${selectedWatchlistItem.suspeita_evolucao.data_entrada_iml}`}
                </div>
                {selectedWatchlistItem.suspeita_evolucao?.tipo_morte && (
                  <div className="text-slate">Causa Mortis IML: {selectedWatchlistItem.suspeita_evolucao.tipo_morte}</div>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-slate uppercase tracking-wider font-mono block">Motivação / Observações do Analista</label>
                <textarea
                  value={proposeMotivo}
                  onChange={(e) => setProposeMotivo(e.target.value)}
                  rows={4}
                  className="w-full bg-ink border border-border rounded-sm p-2 text-paper placeholder:text-slate-dim focus:outline-none focus:border-focus font-mono"
                  placeholder="Justifique a correlação para o supervisor..."
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate uppercase tracking-wider font-mono block">Analista Proponente</label>
                  <select
                    value={proposeAutor}
                    onChange={(e) => setProposeAutor(e.target.value)}
                    className="w-full bg-ink border border-border rounded-sm p-2 text-paper focus:outline-none focus:border-focus"
                  >
                    <option value="Thais Aline">Thais Aline</option>
                    <option value="Sérgio NEAC">Sérgio NEAC</option>
                    <option value="Melissa Neac">Melissa Neac</option>
                    <option value="Laís Policarpto">Laís Policarpto</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate uppercase tracking-wider font-mono block">NIC a Vincular</label>
                  <input
                    type="text"
                    value={selectedWatchlistItem.suspeita_evolucao?.nic || ""}
                    disabled
                    className="w-full bg-ink border border-border rounded-sm p-2 text-slate-dim focus:outline-none font-mono"
                  />
                </div>
              </div>
            </div>

            <div className="px-4 py-3 border-t border-border bg-surface-raised flex items-center justify-end gap-2">
              <button
                onClick={() => setProposeModalOpen(false)}
                className="px-3 py-1.5 rounded-sm bg-ink border border-border text-slate hover:text-paper hover:bg-surface-raised text-[10px] font-bold uppercase tracking-wider cursor-pointer"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmitPropose}
                disabled={submittingPropose}
                className="px-4 py-1.5 rounded-sm bg-critical text-paper text-[10px] font-bold uppercase tracking-wider hover:bg-critical/85 disabled:opacity-50 transition-colors cursor-pointer flex items-center gap-1 border border-critical/30"
              >
                <Check className="w-3.5 h-3.5" />
                {submittingPropose ? "Propondo..." : "Propor Evolução"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
