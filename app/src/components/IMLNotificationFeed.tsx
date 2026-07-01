/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from "react";
import { Bell, CheckCircle2, Info } from "lucide-react";
import { Card } from "./ui/Card";

const API_BASE_URL = typeof window !== "undefined"
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "")
  : "http://localhost:8000";

interface IMLNotification {
  id_notificacao: number;
  nic: string;
  nome_vitima?: string;
  status_iml?: string;
  tipo_mensagem: string;
  lido: number;
  data_evento?: string;
}

interface IMLNotificationFeedProps {
  onRefreshTrigger: number;
  onNotificationRead: () => void;
}

export function IMLNotificationFeed({ onRefreshTrigger, onNotificationRead }: IMLNotificationFeedProps) {
  const [notifications, setNotifications] = useState<IMLNotification[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/notificacoes-iml?lido=0`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar notificações do IML:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notifId: number) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analise/notificacoes-iml/${notifId}/lido`, {
        method: "POST"
      });
      if (res.ok) {
        fetchNotifications();
        onNotificationRead();
      }
    } catch (err) {
      console.error("Erro ao marcar notificação como lida:", err);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [onRefreshTrigger]);

  return (
    <Card className="flex flex-col h-[280px] bg-surface border border-border rounded-md overflow-hidden shrink-0">
      <div className="px-4 py-2.5 border-b border-border bg-surface-raised flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-focus" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-paper font-display">
            Notificações da Base IML (SGOU)
          </h2>
          {notifications.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-critical animate-pulse"></span>
          )}
        </div>
      </div>

      <div className="flex-grow overflow-y-auto custom-scrollbar p-2 space-y-2">
        {loading && notifications.length === 0 ? (
          <div className="h-full flex items-center justify-center text-[10px] text-slate-dim font-mono">
            Carregando notificações IML...
          </div>
        ) : notifications.length === 0 ? (
          <div className="h-full flex items-center justify-center text-[10px] text-slate-dim font-mono text-center px-4">
            Sem novas alterações na base do IML pendentes de verificação.
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id_notificacao}
              className="p-2.5 rounded-sm border border-border bg-ink hover:bg-surface-raised transition-colors flex items-start justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-warning shrink-0" />
                  <span className="text-[10px] font-bold text-paper uppercase tracking-tight leading-none">
                    {n.tipo_mensagem}
                  </span>
                </div>
                <div className="text-[10px] font-mono text-slate leading-tight">
                  Vítima: <span className="text-paper font-semibold">{n.nome_vitima || "Sem Nome"}</span>
                  <br />
                  NIC: <span className="text-focus">{n.nic}</span> | Status: {n.status_iml || "Entrada"}
                </div>
                {n.data_evento && (
                  <span className="text-[8px] text-slate-dim font-mono block mt-1">
                    Detectado em {new Date(n.data_evento).toLocaleTimeString()}
                  </span>
                )}
              </div>

              <button
                onClick={() => handleMarkAsRead(n.id_notificacao)}
                title="Marcar como resolvido"
                className="p-1 rounded-sm text-slate-dim hover:text-ok hover:bg-surface transition-all cursor-pointer shrink-0"
              >
                <CheckCircle2 className="w-4.5 h-4.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
