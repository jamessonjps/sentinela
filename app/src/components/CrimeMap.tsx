/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/Card";

// Corrige problemas de ícones padrão do Leaflet no Next.js
const createCustomIcon = (color: string = "blue") => {
  const iconUrl = color === "blue" 
    ? "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png"
    : "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png";
    
  return new L.Icon({
    iconUrl,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
};

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
  latitude?: number;
  longitude?: number;
}

interface CrimeMapProps {
  selectedAlert: Alert | null;
}

// Componente utilitário para mover o foco do mapa suavemente
function MapController({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lng && lat !== 0 && lng !== 0) {
      map.setView([lat, lng], 14, { animate: true });
    }
  }, [lat, lng, map]);
  return null;
}

// Componente para forçar atualização de layout do Leaflet
function MapEffect() {
  const map = useMap();
  useEffect(() => {
    setTimeout(() => {
      map.invalidateSize();
    }, 250);
  }, [map]);
  return null;
}

export default function CrimeMap({ selectedAlert }: CrimeMapProps) {
  const [mounted, setMounted] = useState(false);
  const [otherPoints, setOtherPoints] = useState<Alert[]>([]);

  useEffect(() => {
    setMounted(true);
    
    // Carrega pontos da mancha criminal local
    const fetchOtherPoints = async () => {
      try {
        const API_BASE_URL = window.location.hostname === "localhost" ? "http://localhost:8000" : "";
        const res = await fetch(`${API_BASE_URL}/api/v1/alertas/?limit=40`);
        if (res.ok) {
          const data = await res.json();
          // Filtra ocorrências que tenham coordenadas válidas
          const validPoints = (data.data || []).filter(
            (p: Alert) => p.latitude && p.longitude && p.latitude !== 0 && p.longitude !== 0
          );
          setOtherPoints(validPoints);
        }
      } catch (err) {
        console.error("Erro ao carregar mancha criminal:", err);
      }
    };
    fetchOtherPoints();
  }, []);

  if (!mounted) {
    return (
      <div className="bg-surface border border-border w-full h-full min-h-[280px] flex items-center justify-center rounded-md overflow-hidden relative">
        <div className="w-6 h-6 border-2 border-focus border-t-transparent rounded-full animate-spin z-10"></div>
      </div>
    );
  }

  // Coordenadas centrais de Maceió, Alagoas
  const defaultPosition: [number, number] = [-9.6658, -35.7350];
  
  // Coordenadas do caso selecionado
  const hasValidCoordinates = selectedAlert && 
    selectedAlert.latitude && 
    selectedAlert.longitude && 
    selectedAlert.latitude !== 0 && 
    selectedAlert.longitude !== 0;

  const activePosition: [number, number] = hasValidCoordinates && selectedAlert.latitude && selectedAlert.longitude
    ? [selectedAlert.latitude, selectedAlert.longitude]
    : defaultPosition;

  return (
    <Card 
      title="Mancha Criminal & Geolocalização" 
      className="w-full h-full min-h-[280px] relative flex flex-col p-1"
    >
      <div className="w-full h-full flex-1 rounded-sm overflow-hidden relative border border-border">
        <MapContainer 
          center={defaultPosition} 
          zoom={12} 
          scrollWheelZoom={true} 
          style={{ height: "100%", width: "100%", zIndex: 0 }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          <MapEffect />

          {/* Plota os outros pontos da mancha criminal em vermelho translúcido */}
          {otherPoints.map((pt) => {
            if (selectedAlert && pt.id_alerta === selectedAlert.id_alerta) return null;
            if (!pt.latitude || !pt.longitude) return null;
            return (
              <CircleMarker
                key={pt.id_alerta}
                center={[pt.latitude, pt.longitude]}
                radius={5}
                pathOptions={{
                  color: "var(--color-critical)",
                  fillColor: "var(--color-critical)",
                  fillOpacity: 0.45,
                  weight: 1
                }}
              >
                <Popup>
                  <div className="font-sans text-[#12151C] p-1.5 text-xs">
                    <strong className="block text-[var(--color-critical)] font-bold mb-1">Alerta #{pt.id_alerta}</strong>
                    <p className="m-0 text-[#5C6379] font-medium">{pt.tipo_alerta}</p>
                    <p className="m-0 mt-1 font-semibold">{pt.cidade} - {pt.bairro}</p>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {/* Marcador do Caso Selecionado */}
          {hasValidCoordinates && selectedAlert.latitude && selectedAlert.longitude && (
            <>
              <Marker position={activePosition} icon={createCustomIcon("blue")}>
                <Popup>
                  <div className="font-sans text-[#12151C] p-2 text-xs">
                    <strong className="text-sm font-semibold block text-[var(--color-focus)] mb-1">Caso em Auditoria</strong>
                    <p className="m-0 font-medium">Alerta: {selectedAlert.tipo_alerta}</p>
                    <p className="m-0 mt-1 text-[#5C6379]">Local: {selectedAlert.bairro}, {selectedAlert.cidade}</p>
                    {selectedAlert.cad && (
                      <p className="m-0 mt-1.5 font-mono text-[10px] bg-slate-100 p-1 rounded border">CAD: {selectedAlert.cad}</p>
                    )}
                  </div>
                </Popup>
              </Marker>
              <MapController lat={selectedAlert.latitude} lng={selectedAlert.longitude} />
            </>
          )}
        </MapContainer>
        
        {/* Banner Indicativo de Falha de GPS */}
        {selectedAlert && !hasValidCoordinates && (
          <div 
            className="absolute bottom-4 left-4 right-4 z-[1001] p-3.5 rounded-sm border border-[var(--color-warning)]/30 bg-[var(--color-warning-bg)] flex items-start gap-3"
          >
            <AlertTriangle className="w-5 h-5 text-[var(--color-warning)] shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-paper">Geolocalização Indisponível (Sem GPS)</h4>
              <p className="text-[10px] text-slate mt-0.5 leading-relaxed">
                As coordenadas GPS deste fato constam como nulas ou zeradas (0.0, 0.0) na integração com o CAD da PM. Exibindo centralização padrão em Maceió.
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
