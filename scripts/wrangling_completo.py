import pandas as pd
import numpy as np
import traceback
import sys

def wrangle_controle_morte_completo(df: pd.DataFrame) -> pd.DataFrame:
    print("--- Iniciando Wrangling Completo (Frente 2) ---")
    df_clean = df.copy()
    erros = []

    # 1. Descarte de Colunas 100% Nulas identificadas no Profiling
    colunas_inuteis = [
        'ALTER_DATE', 'COD_PM_VITIMA', 'MOTIV_FINAL', 'TIPO_PROCEDIMENTO', 'ILICITO',
        'DATA_HORA_INSTAURACAO', 'DATA_HORA_CONCLUSAO', 'FORMA_CONCLUSAO', 'DATA_ENVIO_JUS',
        'NUM_OBITO', 'QTD_INQUERITO_PC', 'BO_SISGOU', 'ARMA_RESISTENCIA', 'TP_USO_ARMA_RESISTENCIA',
        'STATUS_DELEGADO', 'STATUS_PERICIA', 'STATUS_NECROPSIA', 'STATUS_MP', 'GRUPO_MOTIVACAO',
        'COORD_STATUS', 'STATUS_VCVLI', 'SETOR_CENSITARIO_VIT', 'LATITUDE_VITIMA', 'LONGITUDE_VITIMA',
        'ALCATRAZ', 'VTR_COORDENADA', 'OPM_COORDENADA', 'SITUACAO_PROCESSO_TJ', 'ID_FATO'
    ]
    try:
        drop_cols = [c for c in colunas_inuteis if c in df_clean.columns]
        df_clean.drop(columns=drop_cols, inplace=True)
    except Exception as e:
        erros.append(f"Erro ao descartar colunas: {e}")

    # 2. Tratamento de Chaves (Strings Puras, removendo decimais do pandas)
    def clean_key(val):
        if pd.isna(val) or str(val).strip().lower() == 'nan' or val == '':
            return None
        v_str = str(val).strip()
        if v_str.endswith('.0'):
            v_str = v_str[:-2]
        return v_str if v_str else None

    chaves = ['NIC', 'CAD', 'BO_PC', 'COD_PC_VITIMA']
    for c in chaves:
        if c in df_clean.columns:
            df_clean[c] = df_clean[c].apply(clean_key)

    # 3. Tratamento de Datas (ISO 8601)
    datas = ['DATA_HORA_FATO', 'DATA_HORA_IML']
    for d in datas:
        if d in df_clean.columns:
            df_clean[d] = pd.to_datetime(df_clean[d], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    # 4. Tratamento Textual Determinístico (Sociodemográfico e Geografia)
    def clean_text(val):
        if pd.isna(val) or type(val) != str:
            return val
        return val.strip().upper()

    text_cols = ['BAIRRO_FATO', 'CIDADE_FATO', 'SUBJETIVIDADE', 'INSTRUMENTO_UTILIZADO', 
                 'COR_RACA_VITIMA', 'SEXO_VITIMA', 'ESTADO_CIVIL_VITIMA']
    for t in text_cols:
        if t in df_clean.columns:
            df_clean[t] = df_clean[t].apply(clean_text)

    # 5. Regra de Negócio: Flag de Qualidade do BO_PC
    if 'SUBJETIVIDADE' in df_clean.columns and 'BO_PC' in df_clean.columns:
        alta_prioridade = ['CVLI', 'TENTATIVA', 'HOMICIDIO', 'LATROCINIO', 'FEMINICIDIO']
        mask_prioridade = df_clean['SUBJETIVIDADE'].str.contains('|'.join(alta_prioridade), na=False)
        mask_sem_bo = df_clean['BO_PC'].isna()
        df_clean['FLAG_ALERTA_QUALIDADE'] = np.where(mask_prioridade & mask_sem_bo, 'CRITICO_FALTA_BO', 'OK')

    # Auditoria
    if erros:
        print(f"[!] {len(erros)} erros capturados.")
        for err in erros: print(err)
    else:
        print("[OK] Wrangling concluído sem erros.")

    return df_clean

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    args = parser.parse_args()
    
    try:
        df_raw = pd.read_csv(args.input_csv, sep=',', encoding='utf-8', low_memory=False)
        df_tratado = wrangle_controle_morte_completo(df_raw)
        df_tratado.to_csv(args.output_csv, index=False, sep=',', encoding='utf-8')
        print(f"Salvo em: {args.output_csv}")
    except Exception as e:
        print(f"Falha: {e}")
        sys.exit(1)
