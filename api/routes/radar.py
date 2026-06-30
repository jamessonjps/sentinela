"""
SENTINELA — Rotas API do Radar de Ocorrências CAD
=================================================
Endpoints para consulta, filtragem e validação de ocorrências
CVLI-like detectadas no CAD (190 PM) que ainda não possuem
vínculo na base consolidada CONTROLE_MORTE.

⚠️ PROTEÇÃO DE BASE DE DADOS:
  - Todas as queries são READ ONLY nas tabelas fonte
  - Escrita ocorre SOMENTE na tabela SENTINELA_RADAR_CAD (controle do SENTINELA)
  - Cache de estatísticas com TTL para reduzir carga no banco
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..database import get_db
from ..models import SentinelaRadarCAD, VwSentinelaCasoCompleto
import unicodedata

router = APIRouter()

# Cache simples em memória para stats do radar (TTL = 60s)
_stats_cache = {"data": None, "timestamp": None, "ttl_seconds": 60}


def _get_cached_stats():
    """Retorna stats do cache se ainda válido, senão None."""
    if _stats_cache["data"] and _stats_cache["timestamp"]:
        elapsed = (datetime.now() - _stats_cache["timestamp"]).total_seconds()
        if elapsed < _stats_cache["ttl_seconds"]:
            return _stats_cache["data"]
    return None


def _set_cached_stats(data):
    """Atualiza o cache de stats."""
    _stats_cache["data"] = data
    _stats_cache["timestamp"] = datetime.now()


@router.get("/", response_model=Dict[str, Any])
def get_radar_items(
    status_radar: Optional[str] = Query(None, alias="status", description="Filtrar: Novo, Validado, Descartado"),
    prioridade: Optional[int] = Query(None, description="Filtrar por prioridade: 1 (Baixa), 2 (Média), 3 (Alta)"),
    classificacao: Optional[str] = Query(None, description="Filtrar: CVLI_CONFIRMADO, CVLI_PROVAVEL, A_ESCLARECER"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    natureza: Optional[str] = Query(None, description="Busca parcial na natureza do atendimento"),
    turno: Optional[str] = Query(None, description="Filtrar por turno operacional (T1 a T6)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lista ocorrências do Radar CAD com filtros dinâmicos.
    Retorna itens ordenados por prioridade (mais alta primeiro) e data.
    """
    try:
        # Subquery para pegar CADs já presentes no Controle Morte
        excl_subquery = db.query(cast(VwSentinelaCasoCompleto.CAD, Integer)).filter(VwSentinelaCasoCompleto.CAD.isnot(None))
        
        query = db.query(SentinelaRadarCAD)
        
        # Filtros dinâmicos baseados no status do Radar e sua presença no Controle Morte
        if status_radar == "Novo":
            # Ocorrências que estão como Novo no Radar E não possuem vínculo no Controle Morte
            query = query.filter(SentinelaRadarCAD.STATUS_RADAR == "Novo")
            query = query.filter(~SentinelaRadarCAD.ID_OCOR.in_(excl_subquery))
        elif status_radar == "Validado":
            # Ocorrências que estão como Validado no Radar OU já estão vinculadas no Controle Morte
            query = query.filter(
                (SentinelaRadarCAD.STATUS_RADAR == "Validado") |
                (SentinelaRadarCAD.ID_OCOR.in_(excl_subquery))
            )
        elif status_radar == "Descartado":
            # Ocorrências que estão como Descartado no Radar E não possuem vínculo no Controle Morte
            query = query.filter(SentinelaRadarCAD.STATUS_RADAR == "Descartado")
            query = query.filter(~SentinelaRadarCAD.ID_OCOR.in_(excl_subquery))
            
        if prioridade:
            query = query.filter(SentinelaRadarCAD.PRIORIDADE_RADAR == prioridade)
        if classificacao:
            query = query.filter(SentinelaRadarCAD.CLASSIFICACAO_RADAR == classificacao)
        if cidade:
            query = query.filter(SentinelaRadarCAD.CIDADE.ilike(f"%{cidade}%"))
        if natureza:
            query = query.filter(SentinelaRadarCAD.DS_NATUREZA_ATEND.ilike(f"%{natureza}%"))
        if turno:
            query = query.filter(SentinelaRadarCAD.TURNO == turno)
        
        # Ordenação: prioridade DESC, data DESC
        query = query.order_by(
            SentinelaRadarCAD.PRIORIDADE_RADAR.desc(),
            SentinelaRadarCAD.DT_OCOR.desc()
        )
        
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        
        # Obter conjunto de cads do Controle Morte para marcar como 'Validado' serializado
        vinculados_cads = set(
            r[0] for r in db.query(cast(VwSentinelaCasoCompleto.CAD, Integer)).filter(VwSentinelaCasoCompleto.CAD.isnot(None)).all()
        )
        
        items = []
        for r in results:
            is_validado = r.STATUS_RADAR == "Validado" or r.ID_OCOR in vinculados_cads
            items.append({
                "id_radar": r.ID_RADAR,
                "id_ocor": r.ID_OCOR,
                "natureza": r.DS_NATUREZA_ATEND,
                "grupo_crime": r.DS_GRUPO_CRIME_ATEND,
                "data_ocorrencia": r.DT_OCOR,
                "cidade": r.CIDADE,
                "bairro": r.BAIRRO,
                "latitude": r.NR_COOR_LATD,
                "longitude": r.NR_COOR_LONG,
                "tem_gps": r.TEM_GPS,
                "status_cad": r.DS_STATUS,
                "descricao_ocorrencia": r.DS_OCOR,
                "prioridade": r.PRIORIDADE_RADAR,
                "classificacao": r.CLASSIFICACAO_RADAR,
                "nivel": r.NIVEL_RADAR,
                "status_radar": "Validado" if is_validado else r.STATUS_RADAR,
                "turno": r.TURNO,
                "dt_deteccao": r.DT_DETECCAO.isoformat() if r.DT_DETECCAO else None,
                "dt_validacao": r.DT_VALIDACAO.isoformat() if r.DT_VALIDACAO else None,
            })
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": items
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar Radar CAD: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
def get_radar_stats(db: Session = Depends(get_db)):
    """
    Estatísticas consolidadas do Radar CAD.
    Utiliza cache em memória com TTL de 60s para proteger o banco de dados.
    """
    cached = _get_cached_stats()
    if cached:
        return cached
    
    try:
        # Subquery para pegar CADs já presentes no Controle Morte
        excl_subquery = db.query(cast(VwSentinelaCasoCompleto.CAD, Integer)).filter(VwSentinelaCasoCompleto.CAD.isnot(None))
        
        # 1. Total Novos (Fila Ativa)
        novos = db.query(func.count(SentinelaRadarCAD.ID_RADAR))\
                  .filter(SentinelaRadarCAD.STATUS_RADAR == "Novo")\
                  .filter(~SentinelaRadarCAD.ID_OCOR.in_(excl_subquery)).scalar() or 0
                  
        # 2. Total Validados (Vínculo Controle Morte ou status Validado)
        validados = db.query(func.count(SentinelaRadarCAD.ID_RADAR))\
                      .filter(
                          (SentinelaRadarCAD.STATUS_RADAR == "Validado") |
                          (SentinelaRadarCAD.ID_OCOR.in_(excl_subquery))
                      ).scalar() or 0
                      
        # 3. Total Descartados
        descartados = db.query(func.count(SentinelaRadarCAD.ID_RADAR))\
                        .filter(SentinelaRadarCAD.STATUS_RADAR == "Descartado")\
                        .filter(~SentinelaRadarCAD.ID_OCOR.in_(excl_subquery)).scalar() or 0
                        
        total_geral = novos + validados + descartados
        
        # Base query filter para estatísticas da fila ativa (Novos pendentes)
        active_filter = (SentinelaRadarCAD.STATUS_RADAR == "Novo") & (~SentinelaRadarCAD.ID_OCOR.in_(excl_subquery))
        
        # Por prioridade (fila ativa)
        prio_counts = db.query(
            SentinelaRadarCAD.PRIORIDADE_RADAR,
            func.count(SentinelaRadarCAD.ID_RADAR)
        ).filter(active_filter).group_by(SentinelaRadarCAD.PRIORIDADE_RADAR).all()
        prio_dict = {p[0]: p[1] for p in prio_counts}
        
        # Por classificação (fila ativa)
        class_counts = db.query(
            SentinelaRadarCAD.CLASSIFICACAO_RADAR,
            func.count(SentinelaRadarCAD.ID_RADAR)
        ).filter(active_filter).group_by(SentinelaRadarCAD.CLASSIFICACAO_RADAR).all()
        class_dict = {c[0]: c[1] for c in class_counts}
        
        # Top 5 naturezas (fila ativa)
        top_naturezas = db.query(
            SentinelaRadarCAD.DS_NATUREZA_ATEND,
            func.count(SentinelaRadarCAD.ID_RADAR)
        ).filter(active_filter).group_by(SentinelaRadarCAD.DS_NATUREZA_ATEND)\
         .order_by(func.count(SentinelaRadarCAD.ID_RADAR).desc())\
         .limit(5).all()
        
        # Top 5 cidades (fila ativa)
        top_cidades = db.query(
            SentinelaRadarCAD.CIDADE,
            func.count(SentinelaRadarCAD.ID_RADAR)
        ).filter(active_filter).group_by(SentinelaRadarCAD.CIDADE)\
         .order_by(func.count(SentinelaRadarCAD.ID_RADAR).desc())\
         .limit(5).all()
        
        # GPS (fila ativa)
        com_gps = db.query(func.count(SentinelaRadarCAD.ID_RADAR))\
                    .filter(active_filter)\
                    .filter(SentinelaRadarCAD.TEM_GPS == True).scalar() or 0
        
        # Por turno (fila ativa)
        turno_counts = db.query(
            SentinelaRadarCAD.TURNO,
            func.count(SentinelaRadarCAD.ID_RADAR)
        ).filter(active_filter).group_by(SentinelaRadarCAD.TURNO).all()
        turno_dict = {t[0]: t[1] for t in turno_counts}
        
        result = {
            "total": total_geral,
            "status": {
                "novos": novos,
                "validados": validados,
                "descartados": descartados,
            },
            "prioridade": {
                "alta": prio_dict.get(3, 0),
                "media": prio_dict.get(2, 0),
                "baixa": prio_dict.get(1, 0),
            },
            "classificacao": {
                "cvli_confirmado": class_dict.get("CVLI_CONFIRMADO", 0),
                "cvli_provavel": class_dict.get("CVLI_PROVAVEL", 0),
                "a_esclarecer": class_dict.get("A_ESCLARECER", 0),
            },
            "top_naturezas": [{"natureza": t[0], "quantidade": t[1]} for t in top_naturezas],
            "top_cidades": [{"cidade": t[0], "quantidade": t[1]} for t in top_cidades],
            "turnos": {
                "t1": turno_dict.get("T1 (00:00 - 04:00)", 0),
                "t2": turno_dict.get("T2 (04:00 - 08:00)", 0),
                "t3": turno_dict.get("T3 (08:00 - 12:00)", 0),
                "t4": turno_dict.get("T4 (12:00 - 16:00)", 0),
                "t5": turno_dict.get("T5 (16:00 - 20:00)", 0),
                "t6": turno_dict.get("T6 (20:00 - 00:00)", 0),
            },
            "gps": {
                "com_gps": com_gps,
                "sem_gps": novos - com_gps
            }
        }
        
        _set_cached_stats(result)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao computar estatísticas do Radar: {str(e)}"
        )


@router.post("/{radar_id}/validar", response_model=Dict[str, Any])
def validar_radar_item(
    radar_id: int,
    body: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Analista valida ou descarta um item do Radar.
    
    Body JSON esperado:
      {"status": "Validado"} ou {"status": "Descartado"}
    """
    new_status = body.get("status")
    if not new_status or new_status not in ["Novo", "Validado", "Descartado"]:
        raise HTTPException(
            status_code=400,
            detail="Status inválido. Use: 'Novo', 'Validado' ou 'Descartado'."
        )
    
    item = db.query(SentinelaRadarCAD).filter(SentinelaRadarCAD.ID_RADAR == radar_id).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item do Radar com ID {radar_id} não encontrado."
        )
    
    try:
        item.STATUS_RADAR = new_status
        if new_status in ["Validado", "Descartado"]:
            item.DT_VALIDACAO = datetime.now()
        else:
            item.DT_VALIDACAO = None
        
        db.commit()
        
        # Invalida cache de stats
        _stats_cache["data"] = None
        
        return {
            "message": f"Item do Radar atualizado para '{new_status}'.",
            "id_radar": radar_id,
            "id_ocor": item.ID_OCOR,
            "novo_status": new_status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar item do Radar: {str(e)}"
        )


def _normalize_text(text: str) -> str:
    """Remove acentos e padroniza texto para caixa alta."""
    if not text:
        return ""
    text = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


@router.get("/{radar_id}/correlacoes", response_model=List[Dict[str, Any]])
def get_radar_correlations(
    radar_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca no banco (VW_SENTINELA_CASO_COMPLETO) possíveis correlações
    para um determinado item do Radar CAD com base em proximidade temporal e espacial.
    """
    item = db.query(SentinelaRadarCAD).filter(SentinelaRadarCAD.ID_RADAR == radar_id).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item do Radar com ID {radar_id} não encontrado."
        )
    
    # 1. Parsear a data do radar
    try:
        radar_dt = datetime.strptime(item.DT_OCOR[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            # Caso não venha com segundos
            radar_dt = datetime.strptime(item.DT_OCOR[:16], "%Y-%m-%d %H:%M")
        except Exception:
            # Fallback para apenas data
            try:
                radar_dt = datetime.strptime(item.DT_OCOR[:10], "%Y-%m-%d")
            except Exception:
                return []

    radar_cidade_norm = _normalize_text(item.CIDADE)
    radar_bairro_norm = _normalize_text(item.BAIRRO)
    
    # 2. Filtrar candidatos pela mesma cidade para otimizar busca
    candidates = db.query(VwSentinelaCasoCompleto).all()
    
    correlations = []
    for cand in candidates:
        if not cand.DATA_HORA_FATO:
            continue
        
        # Comparar cidade normalizada
        cand_cidade_norm = _normalize_text(cand.CIDADE_FATO)
        if cand_cidade_norm != radar_cidade_norm:
            continue
            
        # Parsear data do candidato
        try:
            cand_dt = datetime.strptime(cand.DATA_HORA_FATO[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                cand_dt = datetime.strptime(cand.DATA_HORA_FATO[:10], "%Y-%m-%d")
            except Exception:
                continue
                
        # Calcular distância temporal em dias
        delta_days = abs((cand_dt - radar_dt).total_seconds()) / 86400.0
        
        # Se for mais de 5 dias, ignora
        if delta_days > 5.0:
            continue
            
        # Calcular pontuação de similaridade
        score = 100.0
        
        # Penalidade por tempo (perde até 60 pontos em 5 dias)
        score -= (delta_days * 12.0)
        
        # Comparação do Bairro
        cand_bairro_norm = _normalize_text(cand.BAIRRO_FATO)
        bairro_match = False
        if radar_bairro_norm and cand_bairro_norm:
            if radar_bairro_norm == cand_bairro_norm:
                score += 30.0
                bairro_match = True
            elif radar_bairro_norm in cand_bairro_norm or cand_bairro_norm in radar_bairro_norm:
                score += 15.0
                bairro_match = True
        
        # Se for muito próximo ou se for o mesmo bairro, adicionamos como correlação
        if score >= 30.0:
            correlations.append({
                "id_controle_morte": cand.ID_CONTROLE_MORTE,
                "subjetividade": cand.SUBJETIVIDADE,
                "tipo_mvi": cand.TIPO_MVI,
                "bo_pc": cand.BO_PC,
                "cad": cand.CAD,
                "nic": cand.NIC,
                "cidade": cand.CIDADE_FATO,
                "bairro": cand.BAIRRO_FATO,
                "data_hora_fato": cand.DATA_HORA_FATO,
                "score": round(score, 1),
                "delta_days": round(delta_days, 1),
                "bairro_match": bairro_match
            })
            
    # Ordenar por maior score
    correlations = sorted(correlations, key=lambda x: x["score"], reverse=True)
    
    return correlations[:5]

