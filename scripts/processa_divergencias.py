import os
import sys
import pandas as pd
from datetime import datetime
import difflib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.database import SessionLocal, engine
from api.models import SentinelaFilaAlertas, Base

def normalize_text(t):
    if pd.isna(t):
        return ""
    return str(t).strip().upper()

def match_score(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def format_date(dt_str):
    if pd.isna(dt_str) or dt_str == 'NAN': return ""
    return str(dt_str).strip()

def processa_divergencias():
    print("Conectando ao banco de dados SQLite (sentinela.db)...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("Limpando alertas antigos de divergência...")
    db.query(SentinelaFilaAlertas).filter(
        SentinelaFilaAlertas.TIPO_ALERTA.like("Divergência%")
    ).delete(synchronize_session=False)
    db.commit()

    print("Carregando bases extraídas...")
    df_cm = pd.read_csv("data/mock/CONTROLE_MORTE_2024_2025.csv", low_memory=False)
    df_iml = pd.read_csv("data/mock/IML_2024_2025.csv", low_memory=False)
    
    # Tratando NICs
    df_cm['NIC'] = df_cm['NIC'].astype(str).str.strip().str.replace('.0', '', regex=False)
    df_iml['NIC'] = df_iml['NIC'].astype(str).str.strip().str.replace('.0', '', regex=False)
    
    # Remover sem NIC
    df_cm = df_cm[(df_cm['NIC'] != 'NAN') & (df_cm['NIC'] != '') & (df_cm['NIC'] != 'nan')]
    df_iml = df_iml[(df_iml['NIC'] != 'NAN') & (df_iml['NIC'] != '') & (df_iml['NIC'] != 'nan')]
    
    print(f"Cruzando {len(df_cm)} registros CM com {len(df_iml)} registros IML por NIC...")
    
    # Manter a entrada mais recente do IML se houver NIC duplicado
    df_iml = df_iml.drop_duplicates(subset=['NIC'], keep='last')
    
    # Join on NIC
    merged = pd.merge(df_cm, df_iml, on='NIC', how='inner', suffixes=('_CM', '_IML'))
    
    count_inseridos = 0
    print(f"Encontrados {len(merged)} matches exatos de NIC. Buscando divergências de dados...")
    
    for i, row in merged.iterrows():
        id_cm = row['ID_CONTROLE_MORTE']
        if pd.isna(id_cm): continue
        
        nic = row['NIC']
        
        # 1. Divergência de Nome
        nome_cm = normalize_text(row['NOME_VITIMA'])
        nome_iml = normalize_text(row['NOM_VITIMA'])
        
        divergencias = []
        
        # Ignorar se IML está como NI
        if nome_iml and nome_cm and not (nome_iml.startswith("NI ") or nome_iml == "NI"):
            score = match_score(nome_cm, nome_iml)
            if score < 0.85: # Nomes muito diferentes
                divergencias.append({
                    "tipo": "Divergência de Nome da Vítima",
                    "nivel": "CRÍTICO",
                    "descricao": f"Nome na CM: '{nome_cm}' | Nome no IML: '{nome_iml}'"
                })
        
        # 2. Divergência de Mãe
        mae_cm = normalize_text(row['MAE_VITIMA'])
        mae_iml = normalize_text(row['MAE'])
        
        if mae_cm and mae_iml and mae_cm != "IGNORADA" and mae_iml != "IGNORADO" and len(mae_cm) > 3 and len(mae_iml) > 3:
            score_mae = match_score(mae_cm, mae_iml)
            if score_mae < 0.85:
                divergencias.append({
                    "tipo": "Divergência de Filiação (Mãe)",
                    "nivel": "ALÉM_NORMAL",
                    "descricao": f"Mãe na CM: '{mae_cm}' | Mãe no IML: '{mae_iml}'"
                })
                
        # 3. Divergência de Nascimento
        nasc_cm = format_date(row['NASC_VITIMA'])
        nasc_iml = format_date(row['NASCIMENTO'])
        
        if nasc_cm and nasc_iml and nasc_cm[:4] != nasc_iml[:4]: # Se diferir o ano
            divergencias.append({
                "tipo": "Divergência de Ano de Nascimento",
                    "nivel": "ALERTA",
                    "descricao": f"Nascimento CM: '{nasc_cm}' | IML: '{nasc_iml}'"
            })
            
        # Inserir alertas
        for div in divergencias:
            alerta = SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=int(id_cm),
                NIC=str(nic) if pd.notna(nic) else None,
                TIPO_ALERTA=f"{div['tipo']} - {div['descricao']}",
                STATUS="Novo",
                PRIORIDADE=1 if div["nivel"] == "CRÍTICO" else 2
            )
            db.add(alerta)
            count_inseridos += 1

    db.commit()
    db.close()
    print(f"\nFinalizado! {count_inseridos} alertas de divergência de dados IML x CM foram gerados.")

if __name__ == "__main__":
    processa_divergencias()
