# Resultados do Agente Delta v3 - Indicador MVI

## Regra Geral
**MVI = CVLI (Todos os Crimes + MILAE)**
RMNC = Resistência com Morte Não Criminal (MIP) - Não-MVI

A tabela CONTROLE_MORTE (CHENEAC) é o Gold Standard.
As demais bases (DAAS, CAD, IML) são fontes complementares consultadas manualmente pelos analistas.

## Composição da Base
| Categoria | Qtd |
|---|---|
| **Total Mestra** | **4682** |
| ✅ MVI Total (CVLI + MILAE) | **1104** |
|  └ CVLI / MILAE | 1104 |
|  └ RMNC (MIP / Não-MVI) | 1127 |
| Outros Não-MVI (Tentativa, Suicídio, etc) | 2451 |

## Alertas MVI (Apenas registros classificados como MVI)
- ⚠️ **BO PC Não Localizado no DAAS:** 21 casos
- ⚠️ **Natureza DAAS Divergente de MVI:** 15 casos
- ⚠️ **CAD não localizado no 190:** 2 casos
- 🚨 **IML com DO Vazia:** 873 casos
- ⚠️ **NIC Faltante (sem corpo registrado no IML):** 3 casos
- ⚠️ **Divergência de Nome de Vítima no IML:** 2 casos

### Detalhamento: Naturezas DAAS Divergentes nos MVIs
- `ENCONTRO DE CADÁVER`: 7 casos
- `CONSTRANGIMENTO ILEGAL`: 1 casos
- `CUMPRIMENTO DE MANDADO - PRISÃO - MORTE POR INTERVENÇÃO POLICIAL`: 1 casos
- `DESTRUIÇÃO, SUBTRAÇÃO OU OCULTAÇÃO DE CADÁVER`: 1 casos
- `ESTUPRO DE VULNERÁVEL - SE DA CONDUTA RESULTA MORTE`: 1 casos
- `POSSE IRREGULAR DE ARMA DE FOGO, ACESSÓRIO OU MUNIÇÃO DE USO PERMITIDO`: 1 casos
- `CUMPRIMENTO DE MANDADO - OUTROS`: 1 casos
- `DESAPARECIMENTO DE PESSOA | LOCALIZAÇÃO DE PESSOA DESAPARECIDA`: 1 casos
- `OUTROS FATOS ATÍPICOS`: 1 casos

---
Arquivo consolidado: `data/output/sentinela_relatorio_delta_2025.csv`
