/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
"use client";

import { useEffect, useState } from "react";
import { Search, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DataTable, Column } from "@/components/ui/DataTable";

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
}

interface AlertQueueProps {
  onSelectAlert: (alert: Alert) => void;
  selectedAlertId?: number;
}

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export function AlertQueue({ onSelectAlert, selectedAlertId }: AlertQueueProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statusFilter, setStatusFilter] = useState("Novo");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async (isBackground = false) => {
    if (!isBackground) {
      setLoading(true);
    }
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/alertas/?status=${statusFilter}&limit=100`);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar alertas:", err);
    } finally {
      if (!isBackground) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchAlerts(false);
    
    // Polling silencioso a cada 30 segundos
    const interval = setInterval(() => fetchAlerts(true), 30000);
    return () => clearInterval(interval);
  }, [statusFilter]);


  const filteredAlerts = alerts.filter(alert => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      (alert.tipo_alerta?.toLowerCase().includes(q)) ||
      (alert.cidade?.toLowerCase().includes(q)) ||
      (alert.bairro?.toLowerCase().includes(q)) ||
      (alert.bo_pc?.toLowerCase().includes(q)) ||
      (alert.cad?.toLowerCase().includes(q))
    );
  });

  const columns: Column<Alert>[] = [
    {
      key: "prioridade",
      label: "PRIO",
      sortable: true,
      render: (alert: Alert) => {
        const variant = alert.prioridade >= 3 ? "critical" : alert.prioridade === 2 ? "warning" : "ok";
        const label = alert.prioridade >= 3 ? "Alta" : alert.prioridade === 2 ? "Média" : "Baixa";
        return <Badge variant={variant}>{label}</Badge>;
      },
      className: "w-20"
    },
    {
      key: "tipo_alerta",
      label: "ALERTA",
      sortable: true,
      className: "font-semibold text-paper"
    },
    {
      key: "id_controle_morte",
      label: "ID CM / SUBJETIVIDADE",
      render: (alert: Alert) => (
        <span className="text-slate">
          {alert.id_controle_morte} • {alert.subjetividade}
        </span>
      ),
      className: "hidden md:table-cell"
    },
    {
      key: "cidade",
      label: "CIDADE",
      sortable: true,
      className: "text-slate"
    },
    {
      key: "bo_pc",
      label: "BO PC",
      render: (alert: Alert) => (
        alert.bo_pc && alert.bo_pc !== "NAN" ? (
          <span className="font-mono px-1.5 py-0.5 bg-ink border border-border rounded-sm text-[10px] text-paper">
            {alert.bo_pc}
          </span>
        ) : (
          <span className="text-slate-dim font-mono text-[10px]">—</span>
        )
      )
    }
  ];

  return (
    <Card
      title="Fila de Auditoria"
      action={
        <span className="text-[10px] font-mono px-2 py-0.5 bg-ink border border-border text-focus font-bold rounded-sm uppercase tracking-wider">
          {filteredAlerts.length} alertas
        </span>
      }
      className="w-full h-full min-h-0 flex flex-col"
    >
      {/* Filtros e Busca */}
      <div className="flex flex-col gap-2.5 mb-3 shrink-0">
        {/* Tabs de Status */}
        <div className="grid grid-cols-3 gap-1 bg-ink p-1 rounded-sm border border-border text-xs font-semibold">
          {["Novo", "Em Tratativa", "Resolvido"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`py-1 rounded-sm transition-all cursor-pointer text-[11px] font-medium uppercase tracking-wider ${
                statusFilter === status
                  ? "bg-surface-raised text-paper border border-border"
                  : "text-slate hover:text-paper"
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Busca */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-dim" />
          <input
            type="text"
            placeholder="Buscar por BO, CAD, local..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-ink border border-border pl-9 pr-3 py-1.5 rounded-sm text-xs text-paper placeholder:text-slate-dim focus:outline-none focus:border-focus transition-all"
          />
        </div>
      </div>

      {/* Lista / Tabela */}
      <div className="flex-1 overflow-y-auto custom-scrollbar min-h-0">
        {loading ? (
          <div className="h-40 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-focus border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="h-40 flex flex-col items-center justify-center text-center text-slate">
            <CheckCircle2 className="w-8 h-8 text-[var(--color-ok)] mb-2" />
            <span className="text-xs font-semibold uppercase tracking-wider">Sem divergências</span>
            <span className="text-[10px] text-slate-dim mt-1">Os dados de MVI estão consistentes nesta fila.</span>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredAlerts}
            rowIdKey="id_alerta"
            selectedRowId={selectedAlertId}
            onRowClick={onSelectAlert}
            zebra={true}
          />
        )}
      </div>
    </Card>
  );
}
