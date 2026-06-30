"""
SENTINELA — Database Seeder (SQLite Local)
==========================================
Popula o banco SQLite local com dados das duas pipelines:

1. CONTROLE_MORTE (Gold Standard) → VW_SENTINELA_CASO_COMPLETO + SENTINELA_FILA_ALERTAS
2. RADAR CAD (Ocorrências sem vínculo) → SENTINELA_RADAR_CAD

⚠️ PROTEÇÃO: Este script opera SOMENTE sobre o SQLite local (sentinela.db).
   Nenhuma operação é realizada contra as bases Oracle de produção.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Adiciona o diretório raiz ao path para poder importar a api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.database import engine, Base, SessionLocal
from api.models import SentinelaFilaAlertas, VwSentinelaCasoCompleto, SentinelaRadarCAD

# Força UTF-8 no stdout para evitar erros de encoding no Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def clean_val(v, is_float=False):
    """Converte valores nulos/NaN para None para o banco."""
    if pd.isna(v) or v == 'nan' or v == 'NAN' or v == '':
        return None
    if is_float:
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
    return str(v)


def seed_casos(session, csv_path):
    """Carrega os casos completos do CSV consolidado Delta."""
    print("\n--- Sementeira: VW_SENTINELA_CASO_COMPLETO ---")
    
    df = pd.read_csv(csv_path, low_memory=False)
    df = df.drop_duplicates(subset=['ID_CONTROLE_MORTE'])
    print(f"  {len(df):,} registros unicos carregados do CSV.")
    
    casos_db = []
    for _, row in df.iterrows():
        caso = VwSentinelaCasoCompleto(
            ID_CONTROLE_MORTE=int(row['ID_CONTROLE_MORTE']),
            SUBJETIVIDADE=clean_val(row.get('SUBJETIVIDADE')),
            TIPO_MVI=clean_val(row.get('TIPO_MVI')),
            EH_MVI=bool(row.get('EH_MVI', False)),
            BO_PC=clean_val(row.get('BO_PC')),
            CAD=clean_val(row.get('CAD')),
            NIC=clean_val(row.get('NIC')),
            BAIRRO_FATO=clean_val(row.get('BAIRRO_FATO')),
            CIDADE_FATO=clean_val(row.get('CIDADE_FATO')),
            DATA_HORA_FATO=clean_val(row.get('DATA_HORA_FATO')),
            INSTRUMENTO_UTILIZADO=clean_val(row.get('INSTRUMENTO_UTILIZADO')),
            MOTIV_INICIAL=clean_val(row.get('MOTIV_INICIAL')),
            AISP=clean_val(row.get('AISP')),
            RISP=clean_val(row.get('RISP')),
            STATUS=clean_val(row.get('STATUS')),
            NOME_VITIMA=clean_val(row.get('NOME_VITIMA')),
            NOM_VITIMA_IML=clean_val(row.get('NOM_VITIMA')),
            ALERTA_BO_INEXISTENTE=clean_val(row.get('ALERTA_BO_INEXISTENTE')),
            ALERTA_NATUREZA_DIVERGENTE=clean_val(row.get('ALERTA_NATUREZA_DIVERGENTE')),
            ALERTA_CAD_FALTANTE=clean_val(row.get('ALERTA_CAD_FALTANTE')),
            ALERTA_DO_IML_VAZIA=clean_val(row.get('ALERTA_DO_IML_VAZIA')),
            ALERTA_NIC_FALTANTE=clean_val(row.get('ALERTA_NIC_FALTANTE')),
            ALERTA_NOME_DIVERGENTE=clean_val(row.get('ALERTA_NOME_DIVERGENTE')),
            NUM_BO=clean_val(row.get('NUM_BO')),
            NO_NATUREZA_OCORRENCIA=clean_val(row.get('NO_NATUREZA_OCORRENCIA')),
            DS_GRUPO_NATUREZA=clean_val(row.get('DS_GRUPO_NATUREZA')),
            ID_OCOR=clean_val(row.get('ID_OCOR')),
            DS_NATUREZA_ATEND=clean_val(row.get('DS_NATUREZA_ATEND')),
            DS_GRUPO_CRIME_ATEND=clean_val(row.get('DS_GRUPO_CRIME_ATEND')),
            NR_COOR_LATD=clean_val(row.get('NR_COOR_LATD'), is_float=True),
            NR_COOR_LONG=clean_val(row.get('NR_COOR_LONG'), is_float=True),
            NIC_IML=clean_val(row.get('NIC_IML')),
            TIPO_MORTE=clean_val(row.get('TIPO_MORTE')),
            NR_DECLARACAO_OBITO=clean_val(row.get('NR_DECLARACAO_OBITO')),
            SEXO=clean_val(row.get('SEXO')),
            ETNIA=clean_val(row.get('ETNIA')),
            NASCIMENTO=clean_val(row.get('NASCIMENTO'))
        )
        casos_db.append(caso)
    
    session.bulk_save_objects(casos_db)
    session.commit()
    print(f"  Inseridos {len(casos_db):,} registros em VW_SENTINELA_CASO_COMPLETO.")


def seed_alertas(session, csv_path):
    """Gera a fila de alertas a partir dos registros MVI com inconsistências."""
    print("\n--- Sementeira: SENTINELA_FILA_ALERTAS ---")
    
    df = pd.read_csv(csv_path, low_memory=False)
    df = df.drop_duplicates(subset=['ID_CONTROLE_MORTE'])
    df_mvi = df[df['EH_MVI'] == True]
    
    alertas_db = []
    for _, row in df_mvi.iterrows():
        id_cm = int(row['ID_CONTROLE_MORTE'])
        nic = clean_val(row.get('NIC'))
        bo_pc = clean_val(row.get('BO_PC'))
        cad = clean_val(row.get('CAD'))
        
        # Alerta 1: BO PC Inexistente
        if row.get('ALERTA_BO_INEXISTENTE') == 'SIM':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=2,
                TIPO_ALERTA="BO PC Não Localizado no DAAS"
            ))
        
        # Alerta 2: Natureza Divergente
        if row.get('ALERTA_NATUREZA_DIVERGENTE') == 'VERIFICAR':
            natureza = row.get('NO_NATUREZA_OCORRENCIA')
            desc = f"Natureza Divergente no DAAS: '{natureza}'" if pd.notna(natureza) else "Natureza Divergente no DAAS"
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=2, TIPO_ALERTA=desc
            ))
        
        # Alerta 3: CAD Faltante
        if row.get('ALERTA_CAD_FALTANTE') == 'SIM':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=1,
                TIPO_ALERTA="Número do CAD não localizado no 190"
            ))
        
        # Alerta 4: DO IML Vazia
        if row.get('ALERTA_DO_IML_VAZIA') == 'CRITICO':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=3,
                TIPO_ALERTA="Corpo sem Declaração de Óbito (DO) no IML"
            ))
        
        # Alerta 5: NIC Faltante
        if row.get('ALERTA_NIC_FALTANTE') == 'SIM':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=2,
                TIPO_ALERTA="Caso MVI sem registro de NIC no IML"
            ))
            
        # Alerta 6: Divergência de Nome da Vítima
        if row.get('ALERTA_NOME_DIVERGENTE') == 'VERIFICAR':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=2,
                TIPO_ALERTA="Divergência de Nome da Vítima (IML)"
            ))
    
    session.bulk_save_objects(alertas_db)
    session.commit()
    print(f"  Gerados {len(alertas_db):,} alertas na fila.")


def seed_radar(session, radar_csv_path):
    """Popula a tabela de Radar CAD com ocorrências sem vínculo na CONTROLE_MORTE."""
    print("\n--- Sementeira: SENTINELA_RADAR_CAD ---")
    
    if not os.path.exists(radar_csv_path):
        print(f"  AVISO: CSV do Radar nao encontrado em '{radar_csv_path}'.")
        print("  Executando scripts/radar_cad.py para gerar...")
        
        # Tenta gerar o CSV do Radar
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
            from radar_cad import run_radar_cad
            run_radar_cad()
        except Exception as e:
            print(f"  ERRO ao gerar Radar: {e}")
            return
    
    df_radar = pd.read_csv(radar_csv_path, low_memory=False)
    df_radar = df_radar.drop_duplicates(subset=['ID_OCOR'])
    print(f"  {len(df_radar):,} registros unicos do Radar carregados.")
    
    radar_db = []
    for _, row in df_radar.iterrows():
        item = SentinelaRadarCAD(
            ID_OCOR=int(row['ID_OCOR']),
            DS_NATUREZA_ATEND=clean_val(row.get('DS_NATUREZA_ATEND')),
            DS_GRUPO_CRIME_ATEND=clean_val(row.get('DS_GRUPO_CRIME_ATEND')),
            DT_OCOR=clean_val(row.get('DT_OCOR')),
            TURNO=clean_val(row.get('TURNO')),
            CIDADE=clean_val(row.get('CIDADE')),
            BAIRRO=clean_val(row.get('BAIRRO')),
            NR_COOR_LATD=clean_val(row.get('NR_COOR_LATD'), is_float=True),
            NR_COOR_LONG=clean_val(row.get('NR_COOR_LONG'), is_float=True),
            TEM_GPS=bool(row.get('TEM_GPS', False)),
            DS_STATUS=clean_val(row.get('DS_STATUS')),
            DS_OCOR=clean_val(row.get('DS_OCOR')),
            PRIORIDADE_RADAR=int(row.get('PRIORIDADE_RADAR', 1)),
            CLASSIFICACAO_RADAR=clean_val(row.get('CLASSIFICACAO_RADAR')),
            NIVEL_RADAR=clean_val(row.get('NIVEL_RADAR')),
            STATUS_RADAR=clean_val(row.get('STATUS_RADAR', 'Novo')),
            DT_DETECCAO=datetime.now(),
            DT_VALIDACAO=None
        )
        radar_db.append(item)
    
    session.bulk_save_objects(radar_db)
    session.commit()
    print(f"  Inseridos {len(radar_db):,} registros em SENTINELA_RADAR_CAD.")


def seed_database():
    print("=" * 60)
    print("  SENTINELA - Sementeira Completa do Banco SQLite")
    print(f"  Execucao: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    delta_csv = "data/output/sentinela_relatorio_delta_2025.csv"
    radar_csv = "data/output/sentinela_radar_cad_2025.csv"
    
    if not os.path.exists(delta_csv):
        print(f"ERRO: '{delta_csv}' nao encontrado. Rode 'python scripts/cruzamento_delta.py' primeiro.")
        return
    
    # Limpar banco existente
    db_path = "sentinela.db"
    if os.path.exists(db_path):
        print(f"\nRemovendo banco existente '{db_path}'...")
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"  AVISO: Nao foi possivel deletar {db_path}: {e}")
    
    # Criar todas as tabelas
    print("Criando tabelas no SQLite...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # 1. Casos completos
        seed_casos(session, delta_csv)
        
        # 2. Fila de alertas
        seed_alertas(session, delta_csv)
        
        # 3. Radar CAD
        seed_radar(session, radar_csv)
        
    except Exception as e:
        session.rollback()
        print(f"\nERRO durante a sementeira: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
    
    print("\n" + "=" * 60)
    print("  Sementeira finalizada com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    seed_database()
