from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict, List, Optional
from ..database import get_db
from ..models import SentinelaFilaAlertas, VwSentinelaCasoCompleto
from .analise import executar_validacao_geografica

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def get_alertas(
    status: Optional[str] = Query(None, description="Filtrar por status: Novo, Em Tratativa, Resolvido"),
    prioridade: Optional[int] = Query(None, description="Filtrar por prioridade: 1, 2, 3"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade do fato"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Retorna os alertas da fila com os detalhes do caso correspondente (cruzamento MVI).
    """
    try:
        # Query base unindo a fila de alertas aos metadados do caso completo
        # Excluindo alertas de DO vazia do IML (que terão card dedicado no dashboard)
        query = db.query(SentinelaFilaAlertas, VwSentinelaCasoCompleto)\
                  .join(VwSentinelaCasoCompleto, SentinelaFilaAlertas.ID_CONTROLE_MORTE == VwSentinelaCasoCompleto.ID_CONTROLE_MORTE)\
                  .filter(SentinelaFilaAlertas.TIPO_ALERTA != "Corpo sem Declaração de Óbito (DO) no IML")
        
        # Filtros dinâmicos
        if status:
            query = query.filter(SentinelaFilaAlertas.STATUS == status)
        if prioridade:
            query = query.filter(SentinelaFilaAlertas.PRIORIDADE == prioridade)
        if cidade:
            query = query.filter(VwSentinelaCasoCompleto.CIDADE_FATO.ilike(f"%{cidade}%"))
            
        # Ordenação por prioridade decrescente (críticos primeiro) e criação
        query = query.order_by(SentinelaFilaAlertas.PRIORIDADE.desc(), SentinelaFilaAlertas.DT_CRIACAO.desc())
        
        # Contagem total
        total = query.count()
        
        # Paginação e execução
        results = query.offset(offset).limit(limit).all()
        
        # Serialização personalizada juntando os campos em um único objeto de dicionário
        alertas = []
        for alerta, caso in results:
            item = {
                # Campos do alerta
                "id_alerta": alerta.ID_ALERTA,
                "id_controle_morte": alerta.ID_CONTROLE_MORTE,
                "nic": alerta.NIC,
                "bo_pc": alerta.BO_PC,
                "cad": alerta.CAD,
                "status_alerta": alerta.STATUS,
                "prioridade": alerta.PRIORIDADE,
                "tipo_alerta": alerta.TIPO_ALERTA,
                "data_criacao": alerta.DT_CRIACAO.isoformat() if alerta.DT_CRIACAO else None,
                
                # Campos do caso
                "subjetividade": caso.SUBJETIVIDADE,
                "tipo_mvi": caso.TIPO_MVI,
                "bairro": caso.BAIRRO_FATO,
                "cidade": caso.CIDADE_FATO,
                "data_hora_fato": caso.DATA_HORA_FATO,
                "instrumento": caso.INSTRUMENTO_UTILIZADO,
                "motivacao": caso.MOTIV_INICIAL,
                "aisp": caso.AISP,
                "risp": caso.RISP,
                "latitude": caso.NR_COOR_LATD,
                "longitude": caso.NR_COOR_LONG,
                
                # Campos complementares dos cruzamentos
                "natureza_daas": caso.NO_NATUREZA_OCORRENCIA,
                "grupo_natureza_daas": caso.DS_GRUPO_NATUREZA,
                "natureza_cad": caso.DS_NATUREZA_ATEND,
                "tipo_morte_iml": caso.TIPO_MORTE,
                "declaracao_obito": caso.NR_DECLARACAO_OBITO,
                "sexo": caso.SEXO,
                "nome_vitima_cm": caso.NOME_VITIMA,
                "nome_vitima_iml": f"IML_VITIMA_{caso.ID_CONTROLE_MORTE}" if caso.NOM_VITIMA_IML else None
            }
            alertas.append(item)
            
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": alertas
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do banco: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
def get_alertas_stats(db: Session = Depends(get_db)):
    """
    Retorna estatísticas consolidadas dos alertas para o Dashboard.
    """
    try:
        # Contagem por status (excluindo DO Vazia)
        status_counts = db.query(SentinelaFilaAlertas.STATUS, func.count(SentinelaFilaAlertas.ID_ALERTA))\
                          .filter(SentinelaFilaAlertas.TIPO_ALERTA != "Corpo sem Declaração de Óbito (DO) no IML")\
                          .group_by(SentinelaFilaAlertas.STATUS).all()
        status_dict = {s[0]: s[1] for s in status_counts}
        
        # Contagem por prioridade (excluindo DO Vazia)
        prioridade_counts = db.query(SentinelaFilaAlertas.PRIORIDADE, func.count(SentinelaFilaAlertas.ID_ALERTA))\
                              .filter(SentinelaFilaAlertas.TIPO_ALERTA != "Corpo sem Declaração de Óbito (DO) no IML")\
                              .group_by(SentinelaFilaAlertas.PRIORIDADE).all()
        prioridade_dict = {p[0]: p[1] for p in prioridade_counts}
        
        # Contagem específica de DOs vazias no IML
        corpos_sem_do = db.query(func.count(SentinelaFilaAlertas.ID_ALERTA))\
                          .filter(SentinelaFilaAlertas.TIPO_ALERTA == "Corpo sem Declaração de Óbito (DO) no IML")\
                          .scalar() or 0
        
        # Contagem por tipo de alerta (excluindo DO Vazia)
        tipo_counts = db.query(SentinelaFilaAlertas.TIPO_ALERTA, func.count(SentinelaFilaAlertas.ID_ALERTA))\
                        .filter(SentinelaFilaAlertas.TIPO_ALERTA != "Corpo sem Declaração de Óbito (DO) no IML")\
                        .group_by(SentinelaFilaAlertas.TIPO_ALERTA)\
                        .order_by(func.count(SentinelaFilaAlertas.TIPO_ALERTA).desc())\
                        .limit(5).all()
        tipos_list = [{"tipo": t[0], "quantidade": t[1]} for t in tipo_counts]
        
        # Métricas gerais de MVI
        mvi_total = db.query(func.count(VwSentinelaCasoCompleto.ID_CONTROLE_MORTE)).filter(VwSentinelaCasoCompleto.EH_MVI == True).scalar()
        
        return {
            "status": {
                "novos": status_dict.get("Novo", 0),
                "em_tratativa": status_dict.get("Em Tratativa", 0),
                "resolvidos": status_dict.get("Resolvido", 0),
                "total": sum(status_dict.values())
            },
            "prioridade": {
                "baixa": prioridade_dict.get(1, 0),
                "media": prioridade_dict.get(2, 0),
                "alta": prioridade_dict.get(3, 0)
            },
            "top_alertas": tipos_list,
            "mvi_total": mvi_total,
            "corpos_sem_do": corpos_sem_do
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao computar estatísticas: {str(e)}"
        )

@router.get("/{alerta_id}", response_model=Dict[str, Any])
def get_alerta_detalhe(alerta_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de um único alerta específico.
    """
    result = db.query(SentinelaFilaAlertas, VwSentinelaCasoCompleto)\
               .join(VwSentinelaCasoCompleto, SentinelaFilaAlertas.ID_CONTROLE_MORTE == VwSentinelaCasoCompleto.ID_CONTROLE_MORTE)\
               .filter(SentinelaFilaAlertas.ID_ALERTA == alerta_id).first()
               
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta com ID {alerta_id} não encontrado."
        )
        
    alerta, caso = result
    geo_val = executar_validacao_geografica(caso, db)
    return {
        "id_alerta": alerta.ID_ALERTA,
        "id_controle_morte": alerta.ID_CONTROLE_MORTE,
        "nic": alerta.NIC,
        "bo_pc": alerta.BO_PC,
        "cad": alerta.CAD,
        "status_alerta": alerta.STATUS,
        "prioridade": alerta.PRIORIDADE,
        "tipo_alerta": alerta.TIPO_ALERTA,
        "data_criacao": alerta.DT_CRIACAO.isoformat() if alerta.DT_CRIACAO else None,
        "data_atualizacao": alerta.DT_ATUALIZACAO.isoformat() if alerta.DT_ATUALIZACAO else None,
        "geo_validacao": geo_val,
        
        "caso": {
            "id_controle_morte": caso.ID_CONTROLE_MORTE,
            "subjetividade": caso.SUBJETIVIDADE,
            "tipo_mvi": caso.TIPO_MVI,
            "bairro": caso.BAIRRO_FATO,
            "cidade": caso.CIDADE_FATO,
            "data_hora_fato": caso.DATA_HORA_FATO,
            "instrumento": caso.INSTRUMENTO_UTILIZADO,
            "motivacao": caso.MOTIV_INICIAL,
            "aisp": caso.AISP,
            "risp": caso.RISP,
            "latitude": caso.NR_COOR_LATD,
            "longitude": caso.NR_COOR_LONG,
            
            "pc_numero_bo": caso.NUM_BO,
            "pc_natureza": caso.NO_NATUREZA_OCORRENCIA,
            "pc_grupo_natureza": caso.DS_GRUPO_NATUREZA,
            
            "pm_id_ocor": caso.ID_OCOR,
            "pm_natureza": caso.DS_NATUREZA_ATEND,
            "pm_grupo_crime": caso.DS_GRUPO_CRIME_ATEND,
            
            "iml_nic": caso.NIC_IML,
            "iml_tipo_morte": caso.TIPO_MORTE,
            "iml_declaracao_obito": caso.NR_DECLARACAO_OBITO,
            "iml_sexo": caso.SEXO,
            "iml_etnia": caso.ETNIA,
            "iml_nascimento": caso.NASCIMENTO,
            "nome_vitima_cm": caso.NOME_VITIMA,
            "nome_vitima_iml": f"IML_VITIMA_{caso.ID_CONTROLE_MORTE}" if caso.NOM_VITIMA_IML else None
        }
    }

@router.post("/{alerta_id}/status", response_model=Dict[str, Any])
def update_alerta_status(alerta_id: int, status_update: Dict[str, str], db: Session = Depends(get_db)):
    """
    Atualiza o status de tratamento de um alerta na fila.
    """
    new_status = status_update.get("status")
    if not new_status or new_status not in ["Novo", "Em Tratativa", "Resolvido"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido. Deve ser 'Novo', 'Em Tratativa' ou 'Resolvido'."
        )
        
    alerta = db.query(SentinelaFilaAlertas).filter(SentinelaFilaAlertas.ID_ALERTA == alerta_id).first()
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta com ID {alerta_id} não encontrado."
        )
        
    try:
        alerta.STATUS = new_status
        db.commit()
        return {
            "message": "Status do alerta atualizado com sucesso.",
            "id_alerta": alerta_id,
            "novo_status": new_status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar no banco: {str(e)}"
        )
