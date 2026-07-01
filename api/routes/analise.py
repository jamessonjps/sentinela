from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import math

from ..database import get_db
from ..models import (
    VwSentinelaCasoCompleto, 
    SentinelaFilaAlertas, 
    SentinelaReconciliacaoLog,
    SentinelaEvolucaoPendente,
    SentinelaNotificacaoIML,
    SentinelaGeoBairro,
    SentinelaEstabelecimentoSaude
)
from agents.reconciliation_agent.orchestrator import ReconciliationOrchestrator
from agents.reconciliation_agent.field_rules import match_names, jaro_winkler_score, parse_date, normalize_text

router = APIRouter()

def calcular_distancia_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância em metros entre dois pontos geográficos usando Haversine.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0
    R = 6371000.0  # Raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def executar_validacao_geografica(caso, db: Session) -> dict:
    """
    Executa a validação geográfica de um caso contra centróides de bairros,
    locais de interesse (hospitais, UPAs, presídios) e procedência da tabela IML.
    """
    lat = caso.NR_COOR_LATD or (float(caso.LATITUDE) if caso.LATITUDE else None)
    lon = caso.NR_COOR_LONG or (float(caso.LONGITUDE) if caso.LONGITUDE else None)
    
    result = {
        "alerta_geografico": False,
        "bairro_divergente": False,
        "fato_em_hospital": False,
        "hospital_nome": None,
        "fato_em_presidio": False,
        "presidio_nome": None,
        "procedencia_prisional": False,
        "orgao_procedencia": None,
        "bairro_cadastrado": caso.BAIRRO_FATO,
        "bairro_gps_centro": None,
        "gps_latitude": lat,
        "gps_longitude": lon
    }
    
    # 1. Analisa procedência do IML para capturar óbitos no sistema prisional
    terms = ["presidio", "penitenciaria", "prisional", "baldomero", "agreste", "cyridiao", "santa luzia"]
    for field in [caso.ORGAO_REQUERENTE, caso.REQUERENTE_OUTROS]:
        if field:
            val_lower = str(field).lower()
            if any(t in val_lower for t in terms):
                result["alerta_geografico"] = True
                result["procedencia_prisional"] = True
                result["orgao_procedencia"] = str(field)
                break
                
    if lat is None or lon is None:
        return result
        
    # 2. Verifica se a coordenada caiu dentro de um local de interesse (hospital/UPA ou presídio)
    locais_interesse = db.query(SentinelaEstabelecimentoSaude).all()
    for loc in locais_interesse:
        dist = calcular_distancia_metros(lat, lon, loc.LATITUDE, loc.LONGITUDE)
        if dist <= loc.RAIO_METROS:
            result["alerta_geografico"] = True
            if getattr(loc, "TIPO", "SAUDE") == "PRESIDIO":
                result["fato_em_presidio"] = True
                result["presidio_nome"] = loc.NOME
            else:
                result["fato_em_hospital"] = True
                result["hospital_nome"] = loc.NOME
            break
            
    # 3. Verifica se a coordenada caiu fora da área de abrangência do bairro cadastrado
    if caso.BAIRRO_FATO and caso.CIDADE_FATO:
        bairro_geo = db.query(SentinelaGeoBairro).filter(
            SentinelaGeoBairro.NOME_BAIRRO.ilike(f"%{caso.BAIRRO_FATO}%"),
            SentinelaGeoBairro.NOME_MUNICIPIO.ilike(f"%{caso.CIDADE_FATO}%")
        ).first()
        
        if bairro_geo:
            result["bairro_gps_centro"] = [bairro_geo.CENTRO_LATITUDE, bairro_geo.CENTRO_LONGITUDE]
            dist_km = calcular_distancia_metros(lat, lon, bairro_geo.CENTRO_LATITUDE, bairro_geo.CENTRO_LONGITUDE) / 1000.0
            if dist_km > bairro_geo.RAIO_KM:
                result["alerta_geografico"] = True
                result["bairro_divergente"] = True
                
    return result



class DuplicadoRequest(BaseModel):
    data_fato: str
    municipio: str
    bairro: Optional[str] = None
    nome_vitima: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class EvolucaoPropostaRequest(BaseModel):
    id_controle_morte: int
    nic_iml: str
    bo_pc: Optional[str] = None
    motivo: str
    autor: str

class EvolucaoProcessoRequest(BaseModel):
    status: str  # Aprovada ou Rejeitada
    motivo_decisao: Optional[str] = None


@router.get("/watchlist", response_model=Dict[str, Any])
def get_watchlist(db: Session = Depends(get_db)):
    """
    Retorna as tentativas de homicídio ativas monitoradas pelo SENTINELA
    e suas possíveis correspondências com corpos do IML.
    """
    try:
        # Busca todas as tentativas sem NIC vinculado na base mestra
        tentativas = db.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.SUBJETIVIDADE.ilike("%TENTATIVA%"),
            VwSentinelaCasoCompleto.NIC.is_(None)
        ).all()
        
        watchlist_data = []
        
        for tent in tentativas:
            # Verifica se há suspeita de evolução na fila de reconciliação
            reconc_log = db.query(SentinelaReconciliacaoLog).filter_by(
                ID_CONTROLE_MORTE=tent.ID_CONTROLE_MORTE,
                CAMPO_MESTRA="SUBJETIVIDADE",
                STATUS="Pendente"
            ).first()
            
            suspeita = None
            if reconc_log and reconc_log.VALOR_FONTE:
                nic_suspeito = reconc_log.VALOR_FONTE
                # Busca detalhes do corpo correspondente no IML
                corpo = db.query(VwSentinelaCasoCompleto).filter(
                    VwSentinelaCasoCompleto.NIC_IML == nic_suspeito
                ).first()
                
                if corpo:
                    suspeita = {
                        "nic": corpo.NIC_IML,
                        "nome_vitima_iml": corpo.NOM_VITIMA_IML,
                        "data_entrada_iml": corpo.IML_ENTRADA,
                        "tipo_morte": corpo.TIPO_MORTE,
                        "score_similaridade": reconc_log.SCORE_SIMILARIDADE,
                        "bo_pc": corpo.BO_PC
                    }
            
            watchlist_data.append({
                "id_controle_morte": tent.ID_CONTROLE_MORTE,
                "nome_vitima": tent.NOME_VITIMA,
                "data_hora_fato": tent.DATA_HORA_FATO,
                "bairro": tent.BAIRRO_FATO,
                "cidade": tent.CIDADE_FATO,
                "bo_pc": tent.BO_PC,
                "cad": tent.CAD,
                "suspeita_evolucao": suspeita
            })
            
        return {
            "total_watchlist": len(watchlist_data),
            "data": watchlist_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter watchlist: {str(e)}"
        )


@router.post("/reconciliar", response_model=Dict[str, Any])
def disparar_reconciliacao(db: Session = Depends(get_db)):
    """
    Dispara a execução do motor de reconciliação local sob demanda.
    """
    try:
        orch = ReconciliationOrchestrator()
        result = orch.run_reconciliation(db)
        return {
            "message": "Ciclo de reconciliação disparado com sucesso.",
            "resultado": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao rodar orquestrador: {str(e)}"
        )


@router.post("/detectar-duplicados", response_model=Dict[str, Any])
def detectar_duplicados(req: DuplicadoRequest, db: Session = Depends(get_db)):
    """
    Busca no banco ocorrências existentes que correspondam a potenciais duplicados
    com base em similaridade fonética, limites temporais e geográficos.
    """
    try:
        dt_fato = parse_date(req.data_fato)
        if not dt_fato:
            raise HTTPException(
                status_code=400,
                detail="Formato de data de fato inválido."
            )
            
        # Janela temporal de +/- 3 dias
        dt_inicio = dt_fato - timedelta(days=3)
        dt_fim = dt_fato + timedelta(days=3)
        
        # Filtra casos no mesmo município dentro da janela temporal
        casos = db.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.CIDADE_FATO.ilike(f"%{req.municipio}%")
        ).all()
        
        potenciais_duplicados = []
        
        for caso in casos:
            dt_caso = parse_date(caso.DATA_HORA_FATO)
            if not dt_caso or dt_caso < dt_inicio or dt_caso > dt_fim:
                continue
                
            score = 0.0
            detalhes = []
            
            # 1. Correspondência de Nome (Jaro-Winkler)
            if req.nome_vitima and caso.NOME_VITIMA:
                nome_sim = jaro_winkler_score(req.nome_vitima, caso.NOME_VITIMA)
                if nome_sim >= 75.0:
                    score += nome_sim * 0.5  # Peso de 50%
                    detalhes.append(f"Nome semelhante (Score: {nome_sim}%)")
            
            # 2. Correspondência de Bairro
            if req.bairro and caso.BAIRRO_FATO:
                b1 = normalize_text(req.bairro)
                b2 = normalize_text(caso.BAIRRO_FATO)
                if b1 == b2:
                    score += 25.0  # Peso de 25%
                    detalhes.append("Mesmo bairro do fato")
                elif b1 in b2 or b2 in b1:
                    score += 15.0
                    detalhes.append("Bairro do fato aproximado")
                    
            # 3. Correspondência Geográfica (raio de 1km)
            if req.latitude and req.longitude and caso.NR_COOR_LATD and caso.NR_COOR_LONG:
                # Distância usando fórmula de Haversine simples
                lat1, lon1 = math.radians(req.latitude), math.radians(req.longitude)
                lat2, lon2 = math.radians(caso.NR_COOR_LATD), math.radians(caso.NR_COOR_LONG)
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distancia_metros = c * 6371000.0  # Raio da Terra em metros
                
                if distancia_metros <= 500:
                    score += 25.0  # Peso de 25%
                    detalhes.append(f"Geolocalização muito próxima ({round(distancia_metros)}m)")
                elif distancia_metros <= 1500:
                    score += 15.0
                    detalhes.append(f"Geolocalização próxima ({round(distancia_metros)}m)")
            
            if score >= 20.0:  # Piso de similaridade de 20%
                potenciais_duplicados.append({
                    "id_controle_morte": caso.ID_CONTROLE_MORTE,
                    "nome_vitima": caso.NOME_VITIMA,
                    "data_hora_fato": caso.DATA_HORA_FATO,
                    "bairro": caso.BAIRRO_FATO,
                    "cidade": caso.CIDADE_FATO,
                    "bo_pc": caso.BO_PC,
                    "cad": caso.CAD,
                    "score_similaridade": round(score, 1),
                    "motivos": detalhes
                })
                
        # Ordenar por similaridade decrescente
        potenciais_duplicados.sort(key=lambda x: x["score_similaridade"], reverse=True)
        
        return {
            "total_duplicados": len(potenciais_duplicados),
            "data": potenciais_duplicados
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na verificação de duplicados: {str(e)}"
        )


@router.get("/evolucoes-pendentes", response_model=Dict[str, Any])
def get_evolucoes_pendentes(db: Session = Depends(get_db)):
    """
    Retorna a fila nativa de evoluções pendentes, substituindo a planilha Excel de analistas.
    """
    try:
        evolucoes = db.query(SentinelaEvolucaoPendente, VwSentinelaCasoCompleto)\
                      .join(VwSentinelaCasoCompleto, SentinelaEvolucaoPendente.ID_CONTROLE_MORTE == VwSentinelaCasoCompleto.ID_CONTROLE_MORTE)\
                      .filter(SentinelaEvolucaoPendente.STATUS == "Pendente")\
                      .order_by(SentinelaEvolucaoPendente.DT_CRIACAO.desc()).all()
                      
        data = []
        for evol, caso in evolucoes:
            data.append({
                "id_evolucao": evol.ID_EVOLUCAO,
                "id_controle_morte": evol.ID_CONTROLE_MORTE,
                "nic_iml": evol.NIC_IML,
                "bo_pc": evol.BO_PC or caso.BO_PC,
                "data_obito": evol.DATA_OBITO.isoformat() if evol.DATA_OBITO else None,
                "motivo": evol.MOTIVO,
                "tipo_evolucao": evol.TIPO_EVOLUCAO,
                "autor": evol.AUTOR_PROPOSTA,
                "data_criacao": evol.DT_CRIACAO.isoformat() if evol.DT_CRIACAO else None,
                "caso_origem": {
                    "nome_vitima": caso.NOME_VITIMA,
                    "subjetividade": caso.SUBJETIVIDADE,
                    "data_hora_fato": caso.DATA_HORA_FATO,
                    "cidade": caso.CIDADE_FATO,
                    "bairro": caso.BAIRRO_FATO,
                    "cad": caso.CAD
                }
            })
            
        return {
            "total_pendentes": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar evoluções: {str(e)}"
        )


@router.post("/evolucoes-pendentes", response_model=Dict[str, Any])
def propor_evolucao(req: EvolucaoPropostaRequest, db: Session = Depends(get_db)):
    """
    Permite que o analista registre uma nova proposta de evolução (substituindo o preenchimento da planilha manual).
    """
    # Verifica se já há proposta ativa para este caso
    proposta_existente = db.query(SentinelaEvolucaoPendente).filter_by(
        ID_CONTROLE_MORTE=req.id_controle_morte,
        STATUS="Pendente"
    ).first()
    
    if proposta_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma proposta de evolução pendente para este caso."
        )
        
    try:
        nova_prop = SentinelaEvolucaoPendente(
            ID_CONTROLE_MORTE=req.id_controle_morte,
            NIC_IML=req.nic_iml,
            BO_PC=req.bo_pc,
            STATUS="Pendente",
            MOTIVO=req.motivo,
            TIPO_EVOLUCAO="Tentativa -> Óbito",
            AUTOR_PROPOSTA=req.autor
        )
        db.add(nova_prop)
        
        # Também altera provisoriamente o status do alerta se existir
        alerta = db.query(SentinelaFilaAlertas).filter_by(
            ID_CONTROLE_MORTE=req.id_controle_morte,
            TIPO_ALERTA="Suspeita de Evolução de Tentativa para Óbito (IML)"
        ).first()
        if alerta:
            alerta.STATUS = "Em Tratativa"
            
        db.commit()
        return {
            "message": "Proposta de evolução cadastrada com sucesso.",
            "id_evolucao": nova_prop.ID_EVOLUCAO
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar proposta de evolução: {str(e)}"
        )


@router.post("/evolucoes-pendentes/{evol_id}/processar", response_model=Dict[str, Any])
def processar_evolucao(evol_id: int, req: EvolucaoProcessoRequest, db: Session = Depends(get_db)):
    """
    Endpoint de decisão (Major/Supervisor).
    Aprova ou rejeita uma evolução. Se aprovado, sincroniza com SIESP/CONTROLE_MORTE
    e resolve o alerta e log correspondente.
    """
    prop = db.query(SentinelaEvolucaoPendente).filter_by(ID_EVOLUCAO=evol_id).first()
    if not prop:
        raise HTTPException(
            status_code=404,
            detail="Proposta de evolução não encontrada."
        )
        
    if prop.STATUS != "Pendente":
        raise HTTPException(
            status_code=400,
            detail="Esta proposta já foi processada anteriormente."
        )
        
    try:
        prop.STATUS = req.status
        prop.DT_ATUALIZACAO = datetime.now()
        
        if req.status == "Aprovada":
            # 1. Simular a evolução na Controle Morte / Base consolidada
            # Atualiza o caso principal
            caso = db.query(VwSentinelaCasoCompleto).filter_by(ID_CONTROLE_MORTE=prop.ID_CONTROLE_MORTE).first()
            if caso:
                caso.SUBJETIVIDADE = "MORTE A ESCLARECER"
                caso.NIC = prop.nic_iml
                if prop.bo_pc:
                    caso.BO_PC = prop.bo_pc
                    
            # 2. Resolver o alerta da fila
            alerta = db.query(SentinelaFilaAlertas).filter_by(
                ID_CONTROLE_MORTE=prop.ID_CONTROLE_MORTE,
                TIPO_ALERTA="Suspeita de Evolução de Tentativa para Óbito (IML)"
            ).first()
            if alerta:
                alerta.STATUS = "Resolvido"
                
            # 3. Resolver log de reconciliação
            log = db.query(SentinelaReconciliacaoLog).filter_by(
                ID_CONTROLE_MORTE=prop.ID_CONTROLE_MORTE,
                CAMPO_MESTRA="SUBJETIVIDADE",
                STATUS="Pendente"
            ).first()
            if log:
                log.STATUS = "Confirmado"
                log.DT_RESOLUCAO = datetime.now()
                
        elif req.status == "Rejeitada":
            # Devolve o alerta para a fila para nova análise
            alerta = db.query(SentinelaFilaAlertas).filter_by(
                ID_CONTROLE_MORTE=prop.ID_CONTROLE_MORTE,
                TIPO_ALERTA="Suspeita de Evolução de Tentativa para Óbito (IML)"
            ).first()
            if alerta:
                alerta.STATUS = "Novo"
                
        db.commit()
        return {
            "message": f"Evolução {req.status} com sucesso.",
            "id_evolucao": evol_id,
            "status": req.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar decisão: {str(e)}"
        )


@router.get("/notificacoes-iml", response_model=Dict[str, Any])
def get_notificacoes_iml(
    lido: Optional[int] = Query(0, description="Filtrar por lido: 0 ou 1"),
    db: Session = Depends(get_db)
):
    """
    Retorna feed de alterações da base do IML para notificar analistas.
    """
    try:
        query = db.query(SentinelaNotificacaoIML)
        if lido is not None:
            query = query.filter(SentinelaNotificacaoIML.LIDO == lido)
            
        notificacoes = query.order_by(SentinelaNotificacaoIML.DT_EVENTO.desc()).all()
        
        data = []
        for n in notificacoes:
            data.append({
                "id_notificacao": n.ID_NOTIFICACAO,
                "nic": n.NIC,
                "nome_vitima": n.NOME_VITIMA,
                "status_iml": n.STATUS_IML,
                "tipo_mensagem": n.TIPO_MENSAGEM,
                "lido": n.LIDO,
                "data_evento": n.DT_EVENTO.isoformat() if n.DT_EVENTO else None
            })
            
        return {
            "total": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar notificações: {str(e)}"
        )


@router.post("/notificacoes-iml/{notif_id}/lido", response_model=Dict[str, Any])
def marcar_notificacao_lida(notif_id: int, db: Session = Depends(get_db)):
    """
    Marca uma notificação do IML como lida.
    """
    n = db.query(SentinelaNotificacaoIML).filter_by(ID_NOTIFICACAO=notif_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")
        
    try:
        n.LIDO = 1
        db.commit()
        return {"message": "Notificação marcada como lida.", "id": notif_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validar-geografia/{id_controle_morte}", response_model=Dict[str, Any])
def validar_geografia_caso(id_controle_morte: int, db: Session = Depends(get_db)):
    """
    Endpoint para auditar e expor a validação geográfica de um caso.
    """
    caso = db.query(VwSentinelaCasoCompleto).filter_by(ID_CONTROLE_MORTE=id_controle_morte).first()
    if not caso:
        raise HTTPException(
            status_code=404,
            detail=f"Caso com ID {id_controle_morte} não encontrado."
        )
        
    try:
        res = executar_validacao_geografica(caso, db)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante a validação geográfica: {str(e)}"
        )

