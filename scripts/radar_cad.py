"""
SENTINELA — Radar de Ocorrências CAD (190 PM)
============================================
Identifica ocorrências com natureza CVLI-like no despacho 190 (PM)
que AINDA NÃO possuem vínculo com a base consolidada CONTROLE_MORTE (CHENEAC).

Regras de Classificação de Prioridade:
  ALTA (3):  Homicídio, Feminicídio, Latrocínio, Lesão Corporal Seguida de Morte
  MÉDIA (2): Tentativa de Homicídio, Tentativa de Feminicídio, Intervenção Policial
  BAIXA (1): Morte a Esclarecer, Resistência, Homicídio Culposo, Morte por Acidente

⚠️  PROTEÇÃO DE BASE DE DADOS (Produção):
  - Este script opera SOMENTE com leitura (SELECT/READ ONLY)
  - Em produção: connection pooling, cache TTL, e rate limiting
  - Nunca realiza INSERT/UPDATE/DELETE nas bases fonte (NEAC, CAD, SGOU)
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DE PADRÕES DE NATUREZA CVLI-LIKE
# ============================================================

# Padrões regex para identificar naturezas CVLI-like no CAD
PADROES_CVLI = {
    'ALTA': [
        r'HOMIC[IÍ]DIO(?!\s+CULPOSO)(?!\s+DECOR)',  # Homicídio (exceto culposo e decorrente de intervenção)
        r'FEMINIC[IÍ]DIO(?!\s+TENT)',                  # Feminicídio (exceto tentativa)
        r'LATROC[IÍ]NIO(?!\s+TENT)',                   # Latrocínio (exceto tentativa)
        r'ROUBO\s+(?:COM|CO)\s+RESULTADO\s+MORTE',     # Roubo com/co resultado morte
        r'LES[AÃ]O\s+CORPORAL\s+SEGUIDA\s+DE\s+MORTE', # Lesão corporal seguida de morte
        r'HOMIC[IÍ]DIO\s+DECOR.*LES[AÃ]O',            # Homicídio decorrente de lesão
    ],
    'MEDIA': [
        r'TENTATIVA\s+DE\s+HOMIC[IÍ]DIO',             # Tentativa de homicídio
        r'TENTATIVA\s+DE\s+FEMINIC[IÍ]DIO',           # Tentativa de feminicídio
        r'LATROC[IÍ]NIO\s+TENTAD[OO]',                # Latrocínio tentado/tentando
        r'DISPARO\s+DE\s+ARMA\s+DE\s+FOGO',           # Disparo de arma de fogo
        r'HOMIC[IÍ]DIO\s+(?:EM\s+)?DECOR.*INTERVEN',  # Homicídio em decorrência de intervenção policial
    ],
    'BAIXA': [
        r'MORTE\s+A\s+ESCLARECER',                    # Morte a esclarecer (ambígua)
        r'RESIST[EÊ]NCIA',                            # Resistência
        r'HOMIC[IÍ]DIO\s+CULPOSO',                    # Homicídio culposo ao volante
        r'MORTE\s+POR\s+ACIDENTE',                    # Morte por acidente
    ]
}

# Classificação de confirmação
CLASSIFICACAO_MAP = {
    'ALTA': 'CVLI_CONFIRMADO',
    'MEDIA': 'CVLI_PROVAVEL',
    'BAIXA': 'A_ESCLARECER'
}

PRIORIDADE_MAP = {
    'ALTA': 3,
    'MEDIA': 2,
    'BAIXA': 1
}


def classificar_natureza(natureza_str: str) -> tuple:
    """
    Classifica uma natureza de atendimento CAD em prioridade e classificação.
    Retorna (prioridade_int, classificacao_str, nivel_str) ou None se não for CVLI-like.
    
    A ordem de verificação é MÉDIA antes de ALTA para que padrões mais 
    específicos (ex: TENTATIVA DE HOMICÍDIO) sejam capturados antes dos
    padrões mais gerais (ex: HOMICÍDIO).
    """
    if not isinstance(natureza_str, str):
        return None
    
    nat_upper = natureza_str.strip().upper()
    
    # Verificar padrões em ordem: MÉDIA primeiro (mais específicos),
    # depois ALTA (mais gerais), depois BAIXA
    for nivel in ['MEDIA', 'ALTA', 'BAIXA']:
        for padrao in PADROES_CVLI[nivel]:
            if re.search(padrao, nat_upper):
                return (PRIORIDADE_MAP[nivel], CLASSIFICACAO_MAP[nivel], nivel)
    
    return None


def obter_turno(dt_str: str) -> str:
    """
    Calcula a qual turno operacional de 4 horas a ocorrência pertence.
    Ex: 00:00-04:00 (T1), 04:00-08:00 (T2), etc.
    """
    if not isinstance(dt_str, str) or len(dt_str) < 13:
        return "T1 (00:00 - 04:00)"
    try:
        # Extrai a hora: '2025-01-01 04:53:18.000' -> hora é '04'
        hora = int(dt_str[11:13])
        if 0 <= hora < 4:
            return "T1 (00:00 - 04:00)"
        elif 4 <= hora < 8:
            return "T2 (04:00 - 08:00)"
        elif 8 <= hora < 12:
            return "T3 (08:00 - 12:00)"
        elif 12 <= hora < 16:
            return "T4 (12:00 - 16:00)"
        elif 16 <= hora < 20:
            return "T5 (16:00 - 20:00)"
        else:
            return "T6 (20:00 - 00:00)"
    except Exception:
        return "T1 (00:00 - 04:00)"



def run_radar_cad():
    """
    Executa a detecção do Radar CAD:
    1. Carrega a base CAD (190 PM) e a base consolidada (CONTROLE_MORTE)
    2. Filtra naturezas CVLI-like no CAD
    3. Remove registros que já possuem vínculo na CONTROLE_MORTE
    4. Classifica por prioridade e exporta o resultado
    """
    print("=" * 60)
    print("  SENTINELA — Radar de Ocorrências CAD (190 PM)")
    print(f"  Execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Carregar bases
    cad_path = "data/mock/extracao_pm_cad_2025.csv"
    cm_path = "data/mock/controle_morte_2025_limpo.csv"
    
    if not os.path.exists(cad_path):
        print(f"ERRO: Arquivo CAD não encontrado: {cad_path}")
        return
    if not os.path.exists(cm_path):
        print(f"ERRO: Arquivo Controle Morte não encontrado: {cm_path}")
        return
    
    print("\n[1/5] Carregando base CAD (190 PM)...")
    colunas_cad = [
        'ID_OCOR', 'DS_NATUREZA_ATEND', 'DS_GRUPO_CRIME_ATEND',
        'DT_OCOR', 'BAIRRO', 'CIDADE',
        'NR_COOR_LATD', 'NR_COOR_LONG',
        'DS_STATUS', 'DS_OCOR'
    ]
    df_cad = pd.read_csv(cad_path, usecols=colunas_cad, low_memory=False)
    print(f"  → {len(df_cad):,} registros carregados do CAD")
    
    print("\n[2/5] Carregando base Controle Morte (Gold Standard)...")
    df_cm = pd.read_csv(cm_path, usecols=['CAD'], low_memory=False)
    df_cm['CAD'] = pd.to_numeric(df_cm['CAD'], errors='coerce')
    cad_ids_cm = set(df_cm['CAD'].dropna().astype(int))
    print(f"  → {len(cad_ids_cm):,} IDs CAD vinculados na CONTROLE_MORTE")
    
    # 2. Classificar naturezas e descrições do CAD
    print("\n[3/5] Classificando naturezas e descrições do CAD...")
    
    prioridades = []
    classificacoes_radar = []
    niveis = []
    
    for idx, row in df_cad.iterrows():
        nat = row['DS_NATUREZA_ATEND']
        txt = row['DS_OCOR']
        
        # Classificação por natureza
        res = classificar_natureza(nat)
        
        # Heurística do texto do despachante contendo 'IML'
        contem_iml = False
        if isinstance(txt, str) and 'IML' in txt.upper():
            contem_iml = True
            
        if res:
            prio, class_str, nivel = res
            # Se contiver IML, elevamos para ALTA se for menor
            if contem_iml and prio < 3:
                prio = 3
                class_str = 'CVLI_CONFIRMADO'
                nivel = 'ALTA'
            prioridades.append(prio)
            classificacoes_radar.append(class_str)
            niveis.append(nivel)
        elif contem_iml:
            # Caso a natureza não seja CVLI-like, mas o texto contenha IML (e.g. Morte a Esclarecer)
            # Classificamos como MÉDIA prioridade de Radar
            prioridades.append(2)
            classificacoes_radar.append('CVLI_PROVAVEL')
            niveis.append('MEDIA')
        else:
            prioridades.append(None)
            classificacoes_radar.append(None)
            niveis.append(None)
            
    df_cad['PRIORIDADE_RADAR'] = prioridades
    df_cad['CLASSIFICACAO_RADAR'] = classificacoes_radar
    df_cad['NIVEL_RADAR'] = niveis
    
    # Filtrar apenas os que foram classificados
    df_cvli = df_cad[df_cad['PRIORIDADE_RADAR'].notna()].copy()
    df_cvli['PRIORIDADE_RADAR'] = df_cvli['PRIORIDADE_RADAR'].astype(int)
    
    print(f"  → {len(df_cvli):,} ocorrências CVLI-like ou contendo IML identificadas")
    print(f"    • ALTA (CVLI Confirmado):  {(df_cvli['NIVEL_RADAR'] == 'ALTA').sum():,}")
    print(f"    • MÉDIA (CVLI Provável):   {(df_cvli['NIVEL_RADAR'] == 'MEDIA').sum():,}")
    print(f"    • BAIXA (A Esclarecer):    {(df_cvli['NIVEL_RADAR'] == 'BAIXA').sum():,}")
    
    # 3. Classificar registros pelo vínculo na CONTROLE_MORTE
    print("\n[4/5] Classificando status de vínculo na CONTROLE_MORTE...")
    
    df_cvli['ID_OCOR'] = pd.to_numeric(df_cvli['ID_OCOR'], errors='coerce')
    df_radar = df_cvli.copy()
    
    # Classificação de status baseada na presença na CM
    df_radar['STATUS_RADAR'] = df_radar['ID_OCOR'].apply(
        lambda x: 'Validado' if x in cad_ids_cm else 'Novo'
    )
    df_radar['DT_VALIDACAO'] = df_radar['STATUS_RADAR'].apply(
        lambda x: datetime.now().strftime('%Y-%m-%d %H:%M:%S') if x == 'Validado' else None
    )
    df_radar['DT_DETECCAO'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_radar['TURNO'] = df_radar['DT_OCOR'].apply(obter_turno)
    df_radar['TEM_GPS'] = (df_radar['NR_COOR_LATD'].notna() & 
                           df_radar['NR_COOR_LONG'].notna() &
                           (df_radar['NR_COOR_LATD'] != 0) &
                           (df_radar['NR_COOR_LONG'] != 0))
    
    # Deduplicar por ID_OCOR (pode ter despachos duplicados)
    df_radar = df_radar.drop_duplicates(subset=['ID_OCOR'])
    
    print(f"  → {len(df_radar):,} ocorrências totais classificadas no RADAR")
    print(f"    • NOVAS (Sem vínculo):     {(df_radar['STATUS_RADAR'] == 'Novo').sum():,}")
    print(f"    • VALIDADAS (Com vínculo):  {(df_radar['STATUS_RADAR'] == 'Validado').sum():,}")
    print(f"    • Com GPS: {df_radar['TEM_GPS'].sum():,}")
    print(f"    • Sem GPS: {(~df_radar['TEM_GPS']).sum():,}")
    
    # 4. Distribuição detalhada
    print("\n  Distribuição por Natureza:")
    dist = df_radar.groupby(['NIVEL_RADAR', 'DS_NATUREZA_ATEND']).size().reset_index(name='QTD')
    dist = dist.sort_values(['NIVEL_RADAR', 'QTD'], ascending=[True, False])
    for _, row in dist.iterrows():
        print(f"    [{row['NIVEL_RADAR']:>5}] {row['DS_NATUREZA_ATEND']}: {row['QTD']}")
    
    print("\n  Top 10 Cidades:")
    top_cidades = df_radar['CIDADE'].value_counts().head(10)
    for cidade, qtd in top_cidades.items():
        print(f"    {cidade}: {qtd}")
    
    # 5. Exportar
    print("\n[5/5] Exportando CSV do Radar...")
    
    colunas_export = [
        'ID_OCOR', 'DS_NATUREZA_ATEND', 'DS_GRUPO_CRIME_ATEND',
        'DT_OCOR', 'TURNO', 'CIDADE', 'BAIRRO',
        'NR_COOR_LATD', 'NR_COOR_LONG', 'TEM_GPS',
        'DS_STATUS', 'DS_OCOR',
        'PRIORIDADE_RADAR', 'CLASSIFICACAO_RADAR', 'NIVEL_RADAR',
        'STATUS_RADAR', 'DT_DETECCAO', 'DT_VALIDACAO'
    ]
    
    os.makedirs("data/output", exist_ok=True)
    output_path = "data/output/sentinela_radar_cad_2025.csv"
    df_radar[colunas_export].to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"  → Salvo em: {output_path}")
    print(f"  → Total de registros: {len(df_radar):,}")
    print("\n" + "=" * 60)
    print("  Radar CAD concluído com sucesso!")
    print("=" * 60)
    
    return df_radar


if __name__ == "__main__":
    run_radar_cad()
