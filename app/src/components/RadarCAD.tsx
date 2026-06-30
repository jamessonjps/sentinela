"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Compass, Search, MapPin, Calendar, Clock, ChevronRight, 
  Check, Trash2, RefreshCw, AlertTriangle, AlertCircle, 
  HelpCircle, ExternalLink, Link2, Sparkles, Filter
} from "lucide-react";

interface RadarCADProps {
  onStatusChanged?: () => void;
}

const API_BASE_URL = typeof window !== "undefined" 
  ? (window.location.hostname === "localhost" ? "http://localhost:8000" : "") 
  : "http://localhost:8000";

export function RadarCAD({ onStatusChanged }: RadarCADProps) {
  const [items, setItems] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("Novo");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [turnoFilter, setTurnoFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [loading, setLoading] = useState(true);
  
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [correlations, setCorrelations] = useState<any[]>([]);
  const [loadingCorrelations, setLoadingCorrelations] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchRadarItems = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE_URL}/api/v1/radar/?status=${statusFilter}&limit=100`;
      if (priorityFilter !== "all") {
        url += `&prioridade=${priorityFilter}`;
      }
      if (turnoFilter !== "all") {
        url += `&turno=${encodeURIComponent(turnoFilter)}`;
      }
      if (cityFilter) {
        url += `&cidade=${encodeURIComponent(cityFilter)}`;
      }
      if (searchQuery) {
        url += `&natureza=${encodeURIComponent(searchQuery)}`;
      }
      
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setItems(data.data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar itens do radar:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCorrelations = async (radarId: number) => {
    setLoadingCorrelations(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/radar/${radarId}/correlacoes`);
      if (res.ok) {
        const data = await res.json();
        setCorrelations(data || []);
      }
    } catch (err) {
      console.error("Erro ao buscar correlações:", err);
    } finally {
      setLoadingCorrelations(false);
    }
  };

  useEffect(() => {
    fetchRadarItems();
    setSelectedItem(null);
    setCorrelations([]);
  }, [statusFilter, priorityFilter, cityFilter, turnoFilter]);

  // Handle search trigger
  const handleSearch = () => {
    fetchRadarItems();
  };

  const handleSelectItem = (item: any) => {
    setSelectedItem(item);
    fetchCorrelations(item.id_radar);
  };

  const handleAction = async (radarId: number, newStatus: "Validado" | "Descartado") => {
    setActionLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/radar/${radarId}/validar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        setItems(prev => prev.filter(i => i.id_radar !== radarId));
        setSelectedItem(null);
        setCorrelations([]);
        if (onStatusChanged) {
          onStatusChanged();
        }
      }
    } catch (err) {
      console.error("Erro ao atualizar item do radar:", err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full min-h-[500px]">
      {/* Coluna de Ocorrências (Listagem e Filtros) */}
      <div className="lg:col-span-7 flex flex-col gap-4 h-full">
        <div className="glass-card p-5 rounded-2xl flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Compass className="text-primary w-5 h-5 animate-pulse" />
              Radar de Ocorrências (190 PM)
            </h2>
            <span className="bg-primary/10 text-primary text-xs px-2.5 py-1 rounded-full font-bold border border-primary/20">
              {items.length} detectadas
            </span>
          </div>

          {/* Abas de Status */}
          <div className="grid grid-cols-3 gap-1 bg-black/30 p-1 rounded-xl border border-white/5 text-xs font-semibold">
            {["Novo", "Validado", "Descartado"].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`py-2 rounded-lg transition-all cursor-pointer text-center ${
                  statusFilter === status
                    ? "bg-primary/25 text-white border border-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]"
                    : "text-muted-foreground hover:text-white"
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          {/* Filtros e Busca */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-2 text-xs">
            <div className="relative group md:col-span-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
              <input
                type="text"
                placeholder="Pesquisar por natureza..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="w-full bg-black/20 border border-white/5 pl-9 pr-3 py-2 rounded-xl text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-all"
              />
            </div>
            
            <div className="relative group md:col-span-2">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full bg-black/20 border border-white/5 pl-8 pr-2 py-2 rounded-xl text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-all appearance-none cursor-pointer"
              >
                <option value="all" className="bg-card">Prioridade: Todas</option>
                <option value="3" className="bg-card">Alta</option>
                <option value="2" className="bg-card">Média</option>
                <option value="1" className="bg-card">Baixa</option>
              </select>
            </div>

            <div className="relative group md:col-span-3">
              <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <select
                value={turnoFilter}
                onChange={(e) => setTurnoFilter(e.target.value)}
                className="w-full bg-black/20 border border-white/5 pl-8 pr-2 py-2 rounded-xl text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-all appearance-none cursor-pointer"
              >
                <option value="all" className="bg-card">Turno: Todos</option>
                <option value="T1 (00:00 - 04:00)" className="bg-card">T1 (00:00 - 04:00)</option>
                <option value="T2 (04:00 - 08:00)" className="bg-card">T2 (04:00 - 08:00)</option>
                <option value="T3 (08:00 - 12:00)" className="bg-card">T3 (08:00 - 12:00)</option>
                <option value="T4 (12:00 - 16:00)" className="bg-card">T4 (12:00 - 16:00)</option>
                <option value="T5 (16:00 - 20:00)" className="bg-card">T5 (16:00 - 20:00)</option>
                <option value="T6 (20:00 - 00:00)" className="bg-card">T6 (20:00 - 00:00)</option>
              </select>
            </div>

            <div className="relative group md:col-span-3">
              <input
                type="text"
                placeholder="Filtrar Cidade..."
                value={cityFilter}
                onChange={(e) => setCityFilter(e.target.value)}
                className="w-full bg-black/20 border border-white/5 px-3 py-2 rounded-xl text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-all"
              />
            </div>

            <button
              onClick={handleSearch}
              className="md:col-span-1 glass-button py-2 px-3 rounded-xl flex items-center justify-center text-white cursor-pointer hover:bg-primary/20 hover:border-primary/30"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Lista de Registros */}
        <div className="flex-1 overflow-y-auto scrollbar-hide space-y-2.5 max-h-[550px]">
          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : items.length === 0 ? (
            <div className="glass-card p-10 rounded-2xl flex flex-col items-center justify-center text-center text-muted-foreground">
              <AlertCircle className="w-10 h-10 text-muted-foreground/60 mb-2" />
              <span className="text-sm font-semibold">Nenhuma ocorrência encontrada</span>
              <p className="text-xs mt-1 text-muted-foreground/75">
                Não há registros pendentes com os critérios de filtro selecionados.
              </p>
            </div>
          ) : (
            <AnimatePresence>
              {items.map((item, index) => {
                const isSelected = selectedItem?.id_radar === item.id_radar;
                return (
                  <motion.div
                    key={item.id_radar}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -50 }}
                    transition={{ duration: 0.2, delay: Math.min(index * 0.03, 0.3) }}
                    onClick={() => handleSelectItem(item)}
                    className={`glass-button p-4 rounded-xl flex items-center justify-between group cursor-pointer transition-all duration-300 ${
                      isSelected
                        ? "bg-primary/10 border-primary/50 shadow-[0_0_15px_rgba(59,130,246,0.15)] scale-[1.01]"
                        : "hover:bg-white/5 border-white/5"
                    }`}
                  >
                    <div className="flex items-start gap-4 flex-1 min-w-0">
                      {/* Priority Tag & Level Indicator */}
                      <div className={`w-3 h-3 rounded-full mt-1.5 shrink-0 ${
                        item.prioridade === 3 ? "bg-destructive shadow-[0_0_10px_rgba(239,68,68,0.8)]" :
                        item.prioridade === 2 ? "bg-warning shadow-[0_0_10px_rgba(245,158,11,0.8)]" :
                        "bg-success shadow-[0_0_10px_rgba(16,185,129,0.8)]"
                      }`} />

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
                            item.prioridade === 3 ? "bg-destructive/10 text-destructive border-destructive/20" :
                            item.prioridade === 2 ? "bg-warning/10 text-warning border-warning/20" :
                            "bg-success/10 text-success border-success/20"
                          }`}>
                            {item.prioridade === 3 ? "Prioridade Alta (CVLI)" :
                             item.prioridade === 2 ? "Prioridade Média (Tentativa/Interv)" :
                             "Prioridade Baixa (A Esclarecer)"}
                          </span>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            CAD: #{item.id_ocor}
                          </span>
                        </div>
                        <h3 className="font-bold text-white text-xs truncate group-hover:text-primary transition-colors">
                          {item.natureza}
                        </h3>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          Grupo: {item.grupo_crime || "Não Especificado"}
                        </p>
                        
                        <div className="flex flex-wrap items-center gap-3 text-[10px] text-muted-foreground mt-2">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5 text-primary/70" />
                            {item.cidade} {item.bairro ? `(${item.bairro})` : ""}
                          </span>
                          <span className="flex items-center gap-1 font-mono">
                            <Calendar className="w-3.5 h-3.5 text-primary/70" />
                            {item.data_ocorrencia}
                          </span>
                          <span className="flex items-center gap-1 font-mono">
                            <Clock className="w-3.5 h-3.5 text-primary/70" />
                            {item.turno ? item.turno.split(" ")[0] : "T1"}
                          </span>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className={`w-5 h-5 text-muted-foreground transition-all duration-300 ${
                      isSelected ? "translate-x-1 text-primary" : "group-hover:translate-x-1 group-hover:text-white"
                    }`} />
                  </motion.div>
                );
              })}
            </AnimatePresence>
          )}
        </div>
      </div>

      {/* Coluna de Detalhe e Correlações */}
      <div className="lg:col-span-5 h-full">
        {selectedItem ? (
          <div className="glass-card p-5 rounded-2xl flex flex-col gap-5 h-full min-h-[500px]">
            {/* Header Detalhe */}
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[9px] uppercase tracking-wider text-muted-foreground font-mono bg-white/5 border border-white/5 px-2 py-0.5 rounded">
                  Radar CAD
                </span>
                <span className={`text-[9px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${
                  selectedItem.status_radar === "Novo" ? "bg-primary/10 text-primary border-primary/20 animate-pulse" :
                  selectedItem.status_radar === "Validado" ? "bg-success/10 text-success border-success/20" :
                  "bg-destructive/10 text-destructive border-destructive/20"
                }`}>
                  {selectedItem.status_radar}
                </span>
              </div>
              <h2 className="text-sm font-bold text-white mt-2 leading-tight">
                {selectedItem.natureza}
              </h2>
              <p className="text-[10px] text-muted-foreground mt-1">
                Identificado no Radar em {new Date(selectedItem.dt_deteccao).toLocaleString("pt-BR")}
              </p>
            </div>

            {/* Ficha Ocorrência */}
            <div className="bg-black/25 rounded-xl border border-white/5 p-4 text-xs space-y-2.5">
              <h3 className="font-bold text-white text-[10px] uppercase tracking-wider text-primary/80">Dados da PM (190)</h3>
              
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <span className="text-muted-foreground block">ID Ocorrência CAD</span>
                  <span className="text-white font-mono">#{selectedItem.id_ocor}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Status CAD</span>
                  <span className="text-white">{selectedItem.status_cad || "Finalizada"}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Turno Operacional</span>
                  <span className="text-white font-bold text-primary">{selectedItem.turno || "T1 (00:00 - 04:00)"}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Coordenadas GPS</span>
                  <span className="text-white font-mono">
                    {selectedItem.tem_gps 
                      ? `${selectedItem.latitude}, ${selectedItem.longitude}` 
                      : "Sem GPS cadastrado"}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-muted-foreground block">Localidade</span>
                  <span className="text-white">{selectedItem.cidade} / {selectedItem.bairro || "Bairro não informado"}</span>
                </div>
                <div className="col-span-2 bg-black/40 border border-white/5 p-3 rounded-lg mt-1">
                  <span className="text-primary/95 font-bold block mb-1">Histórico/Relato do Despachante:</span>
                  <p className="text-[10px] text-white/90 leading-relaxed max-h-32 overflow-y-auto italic whitespace-pre-wrap select-text">
                    {selectedItem.descricao_ocorrencia || "Nenhuma descrição detalhada disponível."}
                  </p>
                </div>
              </div>
            </div>

            {/* Correlações Inteligentes */}
            <div className="flex-1 flex flex-col gap-3 min-h-[220px]">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-white text-[10px] uppercase tracking-wider flex items-center gap-1.5 text-primary/80">
                  <Sparkles className="w-3.5 h-3.5 text-primary animate-pulse" />
                  Cruzamentos Inteligentes
                </h3>
                <span className="text-[9px] text-muted-foreground">Gold Standard MVI</span>
              </div>

              <div className="flex-1 overflow-y-auto scrollbar-hide space-y-2 pr-1">
                {loadingCorrelations ? (
                  <div className="h-32 flex items-center justify-center">
                    <RefreshCw className="w-6 h-6 text-primary animate-spin" />
                  </div>
                ) : correlations.length === 0 ? (
                  <div className="bg-success/5 border border-success/15 rounded-xl p-4 text-center text-success flex flex-col items-center justify-center">
                    <Check className="w-6 h-6 mb-1 text-success" />
                    <span className="text-[11px] font-bold">Nenhuma correlação encontrada</span>
                    <p className="text-[9px] text-muted-foreground mt-1 max-w-[200px]">
                      Nenhum caso de MVI na base consolidada tem similaridade de local/data. Isso indica uma forte suspeita de **Subnotificação** ou **Atraso de Registro**!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-[9px] text-muted-foreground mb-1 leading-relaxed">
                      Possíveis duplicidades/casos correlatos na base do CHENEAC (ordenados por similaridade):
                    </p>
                    {correlations.map((corr) => (
                      <div 
                        key={corr.id_controle_morte}
                        className="bg-white/5 border border-white/5 hover:border-white/10 rounded-xl p-3 flex flex-col gap-2 transition-all"
                      >
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="text-white font-bold flex items-center gap-1">
                            <Link2 className="w-3 h-3 text-primary" />
                            Mestra #{corr.id_controle_morte}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full font-bold text-[8px] ${
                            corr.score > 80 ? "bg-destructive/15 text-destructive" :
                            corr.score > 50 ? "bg-warning/15 text-warning" :
                            "bg-success/15 text-success"
                          }`}>
                            Similaridade: {corr.score}%
                          </span>
                        </div>

                        <p className="text-[10px] text-white/95 font-medium leading-tight">
                          {corr.subjetividade} • {corr.tipo_mvi || "MVI"}
                        </p>

                        <div className="grid grid-cols-2 gap-1.5 text-[9px] text-muted-foreground border-t border-white/5 pt-2">
                          <div>
                            <span>Cidade/Bairro</span>
                            <span className="text-white block truncate">{corr.cidade} / {corr.bairro || "N/I"}</span>
                          </div>
                          <div>
                            <span>Data do Fato</span>
                            <span className="text-white block truncate">{corr.data_hora_fato}</span>
                          </div>
                        </div>

                        <div className="text-[8px] bg-black/20 p-1.5 rounded flex items-center gap-2 justify-between mt-1 text-muted-foreground">
                          <span>Distância Temporal: {corr.delta_days} dias</span>
                          <span>Bairro idêntico: {corr.bairro_match ? "SIM" : "NÃO"}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Botões de Ação */}
            {selectedItem.status_radar === "Novo" && (
              <div className="flex gap-2.5 pt-4 border-t border-white/5 mt-auto">
                <button
                  disabled={actionLoading}
                  onClick={() => handleAction(selectedItem.id_radar, "Descartado")}
                  className="flex-1 bg-destructive/10 hover:bg-destructive/20 text-destructive text-xs font-bold py-2.5 px-3 rounded-xl border border-destructive/20 flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  <Trash2 className="w-4 h-4" />
                  Descartar Sinal
                </button>
                
                <button
                  disabled={actionLoading}
                  onClick={() => handleAction(selectedItem.id_radar, "Validado")}
                  className="flex-1 bg-success/20 hover:bg-success/30 text-success text-xs font-bold py-2.5 px-3 rounded-xl border border-success/30 flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  <Check className="w-4 h-4" />
                  Validar / Investigar
                </button>
              </div>
            )}

            {selectedItem.status_radar !== "Novo" && (
              <div className={`mt-auto p-3.5 rounded-xl border text-center text-xs font-bold ${
                selectedItem.status_radar === "Validado" 
                  ? "bg-success/15 border-success/20 text-success" 
                  : "bg-destructive/15 border-destructive/20 text-destructive"
              }`}>
                Ocorrência classificada como **{selectedItem.status_radar}**
                {selectedItem.dt_validacao && (
                  <span className="block text-[9px] font-normal text-muted-foreground mt-1">
                    em {new Date(selectedItem.dt_validacao).toLocaleString("pt-BR")}
                  </span>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card p-6 rounded-2xl flex flex-col items-center justify-center text-center text-muted-foreground h-full min-h-[500px]">
            <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-muted-foreground mb-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
              <Compass className="w-8 h-8 opacity-40 animate-spin-slow" />
            </div>
            <h3 className="text-sm font-bold text-white">Nenhuma Ocorrência Selecionada</h3>
            <p className="text-xs text-muted-foreground max-w-[240px] mt-2 leading-relaxed">
              Clique em um registro do Radar CAD para inspecionar seus detalhes e calcular possíveis correlações na base de Controle de Morte.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
