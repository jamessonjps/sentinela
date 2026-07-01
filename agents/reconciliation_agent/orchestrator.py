import logging
from sqlalchemy.orm import Session
from .iml_comparator import IMLComparator
from .cad_comparator import CADComparator
from .ppe_comparator import PPEComparator
from .laudo_comparator import LaudoComparator

logger = logging.getLogger(__name__)

class ReconciliationOrchestrator:
    """
    Orquestrador central do Motor de Reconciliação do SENTINELA.
    Gerencia a execução dos comparadores IML, CAD, PPE e Laudos (Forensis).
    """

    def __init__(self):
        self.iml_comp = IMLComparator()
        self.cad_comp = CADComparator()
        self.ppe_comp = PPEComparator()
        self.laudo_comp = LaudoComparator()

    def run_reconciliation(self, session: Session) -> dict:
        """
        Executa todas as rotinas de reconciliação de dados.
        Retorna o resumo das operações.
        """
        logger.info("==================================================")
        logger.info("Iniciando Ciclo Completo de Reconciliação de Dados")
        logger.info("==================================================")
        
        try:
            # 1. Comparação IML
            iml_div = self.iml_comp.compare_linked_records(session)
            iml_evol = self.iml_comp.detect_evolution_attempts(session)
            
            # 2. Correlação CAD ↔ PPE
            cad_corr = self.cad_comp.correlate_cad_ppe(session)
            
            # 3. Comparação PPE
            ppe_div = self.ppe_comp.compare_linked_records(session)
            
            # 4. Auditoria de Laudos Periciais (Forensis)
            laudo_div = self.laudo_comp.compare_laudos(session)
            
            summary = {
                "status": "success",
                "iml_divergencias": iml_div,
                "iml_suspeitas_evolucao": iml_evol,
                "cad_correlacoes_sugeridas": cad_corr,
                "ppe_divergencias": ppe_div,
                "laudo_divergencias": laudo_div,
                "total_alertas_reconciliacao": iml_div + iml_evol + cad_corr + ppe_div + laudo_div
            }
            
            logger.info("==================================================")
            logger.info("Ciclo de Reconciliação Concluído com Sucesso!")
            logger.info(f"Resumo: {summary}")
            logger.info("==================================================")
            
            return summary
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro crítico durante a execução do orquestrador de reconciliação: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
