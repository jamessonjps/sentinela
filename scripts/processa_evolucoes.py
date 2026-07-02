import os
import sys
import pandas as pd
from datetime import datetime
import difflib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.database import SessionLocal, engine
from api.models import SentinelaEvolucaoPendente, Base

def normalize_text(t):
    if pd.isna(t):
        return ""
    return str(t).strip().upper()

def match_score(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def processa_evolucoes():
    print("Conectando ao banco de dados SQLite (sentinela.db)...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("Limpando fila antiga de evoluções...")
    db.query(SentinelaEvolucaoPendente).delete()
    db.commit()

    print("Carregando bases extraídas...")
    df_tent = pd.read_csv("data/mock/TENTATIVAS_2024_2025.csv", low_memory=False)
    df_iml = pd.read_csv("data/mock/IML_2024_2025.csv", low_memory=False)
    
    print("Carregando Mestra Completa para checagem de Duplicatas...")
    df_cm_completa = pd.read_csv("data/mock/CONTROLE_MORTE_2024_2025.csv", low_memory=False)
    df_cm_completa['NIC'] = df_cm_completa['NIC'].astype(str).str.strip().str.replace('.0', '', regex=False)
    nics_cadastrados = set(df_cm_completa[df_cm_completa['NIC'] != 'NAN']['NIC'].dropna().unique())
    
    # Tratando datas
    df_tent['DATA_HORA_FATO'] = pd.to_datetime(df_tent['DATA_HORA_FATO'], errors='coerce')
    df_iml['DATA_ENTRADA'] = pd.to_datetime(df_iml['DATA_ENTRADA'], errors='coerce')
    df_iml['DAT_OBITO'] = pd.to_datetime(df_iml['DAT_OBITO'], errors='coerce')
    
    # Tratando NICs (A chave principal)
    df_tent['NIC'] = df_tent['NIC'].astype(str).str.strip().str.replace('.0', '', regex=False)
    df_iml['NIC'] = df_iml['NIC'].astype(str).str.strip().str.replace('.0', '', regex=False)
    
    count_inseridos = 0
    print(f"Buscando cruzamentos entre {len(df_tent)} tentativas e {len(df_iml)} registros no IML...")

    for i, tent in df_tent.iterrows():
        dt_tent = tent['DATA_HORA_FATO']
        if pd.isna(dt_tent): continue
        
        nome_tent = normalize_text(tent['NOME_VITIMA'])
        mae_tent = normalize_text(tent['MAE_VITIMA'])
        bairro_tent = normalize_text(tent['BAIRRO_FATO'])
        cidade_tent = normalize_text(tent['CIDADE_FATO'])
        nasc_tent = str(tent['NASC_VITIMA']) if pd.notna(tent['NASC_VITIMA']) else ""
        
        # TENTATIVA POR MATCH DE CONTEXTO (Nomes, Mães, NIs e Local)
        if nome_tent:
            for _, iml in df_iml.iterrows():
                dt_corpo = iml['DAT_OBITO'] if pd.notna(iml['DAT_OBITO']) else iml['DATA_ENTRADA']
                if pd.isna(dt_corpo): continue
                
                delta_days = (dt_corpo - dt_tent).days
                if delta_days < 0 or delta_days > 540:
                    continue
                
                # SE O NIC DO CORPO JÁ ESTÁ NA MESTRA COMPLETA, ENTÃO A MORTE JÁ FOI REGISTRADA (CVLI/Etc)
                nic_iml = str(iml['NIC']).strip()
                if nic_iml and nic_iml != 'NAN' and nic_iml in nics_cadastrados:
                    continue
                    
                nome_iml = normalize_text(iml['NOM_VITIMA'])
                mae_iml = normalize_text(iml['MAE'])
                bairro_iml = normalize_text(iml['OCORRENCIA_BAIRRO'])
                cidade_iml = normalize_text(iml['OCORRENCIA_CIDADE'])
                nasc_iml = str(iml['NASCIMENTO']) if pd.notna(iml['NASCIMENTO']) else ""
                
                if not nome_iml:
                    continue
                
                is_ni = nome_iml.startswith("NI ") or nome_iml == "NI"
                
                score_nome = 0
                if not is_ni:
                    if nome_tent[0] == nome_iml[0] or abs(len(nome_tent) - len(nome_iml)) < 10:
                        score_nome = match_score(nome_tent, nome_iml)
                
                score_mae = match_score(mae_tent, mae_iml) if mae_tent and mae_iml else 0
                
                # Critérios de Match:
                # 1. Nome principal bate com muita força (> 85%)
                # 2. Nome da mãe bate forte (> 85%) + Nome razoável (> 60%)
                # 3. É um "NI" e entrou logo após (<= 5 dias) na MESMA cidade e bairro
                
                match_reason = None
                
                if score_nome > 0.85:
                    match_reason = f"Alta correspondência no nome da vítima ({round(score_nome*100)}%)."
                elif score_mae > 0.85 and score_nome > 0.60:
                    match_reason = f"Alta correspondência no nome da mãe ({round(score_mae*100)}%) combinada com nome da vítima."
                elif is_ni and delta_days <= 5 and cidade_tent and cidade_tent == cidade_iml:
                    if bairro_tent and bairro_iml and bairro_tent == bairro_iml:
                        match_reason = f"Corpo Não Identificado (NI) deu entrada {delta_days} dias após a tentativa no MESMO Bairro ({bairro_tent}) e Cidade."
                    elif delta_days <= 2:
                        match_reason = f"Corpo Não Identificado (NI) deu entrada logo após ({delta_days} dias) na mesma Cidade ({cidade_tent})."
                
                if match_reason:
                    motivo = match_reason + f" Vítima IML: '{nome_iml}'. "
                    
                    if nasc_tent and nasc_iml and nasc_tent[:4] == nasc_iml[:4]: # Mesmo ano de nascimento
                        motivo += f"Ano de nascimento bate ({nasc_tent[:4]}). "
                    
                    evolucao = SentinelaEvolucaoPendente(
                        ID_CONTROLE_MORTE=int(tent['ID_CONTROLE_MORTE']),
                        NIC_IML=str(iml['NIC']) if pd.notna(iml['NIC']) else None,
                        BO_PC=str(tent['BO_PC']) if pd.notna(tent['BO_PC']) else None,
                        DATA_OBITO=dt_corpo,
                        STATUS="Pendente",
                        MOTIVO=motivo,
                        TIPO_EVOLUCAO="Tentativa -> Óbito",
                        AUTOR_PROPOSTA="Agente Sentinela (Match Contextual Avançado)"
                    )
                    db.add(evolucao)
                    count_inseridos += 1
                    break

    db.commit()
    db.close()
    print(f"\nFinalizado! {count_inseridos} possíveis evoluções (Tentativas que foram a Óbito) foram injetadas com base nos dados reais.")

if __name__ == "__main__":
    processa_evolucoes()
