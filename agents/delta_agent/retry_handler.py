import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def with_retry(max_retries=3, delay=2, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retries before giving up.
        delay (int): Initial delay between retries in seconds.
        backoff (int): Multiplier for the delay after each retry.
        exceptions (tuple): Tuple of exceptions that should trigger a retry.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries. Final Exception: {e}")
                        raise
                    logger.warning(f"Function {func.__name__} failed: {e}. Retrying in {current_delay} seconds ({retries}/{max_retries})...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
