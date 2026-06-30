"""
Delta Detection Agent for SENTINELA.
Responsible for detecting changes and cross-referencing data to find updates,
such as 'Evolucao para Obito' and BO_PC table crossings.
"""

from .change_detector import ChangeDetector
from .cross_reference import CrossReferenceAnalyzer
from .alert_dispatcher import AlertDispatcher
from .checkpoint_manager import CheckpointManager
from .retry_handler import with_retry

__all__ = [
    'ChangeDetector',
    'CrossReferenceAnalyzer',
    'AlertDispatcher',
    'CheckpointManager',
    'with_retry'
]
