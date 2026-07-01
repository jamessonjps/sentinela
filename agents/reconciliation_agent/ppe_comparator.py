import logging
from sqlalchemy.orm import Session
from api.models import VwSentinelaCasoCompleto, SentinelaFilaAlertas, SentinelaReconciliacaoLog
from .field_rules import (
    normalize_text,
    parse_date
)

logger = logging.getLogger(__name__)

class PPEComparator:
    """
    Comparador de reconciliação entre CONTROLE_MORTE e o PPE/DAAS (Polícia Civil).
    Busca inconsistências e alterações cadastrais ou de classificação nos BOs.
    """

    def __init__(self):
        pass

    def compare_linked_records(self, session: Session) -> int:
        """
        Varre casos que possuem BO_PC e compara campos comuns com a Controle Morte.
        """
        logger.info("Iniciando comparação de registros vinculados da Polícia Civil (PPE)...")
        
        # Seleciona casos que possuem número de BO
        casos = session.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.BO_PC.isnot(None)
        ).all()
        
        logger.info(f"Localizados {len(casos)} casos com BO_PC para auditoria.")
        divergencias_encontradas = 0
        
        for caso in casos:
            bo_pc = caso.BO_PC
            id_cm = caso.ID_CONTROLE_MORTE
            nic = caso.NIC
            cad = caso.CAD
            
            # 1. Comparar BAIRRO_FATO vs ED_BAIRRO
            if caso.BAIRRO_FATO and caso.ED_BAIRRO:
                b_mestra = normalize_text(caso.BAIRRO_FATO)
                b_fonte = normalize_text(caso.ED_BAIRRO)
                if b_mestra != b_fonte and b_mestra not in b_fonte and b_fonte not in b_mestra:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="PPE",
                        campo_mestra="BAIRRO_FATO",
                        val_mestra=caso.BAIRRO_FATO,
                        campo_fonte="ED_BAIRRO",
                        val_fonte=caso.ED_BAIRRO,
                        tipo="VALOR_DIFERENTE",
                        score=0.0,
                        tipo_alerta="Bairro Diverge do BO PC",
                        prioridade=1,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 2. Comparar CIDADE_FATO vs NO_MUNICIPIO
            if caso.CIDADE_FATO and caso.NO_MUNICIPIO:
                c_mestra = normalize_text(caso.CIDADE_FATO)
                c_fonte = normalize_text(caso.NO_MUNICIPIO)
                if c_mestra != c_fonte:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="PPE",
                        campo_mestra="CIDADE_FATO",
                        val_mestra=caso.CIDADE_FATO,
                        campo_fonte="NO_MUNICIPIO",
                        val_fonte=caso.NO_MUNICIPIO,
                        tipo="VALOR_DIFERENTE",
                        score=0.0,
                        tipo_alerta="Cidade Diverge do BO PC",
                        prioridade=1,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 3. Comparar DATA_HORA_FATO vs DT_OCORRENCIA
            if caso.DATA_HORA_FATO and caso.DT_OCORRENCIA:
                dt_mestra = parse_date(caso.DATA_HORA_FATO)
                dt_fonte = parse_date(caso.DT_OCORRENCIA)
                if dt_mestra and dt_fonte:
                    # Tolerância de 24 horas (mudança de fuso/registro)
                    delta_seconds = abs((dt_mestra - dt_fonte).total_seconds())
                    if delta_seconds > 86400.0:
                        self._registrar_divergencia(
                            session=session,
                            id_cm=id_cm,
                            fonte="PPE",
                            campo_mestra="DATA_HORA_FATO",
                            val_mestra=caso.DATA_HORA_FATO,
                            campo_fonte="DT_OCORRENCIA",
                            val_fonte=caso.DT_OCORRENCIA,
                            tipo="VALOR_DIFERENTE",
                            score=0.0,
                            tipo_alerta="Data da Ocorrência Diverge do BO PC",
                            prioridade=1,
                            nic=nic, bo_pc=bo_pc, cad=cad
                        )
                        divergencias_encontradas += 1

            # 4. UPGRADE DE CRIME: Tentativa no BO vs MVI consumado na Mestra (ou vice-versa)
            if caso.SUBJETIVIDADE and caso.SN_TENTATIVA is not None:
                is_tentativa_mestra = "TENTATIVA" in caso.SUBJETIVIDADE.upper()
                is_tentativa_bo = bool(caso.SN_TENTATIVA)
                
                # Se for homicídio consumado (MVI) na mestra mas no BO consta como tentativa
                if not is_tentativa_mestra and is_tentativa_bo:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="PPE",
                        campo_mestra="SUBJETIVIDADE",
                        val_mestra=caso.SUBJETIVIDADE,
                        campo_fonte="SN_TENTATIVA",
                        val_fonte="1 (Tentativa)",
                        tipo="VALOR_DIFERENTE",
                        score=0.0,
                        tipo_alerta="BO Registra como Tentativa, Mestra como CVLI",
                        prioridade=3,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 5. AGRAVANTE: Maria da Penha detectado no BO PC
            if caso.SN_MARIA_DA_PENHA == 1:
                # Alerta para o analista verificar se a Controle Morte está atrelada à violência doméstica/feminicídio
                self._registrar_divergencia(
                    session=session,
                    id_cm=id_cm,
                    fonte="PPE",
                    campo_mestra="SITUACAO_ESPECIAL", # campo hipotético ou informativo
                    val_mestra=None,
                    campo_fonte="SN_MARIA_DA_PENHA",
                    val_fonte="1 (Sim)",
                    tipo="VALOR_DIFERENTE",
                    score=0.0,
                    tipo_alerta="BO com Agravante Maria da Penha — Conferir Mestra",
                    prioridade=2,
                    nic=nic, bo_pc=bo_pc, cad=cad
                )
                divergencias_encontradas += 1

            # 6. ALTERAÇÃO DE STATUS: BO Cancelado ou Inativo no DAAS
            if caso.IN_SITUACAO_ATUAL and caso.IN_SITUACAO_ATUAL != "ATIVO":
                self._registrar_divergencia(
                    session=session,
                    id_cm=id_cm,
                    fonte="PPE",
                    campo_mestra="STATUS",
                    val_mestra=caso.STATUS,
                    campo_fonte="IN_SITUACAO_ATUAL",
                    val_fonte=caso.IN_SITUACAO_ATUAL,
                    tipo="VALOR_DIFERENTE",
                    score=0.0,
                    tipo_alerta="Situação do BO Alterada no DAAS",
                    prioridade=2,
                    nic=nic, bo_pc=bo_pc, cad=cad
                )
                divergencias_encontradas += 1

        session.commit()
        logger.info(f"Comparação do PPE concluída. {divergencias_encontradas} divergências detectadas.")
        return divergencias_encontradas

    def _registrar_divergencia(self, session: Session, id_cm: int, fonte: str,
                              campo_mestra: str, val_mestra: str, campo_fonte: str,
                              val_fonte: str, tipo: str, score: float, tipo_alerta: str,
                              prioridade: int, nic: str = None, bo_pc: str = None,
                              cad: str = None):
        """
        Salva o log de divergência e insere um alerta correspondente na fila de alertas.
        """
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
            
        log_existente = session.query(SentinelaReconciliacaoLog).filter_by(
            ID_CONTROLE_MORTE=id_cm,
            FONTE=fonte,
            CAMPO_MESTRA=campo_mestra,
            STATUS="Pendente"
        ).first()
        
        if not log_existente:
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
