-- ====================================================================
-- SCRIPT DE EXTRAÇÃO DBeaver - CONTROLE_MORTE (ANO 2025 COMPLETO)
-- ====================================================================
-- OBJETIVO: Extrair todos os registros de 2025 para a Frente 1 de 
-- Tratamento (Python), já aplicando mascaramento de PII na fonte (LGPD).
-- ====================================================================

SELECT 
    -- 1. Chaves de Integração (Liberadas)
    ID_CONTROLE_MORTE,
    NIC,
    BO_PC,
    CAD,
    
    -- 2. Dados Pessoais Sensíveis (Mascarados/Pseudonimizados)
    'VITIMA_' || ID_CONTROLE_MORTE AS NOME_VITIMA,
    'MAE_' || ID_CONTROLE_MORTE AS MAE_VITIMA,
    'ALCUNHA_' || ID_CONTROLE_MORTE AS ALCUNHA_VITIMA,
    TRUNC(NASC_VITIMA, 'YEAR') AS NASC_VITIMA_ANO, -- Trunca para 01/01/YYYY
    
    -- 3. Localização (Supressão de dados exatos)
    'ENDERECO_SUPRIMIDO' AS ENDERECO_VITIMA,
    NULL AS LATITUDE_VITIMA,
    NULL AS LONGITUDE_VITIMA,
    AISP,
    RISP,
    BAIRRO_FATO,
    MUNICIPIO_FATO,
    LATITUDE,     -- Latitude do crime (liberado para mancha criminal)
    LONGITUDE,    -- Longitude do crime (liberado para mancha criminal)
    
    -- 4. Dados do Fato (Liberados)
    DATA_HORA_FATO,
    SUBJETIVIDADE,
    STATUS_NECROPSIA,
    INSTRUMENTO_UTILIZADO,
    MOTIVACAO,
    ALTER_DATE,
    
    -- 5. Textos Livres (Supressão preventiva de PII narrativo)
    'HISTORICO_PC_SUPRIMIDO' AS HISTORICO_PC,
    'HISTORICO_PM_SUPRIMIDO' AS HISTORICO_PM,
    'HISTORICO_IC_SUPRIMIDO' AS HISTORICO_IC

FROM 
    NEAC.CONTROLE_MORTE
WHERE 
    -- Filtro de todo o ano de 2025 (Considerando DATA_HORA_FATO como referência)
    DATA_HORA_FATO >= TO_DATE('2025-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
    AND DATA_HORA_FATO < TO_DATE('2026-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
    
ORDER BY 
    DATA_HORA_FATO ASC;
