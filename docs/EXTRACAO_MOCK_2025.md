# Documentação de Extração de Dados - Ano 2025 (Mock LGPD)

## Objetivo
Descrever a query SQL utilizada para extração dos dados da tabela `NEAC.CONTROLE_MORTE` referente ao ano de 2025, garantindo que os dados sejam anonimizados na origem, em estrita conformidade com as regras da LGPD e os requisitos do projeto SENTINELA.

## Regras de Anonimização Aplicadas

Para garantir a proteção dos dados pessoais sensíveis (PII), as seguintes regras foram incorporadas diretamente na cláusula `SELECT`:

1. **Nomes Próprios e Identificadores Familiares**: 
   - `NOME_VITIMA` -> `'VITIMA_' || ID_CONTROLE_MORTE`
   - `MAE_VITIMA` -> `'MAE_' || ID_CONTROLE_MORTE`
   - `ALCUNHA_VITIMA` -> `'ALCUNHA_' || ID_CONTROLE_MORTE`
2. **Datas Relacionadas a Pessoas**: 
   - `NASC_VITIMA` -> Truncado para o ano (`TRUNC(NASC_VITIMA, 'YEAR')`) para manter a idade aproximada sem revelar o dia/mês de nascimento exato.
   - `ENDERECO_FATO`, `ENDERECO_VITIMA`, `PT_REF_FATO`, `PT_REF_VITIMA` -> `'ENDERECO_SUPRIMIDO'`
   - Coordenadas da vítima e da viatura (`LATITUDE_VITIMA`, `LONGITUDE_VITIMA`, `VTR_COORDENADA`, `OPM_COORDENADA`) -> `NULL`
   - As coordenadas do FATO (`LATITUDE` e `LONGITUDE`) foram liberadas para permitir a geração de mapas de calor.
4. **Textos Livres (CLOBs e Históricos)**:
   - Os campos que possam conter descrições ricas que identificariam pessoas (ex: `OBSERVACOES`, `RELATORIO_IC`, `ANTECEDENTES_VITIMA`, `INFO_COMP_INQUERITO`, `HISTORICO_PC`, `HISTORICO_PM`, `HISTORICO_IC`, `OBS_RESISTENCIA`, `OBS_GEO`, `ANTECEDENTE_SISPOL`) foram substituídos pela string `'TEXTO_SUPRIMIDO'`.
   - Foram ocultados e substituídos por strings genéricas os campos como `NUM_INQUERITO_PC`, `NUM_PROC_JUSTICA`, `CPP`, `LINK_SITE`, `ID_DUPLICATED`, `SERVIDOR_RESPONSAVEL`, `BO_SISGOU`.
   - As chaves de integração e identificadores externos (`BO_PC`, `NIC`, `CAD`, `NUM_OBITO`, `COD_PM_VITIMA`, `COD_PC_VITIMA`) foram **liberadas** para cruzamentos.

## Filtro Utilizado
- Apenas os registros onde o fato ocorreu em 2025: `DATA_HORA_FATO >= TO_DATE('2025-01-01', 'YYYY-MM-DD')` e `< TO_DATE('2026-01-01', 'YYYY-MM-DD')`.

## Script SQL Completo

O script completo pode ser localizado no arquivo: `scripts/anonimizacao/extracao_completa_2025.sql`

```sql
SELECT 
    INFO_CONFERE, 
    HOMICIDIO_DETALHE, 
    'VITIMA_' || TO_CHAR(ID_CONTROLE_MORTE) AS NOME_VITIMA, 
    'ALCUNHA_' || TO_CHAR(ID_CONTROLE_MORTE) AS ALCUNHA_VITIMA, 
    SEXO_VITIMA, 
    IDADE_VITIMA, 
    ESTADO_CIVIL_VITIMA, 
    OCUPACAO_VITIMA, 
    ESCOLARIDADE_VITIMA, 
    BO_PC, 
    SUBJETIVIDADE, 
    SUBJETIVIDADE_COMPLEMENTAR, 
    INSTRUMENTO_UTILIZADO, 
    QTD_TIROS, 
    'TEXTO_SUPRIMIDO' AS OBSERVACOES, 
    DATA_HORA_FATO, 
    COR_RACA_VITIMA, 
    CIDADE_FATO, 
    BAIRRO_FATO, 
    'ENDERECO_SUPRIMIDO' AS ENDERECO_FATO, 
    LOCAL_FATO, 
    IML, 
    'MAE_' || TO_CHAR(ID_CONTROLE_MORTE) AS MAE_VITIMA, 
    AFINIDADE_AGRESSOR, 
    'TEXTO_SUPRIMIDO' AS RELATORIO_IC, 
    'URL_SUPRIMIDA' AS LINK_SITE, 
    AISP, 
    RISP, 
    LATITUDE, 
    LONGITUDE, 
    'ENDERECO_SUPRIMIDO' AS PT_REF_FATO, 
    ID_CONTROLE_MORTE, 
    QTD_AUTORES, 
    SITUACAO_ESPECIAL, 
    'TEXTO_SUPRIMIDO' AS ANTECEDENTES_VITIMA, 
    VULNERABILIDADE_VITIMA, 
    TRUNC(NASC_VITIMA, 'YEAR') AS NASC_VITIMA, 
    DATA_HORA_IML, 
    ALTER_DATE, 
    COD_PM_VITIMA, 
    COD_PC_VITIMA, 
    CIDADE_VITIMA, 
    BAIRRO_VITIMA, 
    'ENDERECO_SUPRIMIDO' AS ENDERECO_VITIMA, 
    'ENDERECO_SUPRIMIDO' AS PT_REF_VITIMA, 
    COMUNIDADE_VITIMA, 
    STATUS_SOCORRO, 
    MOTIV_INICIAL, 
    MOTIV_FINAL, 
    TIPO_PROCEDIMENTO, 
    ILICITO, 
    DATA_HORA_INSTAURACAO, 
    DATA_HORA_CONCLUSAO, 
    FORMA_CONCLUSAO, 
    SITUACAO_INQUERITO, 
    'NUM_SUPRIMIDO' AS NUM_INQUERITO_PC, 
    DATA_ENVIO_JUS, 
    'NUM_SUPRIMIDO' AS NUM_PROC_JUSTICA, 
    'TEXTO_SUPRIMIDO' AS INFO_COMP_INQUERITO, 
    CAD, 
    NUM_OBITO, 
    'TEXTO_SUPRIMIDO' AS HISTORICO_PC, 
    'TEXTO_SUPRIMIDO' AS HISTORICO_PM, 
    'TEXTO_SUPRIMIDO' AS HISTORICO_IC, 
    QTD_INQUERITO_PC, 
    'NUM_SUPRIMIDO' AS CPP, 
    CAST(NULL AS NUMBER) AS BO_SISGOU, 
    NIC, 
    ARMA_RESISTENCIA, 
    TP_USO_ARMA_RESISTENCIA, 
    STATUS_DELEGADO, 
    STATUS_PERICIA, 
    STATUS_NECROPSIA, 
    'SERVIDOR_SUPRIMIDO' AS SERVIDOR_RESPONSAVEL, 
    STATUS_MP, 
    'TEXTO_SUPRIMIDO' AS OBS_RESISTENCIA, 
    DATA_HORA_INSERT, 
    DATA_HORA_UPDATE, 
    DESOVA, 
    'TEXTO_SUPRIMIDO' AS OBS_GEO, 
    GRUPO_ANTECEDENTE, 
    GRUPO_MOTIVACAO, 
    COORD_STATUS, 
    STATUS_VCVLI, 
    GEO_STATUS, 
    DUPLICATED, 
    'ID_SUPRIMIDO' AS ID_DUPLICATED, 
    SETOR_CENSITARIO_FATO, 
    SETOR_CENSITARIO_VIT, 
    CAST(NULL AS NUMBER) AS LATITUDE_VITIMA, 
    CAST(NULL AS NUMBER) AS LONGITUDE_VITIMA, 
    'TEXTO_SUPRIMIDO' AS ANTECEDENTE_SISPOL, 
    ALCATRAZ, 
    CAST(NULL AS VARCHAR2(255)) AS VTR_COORDENADA, 
    CAST(NULL AS VARCHAR2(255)) AS OPM_COORDENADA, 
    SITUACAO_PROCESSO_TJ, 
    VULNERABILIDADE_AUTOR, 
    ID_FATO
FROM NEAC.CONTROLE_MORTE
WHERE DATA_HORA_FATO >= TO_DATE('2025-01-01', 'YYYY-MM-DD')
  AND DATA_HORA_FATO <  TO_DATE('2026-01-01', 'YYYY-MM-DD');
```
