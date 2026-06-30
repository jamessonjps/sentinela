"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { motion, AnimatePresence } from "framer-motion";
import { MapPin, AlertTriangle, ShieldAlert } from "lucide-react";

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

interface CrimeMapProps {
  selectedAlert: any;
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
  const [otherPoints, setOtherPoints] = useState<any[]>([]);

  useEffect(() => {
    setMounted(true);
    
    // Carrega pontos adicionais da mancha criminal local para preencher o mapa de forma analítica
    const fetchOtherPoints = async () => {
      try {
        const API_BASE_URL = window.location.hostname === "localhost" ? "http://localhost:8000" : "";
        const res = await fetch(`${API_BASE_URL}/api/v1/alertas/?limit=40`);
        if (res.ok) {
          const data = await res.json();
          // Filtra ocorrências que tenham coordenadas válidas
          const validPoints = (data.data || []).filter(
            (p: any) => p.latitude && p.longitude && p.latitude !== 0 && p.longitude !== 0
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
      <div className="glass-panel w-full h-full min-h-[450px] flex items-center justify-center rounded-2xl overflow-hidden relative">
        <div className="absolute inset-0 bg-background/50 animate-pulse"></div>
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin z-10"></div>
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

  const activePosition: [number, number] = hasValidCoordinates
    ? [selectedAlert.latitude, selectedAlert.longitude]
    : defaultPosition;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-panel w-full h-full min-h-[450px] rounded-2xl overflow-hidden relative z-0 p-1 flex flex-col"
    >
      <div className="w-full h-full flex-1 rounded-xl overflow-hidden relative">
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
            // Evita duplicar o ponto selecionado
            if (selectedAlert && pt.id_alerta === selectedAlert.id_alerta) return null;
            return (
              <CircleMarker
                key={pt.id_alerta}
                center={[pt.latitude, pt.longitude]}
                radius={6}
                pathOptions={{
                  color: "#ef4444",
                  fillColor: "#ef4444",
                  fillOpacity: 0.35,
                  weight: 1
                }}
              >
                <Popup>
                  <div className="font-sans text-[#171717] p-1.5 text-xs">
                    <strong className="block text-red-600 font-bold mb-1">Mancha: Alerta #{pt.id_alerta}</strong>
                    <p className="m-0 text-muted-foreground">{pt.tipo_alerta}</p>
                    <p className="m-0 mt-1 font-semibold">{pt.cidade} - {pt.bairro}</p>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {/* Marcador do Caso Selecionado */}
          {hasValidCoordinates && (
            <>
              <Marker position={activePosition} icon={createCustomIcon("blue")}>
                <Popup className="custom-popup">
                  <div className="font-sans text-[#171717] p-2 text-xs">
                    <strong className="text-sm font-semibold block text-blue-600 mb-1">Caso em Auditoria</strong>
                    <p className="m-0 font-medium">Alerta: {selectedAlert.tipo_alerta}</p>
                    <p className="m-0 mt-1 text-muted-foreground">Local: {selectedAlert.bairro}, {selectedAlert.cidade}</p>
                    {selectedAlert.cad && (
                      <p className="m-0 mt-1.5 font-mono text-[10px] bg-slate-100 p-1 rounded">CAD: {selectedAlert.cad}</p>
                    )}
                  </div>
                </Popup>
              </Marker>
              <MapController lat={selectedAlert.latitude} lng={selectedAlert.longitude} />
            </>
          )}
        </MapContainer>
        
        {/* Sombra interna para integrar o mapa ao glassmorphism */}
        <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_40px_rgba(10,15,25,0.9)] z-[1000]" />
        
        {/* Banner Indicativo de Falha de GPS */}
        <AnimatePresence>
          {selectedAlert && !hasValidCoordinates && (
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 15 }}
              className="absolute bottom-4 left-4 right-4 z-[1001] glass p-3.5 rounded-xl border border-warning/30 bg-warning/5 backdrop-blur-md flex items-start gap-3"
            >
              <AlertTriangle className="w-5 h-5 text-warning shrink-0 mt-0.5 animate-bounce" />
              <div>
                <h4 className="text-xs font-bold text-white">Geolocalização Indisponível (Qualidade do Dado)</h4>
                <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">
                  As coordenadas GPS deste fato constam como nulas ou zeradas (0.0, 0.0) na integração com o CAD/Quimera da PM. Exibindo centralização padrão em Maceió.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
