# Profiling Forense Avançado (Laudos e Cadavérico) 2025

## 1. Análise da Base CADAVÉRICO (SGOU)
**Total de Linhas Analisadas:** 3769

### Qualidade da Chave `NIC`
- Vazios: 0 (0.00%)
- Valores Únicos: 3767 (Mede a taxa de duplicidade)

### Métrica de Ouro: `NR_DECLARACAO_OBITO`
- Vazios: 2723 (72.25%)

### Top 10 Colunas com Menos Preenchimento (Vazias)
- `RG_UF`: 3716 nulos (98.59%)
- `NR_DECLARACAO_OBITO`: 2723 nulos (72.25%)
- `REQUERENTE_OUTROS`: 1881 nulos (49.91%)
- `ORG_EXP`: 801 nulos (21.25%)
- `BAIRRO`: 491 nulos (13.03%)
- `MUNICIPIO`: 328 nulos (8.70%)
- `NATURALIDADE`: 256 nulos (6.79%)
- `ETNIA`: 200 nulos (5.31%)
- `NASCIMENTO`: 95 nulos (2.52%)
- `EST_CIVIL`: 64 nulos (1.70%)

---

## 2. Análise da Base de LAUDOS (IML)
**Total de Linhas Analisadas:** 2023

### Qualidade da Chave `NIC`
- Vazios: 2003 (99.01%)
- Valores Únicos: 20 (Mede a taxa de duplicidade)

### Top 10 Colunas com Menos Preenchimento (Vazias)
- `NIC`: 2003 nulos (99.01%)
- `MUNICIPIO`: 316 nulos (15.62%)
- `NATURALIDADE`: 175 nulos (8.65%)
- `DATA_NASCIMENTO`: 65 nulos (3.21%)
- `DATA_EXAME`: 24 nulos (1.19%)

---

