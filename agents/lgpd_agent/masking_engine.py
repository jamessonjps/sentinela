import hashlib
import re
from typing import Dict, Any, List
from .pii_catalog import PII_CATALOG

class MaskingEngine:
    """
    Engine to apply masking and pseudonymization to dicts/dataframes
    based on the LGPD catalog.
    """
    
    def __init__(self, catalog: Dict[str, str] = None):
        self.catalog = catalog or PII_CATALOG

    def _mask_cpf(self, cpf: str) -> str:
        if not isinstance(cpf, str):
            return "***.***.***-**"
        # Mantém formato se houver, mas esconde os dígitos centrais
        clean_cpf = re.sub(r'\D', '', cpf)
        if len(clean_cpf) == 11:
            return f"***.{clean_cpf[3:6]}.***-**"
        return "***.***.***-**"
        
    def _mask_rg(self, rg: str) -> str:
        return "***.***.***-*"

    def _mask_date(self, date_str: str) -> str:
        # Simplificação: retorna apenas o ano ou uma string fixa
        if not date_str:
            return "****"
        # Se for string no formato YYYY-MM-DD
        if len(str(date_str)) >= 4:
            return str(date_str)[:4]
        return "****"

    def _pseudonymize(self, text: str, prefix: str = "ANON_") -> str:
        if not text:
            return ""
        hash_obj = hashlib.sha256(str(text).encode('utf-8'))
        return f"{prefix}{hash_obj.hexdigest()[:8].upper()}"

    def mask_value(self, field_name: str, value: Any, record_id: str = None) -> Any:
        """Masks a single value based on its field name."""
        if value is None:
            return None
            
        rule = self.catalog.get(field_name.upper())
        if not rule:
            # If not in catalog, assume it is safe (or apply default deny strategy)
            return value

        if rule == "SUPPRESS":
            if "VITIMA" in field_name.upper() and record_id:
                return f"VITIMA_{record_id}"
            if "AUTOR" in field_name.upper() and record_id:
                return f"AUTOR_{record_id}"
            return "[SUPRIMIDO]"
            
        elif rule == "MASK_CPF":
            return self._mask_cpf(str(value))
            
        elif rule == "MASK_RG":
            return self._mask_rg(str(value))
            
        elif rule == "DATE_MASK":
            return self._mask_date(str(value))
            
        elif rule == "TEXT_MASK":
            return "[RELATO OCULTO LGPD]"
            
        return value

    def anonymize_dict(self, data: Dict[str, Any], id_field: str = "ID_CONTROLE_MORTE") -> Dict[str, Any]:
        """
        Anonymizes a dictionary containing a single record.
        """
        record_id = str(data.get(id_field, ""))
        anonymized = {}
        for key, val in data.items():
            anonymized[key] = self.mask_value(key, val, record_id=record_id)
        return anonymized

    def anonymize_records(self, records: List[Dict[str, Any]], id_field: str = "ID_CONTROLE_MORTE") -> List[Dict[str, Any]]:
        """
        Anonymizes a list of dictionaries.
        """
        return [self.anonymize_dict(record, id_field) for record in records]
