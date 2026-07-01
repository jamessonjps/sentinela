import logging
from sqlalchemy.orm import Session
from api.models import VwSentinelaCasoCompleto, SentinelaFilaAlertas, SentinelaLaudoIML
from .field_rules import (
    normalize_text,
    match_names
)

logger = logging.getLogger(__name__)

class LaudoComparator:
    """
    Agente Comparador focado nos Laudos Periciais do IML (Forensis)
    e sua reconciliação contra dados de Despacho (CAD) e Registro Policial (PPE/PC).
    """

    def __init__(self):
        pass

    def compare_laudos(self, session: Session) -> int:
        """
        Executa a reconciliação pericial cruzando a tabela de laudos com os casos mestras.
        """
        logger.info("Iniciando auditoria pericial (Laudos do IML)...")
        
        laudos = session.query(SentinelaLaudoIML).all()
        logger.info(f"Localizados {len(laudos)} laudos periciais para auditoria.")
        alertas_gerados = 0
        
        for laudo in laudos:
            nic = laudo.NIC
            # Busca caso correspondente na view consolidada
            caso = session.query(VwSentinelaCasoCompleto).filter(
                (VwSentinelaCasoCompleto.NIC == nic) |
                (VwSentinelaCasoCompleto.NIC_IML == nic) |
                (VwSentinelaCasoCompleto.CAD == laudo.COD_REQUISICAO) |
                (VwSentinelaCasoCompleto.NIC == laudo.COD_REQUISICAO)
            ).first()
            
            if not caso:
                continue
                
            id_cm = caso.ID_CONTROLE_MORTE
            bo_pc = caso.BO_PC
            cad = caso.CAD
            
            # 1. Regra de Divergência de Causa Mortis vs Subjetividade
            conclusao = (laudo.CONCLUSAO or "").upper()
            subjetividade = (caso.SUBJETIVIDADE or "").upper()
            tipo_mvi = (caso.TIPO_MVI or "").upper()
            
            # Heurísticas de detecção de mortes não-violentas/suicídios descritas no Laudo
            morte_nao_violenta = any(x in conclusao for x in ["INFARTO", "CAUSA NATURAL", "ENFERMIDADE", "AVC", "PARADA CARDIO"])
            suicidio_ou_acidente = any(x in conclusao for x in ["SUICIDIO", "ENFORCAMENTO", "QUEDA", "AFOGAMENTO", "ACIDENTE"])
            
            # Se for morte natural/suicídio no laudo, mas estiver tipificado como CVLI (Homicídio)
            eh_cvli = "CVLI" in subjetividade or "HOMIC" in subjetividade or "HOMIC" in tipo_mvi
            
            # Caso A: Laudo diz morte natural/suicídio/acidente, mas Controle Morte diz que é Homicídio/CVLI
            if (morte_nao_violenta or suicidio_ou_acidente) and eh_cvli:
                motivo = "Morte Natural" if morte_nao_violenta else "Suicídio/Acidente"
                desc_alerta = f"Laudo aponta {motivo}, mas caso está cadastrado como Homicídio/CVLI"
                self._registrar_alerta(
                    session=session,
                    id_cm=id_cm,
                    tipo_alerta="Causa da Morte no Laudo diverge da Subjetividade",
                    status="Novo",
                    prioridade=3, # Alta Prioridade
                    nic=nic, bo_pc=bo_pc, cad=cad
                )
                alertas_gerados += 1
                logger.warning(f"[Laudo] Divergência de Causa Mortis no caso {id_cm}: {desc_alerta}")
                
            # Caso B: Laudo diz explicitamente homicídio por arma de fogo/branca, mas não está registrado como CVLI
            morte_violenta_homicidio = any(x in conclusao for x in ["ARMA DE FOGO", "PROJETIL", "PAF", "ARMA BRANCA", "ESTRANGULAMENTO", "ASFIXIA MECANICA POR SUFOCACAO", "HOMICIDIO"])
            if morte_violenta_homicidio and not eh_cvli:
                self._registrar_alerta(
                    session=session,
                    id_cm=id_cm,
                    tipo_alerta="Causa da Morte no Laudo diverge da Subjetividade",
                    status="Novo",
                    prioridade=3, # Alta
                    nic=nic, bo_pc=bo_pc, cad=cad
                )
                alertas_gerados += 1
                logger.warning(f"[Laudo] Caso {id_cm} sem registro de CVLI, mas laudo aponta óbito por violência mecânica/PAF.")

            # 2. Regra de Divergência de Identidade (PACIENTE no Laudo vs Caso Consolidado)
            if laudo.PACIENTE and caso.NOME_VITIMA:
                name_match, score = match_names(caso.NOME_VITIMA, laudo.PACIENTE)
                if not name_match:
                    self._registrar_alerta(
                        session=session,
                        id_cm=id_cm,
                        tipo_alerta="Identidade no Laudo diverge do Cadastro (CAD/PPE)",
                        status="Novo",
                        prioridade=2, # Média
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    alertas_gerados += 1
                    logger.warning(f"[Laudo] Nome divergente no caso {id_cm}: Mestra '{caso.NOME_VITIMA}' vs Laudo '{laudo.PACIENTE}' (Score: {score}%)")
                    
        session.commit()
        logger.info(f"Auditoria pericial concluída. {alertas_gerados} alertas de inconsistência pericial gerados.")
        return alertas_gerados

    def _registrar_alerta(self, session: Session, id_cm: int, tipo_alerta: str,
                           status: str, prioridade: int, nic: str = None, 
                           bo_pc: str = None, cad: str = None):
        """
        Salva o alerta de laudo pericial na tabela de auditoria sem gerar duplicados.
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
                STATUS=status,
                PRIORIDADE=prioridade,
                TIPO_ALERTA=tipo_alerta
            )
            session.add(novo_alerta)
