"use client";

import { useState } from "react";
import { FileText, AlertTriangle, CheckCircle, RefreshCw, MapPin } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface GeoValidacao {
  alerta_geografico: boolean;
  bairro_divergente: boolean;
  fato_em_hospital: boolean;
  hospital_nome?: string | null;
  fato_em_presidio: boolean;
  presidio_nome?: string | null;
  procedencia_prisional: boolean;
  orgao_procedencia?: string | null;
  bairro_cadastrado: string;
  bairro_gps_centro?: [number, number] | null;
  gps_latitude?: number | null;
  gps_longitude?: number | null;
  distancia_bairro_km?: number | null;
}

interface LaudoPericial {
  numero_protocolo: string;
  tipo_exame: string;
  data_exame: string;
  perito_legista: string;
  conclusao: string;
  paciente: string;
}

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
  geo_validacao?: GeoValidacao;
  laudo?: LaudoPericial;
}

interface CaseTimelineProps {
  selectedAlert: Alert | null;
  onStatusChanged: () => void;
}

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export function CaseTimeline({ selectedAlert, onStatusChanged }: CaseTimelineProps) {
  const [updating, setUpdating] = useState(false);

  if (!selectedAlert) {
    return (
      <Card title="Ficha do Caso" className="w-full h-full flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-sm bg-surface-raised border border-border flex items-center justify-center text-slate mb-4">
          <FileText className="w-6 h-6 opacity-45" />
        </div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-paper">Nenhum Caso Selecionado</h3>
        <p className="text-xs text-slate max-w-[220px] mt-2">
          Selecione uma ocorrência na fila de auditoria para visualizar a consistência de chaves e fluxo dos sistemas.
        </p>
      </Card>
    );
  }

  const handleStatusChange = async (newStatus: string) => {
    setUpdating(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/alertas/${selectedAlert.id_alerta}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        onStatusChanged();
      }
    } catch (err) {
      console.error("Erro ao atualizar status:", err);
    } finally {
      setUpdating(false);
    }
  };

  // Verifica se o caso é uma evolução de tentativa para óbito (evento central)
  const isEvolution = 
    selectedAlert.subjetividade?.toLowerCase().includes("tentativa") || 
    selectedAlert.tipo_alerta?.toLowerCase().includes("evolução") || 
    selectedAlert.tipo_alerta?.toLowerCase().includes("tentativa");

  const hasBo = selectedAlert.bo_pc && selectedAlert.bo_pc !== "None" && selectedAlert.bo_pc !== "NAN";
  const hasCad = selectedAlert.cad && selectedAlert.cad !== "None" && selectedAlert.cad !== "NAN";
  const hasNic = selectedAlert.nic && selectedAlert.nic !== "None" && selectedAlert.nic !== "NAN";
  const hasDo = selectedAlert.declaracao_obito && selectedAlert.declaracao_obito !== "";

  // Definição dos nós do fluxo operacional
  const nodes = [
    { id: "fato", label: "Fato", filled: true, active: true },
    { id: "bo", label: "BO PC", filled: !!hasBo, active: true },
    { id: "cad", label: "CAD PM", filled: !!hasCad, active: true },
    { id: "iml", label: "IML", filled: !!hasNic, isEvol: isEvolution, active: true },
    { id: "nic", label: "NIC", filled: !!hasNic && !!hasDo, active: true },
  ];

  return (
    <Card
      title={`Ficha do Alerta #${selectedAlert.id_alerta}`}
      action={
        <Badge variant={selectedAlert.prioridade >= 3 ? "critical" : selectedAlert.prioridade === 2 ? "warning" : "ok"}>
          {selectedAlert.prioridade >= 3 ? "Alta Prioridade" : selectedAlert.prioridade === 2 ? "Média" : "Baixa"}
        </Badge>
      }
      className="w-full h-full min-h-0 flex flex-col"
    >
      {/* Informações da Vítima e Local */}
      <div className="grid grid-cols-2 gap-3 mb-4 shrink-0 bg-surface-raised/40 p-3 border border-border rounded-sm">
        <div>
          <span className="text-[10px] text-slate uppercase tracking-wider block">Identificação Vítima</span>
          <span className="text-[13px] font-bold text-paper block truncate">
            {selectedAlert.nome_vitima_cm || `VÍTIMA_${selectedAlert.id_controle_morte}`}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate uppercase tracking-wider block">Município / Localidade</span>
          <span className="text-[13px] font-bold text-paper block truncate flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate shrink-0" />
            {selectedAlert.cidade}
          </span>
        </div>
        <div className="col-span-2 grid grid-cols-3 gap-2 mt-1.5 pt-2 border-t border-border/30 text-[11px] text-slate font-mono">
          <span>AISP: {selectedAlert.aisp || "N/A"}</span>
          <span>RISP: {selectedAlert.risp || "N/A"}</span>
          <span>Data: {selectedAlert.data_hora_fato || "N/A"}</span>
        </div>
      </div>

      {/* Linha do Tempo Horizontal */}
      <div className="shrink-0 mb-5 border border-border rounded-sm bg-surface-raised/20">
        <div className="text-[10px] text-slate uppercase tracking-wider font-bold px-3 pt-2.5">
          Fluxo de Integração de Sistemas
        </div>
        <div className="relative flex items-center justify-between w-full px-5 py-4">
          {/* Conector de 1px sólido */}
          <div className="absolute left-10 right-10 h-[1px] bg-border top-1/2 -translate-y-1/2 z-0" />
          
          {nodes.map((node, i) => (
            <div key={node.id} className="relative z-10 flex flex-col items-center gap-1.5">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center border text-[11px] font-mono font-bold transition-all duration-300 ${
                  node.isEvol
                    ? "bg-[var(--color-critical)] border-[var(--color-critical)] text-paper ring-4 ring-[var(--color-critical-bg)]"
                    : node.filled
                    ? "bg-[var(--color-ok)] border-[var(--color-ok)] text-paper"
                    : "bg-surface border-[var(--color-slate-dim)] text-[var(--color-slate-dim)]"
                }`}
              >
                {i + 1}
              </div>
              <span className="text-[9px] text-slate font-bold uppercase tracking-wider">
                {node.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Detalhamento dos Alertas / Divergências */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-1 min-h-0 space-y-3">
        {/* Alerta de Divergência de Nome Vítima */}
        {selectedAlert.tipo_alerta && selectedAlert.tipo_alerta.toLowerCase().includes("nome") && (
          <div className="bg-[var(--color-critical-bg)] border border-[var(--color-critical)]/20 p-3 rounded-sm">
            <h4 className="text-[10px] font-bold text-[var(--color-critical)] uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              Divergência Crítica de Identidade
            </h4>
            <p className="text-[11px] text-slate mb-2">
              Divergência fonética de nome detectada entre o prontuário do necrotério e a ficha de óbito.
            </p>
            <div className="grid grid-cols-2 gap-2 text-[11px] bg-ink/70 p-2.5 border border-border font-mono">
              <div>
                <span className="text-slate text-[9px] block uppercase">Mestra (Controle Morte):</span>
                <span className="text-paper font-bold block truncate">{selectedAlert.nome_vitima_cm || "N/A"}</span>
              </div>
              <div>
                <span className="text-slate text-[9px] block uppercase">IML (Necroscópico):</span>
                <span className="text-[var(--color-warning)] font-bold block truncate">{selectedAlert.nome_vitima_iml || "N/A"}</span>
              </div>
            </div>
          </div>
        )}

        {/* Alertas de Geovalidação & Sistema Prisional */}
        {selectedAlert.geo_validacao?.alerta_geografico && (
          <div className="space-y-2 shrink-0">
            {/* Presídio */}
            {(selectedAlert.geo_validacao.fato_em_presidio || selectedAlert.geo_validacao.procedencia_prisional) && (
              <div className="bg-[var(--color-critical-bg)] border border-[var(--color-critical)]/25 p-3 rounded-sm">
                <h4 className="text-[10px] font-bold text-[var(--color-critical)] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  Óbito Prisional (Alto Risco)
                </h4>
                <p className="text-[11px] text-paper">
                  Este óbito foi geolocalizado em presídio ou possui guia requisitada por órgão prisional:
                </p>
                <div className="text-[11px] font-mono text-[var(--color-critical)] font-bold mt-1.5 bg-ink/50 p-2 border border-border/40">
                  {selectedAlert.geo_validacao.fato_em_presidio && (
                    <div className="block">Local GPS: {selectedAlert.geo_validacao.presidio_nome}</div>
                  )}
                  {selectedAlert.geo_validacao.procedencia_prisional && (
                    <div className="block">Procedência IML: {selectedAlert.geo_validacao.orgao_procedencia}</div>
                  )}
                </div>
              </div>
            )}

            {/* Hospital */}
            {selectedAlert.geo_validacao.fato_em_hospital && (
              <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/20 p-3 rounded-sm">
                <h4 className="text-[10px] font-bold text-[var(--color-warning)] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  Fato Georreferenciado em Hospital
                </h4>
                <p className="text-[11px] text-slate">
                  As coordenadas de GPS apontam para a unidade de socorro: <strong className="text-paper">{selectedAlert.geo_validacao.hospital_nome}</strong>. 
                  Recomenda-se auditar o local real do fato com os analistas de geografia.
                </p>
              </div>
            )}

            {/* Bairro Divergente */}
            {selectedAlert.geo_validacao.bairro_divergente && (
              <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/20 p-3 rounded-sm">
                <h4 className="text-[10px] font-bold text-[var(--color-warning)] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  Inconsistência de Bairro (GPS)
                </h4>
                <p className="text-[11px] text-slate">
                  O registro indica o bairro <strong className="text-paper">{selectedAlert.geo_validacao.bairro_cadastrado}</strong>, mas as coordenadas GPS do fato caem a mais de <strong className="text-paper">{(selectedAlert.geo_validacao.distancia_bairro_km || 1.5).toFixed(1)} km</strong> do centro geométrico esperado.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Alertas Críticos de Laudos do IML */}
        {selectedAlert.laudo && (
          <div className="space-y-2 shrink-0">
            {/* Divergência de Causa Mortis */}
            {selectedAlert.tipo_alerta && selectedAlert.tipo_alerta.toLowerCase().includes("causa da morte") && (
              <div className="bg-[var(--color-critical-bg)] border border-[var(--color-critical)]/25 p-3 rounded-sm">
                <h4 className="text-[10px] font-bold text-[var(--color-critical)] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  Divergência Crítica de Causa Mortis
                </h4>
                <p className="text-[11px] text-paper">
                  Conclusão pericial é incompatível com a subjetividade registrada no caso:
                </p>
                <div className="text-[11px] font-mono mt-1.5 bg-ink/50 p-2.5 border border-border/40 space-y-1">
                  <div>
                    <span className="text-slate text-[9px] block uppercase">Subjetividade Mestra:</span>
                    <span className="text-paper font-bold block">{selectedAlert.subjetividade || "N/A"}</span>
                  </div>
                  <div className="pt-1.5 border-t border-border/20">
                    <span className="text-slate text-[9px] block uppercase">Conclusão do Laudo IML:</span>
                    <span className="text-[var(--color-critical)] font-bold block leading-relaxed">{selectedAlert.laudo.conclusao}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Divergência de Identidade no Laudo */}
            {selectedAlert.tipo_alerta && selectedAlert.tipo_alerta.toLowerCase().includes("identidade no laudo") && (
              <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/20 p-3 rounded-sm">
                <h4 className="text-[10px] font-bold text-[var(--color-warning)] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  Divergência de Nome no Laudo
                </h4>
                <p className="text-[11px] text-slate mb-1.5">
                  Divergência fonética entre o cadastro principal e o laudo pericial:
                </p>
                <div className="grid grid-cols-2 gap-2 text-[11px] bg-ink/50 p-2 border border-border/40 font-mono">
                  <div>
                    <span className="text-slate text-[9px] block uppercase">Nome Mestra:</span>
                    <span className="text-paper font-bold block truncate">{selectedAlert.nome_vitima_cm || "N/A"}</span>
                  </div>
                  <div>
                    <span className="text-slate text-[9px] block uppercase">Paciente no Laudo:</span>
                    <span className="text-[var(--color-warning)] font-bold block truncate">{selectedAlert.laudo.paciente || "N/A"}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Card Detalhado do Laudo Pericial */}
            <div className="border border-border rounded-sm p-3 bg-surface-raised/15 space-y-2">
              <div className="text-[10px] text-slate uppercase tracking-wider font-bold flex items-center justify-between">
                <span>Laudo de Necropsia (Forensis)</span>
                <span className="text-focus text-[9px] font-mono">{selectedAlert.laudo.numero_protocolo}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] bg-ink/75 p-2 rounded-sm border border-border/40">
                <div>
                  <span className="text-slate text-[9px] block uppercase">Perito Legista:</span>
                  <span className="text-paper font-medium block truncate">{selectedAlert.laudo.perito_legista || "N/A"}</span>
                </div>
                <div>
                  <span className="text-slate text-[9px] block uppercase">Data do Exame:</span>
                  <span className="text-paper font-medium block truncate">{selectedAlert.laudo.data_exame || "N/A"}</span>
                </div>
              </div>
              <div className="bg-ink/50 p-2.5 rounded-sm border border-border/40 text-[11px]">
                <span className="text-slate text-[9px] block uppercase mb-1">Discussão e Conclusão Pericial:</span>
                <p className="text-paper font-medium leading-relaxed m-0 italic">
                  &quot;{selectedAlert.laudo.conclusao}&quot;
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Informações dos Sistemas Relacionados */}
        <div className="border border-border rounded-sm p-3 bg-surface-raised/15 space-y-2.5">
          <div className="text-[10px] text-slate uppercase tracking-wider font-bold">
            Auditoria de Chaves do Fluxo
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="flex flex-col gap-1 p-2 bg-ink border border-border/60 rounded-sm">
              <span className="text-[9px] text-slate uppercase font-bold">Boletim de Ocorrência PC</span>
              <span className="font-mono text-paper">
                {hasBo ? selectedAlert.bo_pc : "Não Vinculado"}
              </span>
              <span className="text-[10px] text-slate-dim">
                {selectedAlert.natureza_daas || "Natureza não localizada no PPE"}
              </span>
            </div>

            <div className="flex flex-col gap-1 p-2 bg-ink border border-border/60 rounded-sm">
              <span className="text-[9px] text-slate uppercase font-bold">Despacho 190 PM (CAD)</span>
              <span className="font-mono text-paper">
                {hasCad ? selectedAlert.cad : "Não Vinculado"}
              </span>
              <span className="text-[10px] text-slate-dim">
                {selectedAlert.natureza_cad || "Despacho não localizado no CAD"}
              </span>
            </div>

            <div className="flex flex-col gap-1 p-2 bg-ink border border-border/60 rounded-sm">
              <span className="text-[9px] text-slate uppercase font-bold">Registro de Entrada IML</span>
              <span className="font-mono text-paper">
                {hasNic ? selectedAlert.nic : "Não Vinculado (Sem Corpo)"}
              </span>
              <span className="text-[10px] text-slate-dim">
                {selectedAlert.tipo_morte_iml ? `Morte: ${selectedAlert.tipo_morte_iml}` : "Laudo pendente"}
              </span>
            </div>

            <div className="flex flex-col gap-1 p-2 bg-ink border border-border/60 rounded-sm">
              <span className="text-[9px] text-slate uppercase font-bold">Declaração de Óbito (DO)</span>
              <span className="font-mono text-paper">
                {hasDo ? selectedAlert.declaracao_obito : "DO Vazia/Pendente"}
              </span>
              <span className="text-[10px] text-slate-dim">
                Guia física recolhida no IML
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Ações de Tratamento do Alerta */}
      <div className="mt-4 pt-4 border-t border-border shrink-0">
        <div className="flex gap-2">
          {selectedAlert.status_alerta !== "Resolvido" ? (
            <>
              {selectedAlert.status_alerta === "Novo" ? (
                <button
                  onClick={() => handleStatusChange("Em Tratativa")}
                  disabled={updating}
                  className="flex-1 bg-[var(--color-warning-bg)] hover:bg-[var(--color-warning-bg)]/80 text-[var(--color-warning)] text-xs font-bold py-2 rounded-sm border border-[var(--color-warning)]/30 flex items-center justify-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
                >
                  {updating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Iniciar Tratativa (NEAC)"}
                </button>
              ) : (
                <button
                  onClick={() => handleStatusChange("Resolvido")}
                  disabled={updating}
                  className="flex-1 bg-[var(--color-ok-bg)] hover:bg-[var(--color-ok-bg)]/80 text-[var(--color-ok)] text-xs font-bold py-2 rounded-sm border border-[var(--color-ok)]/30 flex items-center justify-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
                >
                  {updating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Resolver Inconsistência"}
                </button>
              )}
            </>
          ) : (
            <div className="w-full bg-[var(--color-ok-bg)] border border-[var(--color-ok)]/20 py-2 rounded-sm flex items-center justify-center gap-2 text-[var(--color-ok)] text-xs font-bold">
              <CheckCircle className="w-4 h-4" />
              Alerta Resolvido / Auditado
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
