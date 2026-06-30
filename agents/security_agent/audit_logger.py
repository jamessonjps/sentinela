import logging
from datetime import datetime

logger = logging.getLogger("SentinelaAudit")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class AuditLogger:
    """
    Logs queries and security events for audit purposes.
    """
    @staticmethod
    def log_query(user_id: str, query: str, status: str = "SUCCESS", details: str = ""):
        log_msg = f"User: {user_id} | Status: {status} | Query: {query} | Details: {details}"
        if status == "SUCCESS":
            logger.info(log_msg)
        else:
            logger.warning(log_msg)
            
    @staticmethod
    def log_security_event(event_type: str, description: str):
        logger.critical(f"SECURITY EVENT: {event_type} - {description}")
