import logging
from .cross_reference import CrossReferenceAnalyzer
from .retry_handler import with_retry

logger = logging.getLogger(__name__)

class ChangeDetector:
    """
    Detects specific business-critical changes in the database, such as 'Evolucao para Obito'.
    """
    def __init__(self, db_client):
        self.db = db_client
        self.cross_ref = CrossReferenceAnalyzer(db_client)

    @with_retry(max_retries=3, delay=2)
    def detect_evolucao_para_obito(self, last_check_time):
        """
        Core Business Logic: "Evolucao para Obito"
        Checks 'Tentativas' (Homicide attempts, etc.) that subsequently receive an IML entry in SGOU,
        indicating the attempt evolved into a death.
        """
        logger.info(f"Checking for 'Evolucao para Obito' since {last_check_time}")
        
        detected_evolutions = []
        
        try:
            # A lógica real (conforme correção do usuário):
            # O CONTROLE_MORTE tem um ID que foi registrado como TENTATIVA (sem NIC).
            # Precisamos cruzar a tabela do IML (VIEW_IML_NEAC_CADAVERICO) para ver se ele morreu.
            # O cruzamento ocorre pelo BO_PC ou pelo Nome da Vítima. Quando acha, a tentativa "ganha" o NIC.
            query = """
                SELECT 
                    CM.ID_CONTROLE_MORTE, 
                    IML.NIC AS NOVO_NIC, 
                    CM.BO_PC, 
                    CM.NOME_VITIMA, 
                    IML.DAT_OBITO,
                    IML.DATA_ENTRADA
                FROM NEAC.CONTROLE_MORTE CM
                JOIN SGOU.VIEW_IML_NEAC_CADAVERICO IML 
                  ON (CM.BO_PC = IML.DELEGADO_REQUERENTE /* Considerando BO_PC / Doc no IML */
                      OR UTL_MATCH.JARO_WINKLER_SIMILARITY(UPPER(CM.NOME_VITIMA), UPPER(IML.NOM_VITIMA)) > 85)
                WHERE CM.SUBJETIVIDADE LIKE '%TENTATIVA%'
                  AND CM.NIC IS NULL
                  AND IML.DATA_ENTRADA > :last_check_time
            """
            
            records = self.db.execute(query, {"last_check_time": last_check_time})
            
            for r in records:
                detected_evolutions.append({
                    "id_controle_morte": r['ID_CONTROLE_MORTE'],
                    "novo_nic": r['NOVO_NIC'],
                    "bo_pc": r['BO_PC'],
                    "vitima": r['NOME_VITIMA'],
                    "data_obito": r['DAT_OBITO'],
                    "data_entrada_iml": r['DATA_ENTRADA']
                })
        except Exception as e:
            logger.error(f"Failed to detect Evolucao para Obito: {e}")
            raise
            
        return detected_evolutions
        
    def run_all_checks(self, last_check_time):
        """
        Runs all configured change detection algorithms.
        """
        evolutions = self.detect_evolucao_para_obito(last_check_time)
        crossings = self.cross_ref.find_bo_pc_crossings(last_check_time)
        
        return {
            "evolucao_para_obito": evolutions,
            "bo_pc_crossings": crossings
        }
