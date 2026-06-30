import pandas as pd
import sys
import os

def profile_controle_morte_completo(csv_path: str, output_md_path: str):
    try:
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler o arquivo CSV. Detalhe: {e}")
        sys.exit(1)

    total_rows = len(df)
    if total_rows == 0:
        print("[AVISO] O arquivo CSV está vazio.")
        sys.exit(0)

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Profiling Completo: CONTROLE_MORTE (2025)\n\n")
        f.write(f"**Total de Registros Analisados:** {total_rows}\n\n")
        
        # 1. Colunas 100% Nulas
        f.write("## 1. Colunas 100% Nulas (Candidatas a Descarte)\n")
        null_counts = df.isnull().sum()
        pct_null = (null_counts / total_rows) * 100
        colunas_vazias = pct_null[pct_null == 100.0].index.tolist()
        
        for col in colunas_vazias:
            f.write(f"- `{col}`\n")
        if not colunas_vazias:
            f.write("- Nenhuma coluna é 100% vazia.\n")
            
        f.write("\n## 2. Completude de Colunas Relevantes (Parcialmente Nulas)\n")
        colunas_parciais = pct_null[(pct_null > 0) & (pct_null < 100.0)].sort_values(ascending=False)
        for col, pct in colunas_parciais.items():
            f.write(f"- `{col}`: {null_counts[col]} nulos ({pct:.2f}%)\n")
            
        f.write("\n## 3. Análise de Chaves de Integração\n")
        chaves = ['NIC', 'BO_PC', 'CAD', 'COD_PM_VITIMA', 'COD_PC_VITIMA', 'NUM_OBITO']
        for chave in chaves:
            if chave in df.columns:
                nulos = df[chave].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{chave}`: {nulos} vazios ({pct:.2f}%)\n")

        f.write("\n## 4. Análise Geográfica\n")
        geo_cols = ['LATITUDE', 'LONGITUDE', 'BAIRRO_FATO', 'CIDADE_FATO']
        for g in geo_cols:
            if g in df.columns:
                nulos = df[g].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{g}`: {nulos} vazios ({pct:.2f}%)\n")

        f.write("\n## 5. Variáveis Sociodemográficas e Criminais\n")
        socio_cols = ['SEXO_VITIMA', 'IDADE_VITIMA', 'COR_RACA_VITIMA', 'SUBJETIVIDADE', 'INSTRUMENTO_UTILIZADO']
        for s in socio_cols:
            if s in df.columns:
                nulos = df[s].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{s}`: {nulos} vazios ({pct:.2f}%)\n")
                
                # Conta valores únicos
                unicos = df[s].dropna().unique()
                if len(unicos) <= 20:
                    f.write(f"  - Categorias: {', '.join([str(u) for u in unicos])}\n")
                else:
                    f.write(f"  - ({len(unicos)} categorias únicas identificadas)\n")

    print(f"Relatório gerado com sucesso em: {output_md_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("output_md")
    args = parser.parse_args()
    
    profile_controle_morte_completo(args.csv_path, args.output_md)
