"""
SENTINELA LGPD Agent Package
"""
from .pii_catalog import PII_CATALOG, ALLOWED_FIELDS
from .masking_engine import MaskingEngine
from .sample_generator import SampleGenerator

class LGPDAgent:
    """
    Facade for the LGPD Agent functionality.
    Controls the SENTINELA_MASCARAMENTO and anonymization.
    """
    def __init__(self):
        self.engine = MaskingEngine()
        self.generator = SampleGenerator(self.engine)

__all__ = ["LGPDAgent", "PII_CATALOG", "ALLOWED_FIELDS", "MaskingEngine", "SampleGenerator"]
