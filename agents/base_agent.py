import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Setup basic logging for agents
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent(ABC):
    """
    Base Agent for all SENTINELA specialized agents.
    Provides common logging, error handling, and standard interface.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.name)
        
    def log_info(self, message: str) -> None:
        self.logger.info(message)
        
    def log_error(self, message: str, exc_info: bool = True) -> None:
        self.logger.error(message, exc_info=exc_info)
        
    def execute(self, *args, **kwargs) -> Any:
        """
        Wrapper around the run method to handle exceptions and standard logging.
        """
        self.log_info(f"Agent '{self.name}' starting execution.")
        try:
            result = self.run(*args, **kwargs)
            self.log_info(f"Agent '{self.name}' execution completed successfully.")
            return result
        except Exception as e:
            self.log_error(f"Agent '{self.name}' execution failed: {str(e)}")
            self.handle_error(e)
            raise
            
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Core logic of the agent to be implemented by subclasses.
        """
        pass
        
    def handle_error(self, error: Exception) -> None:
        """
        Optional custom error handling logic. Can be overridden by subclasses.
        For example, inserting into SENTINELA_AUDITORIA_ERRO.
        """
        pass
