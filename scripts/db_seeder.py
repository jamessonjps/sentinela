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
            SEXO_VITIMA=clean_val(row.get('SEXO_VITIMA')),
            MAE_VITIMA=clean_val(row.get('MAE_VITIMA')),
            NASC_VITIMA=clean_val(row.get('NASC_VITIMA')),
            COR_RACA_VITIMA=clean_val(row.get('COR_RACA_VITIMA')),
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
            ED_BAIRRO=clean_val(row.get('ED_BAIRRO')),
            NO_MUNICIPIO=clean_val(row.get('NO_MUNICIPIO')),
            DT_OCORRENCIA=clean_val(row.get('DT_OCORRENCIA')),
            SN_TENTATIVA=int(float(row.get('SN_TENTATIVA'))) if pd.notna(row.get('SN_TENTATIVA')) and row.get('SN_TENTATIVA') != '' else None,
            SN_MARIA_DA_PENHA=int(float(row.get('SN_MARIA_DA_PENHA'))) if pd.notna(row.get('SN_MARIA_DA_PENHA')) and row.get('SN_MARIA_DA_PENHA') != '' else None,
            IN_SITUACAO_ATUAL=clean_val(row.get('IN_SITUACAO_ATUAL')),

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
            NASCIMENTO=clean_val(row.get('NASCIMENTO')),
            STATUS_IML=clean_val(row.get('STATUS_IML_STAT')),
            MAE_IML=clean_val(row.get('MAE')),
            IML_ENTRADA=clean_val(row.get('DATA_ENTRADA') or row.get('IML_ENTRADA'))
        )
        casos_db.append(caso)
    
    session.bulk_save_objects(casos_db)
    session.commit()
    print(f"  Inseridos {len(casos_db):,} registros em VW_SENTINELA_CASO_COMPLETO.")
    
    # Inserir Casos Mocks específicos para teste de Geovalidação
    caso_hge = VwSentinelaCasoCompleto(
        ID_CONTROLE_MORTE=99901,
        SUBJETIVIDADE="CVLI HOMICIDIO",
        TIPO_MVI="HOMICÍDIO TIPO HGE",
        EH_MVI=True,
        CAD="CAD-2026-HGE-001",
        NIC="NIC-2026-HGE-001",
        CIDADE_FATO="MACEIO",
        BAIRRO_FATO="CENTRO",
        DATA_HORA_FATO="2026-06-28 22:30:00",
        INSTRUMENTO_UTILIZADO="ARMA DE FOGO",
        MOTIV_INICIAL="DISCUSSÃO",
        AISP="AISP 1",
        RISP="RISP 1",
        STATUS="EM APURACAO",
        NOME_VITIMA="VÍTIMA MOCK GEIVALIDAÇÃO HGE",
        SEXO_VITIMA="M",
        MAE_VITIMA="MAE HGE",
        NASC_VITIMA="1990-01-01",
        COR_RACA_VITIMA="PARDA",
        NOM_VITIMA_IML="VÍTIMA MOCK GEIVALIDAÇÃO HGE",
        ALERTA_BO_INEXISTENTE="NAO",
        ALERTA_NATUREZA_DIVERGENTE="OK",
        ALERTA_CAD_FALTANTE="NAO",
        ALERTA_DO_IML_VAZIA="OK",
        ALERTA_NIC_FALTANTE="NAO",
        ALERTA_NOME_DIVERGENTE="OK",
        ID_OCOR=99901.0,
        DS_NATUREZA_ATEND="HOMICIDIO",
        DS_GRUPO_CRIME_ATEND="VIOLENCIA",
        NR_COOR_LATD=-9.6582, # HGE
        NR_COOR_LONG=-35.7441, # HGE
        NIC_IML="NIC-2026-HGE-001",
        TIPO_MORTE="VIOLENTA",
        NR_DECLARACAO_OBITO="DO-2026-HGE-001",
        SEXO="M",
        ETNIA="PARDA",
        NASCIMENTO="1990-01-01",
        STATUS_IML="CONCLUIDA",
        MAE_IML="MAE HGE",
        IML_ENTRADA="2026-06-28 23:00:00"
    )

    caso_div = VwSentinelaCasoCompleto(
        ID_CONTROLE_MORTE=99902,
        SUBJETIVIDADE="CVLI HOMICIDIO",
        TIPO_MVI="HOMICÍDIO TIPO INCONSISTENCIA",
        EH_MVI=True,
        CAD="CAD-2026-GEO-002",
        NIC="NIC-2026-GEO-002",
        CIDADE_FATO="MACEIO",
        BAIRRO_FATO="JACINTINHO",
        DATA_HORA_FATO="2026-06-29 01:15:00",
        INSTRUMENTO_UTILIZADO="ARMA BRANCA",
        MOTIV_INICIAL="RIXA",
        AISP="AISP 2",
        RISP="RISP 2",
        STATUS="EM APURACAO",
        NOME_VITIMA="VÍTIMA MOCK BAIRRO INCONSISTENTE",
        SEXO_VITIMA="M",
        MAE_VITIMA="MAE INCONSISTENTE",
        NASC_VITIMA="1995-05-15",
        COR_RACA_VITIMA="BRANCA",
        NOM_VITIMA_IML="VÍTIMA MOCK BAIRRO INCONSISTENTE",
        ALERTA_BO_INEXISTENTE="NAO",
        ALERTA_NATUREZA_DIVERGENTE="OK",
        ALERTA_CAD_FALTANTE="NAO",
        ALERTA_DO_IML_VAZIA="OK",
        ALERTA_NIC_FALTANTE="NAO",
        ALERTA_NOME_DIVERGENTE="OK",
        ID_OCOR=99902.0,
        DS_NATUREZA_ATEND="HOMICIDIO",
        DS_GRUPO_CRIME_ATEND="VIOLENCIA",
        NR_COOR_LATD=-9.5492, # Benedito Bentes (Inconsistente com Jacintinho!)
        NR_COOR_LONG=-35.7335, # Benedito Bentes
        NIC_IML="NIC-2026-GEO-002",
        TIPO_MORTE="VIOLENTA",
        NR_DECLARACAO_OBITO="DO-2026-GEO-002",
        SEXO="M",
        ETNIA="BRANCA",
        NASCIMENTO="1995-05-15",
        STATUS_IML="CONCLUIDA",
        MAE_IML="MAE INCONSISTENTE",
        IML_ENTRADA="2026-06-29 02:00:00"
    )

    caso_presidio = VwSentinelaCasoCompleto(
        ID_CONTROLE_MORTE=99903,
        SUBJETIVIDADE="CVLI HOMICIDIO",
        TIPO_MVI="HOMICÍDIO TIPO PRESÍDIO",
        EH_MVI=True,
        CAD="CAD-2026-PRES-003",
        NIC="NIC-2026-PRES-003",
        CIDADE_FATO="MACEIO",
        BAIRRO_FATO="CIDADE UNIVERSITARIA",
        DATA_HORA_FATO="2026-06-29 06:20:00",
        INSTRUMENTO_UTILIZADO="ESTRANGULAMENTO",
        MOTIV_INICIAL="RIXA INTERNA",
        AISP="AISP 5",
        RISP="RISP 1",
        STATUS="EM APURACAO",
        NOME_VITIMA="VÍTIMA MOCK PRESÍDIO MACEIÓ",
        SEXO_VITIMA="M",
        MAE_VITIMA="MAE PRESIDIO",
        NASC_VITIMA="1988-08-12",
        COR_RACA_VITIMA="PRETA",
        NOM_VITIMA_IML="VÍTIMA MOCK PRESÍDIO MACEIÓ",
        ALERTA_BO_INEXISTENTE="NAO",
        ALERTA_NATUREZA_DIVERGENTE="OK",
        ALERTA_CAD_FALTANTE="NAO",
        ALERTA_DO_IML_VAZIA="OK",
        ALERTA_NIC_FALTANTE="NAO",
        ALERTA_NOME_DIVERGENTE="OK",
        ID_OCOR=99903.0,
        DS_NATUREZA_ATEND="HOMICIDIO",
        DS_GRUPO_CRIME_ATEND="VIOLENCIA",
        NR_COOR_LATD=-9.548056, # Complexo Prisional
        NR_COOR_LONG=-35.7775, # Complexo Prisional
        NIC_IML="NIC-2026-PRES-003",
        TIPO_MORTE="VIOLENTA",
        NR_DECLARACAO_OBITO="DO-2026-PRES-003",
        SEXO="M",
        ETNIA="PRETA",
        NASCIMENTO="1988-08-12",
        STATUS_IML="CONCLUIDA",
        MAE_IML="MAE PRESIDIO",
        IML_ENTRADA="2026-06-29 07:15:00",
        ORGAO_REQUERENTE="PRESÍDIO BALDOMERO CAVALCANTE",
        REQUERENTE_OUTROS="COMPLEXO PRISIONAL DE MACEIO"
    )

    session.add(caso_hge)
    session.add(caso_div)
    session.add(caso_presidio)
    session.commit()
    print("  Inseridos 3 casos mock adicionais (HGE, Bairro Inconsistente, Presídio) para testes de geovalidação.")



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
                STATUS="Novo", PRIORIDADE=4,
                TIPO_ALERTA="Caso MVI sem registro de NIC no IML"
            ))
            
        # Alerta 6: Divergência de Nome da Vítima
        if row.get('ALERTA_NOME_DIVERGENTE') == 'VERIFICAR':
            alertas_db.append(SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm, NIC=nic, BO_PC=bo_pc, CAD=cad,
                STATUS="Novo", PRIORIDADE=4,
                TIPO_ALERTA="Divergência de Nome da Vítima (IML)"
            ))
    
    session.bulk_save_objects(alertas_db)
    session.commit()
    print(f"  Gerados {len(alertas_db):,} alertas na fila.")
    
    # Inserir alertas geográficos fictícios correspondentes
    session.add(SentinelaFilaAlertas(
        ID_CONTROLE_MORTE=99901, NIC="NIC-2026-HGE-001", BO_PC="BO-2026-HGE-001", CAD="CAD-2026-HGE-001",
        STATUS="Novo", PRIORIDADE=2,
        TIPO_ALERTA="Local do Fato aponta para Hospital/UPA (Socorro)"
    ))
    session.add(SentinelaFilaAlertas(
        ID_CONTROLE_MORTE=99902, NIC="NIC-2026-GEO-002", BO_PC="BO-2026-GEO-002", CAD="CAD-2026-GEO-002",
        STATUS="Novo", PRIORIDADE=1,
        TIPO_ALERTA="Bairro Divergente das Coordenadas GPS"
    ))
    session.add(SentinelaFilaAlertas(
        ID_CONTROLE_MORTE=99903, NIC="NIC-2026-PRES-003", BO_PC="BO-2026-PRES-003", CAD="CAD-2026-PRES-003",
        STATUS="Novo", PRIORIDADE=3,
        TIPO_ALERTA="Óbito em Estabelecimento Prisional"
    ))
    session.commit()
    print("  Inseridos 3 alertas mock geográficos/prisionais adicionais na fila.")



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


def seed_novas_tabelas(session):
    """Gera dados mock de propostas de evolução e notificações IML para validação local."""
    print("\n--- Sementeira: NOVAS TABELAS OPERACIONAIS (Evolução e Notificação) ---")
    from api.models import SentinelaEvolucaoPendente, SentinelaNotificacaoIML, VwSentinelaCasoCompleto
    from datetime import timedelta
    
    # 1. Tenta recuperar duas tentativas da base para usar IDs de verdade
    tentativas = session.query(VwSentinelaCasoCompleto).filter(
        VwSentinelaCasoCompleto.SUBJETIVIDADE.ilike("%TENTATIVA%")
    ).limit(2).all()
    
    id_1 = tentativas[0].ID_CONTROLE_MORTE if len(tentativas) >= 1 else 67066
    id_2 = tentativas[1].ID_CONTROLE_MORTE if len(tentativas) >= 2 else 67136
    
    # Inserir propostas de evolução de exemplo
    prop_1 = SentinelaEvolucaoPendente(
        ID_CONTROLE_MORTE=id_1,
        NIC_IML="NIC-50122",
        BO_PC="BO-2026-PC-98772",
        DATA_OBITO=datetime.now() - timedelta(days=2),
        STATUS="Pendente",
        MOTIVO="Vítima de tentativa no Jacintinho no dia 20/06, evoluiu a óbito no HGE em 21/06. Consta entrada correspondente no IML.",
        TIPO_EVOLUCAO="Tentativa -> Óbito",
        AUTOR_PROPOSTA="Thais Aline"
    )
    
    prop_2 = SentinelaEvolucaoPendente(
        ID_CONTROLE_MORTE=id_2,
        NIC_IML="NIC-50289",
        BO_PC=None,
        DATA_OBITO=datetime.now() - timedelta(days=1),
        STATUS="Pendente",
        MOTIVO="Óbito confirmado. Inexistência temporária de BO de homicídio, apenas BO de desaparecimento anterior.",
        TIPO_EVOLUCAO="Tentativa -> Óbito",
        AUTOR_PROPOSTA="Laís Policarpto"
    )
    
    session.add(prop_1)
    session.add(prop_2)
    
    # Inserir notificações de exemplo do IML
    notif_1 = SentinelaNotificacaoIML(
        NIC="NIC-50122",
        NOME_VITIMA="ROSEVALDO MENEZES BATISTA",
        STATUS_IML="Concluído",
        TIPO_MENSAGEM="Nova evolução identificada",
        LIDO=0
    )
    
    notif_2 = SentinelaNotificacaoIML(
        NIC="NIC-50289",
        NOME_VITIMA="MARCOS ANTONIO SILVA DA PAZ",
        STATUS_IML="Entrada",
        TIPO_MENSAGEM="Corpo registrado sem Declaração de Óbito (DO)",
        LIDO=0
    )
    
    notif_3 = SentinelaNotificacaoIML(
        NIC="NIC-49877",
        NOME_VITIMA="FABRICIO GOMES DOS SANTOS",
        STATUS_IML="Laudo Pendente",
        TIPO_MENSAGEM="Corpo identificado no IML",
        LIDO=0
    )
    
    session.add(notif_1)
    session.add(notif_2)
    session.add(notif_3)
    
    session.commit()
    print("  Inseridos dados operacionais em SENTINELA_EVOLUCAO_PENDENTE e SENTINELA_NOTIFICACAO_IML.")


def seed_geometria(session):
    """Insere dados centróides dos bairros e estabelecimentos de saúde no banco local."""
    print("\n--- Sementeira: DADOS DE REFERÊNCIA GEOGRÁFICA (Geo Bairros & Hospitais) ---")
    from api.models import SentinelaGeoBairro, SentinelaEstabelecimentoSaude
    
    # 1. Bairros
    bairros = [
        SentinelaGeoBairro(NOME_BAIRRO="Benedito Bentes", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.5492, CENTRO_LONGITUDE=-35.7335, RAIO_KM=3.5),
        SentinelaGeoBairro(NOME_BAIRRO="Jacintinho", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.6436, CENTRO_LONGITUDE=-35.7176, RAIO_KM=1.5),
        SentinelaGeoBairro(NOME_BAIRRO="Centro", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.6644, CENTRO_LONGITUDE=-35.7397, RAIO_KM=1.0),
        SentinelaGeoBairro(NOME_BAIRRO="Clima Bom", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.5750, CENTRO_LONGITUDE=-35.7720, RAIO_KM=2.0),
        SentinelaGeoBairro(NOME_BAIRRO="Jatiúca", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.6480, CENTRO_LONGITUDE=-35.7020, RAIO_KM=1.2),
        SentinelaGeoBairro(NOME_BAIRRO="Ponta Verde", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.6620, CENTRO_LONGITUDE=-35.7010, RAIO_KM=0.8),
        SentinelaGeoBairro(NOME_BAIRRO="Trapiche da Barra", NOME_MUNICIPIO="MACEIO", CENTRO_LATITUDE=-9.6780, CENTRO_LONGITUDE=-35.7560, RAIO_KM=1.2)
    ]
    
    session.add_all(bairros)
    
    # 2. Hospitais / UPAs / Presídios
    hospitais = [
        SentinelaEstabelecimentoSaude(NOME="Hospital Geral do Estado (HGE)", LATITUDE=-9.6582, LONGITUDE=-35.7441, RAIO_METROS=150.0, TIPO="HOSPITAL"),
        SentinelaEstabelecimentoSaude(NOME="UPA Benedito Bentes", LATITUDE=-9.5521, LONGITUDE=-35.7312, RAIO_METROS=120.0, TIPO="UPA"),
        SentinelaEstabelecimentoSaude(NOME="Hospital de Emergência do Agreste (HEA)", LATITUDE=-9.7540, LONGITUDE=-36.6520, RAIO_METROS=150.0, TIPO="HOSPITAL"),
        SentinelaEstabelecimentoSaude(NOME="Complexo Prisional de Maceió", LATITUDE=-9.548056, LONGITUDE=-35.7775, RAIO_METROS=450.0, TIPO="PRESIDIO"),
        SentinelaEstabelecimentoSaude(NOME="Presídio do Agreste (Girau/Craíbas)", LATITUDE=-9.8510, LONGITUDE=-36.8340, RAIO_METROS=300.0, TIPO="PRESIDIO")
    ]
    
    session.add_all(hospitais)
    session.commit()
    print("  Inseridos dados de referência geográfica (incluindo presídios) com sucesso.")


def seed_laudos(session):
    """Insere laudos periciais fictícios para testar a reconciliação (Forensis)."""
    print("\n--- Sementeira: LAUDOS DO IML (Forensis) ---")
    from api.models import SentinelaLaudoIML
    
    laudos = [
        SentinelaLaudoIML(
            NIC="NIC-2026-HGE-001",
            COD_REQUISICAO="CAD-2026-HGE-001",
            DATA_CADASTRO="2026-06-29 03:00:00",
            DATA_EXAME="2026-06-29 05:00:00",
            CONCLUSAO="ÓBITO POR CHOQUE HIPOVOLÊMICO SECUNDÁRIO A FERIMENTOS PENETRANTES POR PROJÉTEIS DE ARMA DE FOGO (PAF). HOMICÍDIO.",
            NUMERO_PROTOCOLO="LAUDO-2026-001",
            TIPO_EXAME="NECROPSIA",
            PACIENTE="VÍTIMA MOCK HGE",
            PERITO_LEGISTA="Dr. Carlos Eduardo (CRM/AL 9988)",
            ORGAO_DESTINO="DHPP MACEIO"
        ),
        # Divergência de Causa Mortis (Suicídio no Laudo, mas CVLI na Controle Morte)
        SentinelaLaudoIML(
            NIC="NIC-2026-GEO-002",
            COD_REQUISICAO="CAD-2026-GEO-002",
            DATA_CADASTRO="2026-06-29 04:00:00",
            DATA_EXAME="2026-06-29 06:15:00",
            CONCLUSAO="ASFIXIA MECÂNICA COMPATÍVEL COM ENFORCAMENTO. INDÍCIOS TÉCNICOS FORTES DE SUICÍDIO.",
            NUMERO_PROTOCOLO="LAUDO-2026-002",
            TIPO_EXAME="NECROPSIA",
            PACIENTE="VÍTIMA MOCK GEO DIVERGENTE",
            PERITO_LEGISTA="Dra. Flávia Albuquerque (CRM/AL 5543)",
            ORGAO_DESTINO="1º DISTRITO POLICIAL"
        ),
        SentinelaLaudoIML(
            NIC="NIC-2026-PRES-003",
            COD_REQUISICAO="CAD-2026-PRES-003",
            DATA_CADASTRO="2026-06-29 07:30:00",
            DATA_EXAME="2026-06-29 09:00:00",
            CONCLUSAO="TRAUMATISMO CRANIOENCEFÁLICO DEVIDO A AÇÃO DE INSTRUMENTO CONTUNDENTE. AGRESSÃO FÍSICA.",
            NUMERO_PROTOCOLO="LAUDO-2026-003",
            TIPO_EXAME="NECROPSIA",
            PACIENTE="VÍTIMA MOCK PRESÍDIO MACEIÓ",
            PERITO_LEGISTA="Dr. Carlos Eduardo (CRM/AL 9988)",
            ORGAO_DESTINO="DELEGACIA DE HOMICÍDIOS"
        ),
        # Divergência Fonética de Nome
        SentinelaLaudoIML(
            NIC="NIC-2025-60400",
            COD_REQUISICAO="160400.0",
            DATA_CADASTRO="2025-04-14 20:00:00",
            DATA_EXAME="2025-04-14 22:00:00",
            CONCLUSAO="ASFIXIA MECÂNICA POR ESTRANGULAMENTO. COMPATÍVEL COM MVI.",
            NUMERO_PROTOCOLO="LAUDO-2025-60400",
            TIPO_EXAME="NECROPSIA",
            PACIENTE="VITIMA DE HOMICIDIO ERRO NOME SEMENTEIRA",
            PERITO_LEGISTA="Dra. Maria Mendes (CRM/AL 1234)",
            ORGAO_DESTINO="DELEGACIA DE RIO LARGO"
        )
    ]
    
    session.add_all(laudos)
    session.commit()
    print("  Inseridos 4 laudos periciais de teste (Forensis) com sucesso.")



def seed_database():
    print("=" * 60)
    print("  SENTINELA - Sementeira Completa do Banco SQLite")
    print(f"  Execucao: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    delta_csv = "data/output/sentinela_relatorio_delta_2025.csv"
    radar_csv = "data/output/sentinela_radar_cad_2025.csv"
    
    if not os.path.exists(delta_csv) or not os.path.exists(radar_csv):
        print("\n[!] Arquivos finais nao encontrados em data/output/.")
        print("    Iniciando geracao de dados mock e processamento do pipeline...")
        try:
            # 1. Gerar dados mock iniciais
            from scripts.generate_mock_data import generate_mock_data
            generate_mock_data()
            
            # 2. Rodar o cruzamento delta
            from scripts.cruzamento_delta import run_delta_v3
            run_delta_v3()
            
            # 3. Rodar o radar cad
            from scripts.radar_cad import run_radar_cad
            run_radar_cad()
            
            print("\n[OK] Pipeline de processamento executado com sucesso!")
        except Exception as e:
            print(f"\n[ERRO] Falha ao executar pipeline automaticamente: {e}")
            import traceback
            traceback.print_exc()
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
        
        # 4. Novas tabelas operacionais
        seed_novas_tabelas(session)
        
        # 5. Tabelas de geometria e estabelecimentos de saúde
        seed_geometria(session)
        
        # 5.1. Tabela de laudos periciais do IML (Forensis)
        seed_laudos(session)
        
        # 6. Executar reconciliação de dados local
        print("\n--- Executando Reconciliador de Dados (Motor local) ---")
        from agents.reconciliation_agent.orchestrator import ReconciliationOrchestrator
        orch = ReconciliationOrchestrator()
        res = orch.run_reconciliation(session)
        print(f"  Resultado do Reconciliador: {res}")
        
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
