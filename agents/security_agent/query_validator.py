import re

class QueryValidator:
    """
    Validates SQL queries to ensure read-only operations on protected schemas.
    """
    FORBIDDEN_OPERATIONS = [r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', r'\bALTER\b', r'\bTRUNCATE\b']
    PROTECTED_SCHEMAS = ['NEAC', 'DAAS', 'SGOU']

    @classmethod
    def validate(cls, query: str) -> bool:
        """
        Validates if the query is allowed. Raises ValueError if forbidden operations are attempted on protected schemas.
        """
        query_upper = query.upper()
        
        for op in cls.FORBIDDEN_OPERATIONS:
            if re.search(op, query_upper):
                for schema in cls.PROTECTED_SCHEMAS:
                    if schema in query_upper:
                        clean_op = op.replace(r'\b', '')
                        raise ValueError(f"Security Alert: Forbidden operation '{clean_op}' detected on protected schema '{schema}'.")

        return True
    
    @classmethod
    def enforce_read_only(cls, query: str) -> str:
        """
        Ensures the query runs in a read-only transaction context.
        """
        read_only_stmt = "SET TRANSACTION READ ONLY;"
        if read_only_stmt not in query.upper():
            return f"{read_only_stmt}\n{query}"
        return query
