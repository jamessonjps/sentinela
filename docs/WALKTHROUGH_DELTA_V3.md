# Resultados do Agente Delta v3 - Indicador MVI

## Regra Geral
**MVI = CVLI (Todos os Crimes + MILAE)**
RMNC = Resistência com Morte Não Criminal (MIP) - Não-MVI

A tabela CONTROLE_MORTE (CHENEAC) é o Gold Standard.
As demais bases (DAAS, CAD, IML) são fontes complementares consultadas manualmente pelos analistas.

## Composição da Base
| Categoria | Qtd |
|---|---|
| **Total Mestra** | **150** |
| ✅ MVI Total (CVLI + MILAE) | **88** |
|  └ CVLI / MILAE | 88 |
|  └ RMNC (MIP / Não-MVI) | 16 |
| Outros Não-MVI (Tentativa, Suicídio, etc) | 46 |

## Alertas MVI (Apenas registros classificados como MVI)
- ⚠️ **BO PC Não Localizado no DAAS:** 0 casos
- ⚠️ **Natureza DAAS Divergente de MVI:** 8 casos
- ⚠️ **CAD não localizado no 190:** 0 casos
- 🚨 **IML com DO Vazia:** 0 casos
- ⚠️ **NIC Faltante (sem corpo registrado no IML):** 16 casos
- ⚠️ **Divergência de Nome de Vítima no IML:** 7 casos

### Detalhamento: Naturezas DAAS Divergentes nos MVIs
- `FURTO DE VEICULO`: 8 casos

---
Arquivo consolidado: `data/output/sentinela_relatorio_delta_2025.csv`
