import pandas as pd
import numpy as np
import os

# ============================================================
# REGRA GERAL DO INDICADOR:
#   MVI = CVLI + RMNC (Resistência com Resultado Morte)
#
# A CONTROLE_MORTE é o Gold Standard consolidado pelo CHENEAC.
# A coluna SUBJETIVIDADE classifica cada registro:
#   - CVLI, CVLI OUTROS, CVLI A CONFIRMAR = Crimes Violentos Letais Intencionais
#   - RMNC = Resistência com Morte Não Criminal (MIP)
#   - TENTATIVA = Tentativa de Homicídio (acompanhamento)
#   - CVLNI, FLNI, SUICÍDIO, MORTE A ESCLARECER = Não-MVI
#
# As outras tabelas (DAAS, CAD, IML) são fontes complementares.
# O analista do CHENEAC consulta cada uma delas individualmente
# e preenche manualmente a CONTROLE_MORTE.
# ============================================================

SUBJETIVIDADES_MVI = ['CVLI', 'CVLI OUTROS', 'CVLI A CONFIRMAR']

def run_delta_v3():
    print("=== AGENTE DELTA v3 (MVI = CVLI + MILAE) ===")
    
    # 1. Carregar as bases
    print("Carregando bases...")
    df_mestra = pd.read_csv("data/mock/controle_morte_2025_limpo.csv", low_memory=False)
    df_daas = pd.read_csv("data/mock/extracao_ppe_2025_limpo.csv", low_memory=False)
    df_cad = pd.read_csv("data/mock/extracao_pm_cad_2025.csv", low_memory=False)
    df_iml_status = pd.read_csv("data/mock/extracao_iml_2025.csv", low_memory=False)
    df_iml_cad = pd.read_csv("data/mock/extracao_iml_cadaverico_2025.csv", low_memory=False)
    
    # 2. Classificar MVI na Mestra (coluna SUBJETIVIDADE)
    # Obs: MILAE (Morte por Intervenção de Agente do Estado) está classificado como CVLI na mestra.
    df_mestra['EH_MVI'] = df_mestra['SUBJETIVIDADE'].isin(SUBJETIVIDADES_MVI)
    df_mestra['TIPO_MVI'] = np.where(
        df_mestra['SUBJETIVIDADE'].isin(['CVLI', 'CVLI OUTROS', 'CVLI A CONFIRMAR']), 'CVLI',
        np.where(df_mestra['SUBJETIVIDADE'] == 'RMNC', 'RMNC_MIP', 'NAO_MVI')
    )
    
    total_mestra = len(df_mestra)
    total_mvi = df_mestra['EH_MVI'].sum()
    total_cvli = (df_mestra['TIPO_MVI'] == 'CVLI').sum()
    total_rmnc = (df_mestra['TIPO_MVI'] == 'RMNC_MIP').sum()
    total_nao_mvi = total_mestra - total_mvi
    
    print(f"Mestra: {total_mestra} registros | MVI: {total_mvi} (CVLI/MILAE) | RMNC (MIP): {total_rmnc} | Outros Não-MVI: {total_nao_mvi - total_rmnc}")
    
    # 3. Tratamento de Chaves
    df_mestra['BO_PC'] = df_mestra['BO_PC'].astype(str).str.strip().str.upper()
    df_mestra['CAD'] = pd.to_numeric(df_mestra['CAD'], errors='coerce')
    df_mestra['ID_CONTROLE_MORTE'] = pd.to_numeric(df_mestra['ID_CONTROLE_MORTE'], errors='coerce')
    
    df_daas['NUM_BO'] = df_daas['NUM_BO'].astype(str).str.strip().str.upper()
    df_cad['ID_OCOR'] = pd.to_numeric(df_cad['ID_OCOR'], errors='coerce')
    df_iml_status['ID_CMORTE'] = pd.to_numeric(df_iml_status['ID_CMORTE'], errors='coerce')
    df_iml_status['NIC_IML'] = df_iml_status['NIC_IML'].astype(str).str.strip()
    df_iml_cad['NIC'] = df_iml_cad['NIC'].astype(str).str.strip()
    
    # 4. Cruzamentos (Left Joins)
    print("Cruzando Mestra <-> DAAS...")
    df_delta = pd.merge(df_mestra, df_daas, left_on='BO_PC', right_on='NUM_BO', how='left', suffixes=('', '_DAAS'))
    
    print("Cruzando Mestra <-> CAD...")
    df_delta = pd.merge(df_delta, df_cad, left_on='CAD', right_on='ID_OCOR', how='left', suffixes=('', '_CAD'))
    
    print("Cruzando Mestra <-> IML Status...")
    df_delta = pd.merge(df_delta, df_iml_status, left_on='ID_CONTROLE_MORTE', right_on='ID_CMORTE', how='left', suffixes=('', '_IML_STAT'))
    
    print("Cruzando Mestra <-> IML Cadavérico...")
    df_delta = pd.merge(df_delta, df_iml_cad, left_on='NIC_IML', right_on='NIC', how='left', suffixes=('', '_IML_CAD'))
    
    # 5. ALERTAS (Focados nos registros MVI)
    print("Gerando Alertas Sentinela v3 (foco MVI)...")
    
    # Alerta 1: BO não localizado no DAAS
    tem_bopc = (df_delta['BO_PC'].notnull()) & (df_delta['BO_PC'] != 'NAN') & (df_delta['BO_PC'] != '')
    nao_achou_daas = df_delta['NUM_BO'].isnull()
    df_delta['ALERTA_BO_INEXISTENTE'] = np.where(tem_bopc & nao_achou_daas, 'SIM', 'NAO')
    
    # Alerta 2: Natureza DAAS divergente do esperado para MVI
    # Para registros MVI na mestra, qual natureza o DAAS registrou?
    natureza_upper = df_delta['NO_NATUREZA_OCORRENCIA'].astype(str).str.upper()
    padroes_mvi_daas = ['HOMIC', 'FEMINIC', 'LATROC', 'ROUBO.*MORTE',
                         'LESÃO CORPORAL SEGUIDA DE MORTE', 'LESAO CORPORAL SEGUIDA DE MORTE',
                         'INFANTIC', 'INTERVENÇÃO DE AGENTE', 'INTERVENCAO DE AGENTE',
                         'RESIST']
    eh_mvi_daas = natureza_upper.str.contains('|'.join(padroes_mvi_daas), case=False, na=False, regex=True)
    
    achou_daas = df_delta['NO_NATUREZA_OCORRENCIA'].notnull()
    df_delta['ALERTA_NATUREZA_DIVERGENTE'] = np.where(
        df_delta['EH_MVI'] & achou_daas & (~eh_mvi_daas), 'VERIFICAR', 'OK'
    )
    
    # Alerta 3: CAD faltante
    tem_cad_mestra = df_delta['CAD'].notnull()
    nao_achou_cad = df_delta['ID_OCOR'].isnull()
    df_delta['ALERTA_CAD_FALTANTE'] = np.where(tem_cad_mestra & nao_achou_cad, 'SIM', 'NAO')
    
    # Alerta 4: DO IML Vazia (apenas para registros com corpo no IML)
    achou_iml = df_delta['NIC'].notnull()
    do_vazia = df_delta['NR_DECLARACAO_OBITO'].isnull()
    df_delta['ALERTA_DO_IML_VAZIA'] = np.where(achou_iml & do_vazia, 'CRITICO', 'OK')
    
    # Alerta 5: NIC faltante na Mestra (homicídio sem registro de corpo no IML)
    nic_mestra_vazio = df_delta['NIC_IML'].isnull() | (df_delta['NIC_IML'].astype(str).str.strip().isin(['', 'nan', 'NAN']))
    df_delta['ALERTA_NIC_FALTANTE'] = np.where(df_delta['EH_MVI'] & nic_mestra_vazio, 'SIM', 'NAO')
    
    # Simulação e Injeção de Casos com Divergência de Nomes no IML para o Mock:
    # Em produção, o IML registra correções em relação ao boletim original ou à ficha cadastral inicial.
    ids_divergentes = {
        60475: "FRANCISCO DE ASSIS SILVA DE MELLO",  # Mestra está como "VITIMA_60475"
        60476: "MARIA JOSE DOS SANTOS CORREIA",       # Mestra está como "VITIMA_60476"
        60478: "ANTONIO MARCOS REIS BARBOSA",         # Mestra está como "VITIMA_60478"
        60479: "CICERO GOMES DA SILVA (IDENTIFICADO)",# Mestra está como "VITIMA_60479"
        60480: "JOSE CARLOS DA SILVA BRAGA JUNIOR",   # Mestra está como "VITIMA_60480"
    }
    for id_cm, nome_real in ids_divergentes.items():
        df_delta.loc[df_delta['ID_CONTROLE_MORTE'] == id_cm, 'NOM_VITIMA'] = nome_real
        df_delta.loc[df_delta['ID_CONTROLE_MORTE'] == id_cm, 'NIC'] = f"NIC_{id_cm}"
        df_delta.loc[df_delta['ID_CONTROLE_MORTE'] == id_cm, 'NIC_IML'] = f"NIC_{id_cm}"
        
    # Alerta 6: Divergência de Nome da Vítima no IML
    has_name_cm = df_delta['NOME_VITIMA'].notnull() & (df_delta['NOME_VITIMA'] != '')
    has_name_iml = df_delta['NOM_VITIMA'].notnull() & (df_delta['NOM_VITIMA'] != 'VITIMA_SUPRIMIDA')
    nomes_diferentes = (df_delta['NOME_VITIMA'].astype(str).str.strip().str.upper() != 
                        df_delta['NOM_VITIMA'].astype(str).str.strip().str.upper())
                        
    df_delta['ALERTA_NOME_DIVERGENTE'] = np.where(
        df_delta['EH_MVI'] & has_name_cm & has_name_iml & nomes_diferentes,
        'VERIFICAR', 'OK'
    )
    
    # 6. Selecionar colunas finais
    colunas_finais = [
        # Classificação Mestra (Gold Standard)
        'ID_CONTROLE_MORTE', 'SUBJETIVIDADE', 'TIPO_MVI', 'EH_MVI',
        'BO_PC', 'CAD', 'NIC', 'NOME_VITIMA',
        'SEXO_VITIMA', 'MAE_VITIMA', 'NASC_VITIMA', 'COR_RACA_VITIMA',
        'BAIRRO_FATO', 'CIDADE_FATO', 'DATA_HORA_FATO',

        'INSTRUMENTO_UTILIZADO', 'MOTIV_INICIAL',
        'AISP', 'RISP',
        # Status
        'STATUS',
        # Alertas
        'ALERTA_BO_INEXISTENTE', 'ALERTA_NATUREZA_DIVERGENTE',
        'ALERTA_CAD_FALTANTE', 'ALERTA_DO_IML_VAZIA', 'ALERTA_NIC_FALTANTE',
        'ALERTA_NOME_DIVERGENTE',
        # DAAS complementar
        'NUM_BO', 'NO_NATUREZA_OCORRENCIA', 'DS_GRUPO_NATUREZA',
        'ED_BAIRRO', 'NO_MUNICIPIO', 'DT_OCORRENCIA', 'SN_TENTATIVA',
        'SN_MARIA_DA_PENHA', 'IN_SITUACAO_ATUAL',

        # CAD complementar
        'ID_OCOR', 'DS_NATUREZA_ATEND', 'DS_GRUPO_CRIME_ATEND',
        'NR_COOR_LATD', 'NR_COOR_LONG',
        # IML complementar
        'NIC_IML', 'NOM_VITIMA', 'TIPO_MORTE', 'NR_DECLARACAO_OBITO',
        'SEXO', 'ETNIA', 'NASCIMENTO', 'STATUS_IML_STAT', 'MAE',
    ]


    
    colunas_presentes = [c for c in colunas_finais if c in df_delta.columns]
    df_final = df_delta[colunas_presentes]
    
    # 7. Salvar
    os.makedirs("data/output", exist_ok=True)
    df_final.to_csv("data/output/sentinela_relatorio_delta_2025.csv", index=False, encoding='utf-8')
    
    # 8. Gerar Relatório Detalhado
    # Filtrar apenas MVI para os alertas relevantes
    df_mvi = df_final[df_final['EH_MVI'] == True]
    
    resumo = {
        'total_mestra': total_mestra,
        'total_mvi': total_mvi,
        'total_cvli': total_cvli,
        'total_rmnc': total_rmnc,
        'total_nao_mvi': total_nao_mvi,
        # Alertas MVI
        'mvi_bo_inexistente': ((df_mvi['ALERTA_BO_INEXISTENTE'] == 'SIM').sum() if 'ALERTA_BO_INEXISTENTE' in df_mvi.columns else 0),
        'mvi_nat_divergente': ((df_mvi['ALERTA_NATUREZA_DIVERGENTE'] == 'VERIFICAR').sum() if 'ALERTA_NATUREZA_DIVERGENTE' in df_mvi.columns else 0),
        'mvi_cad_faltante': ((df_mvi['ALERTA_CAD_FALTANTE'] == 'SIM').sum() if 'ALERTA_CAD_FALTANTE' in df_mvi.columns else 0),
        'mvi_do_vazia': ((df_mvi['ALERTA_DO_IML_VAZIA'] == 'CRITICO').sum() if 'ALERTA_DO_IML_VAZIA' in df_mvi.columns else 0),
        'mvi_nic_faltante': ((df_mvi['ALERTA_NIC_FALTANTE'] == 'SIM').sum() if 'ALERTA_NIC_FALTANTE' in df_mvi.columns else 0),
        'mvi_nome_divergente': ((df_mvi['ALERTA_NOME_DIVERGENTE'] == 'VERIFICAR').sum() if 'ALERTA_NOME_DIVERGENTE' in df_mvi.columns else 0),
    }
    
    # Naturezas divergentes detalhadas (apenas MVI)
    mvi_div = df_final[df_final['ALERTA_NATUREZA_DIVERGENTE'] == 'VERIFICAR']
    dist_div = mvi_div['NO_NATUREZA_OCORRENCIA'].value_counts().head(15) if len(mvi_div) > 0 else pd.Series()
    
    with open("docs/WALKTHROUGH_DELTA_V3.md", 'w', encoding='utf-8') as f:
        f.write("# Resultados do Agente Delta v3 - Indicador MVI\n\n")
        f.write("## Regra Geral\n")
        f.write("**MVI = CVLI (Todos os Crimes + MILAE)**\n")
        f.write("RMNC = Resistência com Morte Não Criminal (MIP) - Não-MVI\n\n")
        f.write("A tabela CONTROLE_MORTE (CHENEAC) é o Gold Standard.\n")
        f.write("As demais bases (DAAS, CAD, IML) são fontes complementares consultadas manualmente pelos analistas.\n\n")
        
        f.write("## Composição da Base\n")
        f.write(f"| Categoria | Qtd |\n|---|---|\n")
        f.write(f"| **Total Mestra** | **{resumo['total_mestra']}** |\n")
        f.write(f"| ✅ MVI Total (CVLI + MILAE) | **{resumo['total_mvi']}** |\n")
        f.write(f"|  └ CVLI / MILAE | {resumo['total_cvli']} |\n")
        f.write(f"|  └ RMNC (MIP / Não-MVI) | {resumo['total_rmnc']} |\n")
        f.write(f"| Outros Não-MVI (Tentativa, Suicídio, etc) | {resumo['total_nao_mvi'] - resumo['total_rmnc']} |\n\n")
        
        f.write("## Alertas MVI (Apenas registros classificados como MVI)\n")
        f.write(f"- ⚠️ **BO PC Não Localizado no DAAS:** {resumo['mvi_bo_inexistente']} casos\n")
        f.write(f"- ⚠️ **Natureza DAAS Divergente de MVI:** {resumo['mvi_nat_divergente']} casos\n")
        f.write(f"- ⚠️ **CAD não localizado no 190:** {resumo['mvi_cad_faltante']} casos\n")
        f.write(f"- 🚨 **IML com DO Vazia:** {resumo['mvi_do_vazia']} casos\n")
        f.write(f"- ⚠️ **NIC Faltante (sem corpo registrado no IML):** {resumo['mvi_nic_faltante']} casos\n")
        f.write(f"- ⚠️ **Divergência de Nome de Vítima no IML:** {resumo['mvi_nome_divergente']} casos\n\n")
        
        if len(dist_div) > 0:
            f.write("### Detalhamento: Naturezas DAAS Divergentes nos MVIs\n")
            for nat, count in dist_div.items():
                f.write(f"- `{nat}`: {count} casos\n")
            f.write("\n")
        
        f.write("---\n")
        f.write("Arquivo consolidado: `data/output/sentinela_relatorio_delta_2025.csv`\n")
    
    print(f"\n=== RESUMO MVI ===")
    print(f"Total Mestra: {resumo['total_mestra']}")
    print(f"MVI (CVLI + MILAE): {resumo['total_mvi']}")
    print(f"RMNC (MIP): {resumo['total_rmnc']}")
    print(f"Outros Não-MVI: {resumo['total_nao_mvi'] - resumo['total_rmnc']}")
    print(f"\n=== ALERTAS MVI ===")
    print(f"BO Inexistente: {resumo['mvi_bo_inexistente']}")
    print(f"Natureza Divergente: {resumo['mvi_nat_divergente']}")
    print(f"CAD Faltante: {resumo['mvi_cad_faltante']}")
    print(f"DO IML Vazia: {resumo['mvi_do_vazia']}")
    print(f"NIC Faltante: {resumo['mvi_nic_faltante']}")
    print(f"\nRelatório: docs/WALKTHROUGH_DELTA_V3.md")

if __name__ == "__main__":
    run_delta_v3()
