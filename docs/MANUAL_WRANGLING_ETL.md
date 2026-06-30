# Manual de Wrangling e Tratamento (ETL) - SENTINELA

Este manual documenta as regras de negócio definitivas para o tratamento de dados extraídos (após a anonimização na origem) para uso diário na plataforma SENTINELA.

## 1. Regras de Tratamento: `CONTROLE_MORTE` (Tabela Mestra)
**Objetivo:** Limpar chaves de integração e destacar alertas de qualidade.
- **Descarte:** Colunas com 100% de nulidade no profiling do ano vigente.
- **Limpeza de Chaves:** Remoção de formato decimal flutuante (ex: `1234.0` -> `1234`) nas colunas `NIC`, `CAD`, `BO_PC` e `COD_PC_VITIMA`.
- **Datas:** Padronização rigorosa para ISO 8601 (`YYYY-MM-DD HH:MM:SS`).
- **Alerta de Qualidade (Falta de BO):** 
  - Se a `SUBJETIVIDADE` for crítica (CVLI, TENTATIVA, HOMICIDIO, LATROCINIO, FEMINICIDIO) **E** a coluna `BO_PC` for Nula -> Flag `CRITICO_FALTA_BO`.

---

## 2. Regras de Tratamento: `TB_PPE / VW_BOLETIM_OCORRENCIA` (DAAS - Polícia Civil)
**Objetivo:** Achatamento (Flattening) para relação 1:1, garantindo que o cruzamento com a tabela mestra não exploda a volumetria.
- **Descarte:** Colunas com 100% de nulidade.
- **Desduplicação de `NUM_BO` (Agrupamento/Flattening):**
  - Ocorrências policiais frequentemente registram múltiplas naturezas criminais ou aditamentos (múltiplos `ID_PROCEDIMENTO`). O Wrangling agrupa todas as linhas pelo mesmo `NUM_BO`.
  - **Naturezas do Crime (`NO_NATUREZA_OCORRENCIA`, `DS_GRUPO_NATUREZA`):** Agregadas em formato de lista textual, separadas por barra ou vírgula (ex: `ROUBO | AMEAÇA`).
  - **Agravantes (`SN_TENTATIVA`, `SN_MARIA_DA_PENHA`):** Regra gulosa (MAX). Se qualquer linha do BO possuir `1.0`, o BO consolidado receberá `1.0`.
  - **Status e Tempos (`IN_SITUACAO_ATUAL`, `DT_HORA_REGISTRO`):** Coleta-se o registro mais recente (ou a concatenação única) garantindo a posição final da delegacia.
  - **Geolocalização (`ED_LATITUDE_LONGITUDE`):** Preserva-se a primeira coordenada não nula válida para aquele BO.
