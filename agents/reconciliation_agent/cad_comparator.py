import logging
from sqlalchemy.orm import Session
from api.models import VwSentinelaCasoCompleto, SentinelaFilaAlertas, SentinelaReconciliacaoLog, SentinelaRadarCAD
from .field_rules import (
    normalize_text,
    normalize_sex,
    normalize_race,
    parse_date,
    match_names,
    jaro_winkler_score
)

logger = logging.getLogger(__name__)

class CADComparator:
    """
    Comparador de correlação probabilística entre CAD (PM) e PPE (PC).
    Calcula a probabilidade de uma ocorrência PM ser o mesmo fato que um BO da PC.
    """

    def __init__(self, correlation_floor: float = 20.0):
        self.correlation_floor = correlation_floor

    def correlate_cad_ppe(self, session: Session) -> int:
        """
        Varre ocorrências do Radar CAD (não vinculadas) e busca possíveis correspondências
        com BOs da Polícia Civil presentes em VwSentinelaCasoCompleto.
        """
        logger.info("Iniciando análise de correlação probabilística CAD ↔ PPE...")
        
        # 1. Busca ocorrências do Radar CAD pendentes (Novos)
        ocorrencias_cad = session.query(SentinelaRadarCAD).filter_by(STATUS_RADAR="Novo").all()
        logger.info(f"Localizadas {len(ocorrencias_cad)} ocorrências no Radar CAD para análise.")
        
        if not ocorrencias_cad:
            return 0
            
        # 2. Busca BOs da Polícia Civil na base consolidada
        # Para fins de correlação local, buscamos registros em VwSentinelaCasoCompleto
        casos_pc = session.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.BO_PC.isnot(None)
        ).all()
        
        correlacoes_geradas = 0
        
        for cad in ocorrencias_cad:
            dt_cad = parse_date(cad.DT_OCOR)
            if not dt_cad:
                continue
                
            for caso in casos_pc:
                # Pula se já estiver vinculado de alguma forma
                if str(cad.ID_OCOR) == str(caso.CAD):
                    continue
                    
                score = 0.0
                
                # FATOR 1: Temporal (Máx 30%)
                dt_pc = parse_date(caso.DATA_HORA_FATO)
                if dt_pc:
                    delta_seconds = abs((dt_cad - dt_pc).total_seconds())
                    delta_hours = delta_seconds / 3600.0
                    
                    if delta_hours <= 2.0:
                        score += 30.0
                    elif delta_hours <= 12.0:
                        score += 20.0
                    elif delta_hours <= 24.0:
                        score += 10.0
                
                # FATOR 2: Espacial (Máx 30%)
                # Compara Cidade e Bairro
                cad_cidade = normalize_text(cad.CIDADE)
                caso_cidade = normalize_text(caso.CIDADE_FATO)
                
                if cad_cidade and caso_cidade and cad_cidade == caso_cidade:
                    score += 10.0 # Bateu cidade
                    
                    cad_bairro = normalize_text(cad.BAIRRO)
                    caso_bairro = normalize_text(caso.BAIRRO_FATO)
                    
                    if cad_bairro and caso_bairro:
                        if cad_bairro == caso_bairro:
                            score += 20.0 # Match exato
                        elif cad_bairro in caso_bairro or caso_bairro in cad_bairro:
                            score += 10.0 # Substring
                            
                # FATOR 3: Envolvido / Vítima (Máx 30%)
                # Busca similaridade fonética/nome se disponível
                # No Radar CAD não temos o nome da vítima estruturado (vem no texto livre DS_OCOR)
                # Na Controle Morte temos caso.NOME_VITIMA.
                if caso.NOME_VITIMA and cad.DS_OCOR:
                    # Tenta encontrar correspondência de nome no texto descritivo do CAD
                    # Vamos verificar se o nome do caso está no despacho ou similar
                    # Usamos Jaro-Winkler do nome contra palavras no relato ou uma busca direta
                    nome_mestra = normalize_text(caso.NOME_VITIMA)
                    nome_partes = nome_mestra.split()
                    
                    # Heurística simples: se o sobrenome principal e o primeiro nome estão no relato
                    if len(nome_partes) >= 2:
                        relato_cad = normalize_text(cad.DS_OCOR)
                        if nome_partes[0] in relato_cad and nome_partes[-1] in relato_cad:
                            score += 20.0 # Alta probabilidade
                            
                            # Adiciona 10% se o sexo também bater (se pudermos extrair do relato)
                            if caso.SEXO and caso.SEXO in relato_cad:
                                score += 10.0
                            elif caso.SEXO_VITIMA and caso.SEXO_VITIMA in relato_cad:
                                score += 10.0

                # FATOR 4: Natureza (Máx 10%)
                # Compara natureza do CAD com tipificação PC
                cad_nat = normalize_text(cad.DS_NATUREZA_ATEND)
                pc_nat = normalize_text(caso.NO_NATUREZA_OCORRENCIA)
                
                if cad_nat and pc_nat:
                    # Match exato ou padrões MVI comuns
                    mvi_pats = ["HOMICIDIO", "FEMINICIDIO", "LATROCINIO", "MORTE"]
                    cad_mvi = any(p in cad_nat for p in mvi_pats)
                    pc_mvi = any(p in pc_nat for p in mvi_pats)
                    
                    if cad_nat == pc_nat:
                        score += 10.0
                    elif cad_mvi and pc_mvi:
                        score += 8.0
                    elif cad.DS_GRUPO_CRIME_ATEND == caso.DS_GRUPO_NATUREZA:
                        score += 5.0

                # 3. Registra a correlação se passar do piso de ruído
                if score >= self.correlation_floor:
                    logger.debug(f"Correlação potencial: CAD {cad.ID_OCOR} ↔ PPE BO {caso.BO_PC} | Score: {score}%")
                    
                    self._registrar_divergencia_reconciliacao(
                        session=session,
                        id_cm=caso.ID_CONTROLE_MORTE,
                        fonte="CAD",
                        campo_mestra="CAD",
                        val_mestra=str(caso.CAD) if caso.CAD else None,
                        campo_fonte="ID_OCOR",
                        val_fonte=str(cad.ID_OCOR),
                        tipo="CORRELACAO_PROBABILISTICA",
                        score=score,
                        tipo_alerta="GPS CAD Disponível para Validação Manual",
                        prioridade=1 if score < 50.0 else 2, # Prioridade Média se score alto
                        nic=caso.NIC,
                        bo_pc=caso.BO_PC,
                        cad=str(cad.ID_OCOR)
                    )
                    correlacoes_geradas += 1
                    
        session.commit()
        logger.info(f"Análise de correlação CAD ↔ PPE concluída. {correlacoes_geradas} potenciais vínculos encontrados.")
        return correlacoes_geradas

    def _registrar_divergencia_reconciliacao(self, session: Session, id_cm: int, fonte: str,
                                            campo_mestra: str, val_mestra: str, campo_fonte: str,
                                            val_fonte: str, tipo: str, score: float, tipo_alerta: str,
                                            prioridade: int, nic: str = None, bo_pc: str = None,
                                            cad: str = None):
        """
        Grava o log de reconciliação e cria alertas associados.
        """
        # Só cria o alerta físico se o score de convergência for relevante (ex: >= 50%) para evitar inundar a fila
        if score >= 50.0:
            alerta_existente = session.query(SentinelaFilaAlertas).filter_by(
                ID_CONTROLE_MORTE=id_cm,
                TIPO_ALERTA=tipo_alerta
            ).first()
            
            if not alerta_existente:
                novo_alerta = SentinelaFilaAlertas(
                    ID_CONTROLE_MORTE=id_cm,
                    NIC=nic,
                    BO_PC=bo_pc,
                    CAD=cad,
                    STATUS="Novo",
                    PRIORIDADE=prioridade,
                    TIPO_ALERTA=tipo_alerta
                )
                session.add(novo_alerta)
                
        # Grava a correlação no log (sempre que passar do piso mínimo de ruído de 20%)
        # Permite atualizar o score se o cálculo mudar ou recalcular para Pendentes
        log_existente = session.query(SentinelaReconciliacaoLog).filter_by(
            ID_CONTROLE_MORTE=id_cm,
            FONTE=fonte,
            VALOR_FONTE=val_fonte,
            STATUS="Pendente"
        ).first()
        
        if log_existente:
            log_existente.SCORE_SIMILARIDADE = score
            log_existente.VALOR_MESTRA = str(val_mestra) if val_mestra else None
        else:
            novo_log = SentinelaReconciliacaoLog(
                ID_CONTROLE_MORTE=id_cm,
                FONTE=fonte,
                CAMPO_MESTRA=campo_mestra,
                VALOR_MESTRA=str(val_mestra) if val_mestra else None,
                CAMPO_FONTE=campo_fonte,
                VALOR_FONTE=str(val_fonte) if val_fonte else None,
                TIPO_DIVERGENCIA=tipo,
                SCORE_SIMILARIDADE=score,
                STATUS="Pendente"
            )
            session.add(novo_log)
