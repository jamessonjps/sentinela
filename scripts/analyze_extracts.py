import pandas as pd
from datetime import datetime
import json
import difflib

def normalize_text(t):
    if pd.isna(t):
        return ""
    return str(t).strip().upper()

def match_score(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def analyze():
    print("Carregando TENTATIVAS...")
    df_tent = pd.read_csv(r"c:\Users\jamerson.jpd\Desktop\SENTINELA\data\mock\TENTATIVAS_2024_2025.csv", low_memory=False)
    print("Carregando IML...")
    df_iml = pd.read_csv(r"c:\Users\jamerson.jpd\Desktop\SENTINELA\data\mock\IML_2024_2025.csv", low_memory=False)
    
    # Tratando datas
    df_tent['DATA_HORA_FATO'] = pd.to_datetime(df_tent['DATA_HORA_FATO'], errors='coerce')
    df_iml['DATA_ENTRADA'] = pd.to_datetime(df_iml['DATA_ENTRADA'], errors='coerce')
    df_iml['DAT_OBITO'] = pd.to_datetime(df_iml['DAT_OBITO'], errors='coerce')
    
    matches = []
    
    print(f"Total de tentativas processadas: {len(df_tent)}", flush=True)
    print(f"Total de registros IML processados: {len(df_iml)}", flush=True)
    
    count = 0
    for i, tent in df_tent.iterrows():
        count += 1
        if count % 100 == 0:
            print(f"Processando tentativa {count}/{len(df_tent)}...", flush=True)
        dt_tent = tent['DATA_HORA_FATO']
        if pd.isna(dt_tent): continue
        
        nome_tent = normalize_text(tent['NOME_VITIMA'])
        bo_tent = normalize_text(tent['BO_PC'])
        
        # Filtra IML para corpos que entraram após a tentativa (até 540 dias)
        for j, iml in df_iml.iterrows():
            dt_corpo = iml['DAT_OBITO'] if pd.notna(iml['DAT_OBITO']) else iml['DATA_ENTRADA']
            if pd.isna(dt_corpo): continue
            
            delta_days = (dt_corpo - dt_tent).days
            if delta_days < 0 or delta_days > 540:
                continue
                
            nome_iml = normalize_text(iml['NOM_VITIMA'])
            
            bo_match = False
            # if we had BO_PC in IML we could match, but the IML query doesn't have it explicitly
            # so we match mostly by name.
            
            if not nome_tent or not nome_iml:
                continue
                
            if nome_tent[0] != nome_iml[0]:
                continue
                
            score = match_score(nome_tent, nome_iml)
            
            if score > 0.85:
                matches.append({
                    "tentativa_id": tent['ID_CONTROLE_MORTE'],
                    "nome_tentativa": nome_tent,
                    "data_tentativa": dt_tent.strftime('%Y-%m-%d'),
                    "iml_nic": iml['NIC'],
                    "nome_iml": nome_iml,
                    "data_obito": dt_corpo.strftime('%Y-%m-%d'),
                    "score": round(score * 100, 2),
                    "dias_ate_obito": delta_days
                })
                
    df_matches = pd.DataFrame(matches)
    print(f"\nEvoluções suspeitas detectadas: {len(matches)}")
    if len(matches) > 0:
        df_matches = df_matches.sort_values(by='score', ascending=False)
        print("\nTOP 5 Matches (Maior Similaridade Fonética/Ortográfica):")
        print(df_matches.head(5).to_string(index=False))
        
        # Salvando os matches num CSV para o usuário consultar
        out_path = r"c:\Users\jamerson.jpd\Desktop\SENTINELA\data\output\evolucoes_detectadas.csv"
        df_matches.to_csv(out_path, index=False)
        print(f"\nResultados completos salvos em: {out_path}")

if __name__ == "__main__":
    analyze()
