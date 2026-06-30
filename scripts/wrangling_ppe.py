import pandas as pd
import numpy as np

def wrangling_ppe(input_csv, output_csv):
    print(f"Lendo base do DAAS: {input_csv}...")
    df = pd.read_csv(input_csv, sep=',', encoding='utf-8', low_memory=False)
    
    total_linhas_originais = len(df)
    
    # 1. Descartar colunas 100% nulas
    print("Removendo colunas 100% nulas...")
    cols_to_drop = ['CO_REGISTRO_NACIONAL', 'TP_INSTAURACAO']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    # 2. Lógica de Agregação (Achatamento 1:1 por NUM_BO)
    print("Iniciando achatamento por NUM_BO...")
    
    # Preencher NaN com zero temporariamente para o MAX funcionar bem nas flags numéricas
    for c in ['SN_TENTATIVA', 'SN_MARIA_DA_PENHA']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

    # Função customizada para juntar strings únicas separadas por pipe
    def join_unique_strings(series):
        uniques = series.dropna().astype(str).unique()
        return " | ".join(uniques) if len(uniques) > 0 else np.nan
        
    # Definir como cada coluna será agregada
    agg_funcs = {
        'NO_NATUREZA_OCORRENCIA': join_unique_strings,
        'DS_GRUPO_NATUREZA': join_unique_strings,
        'SN_TENTATIVA': 'max',
        'SN_MARIA_DA_PENHA': 'max',
        'ID_PROCEDIMENTO': 'max', # Pegar o ID mais recente
        'DT_HORA_REGISTRO': 'max',
        'DT_OCORRENCIA': 'first',
        'ED_LATITUDE_LONGITUDE': 'first',
        'ED_BAIRRO': 'first',
        'DS_LOCAL_OCORRENCIA': 'first',
        'IN_SITUACAO_ATUAL': 'max'
    }
    
    # Para as demais colunas (se houver), pegar o first()
    for col in df.columns:
        if col not in agg_funcs and col != 'NUM_BO':
            agg_funcs[col] = 'first'
            
    df_clean = df.groupby('NUM_BO', as_index=False).agg(agg_funcs)
    
    total_linhas_finais = len(df_clean)
    
    print(f"Achatamento concluído!")
    print(f"Linhas Originais: {total_linhas_originais} | Linhas Únicas (BOs): {total_linhas_finais}")
    
    # 3. Salvar
    df_clean.to_csv(output_csv, index=False, sep=',', encoding='utf-8')
    print(f"Base salva com sucesso em: {output_csv}")

if __name__ == "__main__":
    wrangling_ppe("data/mock/extracao_ppe_2025.csv", "data/mock/extracao_ppe_2025_limpo.csv")
