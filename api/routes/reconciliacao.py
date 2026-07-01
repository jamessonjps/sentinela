from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..database import get_db
from ..models import SentinelaReconciliacaoLog, VwSentinelaCasoCompleto

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def get_divergencias(
    fonte: Optional[str] = Query(None, description="Filtrar por fonte: IML, CAD, PPE"),
    status_reconc: Optional[str] = Query("Pendente", alias="status", description="Filtrar por status: Pendente, Confirmado, Ignorado"),
    campo: Optional[str] = Query(None, description="Filtrar por nome de campo"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Retorna os logs de reconciliação/divergências com os detalhes do caso associado.
    """
    try:
        # Base query joining reconciliation log with case details
        query = db.query(SentinelaReconciliacaoLog, VwSentinelaCasoCompleto)\
                  .join(VwSentinelaCasoCompleto, SentinelaReconciliacaoLog.ID_CONTROLE_MORTE == VwSentinelaCasoCompleto.ID_CONTROLE_MORTE)
                  
        # Filtros dinâmicos
        if status_reconc:
            query = query.filter(SentinelaReconciliacaoLog.STATUS == status_reconc)
        if fonte:
            query = query.filter(SentinelaReconciliacaoLog.FONTE == fonte)
        if campo:
            query = query.filter(SentinelaReconciliacaoLog.CAMPO_MESTRA == campo)
            
        # Ordenação por score de similaridade decrescente e data de detecção
        query = query.order_by(
            SentinelaReconciliacaoLog.SCORE_SIMILARIDADE.desc(),
            SentinelaReconciliacaoLog.DT_DETECCAO.desc()
        )
        
        # Contagem total
        total = query.count()
        
        # Paginação e execução
        results = query.offset(offset).limit(limit).all()
        
        # Serialização personalizada juntando dados do log e do caso
        data = []
        for log, caso in results:
            item = {
                # Campos do log de reconciliação
                "id_reconciliacao": log.ID_RECONCILIACAO,
                "id_controle_morte": log.ID_CONTROLE_MORTE,
                "fonte": log.FONTE,
                "campo_mestra": log.CAMPO_MESTRA,
                "valor_mestra": log.VALOR_MESTRA,
                "campo_fonte": log.CAMPO_FONTE,
                "valor_fonte": log.VALOR_FONTE,
                "tipo_divergencia": log.TIPO_DIVERGENCIA,
                "score_similaridade": log.SCORE_SIMILARIDADE,
                "status_reconc": log.STATUS,
                "dt_deteccao": log.DT_DETECCAO.isoformat() if log.DT_DETECCAO else None,
                "dt_resolucao": log.DT_RESOLUCAO.isoformat() if log.DT_RESOLUCAO else None,
                
                # Contexto da Controle Morte para o Analista
                "caso": {
                    "nic": caso.NIC,
                    "bo_pc": caso.BO_PC,
                    "cad": caso.CAD,
                    "subjetividade": caso.SUBJETIVIDADE,
                    "cidade": caso.CIDADE_FATO,
                    "bairro": caso.BAIRRO_FATO,
                    "data_hora_fato": caso.DATA_HORA_FATO,
                    "nome_vitima": caso.NOME_VITIMA,
                    
                    # Campos específicos da PC (para visualização side-by-side)
                    "pc_natureza": caso.NO_NATUREZA_OCORRENCIA,
                    "pc_bairro": caso.ED_BAIRRO,
                    "pc_cidade": caso.NO_MUNICIPIO,
                    "pc_data": caso.DT_OCORRENCIA,
                    
                    # Coordenadas do CAD
                    "cad_latitude": caso.NR_COOR_LATD,
                    "cad_longitude": caso.NR_COOR_LONG
                }
            }
            data.append(item)
            
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter logs de reconciliação: {str(e)}"
        )

@router.post("/{reconc_id}/resolver", response_model=Dict[str, Any])
def resolver_divergencia(
    reconc_id: int,
    body: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Atualiza o status de resolução de uma divergência de reconciliação (Confirmado ou Ignorado).
    """
    new_status = body.get("status")
    if not new_status or new_status not in ["Pendente", "Confirmado", "Ignorado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido. Deve ser 'Pendente', 'Confirmado' ou 'Ignorado'."
        )
        
    log = db.query(SentinelaReconciliacaoLog).filter(
        SentinelaReconciliacaoLog.ID_RECONCILIACAO == reconc_id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log de reconciliação com ID {reconc_id} não encontrado."
        )
        
    try:
        log.STATUS = new_status
        if new_status in ["Confirmado", "Ignorado"]:
            log.DT_RESOLUCAO = datetime.now()
        else:
            log.DT_RESOLUCAO = None
            
        db.commit()
        return {
            "message": "Resolução registrada com sucesso.",
            "id_reconciliacao": reconc_id,
            "status": new_status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar resolução no banco: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
def get_reconciliacao_stats(db: Session = Depends(get_db)):
    """
    Estatísticas agregadas de divergências para o Painel.
    """
    try:
        # Contagem por Status
        status_counts = db.query(SentinelaReconciliacaoLog.STATUS, func.count(SentinelaReconciliacaoLog.ID_RECONCILIACAO))\
                          .group_by(SentinelaReconciliacaoLog.STATUS).all()
        status_dict = {s[0]: s[1] for s in status_counts}
        
        # Contagem por Fonte
        fonte_counts = db.query(SentinelaReconciliacaoLog.FONTE, func.count(SentinelaReconciliacaoLog.ID_RECONCILIACAO))\
                         .group_by(SentinelaReconciliacaoLog.FONTE).all()
        fonte_dict = {f[0]: f[1] for f in fonte_counts}
        
        # Distribuição de tipos de divergências pendentes
        tipo_counts = db.query(SentinelaReconciliacaoLog.TIPO_DIVERGENCIA, func.count(SentinelaReconciliacaoLog.ID_RECONCILIACAO))\
                        .filter(SentinelaReconciliacaoLog.STATUS == "Pendente")\
                        .group_by(SentinelaReconciliacaoLog.TIPO_DIVERGENCIA).all()
        tipos_list = [{"tipo": t[0], "quantidade": t[1]} for t in tipo_counts]
        
        # Campos mais divergentes
        campos_counts = db.query(SentinelaReconciliacaoLog.CAMPO_MESTRA, func.count(SentinelaReconciliacaoLog.ID_RECONCILIACAO))\
                          .filter(SentinelaReconciliacaoLog.STATUS == "Pendente")\
                          .group_by(SentinelaReconciliacaoLog.CAMPO_MESTRA)\
                          .order_by(func.count(SentinelaReconciliacaoLog.CAMPO_MESTRA).desc())\
                          .limit(5).all()
        campos_list = [{"campo": c[0], "quantidade": c[1]} for c in campos_counts]
        
        return {
            "status": {
                "pendentes": status_dict.get("Pendente", 0),
                "confirmados": status_dict.get("Confirmado", 0),
                "ignorados": status_dict.get("Ignorado", 0),
                "total": sum(status_dict.values())
            },
            "fontes": {
                "iml": fonte_dict.get("IML", 0),
                "cad": fonte_dict.get("CAD", 0),
                "ppe": fonte_dict.get("PPE", 0)
            },
            "top_divergencias_pendentes": tipos_list,
            "campos_mais_divergentes": campos_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao computar estatísticas de reconciliação: {str(e)}"
        )
