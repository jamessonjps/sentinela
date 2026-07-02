/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from "react";
import { ShieldAlert, RefreshCw, Check } from "lucide-react";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

const API_BASE_URL = typeof window !== "undefined"
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "")
  : "http://localhost:8000";

interface WatchlistItem {
  id_controle_morte: number;
  nome_vitima: string;
  data_hora_fato: string;
  bairro?: string;
  cidade: string;
  bo_pc?: string;
  cad?: string;
  suspeita_evolucao?: {
    nic: string;
    nome_vitima_iml?: string;
    data_entrada_iml?: string;
    tipo_morte?: string;
    score_similaridade: number;
    bo_pc?: string;
  } | null;
}

interface WatchlistPanelProps {
  onRefreshTrigger: number;
}

export function WatchlistPanel({ onRefreshTrigger }: WatchlistPanelProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [auditRunning, setAuditRunning] = useState(false);

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/watchlist`);
      if (res.ok) {
        const data = await res.json();
        setWatchlist(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar watchlist:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAudit = async () => {
    setAuditRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/reconciliar`, { method: "POST" });
      if (res.ok) {
        fetchWatchlist();
      }
    } catch (err) {
      console.error("Erro ao rodar auditoria:", err);
    } finally {
      setAuditRunning(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, [onRefreshTrigger]);

  return (
    <Card className="flex-1 flex flex-col min-h-0 bg-surface border border-border rounded-md overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-surface-raised flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-warning" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-paper font-display">
            Watchlist de Tentativas
          </h2>
          <span className="px-1.5 py-0.5 rounded-sm bg-ink border border-border text-[8px] font-mono text-slate">
            {watchlist.length} monitoradas
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchWatchlist}
            disabled={loading}
            title="Atualizar Watchlist"
            className="p-1.5 rounded-sm bg-ink border border-border text-slate hover:text-paper hover:bg-surface disabled:opacity-50 transition-all cursor-pointer flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin text-focus" : ""}`} />
            {loading ? "Atualizando..." : "Atualizar"}
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
        {loading ? (
          <div className="h-32 flex items-center justify-center text-xs text-slate-dim font-mono">
            Carregando monitoramento de tentativas...
          </div>
        ) : watchlist.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-xs text-slate-dim font-mono">
            Nenhuma tentativa de homicídio ativa em monitoramento.
          </div>
        ) : (
          watchlist.map((item) => (
            <div
              key={item.id_controle_morte}
              className={`p-3 rounded-sm border transition-colors ${
                item.suspeita_evolucao 
                  ? "bg-critical-bg/10 border-critical/30 hover:bg-critical-bg/20" 
                  : "bg-ink border-border hover:bg-surface-raised"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold font-mono text-slate">
                      ID {item.id_controle_morte}
                    </span>
                    <span className="text-xs font-bold text-paper font-display uppercase">
                      {item.nome_vitima || "Sem Identificação"}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-slate font-mono">
                    <span>{item.cidade}{item.bairro ? ` - ${item.bairro}` : ""}</span>
                    <span>•</span>
                    <span>{item.data_hora_fato}</span>
                  </div>
                  {item.bo_pc && (
                    <div className="text-[9px] text-slate-dim font-mono mt-1">
                      BO: {item.bo_pc} {item.cad ? `| CAD: ${item.cad}` : ""}
                    </div>
                  )}
                </div>

                {item.suspeita_evolucao && (
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <Badge variant="critical" className="text-[8px]">
                      Suspeita de Óbito ({item.suspeita_evolucao.score_similaridade}%)
                    </Badge>
                  </div>
                )}
              </div>

              {/* Detalhes do Match Probabilístico lado a lado */}
              {item.suspeita_evolucao && (
                <div className="mt-2.5 pt-2.5 border-t border-critical/20 grid grid-cols-2 gap-3 text-[9px] bg-critical-bg/5 p-2 rounded-sm">
                  <div>
                    <span className="text-slate-dim block mb-0.5 uppercase tracking-wider font-mono">Registro SIESP (Mestra)</span>
                    <span className="text-paper block font-semibold">{item.nome_vitima || "Sem Nome"}</span>
                    <span className="text-slate block mt-0.5">{item.data_hora_fato}</span>
                  </div>
                  <div className="border-l border-critical/20 pl-3">
                    <span className="text-slate-dim block mb-0.5 uppercase tracking-wider font-mono">Corpo IML (SGOU)</span>
                    <span className="text-critical block font-bold">{item.suspeita_evolucao.nome_vitima_iml || "Sem Identificação"}</span>
                    <span className="text-slate block mt-0.5">NIC: {item.suspeita_evolucao.nic} | {item.suspeita_evolucao.data_entrada_iml}</span>
                  </div>
                  <div className="col-span-2 border-t border-critical/10 pt-1.5 text-center text-slate font-sans leading-relaxed text-[8.5px]">
                    Oriente a reclassificação de tentativa para MVI e vincule o NIC na base SIESP para consolidar automaticamente.
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
