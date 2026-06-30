import pandas as pd

def investiga_duplicados(csv_path):
    print("Iniciando investigação de BOs duplicados...")
    try:
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return

    # Filter rows where NUM_BO is duplicated
    duplicados = df[df.duplicated(subset=['NUM_BO'], keep=False)]
    
    if len(duplicados) == 0:
        print("Não há BOs duplicados (algo mudou no dataset).")
        return

    print(f"Encontradas {len(duplicados)} linhas referentes a BOs que se repetem.")
    
    # Check which columns vary the most among the duplicated BO groups
    colunas_variacao = []
    
    # We group by NUM_BO and check unique counts per column
    print("Calculando quais colunas causam a multiplicidade de linhas (variam dentro do mesmo BO)...")
    grouped = duplicados.groupby('NUM_BO')
    nunique_per_bo = grouped.nunique()
    
    # For each column, if max unique values > 1, it means this column varies within the same BO
    max_unique_cols = nunique_per_bo.max()
    variating_cols = max_unique_cols[max_unique_cols > 1].index.tolist()
    
    print("\nColunas que sofrem variação dentro do mesmo BO (motivo da duplicidade):")
    for col in variating_cols:
        print(f"- {col}")
        
    # Pick a random duplicated BO to display as an example
    sample_bo = duplicados['NUM_BO'].iloc[0]
    print(f"\nExemplo real de variação - NUM_BO: {sample_bo}")
    exemplo = duplicados[duplicados['NUM_BO'] == sample_bo]
    
    # Show only the columns that vary, plus the BO number
    cols_to_show = ['NUM_BO'] + variating_cols
    print(exemplo[cols_to_show].to_string())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()
    investiga_duplicados(args.csv_path)
