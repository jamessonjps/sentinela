import pandas as pd
import sys

def profile_csv(csv_path: str, md_file, title: str):
    try:
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        md_file.write(f"## [ERRO] Falha ao ler {csv_path}: {e}\n\n")
        return

    total_rows = len(df)
    md_file.write(f"## {title}\n")
    md_file.write(f"**Total de Linhas Analisadas:** {total_rows}\n\n")
    
    if total_rows == 0:
        md_file.write("Arquivo vazio.\n\n")
        return

    # Chave principal NIC se existir
    if 'NIC' in df.columns:
        nulos = df['NIC'].isnull().sum()
        unicos = df['NIC'].nunique()
        md_file.write(f"### Qualidade da Chave `NIC`\n")
        md_file.write(f"- Vazios: {nulos} ({(nulos/total_rows)*100:.2f}%)\n")
        md_file.write(f"- Valores Únicos: {unicos} (Mede a taxa de duplicidade)\n\n")

    # NR_DECLARACAO_OBITO
    if 'NR_DECLARACAO_OBITO' in df.columns:
        nulos = df['NR_DECLARACAO_OBITO'].isnull().sum()
        md_file.write(f"### Métrica de Ouro: `NR_DECLARACAO_OBITO`\n")
        md_file.write(f"- Vazios: {nulos} ({(nulos/total_rows)*100:.2f}%)\n\n")
        
    # Top 10 mais vazias
    null_counts = df.isnull().sum()
    pct_null = (null_counts / total_rows) * 100
    md_file.write("### Top 10 Colunas com Menos Preenchimento (Vazias)\n")
    vazias = pct_null[pct_null > 0].sort_values(ascending=False).head(10)
    for col, pct in vazias.items():
        md_file.write(f"- `{col}`: {null_counts[col]} nulos ({pct:.2f}%)\n")
    if len(vazias) == 0:
        md_file.write("- Nenhuma coluna possui vazios.\n")
    
    md_file.write("\n---\n\n")

if __name__ == "__main__":
    output_md_path = "docs/PROFILING_IML_AVANCADO_2025.md"
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write("# Profiling Forense Avançado (Laudos e Cadavérico) 2025\n\n")
        
        # Profile Cadaverico
        profile_csv("data/mock/extracao_iml_cadaverico_2025.csv", f, "1. Análise da Base CADAVÉRICO (SGOU)")
        
        # Profile Laudos
        profile_csv("data/mock/extracao_iml_laudo_2025.csv", f, "2. Análise da Base de LAUDOS (IML)")
        
    print(f"Relatório salvo em: {output_md_path}")
