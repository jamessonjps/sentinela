# Documentação de Extração de Dados - DAAS (Mock LGPD 2025)

## Objetivo
Descrever a query SQL utilizada para extração dos dados de Boletins de Ocorrência da Polícia Civil através da View Autorizada (`DAAS.VW_BOLETIM_OCORRENCIA`) referente ao ano de 2025. O objetivo é garantir o cruzamento de dados com a Tabela Mestra enquanto mantemos conformidade com a LGPD.

## Regras de Anonimização Aplicadas

Para garantir a proteção dos dados sensíveis, aplicou-se o mascaramento sobre as colunas da View:

1. **Textos Livres (Históricos de Ocorrência)**:
   - A coluna `RELATO_HISTORICO` foi substituída pela string `'TEXTO_SUPRIMIDO'`, pois carrega a narrativa policial com possíveis PIIs.
2. **Endereços Exatos Residenciais/Logradouro**:
   - `ED_LOGRADOURO`, `ED_COMPLEMENTO`, `DS_PTO_REF_OCORRENCIA` -> `'ENDERECO_SUPRIMIDO'`
   - `ED_NUMERO` -> `'NUM_SUPRIMIDO'`
   - `ED_CEP` -> `'CEP_SUPRIMIDO'`
3. **Geolocalização do Crime Preservada**:
   - `ED_LATITUDE_LONGITUDE` -> Mantida intacta para fins analíticos de mancha criminal.
4. **Chaves Preservadas para Integração**:
   - A coluna `NUM_BO` (livre de máscaras) e a coluna `CO_REGISTRO_NACIONAL` foram preservadas intactas, permitindo o cruzamento com `BO_PC` da `CONTROLE_MORTE`.

## Script SQL Completo

O script completo pode ser localizado no arquivo: `scripts/anonimizacao/extracao_ppe_2025.sql`
