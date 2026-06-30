import pandas as pd
import numpy as np
import re
import sys

def profile_controle_morte(csv_path: str):
    """
    Realiza o profiling estrutural e diagnóstico de qualidade de dados 
    da tabela CONTROLE_MORTE (Amostra Anonimizada).
    
    Args:
        csv_path (str): Caminho para o arquivo CSV anonimizado.
    """
    print(f"--- Iniciando Profiling (Frente 1) para: {csv_path} ---\n")
    
    try:
        # Carregamento seguro. O low_memory=False previne warnings de tipos mistos em amostras grandes
        # Removido o sep=';' para que o pandas leia corretamente o CSV exportado com vírgulas pelo DBeaver
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler o arquivo CSV. Detalhe: {e}")
        sys.exit(1)

    total_rows = len(df)
    print(f"Total de Registros Analisados: {total_rows}\n")
    
    if total_rows == 0:
        print("[AVISO] O arquivo CSV está vazio.")
        sys.exit(0)

    # ==========================================
    # 1. ANÁLISE DE ESTRUTURA E TIPOS
    # ==========================================
    print("1. ESTRUTURA E TIPOS DE DADOS IDENTIFICADOS:")
    for col in df.columns:
        tipo = df[col].dtype
        print(f"  - {col}: {tipo}")
    print("\n")

    # ==========================================
    # 2. PERCENTUAL DE VALORES NULOS (NaN)
    # ==========================================
    print("2. PERCENTUAL DE VALORES NULOS (NaN) POR COLUNA:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            pct = (count / total_rows) * 100
            print(f"  - {col}: {count} nulos ({pct:.2f}%)")
    print("\n")

    # ==========================================
    # 3. ANÁLISE DE CHAVES PRINCIPAIS (NIC, BO_PC, CAD)
    # ==========================================
    print("3. DIAGNÓSTICO DE CHAVES (INCONSISTÊNCIAS DE FORMATAÇÃO):")
    
    # Validação BO_PC (Padrão esperado comum: apenas números ou formato 'Num/Ano')
    if 'BO_PC' in df.columns:
        df['BO_PC_str'] = df['BO_PC'].astype(str).fillna('')
        bo_invalidos = df[~df['BO_PC_str'].str.match(r'^(\d+|[A-Za-z0-9\-/]+)$') & (df['BO_PC_str'] != '')]
        print(f"  - BO_PC: {len(bo_invalidos)} registros com caracteres suspeitos ou fora de padrão.")

    # Validação NIC (Normalmente numérico)
    if 'NIC' in df.columns:
        df['NIC_str'] = df['NIC'].astype(str).fillna('')
        nic_invalidos = df[~df['NIC_str'].str.match(r'^\d+$') & (df['NIC_str'] != '') & (df['NIC_str'] != 'nan')]
        print(f"  - NIC: {len(nic_invalidos)} registros que não são estritamente numéricos.")

    # Validação CAD
    if 'CAD' in df.columns:
        df['CAD_str'] = df['CAD'].astype(str).fillna('')
        cad_invalidos = df[~df['CAD_str'].str.match(r'^[A-Za-z0-9]+$') & (df['CAD_str'] != '') & (df['CAD_str'] != 'nan')]
        print(f"  - CAD: {len(cad_invalidos)} registros suspeitos (espaços ou caracteres especiais).")
    print("\n")

    # ==========================================
    # 4. ANOMALIAS EM CAMPOS DE TEXTO E GEOGRAFIA
    # ==========================================
    print("4. ANOMALIAS EM CAMPOS DE TEXTO (GEOGRAFIA E SUJEITOS):")
    campos_texto = ['BAIRRO_FATO', 'MUNICIPIO_FATO', 'AISP', 'RISP', 'SUBJETIVIDADE']
    for campo in campos_texto:
        if campo in df.columns:
            # Conta valores únicos para identificar fragmentação (ex: 'CENTRO', 'Centro', ' CENTRO ')
            valores_unicos = df[campo].dropna().unique()
            espacos_extras = [v for v in valores_unicos if isinstance(v, str) and (v.startswith(' ') or v.endswith(' '))]
            
            print(f"  - {campo}: {len(valores_unicos)} categorias únicas identificadas.")
            if espacos_extras:
                print(f"    [!] Alerta: Encontrados {len(espacos_extras)} valores com espaços em branco extras (ex: ' {espacos_extras[0]}').")
    print("\n")

    # ==========================================
    # 5. PADRÕES DE DATAS (YYYY-MM-DD HH:MM:SS)
    # ==========================================
    print("5. DIAGNÓSTICO DE PADRÕES DE DATAS:")
    campos_data = ['DATA_HORA_FATO', 'ALTER_DATE', 'DATA_REGISTRO']
    padrao_data = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    
    for campo in campos_data:
        if campo in df.columns:
            datas = df[campo].dropna().astype(str)
            fora_padrao = datas[~datas.str.match(padrao_data)]
            pct_fora = (len(fora_padrao) / total_rows) * 100 if total_rows > 0 else 0
            
            print(f"  - {campo}: {len(fora_padrao)} registros ({pct_fora:.2f}%) fora do formato 'YYYY-MM-DD HH:MM:SS'.")
            if len(fora_padrao) > 0:
                print(f"    Exemplos fora do padrão: {fora_padrao.head(3).tolist()}")

    print("\n--- Profiling Concluído ---")
    print("Aguardando sua validação sobre o relatório antes de gerar o script de Tratamento (Wrangling).")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gera relatório de Profiling para o SENTINELA.")
    parser.add_argument("csv_path", help="Caminho para o arquivo CSV de amostra.")
    args = parser.parse_args()
    
    profile_controle_morte(args.csv_path)
