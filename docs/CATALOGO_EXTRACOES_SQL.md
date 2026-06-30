# Catálogo de Extrações SQL (LGPD Compliant)

Este documento centraliza todas as queries de extração de dados validadas para o projeto SENTINELA.
Todas as queries já contemplam o tratamento de anonimização (Supressão de PII) exigido pela LGPD e pelas normas de segurança do banco Oracle (`NEAC`).

---

## 1. Tabela Mestra: `CONTROLE_MORTE` (Estatística e Fatos)
- **Função**: Tabela primária que consolida mortes violentas (CVLI), tentativas e outras naturezas.
- **Mascaramento Aplicado**: `NOME_VITIMA`, `MAE_VITIMA`, `ALCUNHA_VITIMA`, textos livres (Históricos) e endereços residenciais da vítima suprimidos. 
- **Chaves de Integração (Liberadas)**: `BO_PC`, `NIC`, `CAD`, `NUM_OBITO`, `COD_PM_VITIMA`, `COD_PC_VITIMA`.
- **Geolocalização (Liberada)**: `LATITUDE` e `LONGITUDE` do fato preservadas para mapas de calor.

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

---

## 2. DAAS - Integração Policial Civil: `VW_BOLETIM_OCORRENCIA` (Boletins de Ocorrência Autorizados)
- **Função**: Tabela operacional primária de Boletins de Ocorrência da PC (Via View Autorizada do DAAS que não possui restrições de Redaction DBA).
- **Mascaramento Aplicado**: Colunas de texto narrativo (`RELATO_HISTORICO`), detalhes exatos de logradouro (`ED_LOGRADOURO`, `ED_NUMERO`, `ED_COMPLEMENTO`, `ED_CEP`, `DS_PTO_REF_OCORRENCIA`) foram suprimidos estritamente para prevenir exposição de detalhes descritivos e residenciais precisos.
- **Geolocalização (Liberada)**: `ED_LATITUDE_LONGITUDE` preservada para análises espaciais.
- **Chaves de Integração (Liberadas)**: A coluna **`NUM_BO` está completamente livre de supressão**, assim como o `CO_REGISTRO_NACIONAL`. Isso é essencial para o join com `CONTROLE_MORTE`.

```sql
SELECT 
    ID_PROCEDIMENTO, 
    NUM_BO, 
    CO_REGISTRO_NACIONAL, 
    NO_NATUREZA_OCORRENCIA, 
    DT_HORA_REGISTRO, 
    DT_OCORRENCIA, 
    HO_OCORRENCIA, 
    ID_UF, 
    NO_MUNICIPIO, 
    ED_BAIRRO, 
    'ENDERECO_SUPRIMIDO' AS ED_LOGRADOURO, 
    'NUM_SUPRIMIDO' AS ED_NUMERO, 
    'ENDERECO_SUPRIMIDO' AS ED_COMPLEMENTO, 
    'CEP_SUPRIMIDO' AS ED_CEP, 
    DS_LOCAL_OCORRENCIA, 
    'ENDERECO_SUPRIMIDO' AS DS_PTO_REF_OCORRENCIA, 
    ED_LATITUDE_LONGITUDE, 
    'TEXTO_SUPRIMIDO' AS RELATO_HISTORICO, 
    IN_SITUACAO_ATUAL, 
    IN_TIPO_PROCEDIMENTO, 
    TP_INSTAURACAO, 
    SN_TENTATIVA, 
    SN_MARIA_DA_PENHA, 
    SN_SIGILOSO, 
    DS_GRUPO_NATUREZA
FROM DAAS.VW_BOLETIM_OCORRENCIA
WHERE DT_OCORRENCIA >= TO_DATE('2025-01-01', 'YYYY-MM-DD')
  AND DT_OCORRENCIA <  TO_DATE('2026-01-01', 'YYYY-MM-DD');
```

*(Outros scripts serão apensados aqui à medida que exploramos novas tabelas, como `TB_NIC` no SGOU).*


## 3. IML - Polícia Científica (Status, Laudos e Cadavérico)
- **Função**: Bases da Polícia Científica para identificação de vítimas e causa da morte.
- **Mascaramento**: Nomes, Filiação, Endereços, RGs e textos periciais suprimidos.
- **Chaves (Liberadas)**: NIC, ID_CMORTE, NR_DECLARACAO_OBITO.

*(Os scripts detalhados encontram-se em scripts/anonimizacao/extracao_iml_cadaverico_2025.sql e extracao_iml_laudos_2025.sql)*


## 4. Ponte de Integração: Envolvidos (VISAO_PC_ENVOLVIDOS)
- **Função**: Resolve o problema de isolamento do IML, ligando o BO (Polícia Civil) ao ID da Vítima (Polícia Científica).
- **Chaves (Liberadas)**: NUMERO_BO e COD_ENVOLVIDO.


## 5. Polícia Militar - Despacho 190 (OVRCAD.VW_BO_GERAL_CAD)
- **Função**: Tabela operacional do sistema CAD (190). Contém as origens das chamadas de emergência, coordenadas geográficas da viatura e o despacho Policial.
- **Mascaramento Aplicado**: Textos livres do despachante, equipe policial (CPFs das guarnições) e endereços exatos ocultados rigorosamente.
- **Chave (Liberada)**: ID_OCOR (que será cruzada com a coluna CAD da tabela Mestra).
