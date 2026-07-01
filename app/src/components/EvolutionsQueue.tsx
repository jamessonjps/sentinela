/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from "react";
import { FolderGit, Check, X, Shield, Clock } from "lucide-react";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

const API_BASE_URL = typeof window !== "undefined"
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "")
  : "http://localhost:8000";

interface EvolutionPropose {
  id_evolucao: number;
  id_controle_morte: number;
  nic_iml: string;
  bo_pc?: string;
  data_obito?: string;
  motivo: string;
  tipo_evolucao: string;
  autor: string;
  data_criacao: string;
  caso_origem: {
    nome_vitima: string;
    subjetividade: string;
    data_hora_fato: string;
    cidade: string;
    bairro?: string;
    cad?: string;
  };
}

interface EvolutionsQueueProps {
  onRefreshTrigger: number;
  onEvolutionProcessed: () => void;
}

export function EvolutionsQueue({ onRefreshTrigger, onEvolutionProcessed }: EvolutionsQueueProps) {
  const [propostas, setPropostas] = useState<EvolutionPropose[]>([]);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);

  const fetchPropostas = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/evolucoes-pendentes`);
      if (res.ok) {
        const data = await res.json();
        setPropostas(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar propostas de evolução:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (evolId: number, decision: "Aprovada" | "Rejeitada") => {
    setProcessingId(evolId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/evolucoes-pendentes/${evolId}/processar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: decision,
          motivo_decisao: `Decisão de supervisor tomada via console operacional.`
        })
      });
      if (res.ok) {
        fetchPropostas();
        onEvolutionProcessed();
      }
    } catch (err) {
      console.error("Erro ao registrar decisão de evolução:", err);
    } finally {
      setProcessingId(null);
    }
  };

  useEffect(() => {
    fetchPropostas();
  }, [onRefreshTrigger]);

  return (
    <Card className="flex-grow flex flex-col min-h-0 bg-surface border border-border rounded-md overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-surface-raised flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <FolderGit className="w-4 h-4 text-focus" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-paper font-display">
            Fila de Evolução Pendente (Substitui Excel)
          </h2>
          <span className="px-1.5 py-0.5 rounded-sm bg-ink border border-border text-[8px] font-mono text-slate">
            {propostas.length} pendentes
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
        {loading ? (
          <div className="h-32 flex items-center justify-center text-xs text-slate-dim font-mono">
            Carregando fila de evoluções...
          </div>
        ) : propostas.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-xs text-slate-dim font-mono text-center px-4">
            Nenhuma evolução pendente. A base do SIESP está atualizada com as reclassificações.
          </div>
        ) : (
          propostas.map((prop) => (
            <div
              key={prop.id_evolucao}
              className="p-3 rounded-sm border border-border bg-ink hover:bg-surface-raised transition-colors"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold font-mono text-slate">
                      ID {prop.id_controle_morte}
                    </span>
                    <span className="text-xs font-bold text-paper font-display uppercase">
                      {prop.caso_origem.nome_vitima || "Sem Nome"}
                    </span>
                    <Badge variant="warning" className="text-[7px]">
                      {prop.tipo_evolucao}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[9px] font-mono text-slate bg-surface/40 p-2 rounded-sm border border-border/40">
                    <div>
                      <span className="text-slate-dim block uppercase tracking-wider">SIESP Origem:</span>
                      <span className="text-paper font-semibold block">{prop.caso_origem.subjetividade}</span>
                      <span className="text-slate-dim block mt-0.5">{prop.caso_origem.data_hora_fato}</span>
                      <span className="text-slate-dim block">{prop.caso_origem.cidade}</span>
                    </div>
                    <div className="border-l border-border/40 pl-3">
                      <span className="text-slate-dim block uppercase tracking-wider">Novo NIC (IML):</span>
                      <span className="text-focus font-bold block">{prop.nic_iml}</span>
                      {prop.bo_pc && <span className="text-paper block">BO PC: {prop.bo_pc}</span>}
                    </div>
                  </div>

                  <div className="text-[10px] text-slate-dim font-mono leading-relaxed bg-surface/20 p-2 rounded-sm border border-border/20">
                    <span className="text-slate font-bold block mb-1">Motivação / Detalhes da Proposta:</span>
                    &quot;{prop.motivo}&quot;
                  </div>

                  <div className="flex items-center gap-2 text-[9px] text-slate-dim font-mono">
                    <Clock className="w-3 h-3" />
                    <span>Proposto por {prop.autor} em {prop.data_criacao ? new Date(prop.data_criacao).toLocaleString() : ""}</span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0 self-end md:self-start bg-surface p-1 rounded-sm border border-border">
                  <span className="text-[8px] font-mono text-slate-dim uppercase tracking-wider mr-2 hidden lg:inline-block flex items-center gap-1">
                    <Shield className="w-2.5 h-2.5 text-focus" />
                    Supervisor
                  </span>
                  <button
                    onClick={() => handleDecision(prop.id_evolucao, "Aprovada")}
                    disabled={processingId === prop.id_evolucao}
                    className="p-1 px-2.5 rounded-sm bg-ok text-ink text-[9px] font-bold uppercase tracking-wider hover:bg-ok/90 disabled:opacity-50 transition-all cursor-pointer flex items-center gap-1"
                  >
                    <Check className="w-3 h-3" />
                    Aprovar
                  </button>
                  <button
                    onClick={() => handleDecision(prop.id_evolucao, "Rejeitada")}
                    disabled={processingId === prop.id_evolucao}
                    className="p-1 px-2.5 rounded-sm bg-ink border border-border text-slate hover:text-paper hover:bg-surface-raised disabled:opacity-50 transition-all cursor-pointer flex items-center gap-1"
                  >
                    <X className="w-3 h-3 text-critical" />
                    Rejeitar
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
