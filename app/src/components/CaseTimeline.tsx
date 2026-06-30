"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, MapPin, Calendar, Clock, AlertTriangle, ShieldCheck, ArrowRight, RefreshCw, CheckCircle, HelpCircle } from "lucide-react";

interface CaseTimelineProps {
  selectedAlert: any;
  onStatusChanged: () => void;
}

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export function CaseTimeline({ selectedAlert, onStatusChanged }: CaseTimelineProps) {
  const [updating, setUpdating] = useState(false);

  if (!selectedAlert) {
    return (
      <div className="glass-card p-6 w-full h-full flex flex-col items-center justify-center text-center rounded-2xl">
        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-muted-foreground mb-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
          <FileText className="w-8 h-8 opacity-40" />
        </div>
        <h3 className="text-sm font-bold text-white">Nenhum Alerta Selecionado</h3>
        <p className="text-xs text-muted-foreground max-w-[200px] mt-2">
          Selecione uma ocorrência na fila de auditoria para visualizar a consistência de chaves e dados.
        </p>
      </div>
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

  // Prepara as etapas da linha do tempo com base nas chaves do caso selecionado
  const steps = [
    {
      id: "fato",
      title: "Fato Registrado (Mestra)",
      subtitle: `ID Mestra: #${selectedAlert.id_controle_morte}`,
      description: `Classificação: ${selectedAlert.subjetividade} • Instrumento: ${selectedAlert.instrumento || 'Não Informado'}`,
      date: selectedAlert.data_hora_fato || "Data N/I",
      status: "success",
      badge: selectedAlert.tipo_mvi || "MVI"
    },
    {
      id: "cad",
      title: "Despacho 190 (PM)",
      subtitle: selectedAlert.cad && selectedAlert.cad !== "None" && selectedAlert.cad !== "NAN" 
        ? `CAD ID: ${selectedAlert.cad}` 
        : "Vínculo CAD Faltante",
      description: selectedAlert.natureza_cad 
        ? `Natureza Despachada: ${selectedAlert.natureza_cad}` 
        : "Nenhum vínculo automático ou manual com o despacho 190.",
      date: selectedAlert.cad && selectedAlert.cad !== "NAN" ? "Integrado" : "Pendente",
      status: selectedAlert.cad && selectedAlert.cad !== "NAN" ? "success" : "warning",
      alert: selectedAlert.cad === "NAN" || !selectedAlert.cad
    },
    {
      id: "bo",
      title: "Boletim de Ocorrência (PC)",
      subtitle: selectedAlert.bo_pc && selectedAlert.bo_pc !== "None" && selectedAlert.bo_pc !== "NAN" 
        ? `BO PC: ${selectedAlert.bo_pc}` 
        : "BO Não Localizado",
      description: selectedAlert.natureza_daas 
        ? `Natureza PPE: ${selectedAlert.natureza_daas}`
        : "Ocorrência sem Boletim de Ocorrência registrado no DAAS.",
      date: selectedAlert.bo_pc && selectedAlert.bo_pc !== "NAN" ? "Integrado" : "Pendente",
      status: selectedAlert.bo_pc && selectedAlert.bo_pc !== "NAN" 
        ? (selectedAlert.alerta_natureza_divergente === "VERIFICAR" ? "warning" : "success") 
        : "warning",
      alert: selectedAlert.alerta_bo_inexistente === "SIM" || selectedAlert.alerta_natureza_divergente === "VERIFICAR"
    },
    {
      id: "iml",
      title: "Entrada Necrotério (IML)",
      subtitle: selectedAlert.nic && selectedAlert.nic !== "None" && selectedAlert.nic !== "NAN" 
        ? `NIC IML: ${selectedAlert.nic}` 
        : "NIC Faltante",
      description: selectedAlert.nic && selectedAlert.nic !== "NAN"
        ? (selectedAlert.declaracao_obito 
            ? `DO: ${selectedAlert.declaracao_obito} • Causa: ${selectedAlert.tipo_morte_iml || 'N/I'}`
            : "Corpo deu entrada no IML, porém o número da Declaração de Óbito (DO) está VAZIO.")
        : "Nenhum registro de laudo necroscópico ou NIC associado.",
      date: selectedAlert.nic && selectedAlert.nic !== "NAN" ? "Integrado" : "Pendente",
      status: selectedAlert.nic && selectedAlert.nic !== "NAN"
        ? (selectedAlert.declaracao_obito ? "success" : "danger") 
        : "warning",
      alert: selectedAlert.alerta_nic_faltante === "SIM" || selectedAlert.declaracao_obito === null || !selectedAlert.declaracao_obito
    }
  ];

  return (
    <div className="glass-card p-5 w-full h-full flex flex-col rounded-2xl overflow-hidden">
      {/* Cabeçalho do Detalhe */}
      <div className="mb-4 shrink-0">
        <h2 className="text-sm font-bold text-white flex items-center gap-1.5 mb-1">
          <FileText className="text-primary w-4.5 h-4.5" />
          Ficha do Alerta #{selectedAlert.id_alerta}
        </h2>
        <span className="text-[10px] text-muted-foreground font-mono block truncate">
          Vítima: VITIMA_{selectedAlert.id_controle_morte}
        </span>
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-2">
          <span className="flex items-center gap-1 bg-white/5 px-2 py-0.5 rounded border border-white/5">
            AISP: {selectedAlert.aisp}
          </span>
          <span className="flex items-center gap-1 bg-white/5 px-2 py-0.5 rounded border border-white/5">
            RISP: {selectedAlert.risp}
          </span>
        </div>
      </div>

      {/* Alerta de Divergência de Nome Vítima */}
      {selectedAlert.tipo_alerta && selectedAlert.tipo_alerta.includes("Divergência de Nome") && (
        <div className="bg-destructive/10 border border-destructive/20 p-3.5 rounded-xl mb-4 text-xs shrink-0">
          <h4 className="font-bold text-destructive flex items-center gap-1.5 mb-1.5 uppercase tracking-wider text-[9px]">
            <AlertTriangle className="w-4 h-4 text-destructive animate-pulse" />
            Divergência de Nome no IML
          </h4>
          <p className="text-[10px] text-muted-foreground mb-2 leading-tight">
            O necrotério registrou um nome de vítima divergente ou identificou o corpo na base.
          </p>
          <div className="grid grid-cols-2 gap-2 text-[10px] bg-black/45 p-2 rounded-lg border border-white/5 font-mono">
            <div>
              <span className="text-muted-foreground text-[8px] block uppercase">Controle Morte:</span>
              <span className="text-white font-bold block truncate" title={selectedAlert.nome_vitima_cm}>
                {selectedAlert.nome_vitima_cm || "N.I."}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground text-[8px] block uppercase">Registrado IML:</span>
              <span className="text-warning font-bold block truncate" title={selectedAlert.nome_vitima_iml}>
                {selectedAlert.nome_vitima_iml || "N.I."}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Linha do Tempo Física */}
      <div className="flex-1 overflow-y-auto scrollbar-hide py-2 pr-1 relative">
        <div className="absolute left-[17px] top-6 bottom-6 w-[2px] bg-white/5 rounded-full" />

        <div className="space-y-5">
          {steps.map((step) => {
            const isSuccess = step.status === "success";
            const isDanger = step.status === "danger";
            
            return (
              <div key={step.id} className="relative flex items-start gap-4">
                {/* Indicador Visual do Nó */}
                <div className={`relative z-10 w-9 h-9 rounded-full flex items-center justify-center border transition-all duration-300 ${
                  isSuccess ? "bg-success/10 border-success/30 text-success" : 
                  isDanger ? "bg-destructive/10 border-destructive/30 text-destructive animate-pulse" : 
                  "bg-warning/10 border-warning/30 text-warning"
                }`}>
                  <FileText className="w-4 h-4" />
                </div>

                <div className="flex-1 min-w-0 pt-0.5">
                  <div className="flex justify-between items-start gap-2">
                    <h3 className="font-semibold text-white text-xs truncate">
                      {step.title}
                    </h3>
                    <span className="text-[9px] text-muted-foreground font-mono bg-white/5 px-1.5 py-0.5 rounded border border-white/5 shrink-0">
                      {step.date}
                    </span>
                  </div>
                  <p className="text-[10px] text-white/80 font-medium mt-1 truncate">{step.subtitle}</p>
                  <p className="text-[10px] text-muted-foreground mt-1 leading-relaxed">
                    {step.description}
                  </p>
                  
                  {/* Sinalizador de inconsistência local */}
                  {step.alert && (
                    <div className="mt-1.5 flex items-center gap-1 text-[9px] bg-destructive/5 text-destructive border border-destructive/10 px-2 py-0.5 rounded-md w-fit">
                      <AlertTriangle className="w-3 h-3" />
                      Inconsistência Identificada
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ações de Tratamento */}
      <div className="mt-4 pt-4 border-t border-white/5 shrink-0">
        <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2">Tratamento do Alerta</h4>
        <div className="flex gap-2">
          {selectedAlert.status_alerta !== "Resolvido" ? (
            <>
              {selectedAlert.status_alerta === "Novo" ? (
                <button
                  onClick={() => handleStatusChange("Em Tratativa")}
                  disabled={updating}
                  className="flex-1 bg-warning/20 hover:bg-warning/30 text-warning text-xs font-bold py-2 px-3 rounded-xl border border-warning/30 flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  {updating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Iniciar Tratativa"}
                </button>
              ) : (
                <button
                  onClick={() => handleStatusChange("Resolvido")}
                  disabled={updating}
                  className="flex-1 bg-success/20 hover:bg-success/30 text-success text-xs font-bold py-2 px-3 rounded-xl border border-success/30 flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  {updating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Resolver Inconsistência"}
                </button>
              )}
            </>
          ) : (
            <div className="w-full bg-success/15 border border-success/20 py-2.5 rounded-xl flex items-center justify-center gap-2 text-success text-xs font-bold">
              <CheckCircle className="w-4 h-4" />
              Alerta Resolvido
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
