# Relatório de Profiling: Amostra CONTROLE_MORTE (Ano 2025)

**Total de Registros Analisados:** 4.682 casos (Mock).

## 1. Completude e Nulos (Ação Necessária)
O nível de preenchimento mostra lacunas cruciais na origem dos dados:
* **`BO_PC`**: 50,17% Vazio. (Crítico para cruzar com a Polícia Civil).
* **`NIC`**: 19,41% Vazio. (Significa que ~80% já evoluíram para o IML ou nasceram como CVLI).
* **`CAD`**: 9,06% Vazio. (Quase todos os casos possuem registro na Polícia Militar).
* **Geolocalização do Fato (`LATITUDE` / `LONGITUDE`)**: 63,41% Vazios. A inteligência espacial (Mancha Criminal) está cega em grande parte de 2025.
* **Motivação Inicial**: 66,38% Vazio.
* **Colunas 100% Vazias (Inúteis nesta amostra)**: `STATUS_NECROPSIA`, `MOTIV_FINAL`, `ALTER_DATE`, `LATITUDE_VITIMA`, `LONGITUDE_VITIMA`. Podemos descartá-las com `drop()`.

## 2. Inconsistência de Formatação (Chaves)
* O Pandas identificou as chaves `NIC` e `CAD` como numéricas (float), o que gera um `.0` no final quando há dados ausentes. No Wrangling, precisaremos converter essas colunas garantindo que fiquem como **Strings limpas e inteiras** (ex: `12345` e não `12345.0`).
* Foi detectado 1 registro de `BO_PC` com caractere especial fora do padrão da SSP.

## 3. Padrão de Datas
* 100% dos dados da coluna `DATA_HORA_FATO` vieram acompanhados de milissegundos (ex: `2025-01-01 03:24:00.000`).
* No Wrangling, teremos que truncar esses milissegundos ou formatar explicitamente para `YYYY-MM-DD HH:MM:SS` usando `pd.to_datetime()`.

## 4. Análise de Texto (Subjetividade e Local)
* Encontramos 139 categorias de bairros diferentes. Provavelmente há fragmentação (erros de digitação, espaços). O Sentinela terá que passar pelo dicionário `TRATAR_BAIRROS` na Frente 2.
* A coluna `SUBJETIVIDADE` apresentou 9 classificações únicas, que estão consistentes, mas a `SUBJETIVIDADE_COMPLEMENTAR` não estava no SELECT (conforme seu aviso anterior) e precisaremos ficar atentos se ela reaparecer.
