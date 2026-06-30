import pandas as pd
import sys

def profile_cad(csv_path: str, output_md_path: str):
    print(f"Lendo CSV gigante do CAD: {csv_path}...")
    try:
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler {csv_path}. Detalhe: {e}")
        sys.exit(1)

    total_rows = len(df)
    
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Profiling: PM CAD 190 (VW_BO_GERAL_CAD) 2025\n\n")
        f.write(f"**Total de Ocorrências Analisadas:** {total_rows}\n\n")
        
        # 1. Chave Principal
        f.write("## 1. Qualidade da Chave Mestra (`ID_OCOR`)\n")
        if 'ID_OCOR' in df.columns:
            nulos = df['ID_OCOR'].isnull().sum()
            pct = (nulos / total_rows) * 100
            unicos = df['ID_OCOR'].nunique()
            f.write(f"- **Vazios**: {nulos} ({pct:.2f}%)\n")
            f.write(f"- **Valores Únicos**: {unicos} (Indicador de multiplicidade de despacho por ocorrência)\n")
            
        # 2. Coordenadas
        f.write("\n## 2. Qualidade Espacial (Coordenadas)\n")
        for coord in ['NR_COOR_LATD', 'NR_COOR_LONG', 'NR_COOR_LATD_QUIMERA', 'NR_COOR_LONG_QUIMERA']:
            if coord in df.columns:
                nulos = df[coord].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{coord}`: {nulos} vazios ({pct:.2f}%)\n")
                
        # 3. Organizações e Tempos
        f.write("\n## 3. Despacho e Tempos de Resposta\n")
        for col in ['DS_ORGA', 'DT_INCL', 'DT_FECH', 'DT_ATLZ_DESPC']:
            if col in df.columns:
                nulos = df[col].isnull().sum()
                pct = (nulos / total_rows) * 100
                f.write(f"- `{col}`: {nulos} vazios ({pct:.2f}%)\n")
                
        # 4. Top 10 Vazios Gerais
        f.write("\n## 4. Colunas com Menor Preenchimento (Top 10)\n")
        null_counts = df.isnull().sum()
        pct_null = (null_counts / total_rows) * 100
        vazias = pct_null[pct_null > 0].sort_values(ascending=False).head(10)
        for col, pct in vazias.items():
            f.write(f"- `{col}`: {null_counts[col]} nulos ({pct:.2f}%)\n")

    print(f"Relatório CAD salvo em: {output_md_path}")

if __name__ == "__main__":
    profile_cad("data/mock/extracao_pm_cad_2025.csv", "docs/PROFILING_PM_CAD_2025.md")
