import random
from typing import List, Dict, Any
from .masking_engine import MaskingEngine
from .pii_catalog import ALLOWED_FIELDS

class SampleGenerator:
    """
    Generates mock data for testing and validation,
    ensuring all generated data is either inherently fake or anonymized.
    """
    
    def __init__(self, masking_engine: MaskingEngine):
        self.engine = masking_engine
        
    def generate_mock_caso(self, caso_id: int) -> Dict[str, Any]:
        """Generates a single mock case with PII that will need masking."""
        
        # Dados Falsos
        raw_data = {
            "ID_CONTROLE_MORTE": caso_id,
            "NIC": f"NIC-{random.randint(1000, 9999)}",
            "BO_PC": f"BO-{random.randint(10000, 99999)}",
            "CAD": f"CAD-{random.randint(100000, 999999)}",
            "NOME_VITIMA": f"Fulano de Tal {caso_id}",
            "MAE_VITIMA": f"Maria de Tal {caso_id}",
            "NASC_VITIMA": "1990-05-15",
            "ENDERECO": "Rua Falsa, 123",
            "NOME_AUTOR": "Ciclano Souza",
            "CPF_AUTOR": "12345678901",
            "ALCUNHA_AUTOR": "Ciclano",
            "RELATO_HISTORICO": "Autor agrediu a vítima com instrumento perfurocortante.",
            "AISP": "AISP 01",
            "RISP": "RISP A",
            "BAIRRO_FATO": "Centro",
            "SUBJETIVIDADE": "Homicídio Doloso",
            "INSTRUMENTO_UTILIZADO": "Arma Branca"
        }
        
        return raw_data
        
    def generate_anonymized_samples(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generates `count` mock cases and returns them already anonymized
        by the MaskingEngine, ready for use by the Science Agent.
        """
        raw_records = [self.generate_mock_caso(i) for i in range(1, count + 1)]
        return self.engine.anonymize_records(raw_records)
