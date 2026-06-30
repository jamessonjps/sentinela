class DedupDetector:
    """
    Detects potential duplicate records based on specified attributes.
    """
    @staticmethod
    def is_duplicate(record1: dict, record2: dict, keys: list) -> bool:
        """
        Checks if two records have identical values for the specified keys.
        """
        if not keys:
            return False
            
        for key in keys:
            val1 = record1.get(key)
            val2 = record2.get(key)
            if val1 != val2 or val1 is None:
                return False
        return True
