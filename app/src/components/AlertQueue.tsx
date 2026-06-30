"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Clock, MapPin, ChevronRight, Search, Eye, CheckCircle2, ShieldAlert } from "lucide-react";

interface AlertQueueProps {
  onSelectAlert: (alert: any) => void;
  selectedAlertId?: number;
}

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export function AlertQueue({ onSelectAlert, selectedAlertId }: AlertQueueProps) {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("Novo");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/alertas/?status=${statusFilter}&limit=100`);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar alertas:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // Configura um intervalo para atualizar a fila a cada 30 segundos
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  // Filtro local adicional de busca (por BO, CAD, Cidade ou Bairro)
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

  return (
    <div className="glass-card p-3.5 w-full h-full min-h-0 flex flex-col rounded-xl overflow-hidden">
      {/* Header com Filtros Principais */}
      <div className="flex flex-col gap-2.5 mb-3 shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-1.5">
            <ShieldAlert className="text-primary w-4 h-4 animate-pulse" />
            Fila de Auditoria
          </h2>
          <span className="bg-primary/10 text-primary text-xs px-2.5 py-1 rounded-full font-bold border border-primary/20">
            {filteredAlerts.length} alertas
          </span>
        </div>

        {/* Tabs de Status */}
        <div className="grid grid-cols-3 gap-1 bg-black/30 p-1 rounded-xl border border-white/5 text-xs font-semibold">
          {["Novo", "Em Tratativa", "Resolvido"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`py-1.5 rounded-md transition-all cursor-pointer ${
                statusFilter === status
                  ? "bg-primary/20 text-white border border-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]"
                  : "text-muted-foreground hover:text-white"
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Input de Busca */}
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input
            type="text"
            placeholder="Buscar por BO, CAD, local..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/20 border border-white/5 pl-9 pr-3 py-1.5 rounded-lg text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-all"
          />
        </div>
      </div>

      {/* Lista de Alertas */}
      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1 min-h-0">
        {loading ? (
          <div className="h-40 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="h-40 flex flex-col items-center justify-center text-center text-muted-foreground">
            <CheckCircle2 className="w-8 h-8 text-success/60 mb-2" />
            <span className="text-sm font-semibold">Nenhum alerta pendente</span>
            <span className="text-[10px] mt-1">Ótimo! Os dados de MVI estão consistentes.</span>
          </div>
        ) : (
          <AnimatePresence>
            {filteredAlerts.map((alert, index) => {
              const isSelected = selectedAlertId === alert.id_alerta;
              return (
                <motion.div
                  key={alert.id_alerta}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.2, delay: Math.min(index * 0.05, 0.5) }}
                  onClick={() => onSelectAlert(alert)}
                  className={`glass-button p-2.5 rounded-lg flex items-center justify-between group cursor-pointer transition-all duration-300 ${
                    isSelected
                      ? "bg-primary/10 border-primary/50 shadow-[0_0_15px_rgba(59,130,246,0.15)] scale-[1.01]"
                      : "hover:bg-white/5 border-white/5"
                  }`}
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    {/* Indicador de Prioridade */}
                    <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${
                      alert.prioridade >= 3 ? "bg-destructive shadow-[0_0_10px_rgba(239,68,68,0.8)]" :
                      alert.prioridade === 2 ? "bg-warning shadow-[0_0_10px_rgba(245,158,11,0.8)]" :
                      "bg-success shadow-[0_0_10px_rgba(16,185,129,0.8)]"
                    }`} />
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white text-xs truncate group-hover:text-primary transition-colors">
                        {alert.tipo_alerta}
                      </h3>
                      
                      {/* Sub-informações */}
                      <p className="text-[10px] text-muted-foreground mt-1 truncate">
                        ID: {alert.id_controle_morte} • {alert.subjetividade}
                      </p>
                      
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground mt-1.5">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-primary/75" />
                          {alert.cidade}
                        </span>
                        {alert.bo_pc && alert.bo_pc !== "NAN" && (
                          <span className="font-mono bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                            BO: {alert.bo_pc}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className={`w-4 h-4 text-muted-foreground transition-all duration-300 ${
                    isSelected ? "translate-x-1 text-primary" : "group-hover:translate-x-1 group-hover:text-white"
                  }`} />
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
