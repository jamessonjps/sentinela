import pandas as pd
import numpy as np
import traceback

def wrangle_controle_morte(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza a limpeza, padronização e enriquecimento da tabela CONTROLE_MORTE.
    
    Regras Aplicadas:
    1. Descarte de colunas 100% nulas.
    2. Conversão determinística de chaves numéricas (NIC, CAD) para String pura.
    3. Padronização de datas ISO.
    4. Limpeza de campos de texto (Espaços extras, UPPERCASE).
    5. Regra de Negócio: Flag de Qualidade Crítica para CVLI/Tentativas sem BO_PC.
    
    Args:
        df (pd.DataFrame): DataFrame bruto anonimizado (Frente 1).
        
    Returns:
        pd.DataFrame: DataFrame tratado pronto para ingestão no SENTINELA.
    """
    
    print("--- Iniciando Wrangling (Frente 2) ---")
    
    # Cópia segura para evitar SettingWithCopyWarning
    df_clean = df.copy()
    erros_auditoria = []

    # 1. DESCARTE DE COLUNAS INÚTEIS (Vazias ou não priorizadas agora)
    try:
        colunas_para_descartar = ['STATUS_NECROPSIA', 'MOTIV_FINAL', 'ALTER_DATE', 
                                  'LATITUDE_VITIMA', 'LONGITUDE_VITIMA']
        colunas_existentes = [col for col in colunas_para_descartar if col in df_clean.columns]
        df_clean.drop(columns=colunas_existentes, inplace=True)
    except Exception as e:
        erros_auditoria.append({"processo": "drop_colunas", "erro": str(e), "linha": None})

    # 2. TRATAMENTO DE CHAVES (NIC, CAD, BO_PC)
    def clean_key(val):
        if pd.isna(val) or val == '' or val == 'nan':
            return None
        # Converte float (123.0) para string ('123')
        v_str = str(val).strip()
        if v_str.endswith('.0'):
            v_str = v_str[:-2]
        return v_str if v_str else None

    try:
        if 'NIC' in df_clean.columns:
            df_clean['NIC'] = df_clean['NIC'].apply(clean_key)
        if 'CAD' in df_clean.columns:
            df_clean['CAD'] = df_clean['CAD'].apply(clean_key)
        if 'BO_PC' in df_clean.columns:
            df_clean['BO_PC'] = df_clean['BO_PC'].apply(clean_key)
    except Exception as e:
        erros_auditoria.append({"processo": "tratamento_chaves", "erro": str(e), "linha": traceback.format_exc()})

    # 3. TRATAMENTO DE DATAS
    try:
        if 'DATA_HORA_FATO' in df_clean.columns:
            # Remove milissegundos e padroniza
            # Tenta converter para datetime e depois formatar, erros são convertidos para NaT
            df_clean['DATA_HORA_FATO'] = pd.to_datetime(df_clean['DATA_HORA_FATO'], errors='coerce')
            # Converte de volta para string ISO 8601 (YYYY-MM-DD HH:MM:SS)
            df_clean['DATA_HORA_FATO'] = df_clean['DATA_HORA_FATO'].dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        erros_auditoria.append({"processo": "tratamento_datas", "erro": str(e), "linha": traceback.format_exc()})

    # 4. TRATAMENTO DE TEXTOS E CATEGORIAS (Determinístico)
    def clean_text(val):
        if pd.isna(val) or type(val) != str:
            return val
        return val.strip().upper()

    try:
        campos_texto = ['BAIRRO_FATO', 'CIDADE_FATO', 'SUBJETIVIDADE', 'INSTRUMENTO_UTILIZADO']
        for campo in campos_texto:
            if campo in df_clean.columns:
                df_clean[campo] = df_clean[campo].apply(clean_text)
    except Exception as e:
        erros_auditoria.append({"processo": "tratamento_texto", "erro": str(e), "linha": traceback.format_exc()})

    # 5. REGRA DE NEGÓCIO: QUALIDADE (SLA DO ANALISTA)
    # CVLI e Tentativas OBRIGATORIAMENTE devem ter BO_PC. Demais crimes, não é crítico.
    try:
        if 'SUBJETIVIDADE' in df_clean.columns and 'BO_PC' in df_clean.columns:
            # Palavras-chave determinísticas de alta prioridade
            alta_prioridade = ['CVLI', 'HOMICIDIO', 'TENTATIVA', 'LATROCINIO', 'FEMINICIDIO']
            
            # Cria a Flag usando vetorização do Pandas
            # 1. É de alta prioridade?
            mask_prioridade = df_clean['SUBJETIVIDADE'].str.contains('|'.join(alta_prioridade), na=False)
            # 2. O BO_PC está vazio?
            mask_sem_bo = df_clean['BO_PC'].isna()
            
            # Aplica a flag
            df_clean['FLAG_ALERTA_QUALIDADE'] = np.where(mask_prioridade & mask_sem_bo, 
                                                        'CRITICO_FALTA_BO', 'OK')
    except Exception as e:
        erros_auditoria.append({"processo": "regra_negocio_qualidade", "erro": str(e), "linha": traceback.format_exc()})


    # Auditoria de Erros Final
    if erros_auditoria:
        print(f"[!] Atenção: {len(erros_auditoria)} erros estruturados capturados na Auditoria.")
        for err in erros_auditoria:
            print(f"  -> Processo: {err['processo']} | Erro: {err['erro']}")
    else:
        print("[OK] Tratamento concluído sem lançar exceções.")

    print(f"Tamanho Final: {len(df_clean)} registros.")
    return df_clean

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Executa o Wrangling no dataset do SENTINELA.")
    parser.add_argument("input_csv", help="Caminho do CSV bruto anonimizado")
    parser.add_argument("output_csv", help="Caminho para salvar o CSV tratado")
    args = parser.parse_args()
    
    try:
        # Lê o CSV ignorando avisos de tipo
        df_raw = pd.read_csv(args.input_csv, sep=',', encoding='utf-8', low_memory=False)
        # Executa o Tratamento
        df_tratado = wrangle_controle_morte(df_raw)
        # Salva o resultado
        df_tratado.to_csv(args.output_csv, index=False, sep=',', encoding='utf-8')
        print(f"\n[SUCESSO] Arquivo tratado salvo em: {args.output_csv}")
        
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na esteira de wrangling: {e}")
        sys.exit(1)
