import pandas as pd
import sys

def profile_ppe(csv_path: str, output_md_path: str):
    try:
        # Lendo o CSV. Como pode ser grande, vamos usar low_memory=False
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler {csv_path}. Detalhe: {e}")
        sys.exit(1)

    total_rows = len(df)
    
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Profiling: DAAS (TB_PPE / VW_BOLETIM_OCORRENCIA) 2025\n\n")
        f.write(f"**Total de Boletins de Ocorrência (BOs) Analisados:** {total_rows}\n\n")
        
        # 1. Colunas 100% Nulas
        f.write("## 1. Colunas 100% Nulas (Sem Preenchimento)\n")
        null_counts = df.isnull().sum()
        pct_null = (null_counts / total_rows) * 100
        colunas_vazias = pct_null[pct_null == 100.0].index.tolist()
        
        for col in colunas_vazias:
            f.write(f"- `{col}`\n")
        if not colunas_vazias:
            f.write("- Nenhuma coluna é 100% vazia.\n")
            
        # 2. Chaves de Integração
        f.write("\n## 2. Qualidade da Chave Mestra (`NUM_BO`)\n")
        if 'NUM_BO' in df.columns:
            nulos_bo = df['NUM_BO'].isnull().sum()
            pct_bo = (nulos_bo / total_rows) * 100
            unicos_bo = df['NUM_BO'].nunique()
            f.write(f"- **Vazios**: {nulos_bo} ({pct_bo:.2f}%)\n")
            f.write(f"- **Valores Únicos**: {unicos_bo} (Mede a taxa de duplicidade do BO na tabela)\n")
        else:
            f.write("- `NUM_BO` não encontrado no dataset.\n")
            
        # 3. Naturezas e Situações
        f.write("\n## 3. Naturezas da Ocorrência e Status\n")
        cols_interesse = ['NO_NATUREZA_OCORRENCIA', 'DS_GRUPO_NATUREZA', 'IN_SITUACAO_ATUAL', 'SN_TENTATIVA', 'SN_MARIA_DA_PENHA']
        for c in cols_interesse:
            if c in df.columns:
                nulos = df[c].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{c}`: {nulos} vazios ({pct:.2f}%)\n")
                if c in ['IN_SITUACAO_ATUAL', 'SN_TENTATIVA', 'SN_MARIA_DA_PENHA', 'DS_GRUPO_NATUREZA']:
                    unicos = df[c].dropna().unique()
                    if len(unicos) <= 30:
                        f.write(f"  - Categorias: {', '.join([str(u) for u in unicos])}\n")

        # 4. Outras Completudes Relevantes
        f.write("\n## 4. Completude Restante (Top 10 Vazios)\n")
        outras = pct_null[(pct_null > 0) & (pct_null < 100.0)].sort_values(ascending=False).head(10)
        for col, pct in outras.items():
            f.write(f"- `{col}`: {null_counts[col]} nulos ({pct:.2f}%)\n")

    print(f"Relatório PPE salvo em: {output_md_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("output_md")
    args = parser.parse_args()
    
    profile_ppe(args.csv_path, args.output_md)
