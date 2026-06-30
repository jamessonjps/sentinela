# Profiling Completo: CONTROLE_MORTE (2025)

**Total de Registros Analisados:** 4682

## 1. Colunas 100% Nulas (Candidatas a Descarte)
- `ALTER_DATE`
- `COD_PM_VITIMA`
- `MOTIV_FINAL`
- `TIPO_PROCEDIMENTO`
- `ILICITO`
- `DATA_HORA_INSTAURACAO`
- `DATA_HORA_CONCLUSAO`
- `FORMA_CONCLUSAO`
- `DATA_ENVIO_JUS`
- `NUM_OBITO`
- `QTD_INQUERITO_PC`
- `BO_SISGOU`
- `ARMA_RESISTENCIA`
- `TP_USO_ARMA_RESISTENCIA`
- `STATUS_DELEGADO`
- `STATUS_PERICIA`
- `STATUS_NECROPSIA`
- `STATUS_MP`
- `GRUPO_MOTIVACAO`
- `COORD_STATUS`
- `STATUS_VCVLI`
- `SETOR_CENSITARIO_VIT`
- `LATITUDE_VITIMA`
- `LONGITUDE_VITIMA`
- `ALCATRAZ`
- `VTR_COORDENADA`
- `OPM_COORDENADA`
- `SITUACAO_PROCESSO_TJ`
- `ID_FATO`

## 2. Completude de Colunas Relevantes (Parcialmente Nulas)
- `SETOR_CENSITARIO_FATO`: 4681 nulos (99.98%)
- `COD_PC_VITIMA`: 4680 nulos (99.96%)
- `COMUNIDADE_VITIMA`: 4680 nulos (99.96%)
- `QTD_AUTORES`: 4679 nulos (99.94%)
- `VULNERABILIDADE_AUTOR`: 4666 nulos (99.66%)
- `SITUACAO_ESPECIAL`: 4656 nulos (99.44%)
- `QTD_TIROS`: 4646 nulos (99.23%)
- `DUPLICATED`: 4530 nulos (96.75%)
- `VULNERABILIDADE_VITIMA`: 3927 nulos (83.87%)
- `SITUACAO_INQUERITO`: 3866 nulos (82.57%)
- `HOMICIDIO_DETALHE`: 3528 nulos (75.35%)
- `INFO_CONFERE`: 3289 nulos (70.25%)
- `MOTIV_INICIAL`: 3108 nulos (66.38%)
- `LATITUDE`: 2969 nulos (63.41%)
- `LONGITUDE`: 2969 nulos (63.41%)
- `BO_PC`: 2349 nulos (50.17%)
- `OCUPACAO_VITIMA`: 2156 nulos (46.05%)
- `ESCOLARIDADE_VITIMA`: 2145 nulos (45.81%)
- `DESOVA`: 2116 nulos (45.19%)
- `ESTADO_CIVIL_VITIMA`: 1807 nulos (38.59%)
- `AFINIDADE_AGRESSOR`: 1727 nulos (36.89%)
- `GRUPO_ANTECEDENTE`: 1237 nulos (26.42%)
- `DATA_HORA_IML`: 1138 nulos (24.31%)
- `IML`: 1110 nulos (23.71%)
- `NIC`: 909 nulos (19.41%)
- `BAIRRO_VITIMA`: 742 nulos (15.85%)
- `DATA_HORA_UPDATE`: 695 nulos (14.84%)
- `CIDADE_VITIMA`: 681 nulos (14.55%)
- `NASC_VITIMA`: 616 nulos (13.16%)
- `STATUS_SOCORRO`: 558 nulos (11.92%)
- `CAD`: 424 nulos (9.06%)
- `IDADE_VITIMA`: 212 nulos (4.53%)
- `DATA_HORA_INSERT`: 152 nulos (3.25%)
- `LOCAL_FATO`: 113 nulos (2.41%)
- `SEXO_VITIMA`: 27 nulos (0.58%)
- `COR_RACA_VITIMA`: 3 nulos (0.06%)

## 3. Análise de Chaves de Integração
- `NIC`: 909 vazios (19.41%)
- `BO_PC`: 2349 vazios (50.17%)
- `CAD`: 424 vazios (9.06%)
- `COD_PM_VITIMA`: 4682 vazios (100.00%)
- `COD_PC_VITIMA`: 4680 vazios (99.96%)
- `NUM_OBITO`: 4682 vazios (100.00%)

## 4. Análise Geográfica
- `LATITUDE`: 2969 vazios (63.41%)
- `LONGITUDE`: 2969 vazios (63.41%)
- `BAIRRO_FATO`: 0 vazios (0.00%)
- `CIDADE_FATO`: 0 vazios (0.00%)

## 5. Variáveis Sociodemográficas e Criminais
- `SEXO_VITIMA`: 27 vazios (0.58%)
  - Categorias: Masculino, Feminino, NI
- `IDADE_VITIMA`: 212 vazios (4.53%)
  - (103 categorias únicas identificadas)
- `COR_RACA_VITIMA`: 3 vazios (0.06%)
  - Categorias: NI, Parda, Branca, Preta, Indígena, Amarela
- `SUBJETIVIDADE`: 0 vazios (0.00%)
  - Categorias: Tentativa, RMNC, CVLNI, CVLI, FLNI, Suicídio, Morte a Esclarecer, CVLI OUTROS, CVLI a Confirmar
- `INSTRUMENTO_UTILIZADO`: 0 vazios (0.00%)
  - Categorias: BRANCA, NI, ACIDENTE DE TRÂNSITO, PAF, OUTROS, AFOGAMENTO, CHOQUE ELÉTRICO, QUEIMADURA, ASFIXIA MECÂNICA, QUEDA, PAF/B, ATROPELAMENTO, ESPANCAMENTO, SOTERRAMENTO, INTOXICAÇÃO, ACIDENTE, OVERDOSE
