from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Any, Dict
from ..database import get_db

router = APIRouter()

@router.get("/hypotheses/temporal-distribution", response_model=Dict[str, Any])
def get_temporal_distribution(db: Session = Depends(get_db)):
    """
    Retorna dados estatísticos da distribuição temporal de casos.
    Diferencia sintaxe entre SQLite (dev) e Oracle (prod).
    """
    try:
        if db.bind.dialect.name == "sqlite":
            query = text("""
                SELECT 
                    SUBSTR(DATA_HORA_FATO, 1, 7) as mes_ano,
                    COUNT(*) as total_casos
                FROM VW_SENTINELA_CASO_COMPLETO
                WHERE DATA_HORA_FATO IS NOT NULL
                GROUP BY SUBSTR(DATA_HORA_FATO, 1, 7)
                ORDER BY mes_ano
            """)
        else:
            query = text("""
                SELECT 
                    TO_CHAR(DATA_HORA_FATO, 'YYYY-MM') as mes_ano,
                    COUNT(*) as total_casos
                FROM VW_SENTINELA_CASO_COMPLETO
                WHERE DATA_HORA_FATO IS NOT NULL
                GROUP BY TO_CHAR(DATA_HORA_FATO, 'YYYY-MM')
                ORDER BY mes_ano
            """)
            
        result = db.execute(query)
        data = [dict(row._mapping) for row in result]
        
        return {
            "hypothesis_context": "Variação temporal de MVI",
            "metric": "Contagem mensal de ocorrências",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro no banco de dados: {str(e)}"
        )

@router.get("/hypotheses/categorical-stats", response_model=Dict[str, Any])
def get_categorical_stats(category_column: str = "SUBJETIVIDADE", db: Session = Depends(get_db)):
    """
    Retorna a distribuição de categorias para uma coluna específica.
    """
    # Lista de colunas seguras para evitar SQL Injection
    allowed_columns = ["SUBJETIVIDADE", "TIPO_MVI", "STATUS", "AISP", "RISP", "CIDADE_FATO"]
    if category_column.upper() not in [c.upper() for c in allowed_columns]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Coluna inválida. Deve ser uma de {allowed_columns}"
        )

    try:
        # Resolve o nome exato da coluna da whitelist
        col_name = next(c for c in allowed_columns if c.upper() == category_column.upper())
        
        query = text(f"""
            SELECT 
                {col_name} as categoria,
                COUNT(*) as quantidade,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM VW_SENTINELA_CASO_COMPLETO), 2) as percentual
            FROM VW_SENTINELA_CASO_COMPLETO
            WHERE {col_name} IS NOT NULL
            GROUP BY {col_name}
            ORDER BY quantidade DESC
        """)
        
        result = db.execute(query)
        data = [dict(row._mapping) for row in result]
        
        return {
            "hypothesis_context": f"Distribuição de casos por {col_name}",
            "metric": "Contagem e Percentual",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro no banco de dados: {str(e)}"
        )
