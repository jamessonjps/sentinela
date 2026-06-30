import sqlite3
import pandas as pd
import os

db_path = r"c:\Users\jamerson.jpd\Desktop\SENTINELA\sentinela.db"
artifact_path = r"c:\Users\jamerson.jpd\.gemini\antigravity\brain\a085c6c7-d6f4-4d23-b5f0-c1675dab2c02\auditoria_naturezas_cad.md"

conn = sqlite3.connect(db_path)

query = """
SELECT 
    DS_GRUPO_CRIME_ATEND as Grupo_Natureza_CAD,
    COUNT(*) as Ocorrencias,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as Percentual
FROM 
    VW_SENTINELA_CASO_COMPLETO
WHERE 
    CAD IS NOT NULL 
    AND CAD != ''
    AND DS_GRUPO_CRIME_ATEND IS NOT NULL
GROUP BY 
    DS_GRUPO_CRIME_ATEND
ORDER BY 
    Ocorrencias DESC;
"""

df = pd.read_sql_query(query, conn)

query_natureza = """
SELECT 
    DS_NATUREZA_ATEND as Natureza_Especifica_CAD,
    COUNT(*) as Ocorrencias,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as Percentual
FROM 
    VW_SENTINELA_CASO_COMPLETO
WHERE 
    CAD IS NOT NULL 
    AND CAD != ''
    AND DS_NATUREZA_ATEND IS NOT NULL
GROUP BY 
    DS_NATUREZA_ATEND
ORDER BY 
    Ocorrencias DESC
LIMIT 20;
"""

df_natureza = pd.read_sql_query(query_natureza, conn)

with open(artifact_path, "w", encoding="utf-8") as f:
    f.write("# Auditoria de Naturezas CAD para o Radar 190\n\n")
    f.write("Esta auditoria extrai da base mestra `CONTROLE_MORTE` as frequências dos Grupos de Natureza e Naturezas Específicas do CAD/190 que efetivamente resultaram em óbitos confirmados (MVI).\n")
    f.write("Estes parâmetros devem ser utilizados para **robustecer a busca (query)** na tabela bruta do CAD, permitindo que o Radar 190 detecte CVLIs com alta precisão.\n\n")
    
    def df_to_markdown(df):
        cols = df.columns.tolist()
        res = "| " + " | ".join(cols) + " |\n"
        res += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for _, row in df.iterrows():
            res += "| " + " | ".join(str(x) for x in row.values) + " |\n"
        return res

    f.write("## 1. Grupos de Natureza (CAD) mais frequentes em óbitos\n\n")
    f.write(df_to_markdown(df))
    
    f.write("\n## 2. Top 20 Naturezas Específicas (CAD) em óbitos\n\n")
    f.write(df_to_markdown(df_natureza))

conn.close()
