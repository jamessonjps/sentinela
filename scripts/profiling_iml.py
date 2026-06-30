import pandas as pd
import sys

def profile_iml(csv_path: str, output_md_path: str):
    try:
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler {csv_path}. Detalhe: {e}")
        sys.exit(1)

    total_rows = len(df)
    
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Profiling: IML (VW_IML_STATUS) 2025\n\n")
        f.write(f"**Total de Cadastros/Status IML Analisados:** {total_rows}\n\n")
        
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
        f.write("\n## 2. Qualidade das Chaves Mestra (`NIC_IML` e `ID_CMORTE`)\n")
        for key in ['NIC_IML', 'ID_CMORTE']:
            if key in df.columns:
                nulos = df[key].isnull().sum()
                pct = (nulos / total_rows) * 100
                unicos = df[key].nunique()
                f.write(f"- **{key}**:\n  - Vazios: {nulos} ({pct:.2f}%)\n  - Valores Únicos: {unicos}\n")
            
        # 3. Status e Detalhes
        f.write("\n## 3. Preenchimento de Status e Óbito\n")
        cols_interesse = ['STATUS', 'TIPO_MORTE', 'DATA_ENTRADA', 'DATA_OBITO']
        for c in cols_interesse:
            if c in df.columns:
                nulos = df[c].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{c}`: {nulos} vazios ({pct:.2f}%)\n")

        # 4. Outras Completudes Relevantes
        f.write("\n## 4. Completude Restante\n")
        outras = pct_null[(pct_null > 0) & (pct_null < 100.0)].sort_values(ascending=False)
        for col, pct in outras.items():
            if col not in cols_interesse and col not in ['NIC_IML', 'ID_CMORTE']:
                f.write(f"- `{col}`: {null_counts[col]} nulos ({pct:.2f}%)\n")

    print(f"Relatório IML salvo em: {output_md_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("output_md")
    args = parser.parse_args()
    
    profile_iml(args.csv_path, args.output_md)
