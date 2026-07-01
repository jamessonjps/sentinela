import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data():
    print("============================================================")
    # Forçar criação do diretório data/mock
    os.makedirs("data/mock", exist_ok=True)
    print("Gerando arquivos de dados mock em data/mock/...")

    # Gerador de números pseudo-aleatórios com semente fixa para reprodutibilidade
    np.random.seed(42)
    
    # 1. CONTROLE_MORTE (Base Mestra)
    # Vamos gerar 150 registros
    n_casos = 150
    ids_cm = list(range(60400, 60400 + n_casos))
    
    subjetividades = ['CVLI', 'CVLI OUTROS', 'CVLI A CONFIRMAR', 'RMNC', 'TENTATIVA', 'SUICÍDIO', 'MORTE A ESCLARECER']
    probs_subjetividade = [0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    
    instrumentos = ['ARMA DE FOGO', 'ARMA BRANCA', 'ASFIXIA', 'OUTRO', 'DESCONHECIDO']
    motivacoes = ['TRÁFICO DE DROGAS', 'ACERTO DE CONTAS', 'FATO A ESCLARECER', 'CONFLITO FAMILIAR', 'RIXA']
    cidades = ['MACEIO', 'ARAPIRACA', 'PALMEIRA DOS INDIOS', 'RIO LARGO', 'MARECHAL DEODORO']
    bairros = ['CENTRO', 'JATIUCA', 'TABULEIRO DO PINTO', 'BENEDITO BENTES', 'CLIMA BOM', 'POCO']
    
    cm_records = []
    
    for i, id_cm in enumerate(ids_cm):
        # Gerar datas plausíveis ao longo de 2025
        dia_ano = np.random.randint(1, 365)
        dt_fato = datetime(2025, 1, 1) + timedelta(days=dia_ano, hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        dt_fato_str = dt_fato.strftime('%Y-%m-%d %H:%M:%S')
        
        # Subjetividade
        sub = np.random.choice(subjetividades, p=probs_subjetividade)
        
        # Chaves de cruzamento (às vezes nulas para testar alertas)
        has_bo = np.random.rand() > 0.15
        bo_pc = f"BO-{dt_fato.strftime('%Y')}-{id_cm:04d}" if has_bo else None
        
        has_cad = np.random.rand() > 0.15
        cad = id_cm + 100000 if has_cad else None
        
        has_nic = np.random.rand() > 0.10
        nic = f"NIC-{dt_fato.strftime('%Y')}-{id_cm:04d}" if has_nic else None
        
        # Forçar casos específicos de reconciliação de evolução tentativa -> óbito
        if id_cm == 60413:
            dt_fato = datetime(2025, 8, 8, 14, 0, 0)
            dt_fato_str = dt_fato.strftime('%Y-%m-%d %H:%M:%S')
            sub = 'CVLI'
            bo_pc = "BO-2025-0413"
            cad = 160413
            nic = "NIC-2025-0413"
        elif id_cm == 60415:
            dt_fato = datetime(2025, 8, 1, 10, 0, 0)
            dt_fato_str = dt_fato.strftime('%Y-%m-%d %H:%M:%S')
            sub = 'TENTATIVA'
            bo_pc = "BO-2025-0413"
            cad = 160415
            nic = None
            
        # Testar alertas específicos nos casos MVI:
        is_mvi = sub in ['CVLI', 'CVLI OUTROS', 'CVLI A CONFIRMAR']
        
        # Forçar alguns alertas específicos nos MVI
        if is_mvi and i % 10 == 0:
            bo_pc = None  # Alerta 1: BO PC Inexistente
        if is_mvi and i % 10 == 1:
            cad = None  # Alerta 3: CAD Faltante
        if is_mvi and i % 10 == 2:
            nic = None  # Alerta 5: NIC Faltante (sem corpo registrado no IML)
            
        nome_vit = f"VITIMA_{id_cm}"
        if id_cm in [60413, 60415]:
            nome_vit = "VALENTINA DOS SANTOS ALMEIDA"

            
        # Sobrescrever casos específicos de teste de nome divergente (Fase 8)
        # ID_CONTROLE_MORTE específicos esperados em cruzamento_delta.py
        if id_cm in [60475, 60476, 60478, 60479, 60480]:
            nome_vit = f"VITIMA_{id_cm}"  # Mestra está como "VITIMA_XXXX"
            sub = 'CVLI'  # Garantir que seja MVI
            nic = f"NIC_{id_cm}"
            cad = id_cm + 100000
            bo_pc = f"BO-2025-{id_cm:04d}"

            
        cm_records.append({
            'ID_CONTROLE_MORTE': id_cm,
            'SUBJETIVIDADE': sub,
            'BO_PC': bo_pc,
            'CAD': cad,
            'NIC': nic,
            'NOME_VITIMA': nome_vit,
            'SEXO_VITIMA': np.random.choice(['M', 'F'], p=[0.8, 0.2]),
            'MAE_VITIMA': f"MAE_{nome_vit}",
            'COR_RACA_VITIMA': np.random.choice(['PRETA', 'PARDA', 'BRANCA'], p=[0.3, 0.6, 0.1]),
            'BAIRRO_FATO': np.random.choice(bairros),
            'CIDADE_FATO': np.random.choice(cidades),
            'DATA_HORA_FATO': dt_fato_str,
            'INSTRUMENTO_UTILIZADO': np.random.choice(instrumentos),
            'MOTIV_INICIAL': np.random.choice(motivacoes),
            'AISP': f"AISP {np.random.randint(1, 10)}",
            'RISP': f"RISP {np.random.randint(1, 4)}",
            'STATUS': 'CONCLUIDO' if np.random.rand() > 0.3 else 'EM APURACAO',
            'STATUS_NECROPSIA': 'CONCLUIDA' if np.random.rand() > 0.1 else 'PENDENTE',
            'ALTER_DATE': (dt_fato + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'NASC_VITIMA': (dt_fato - timedelta(days=365*np.random.randint(18, 60))).strftime('%Y-%m-%d')

        })
        
    df_cm = pd.DataFrame(cm_records)
    df_cm.to_csv("data/mock/controle_morte_2025_limpo.csv", index=False)
    print(f"  → Gerado controle_morte_2025_limpo.csv ({len(df_cm)} linhas)")
    
    # 2. EXTRAÇÃO PPE (DAAS - Polícia Civil)
    # Contém dados de boletins de ocorrência
    ppe_records = []
    for row in cm_records:
        bo = row['BO_PC']
        if bo:
            # Gerar natureza (algumas divergentes da subjetividade do Mestra)
            sub = row['SUBJETIVIDADE']
            if sub in ['CVLI', 'CVLI OUTROS', 'CVLI A CONFIRMAR']:
                # Homicídio real
                natureza = 'HOMICIDIO QUALIFICADO' if np.random.rand() > 0.2 else 'LESÃO CORPORAL SEGUIDA DE MORTE'
                # Forçar natureza divergente para teste do Alerta 2
                if row['ID_CONTROLE_MORTE'] % 10 == 3:
                    natureza = 'FURTO DE VEICULO'  # Totalmente divergente para MVI
            elif sub == 'RMNC':
                natureza = 'MORTE DECORRENTE DE INTERVENÇÃO POLICIAL'
            elif sub == 'TENTATIVA':
                natureza = 'TENTATIVA DE HOMICIDIO'
            else:
                natureza = 'ACHADO DE CADÁVER'
                
            ppe_records.append({
                'NUM_BO': bo,
                'NO_NATUREZA_OCORRENCIA': natureza,
                'DS_GRUPO_NATUREZA': 'CRIMES CONTRA A PESSOA' if 'HOMICIDIO' in natureza or 'MORTE' in natureza or 'LESÃO' in natureza else 'CRIMES CONTRA O PATRIMONIO',
                'SN_TENTATIVA': 1 if 'TENTATIVA' in natureza else 0,
                'SN_MARIA_DA_PENHA': 1 if np.random.rand() > 0.9 else 0,
                'ID_PROCEDIMENTO': np.random.randint(200000, 300000),
                'DT_HORA_REGISTRO': row['DATA_HORA_FATO'],
                'DT_OCORRENCIA': row['DATA_HORA_FATO'],
                'ED_LATITUDE_LONGITUDE': f"{np.random.uniform(-10.0, -9.0):.6f}, {np.random.uniform(-36.5, -35.5):.6f}",
                'ED_BAIRRO': row['BAIRRO_FATO'],
                'DS_LOCAL_OCORRENCIA': 'VIA PUBLICA',
                'IN_SITUACAO_ATUAL': 'ATIVO'
            })
            
    df_ppe = pd.DataFrame(ppe_records)
    # A pipeline espera a base bruta extracao_ppe_2025.csv, e depois roda wrangling nela para gerar a limpa
    df_ppe.to_csv("data/mock/extracao_ppe_2025.csv", index=False)
    # E vamos também gerar uma limpa caso rodem direto
    df_ppe.to_csv("data/mock/extracao_ppe_2025_limpo.csv", index=False)
    print(f"  → Gerado extracao_ppe_2025.csv e extracao_ppe_2025_limpo.csv ({len(df_ppe)} linhas)")
    
    # 3. EXTRAÇÃO PM CAD 2025 (CAD - Polícia Militar)
    # Contém ocorrências de despacho do 190.
    # Precisamos incluir ocorrências que dão MATCH com a CONTROLE_MORTE (CAD da mestra),
    # E ocorrências NÃO VINCULADAS (para popular o Radar CAD).
    cad_records = []
    
    # Primeiro: Ocorrências vinculadas
    for row in cm_records:
        cad_id = row['CAD']
        if cad_id:
            # Converter para int
            cad_id = int(cad_id)
            sub = row['SUBJETIVIDADE']
            
            # Mapeia subjetividade para natureza CAD
            if 'CVLI' in sub:
                natureza = 'HOMICÍDIO'
                grupo = 'CÓDIGO PENAL'
            elif sub == 'TENTATIVA':
                natureza = 'TENTATIVA DE HOMICÍDIO'
                grupo = 'CÓDIGO PENAL'
            elif sub == 'RMNC':
                natureza = 'HOMICÍDIO EM DECORRENCIA DE INTERVENÇÃO POLICIAL'
                grupo = 'CÓDIGO PENAL'
            elif sub == 'MORTE A ESCLARECER':
                natureza = 'MORTE A ESCLARECER'
                grupo = 'OCORRÊNCIA SEM ILICITUDE'
            else:
                natureza = 'ACHADO DE CADÁVER'
                grupo = 'OCORRÊNCIA SEM ILICITUDE'
                
            cad_records.append({
                'ID_OCOR': cad_id,
                'DS_NATUREZA_ATEND': natureza,
                'DS_GRUPO_CRIME_ATEND': grupo,
                'DT_OCOR': row['DATA_HORA_FATO'],
                'BAIRRO': row['BAIRRO_FATO'],
                'CIDADE': row['CIDADE_FATO'],
                'NR_COOR_LATD': np.random.uniform(-10.0, -9.0),
                'NR_COOR_LONG': np.random.uniform(-36.5, -35.5),
                'DS_STATUS': 'FINALIZADA',
                'DS_OCOR': f"Despacho da ocorrencia {cad_id}. Viacao deslocada ao local do fato. Constatado obito no local."
            })
            
    # Segundo: Ocorrências NÃO vinculadas para o RADAR (cerca de 50 registros)
    # Precisam ser do tipo CVLI-like (Homicídio, Feminicídio, Latrocínio, Tentativa de Homicídio, Morte a Esclarecer)
    radar_naturezas = [
        ('HOMICÍDIO', 'CÓDIGO PENAL', 'ALTA'),
        ('FEMINICÍDIO', 'CÓDIGO PENAL', 'ALTA'),
        ('LATROCINIO TENTADO', 'CÓDIGO PENAL', 'MEDIA'),
        ('TENTATIVA DE HOMICÍDIO', 'CÓDIGO PENAL', 'MEDIA'),
        ('MORTE A ESCLARECER', 'OCORRÊNCIA SEM ILICITUDE', 'BAIXA'),
        ('DISPARO DE ARMA DE FOGO', 'ESTATUTO DO DESARMAMENTO', 'MEDIA')
    ]
    
    for k in range(50):
        radar_id = 900000 + k
        nat, gp, nivel = radar_naturezas[k % len(radar_naturezas)]
        
        # Gerar datas ao longo de 2025
        dia_ano = np.random.randint(1, 365)
        dt_ocor = datetime(2025, 1, 1) + timedelta(days=dia_ano, hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        dt_ocor_str = dt_ocor.strftime('%Y-%m-%d %H:%M:%S')
        
        despacho = f"Chamada 190. Ocorrencia de {nat}. Solicitante relata disparos de arma de fogo e individuo ao solo. "
        if k % 3 == 0:
            despacho += "Acionado IML e IC para remocao de corpo." # Heurística do texto contendo 'IML'
            
        cad_records.append({
            'ID_OCOR': radar_id,
            'DS_NATUREZA_ATEND': nat,
            'DS_GRUPO_CRIME_ATEND': gp,
            'DT_OCOR': dt_ocor_str,
            'BAIRRO': np.random.choice(bairros),
            'CIDADE': np.random.choice(cidades),
            'NR_COOR_LATD': np.random.uniform(-10.0, -9.0),
            'NR_COOR_LONG': np.random.uniform(-36.5, -35.5),
            'DS_STATUS': 'FINALIZADA',
            'DS_OCOR': despacho
        })
        
    df_cad = pd.DataFrame(cad_records)
    df_cad.to_csv("data/mock/extracao_pm_cad_2025.csv", index=False)
    print(f"  → Gerado extracao_pm_cad_2025.csv ({len(df_cad)} linhas)")
    
    # 4. EXTRAÇÃO IML 2025 (IML Status)
    # Mapeia ID_CONTROLE_MORTE para NIC_IML
    iml_status_records = []
    for row in cm_records:
        nic = row['NIC']
        if nic:
            id_cm = row['ID_CONTROLE_MORTE']
            
            # Declaração de óbito (às vezes vazia para testar alerta 4)
            dec_obito = f"DO-{datetime.now().year}-{id_cm:05d}"
            if is_mvi and id_cm % 10 == 4:
                dec_obito = None  # Alerta 4: DO IML Vazia
                
            iml_status_records.append({
                'ID_CMORTE': id_cm,
                'NIC_IML': nic,
                'TIPO_MORTE': 'VIOLENTA' if row['SUBJETIVIDADE'] in subjetividades[:3] else 'NATURAL',
                'NR_DECLARACAO_OBITO': dec_obito,
                'STATUS': np.random.choice(['CONCLUIDA', 'PENDENTE'], p=[0.9, 0.1])
            })

            
    df_iml = pd.DataFrame(iml_status_records)
    df_iml.to_csv("data/mock/extracao_iml_2025.csv", index=False)
    print(f"  → Gerado extracao_iml_2025.csv ({len(df_iml)} linhas)")
    
    # 5. EXTRAÇÃO IML CADAVÉRICO 2025
    # Detalhes do cadáver no IML
    iml_cad_records = []
    
    # Dicionário de divergências de nomes da Fase 8 para popular no IML
    ids_divergentes = {
        60475: "FRANCISCO DE ASSIS SILVA DE MELLO",
        60476: "MARIA JOSE DOS SANTOS CORREIA",
        60478: "ANTONIO MARCOS REIS BARBOSA",
        60479: "CICERO GOMES DA SILVA (IDENTIFICADO)",
        60480: "JOSE CARLOS DA SILVA BRAGA JUNIOR",
    }
    
    for row in cm_records:
        nic = row['NIC']
        if nic:
            id_cm = row['ID_CONTROLE_MORTE']
            
            # Determinar nome no IML
            if id_cm in ids_divergentes:
                nome_iml = ids_divergentes[id_cm]
            else:
                nome_iml = f"VITIMA_{id_cm}" # Padrão
                
            iml_cad_records.append({
                'NIC': nic,
                'NOM_VITIMA': nome_iml,
                'PAI': 'NOME DO PAI SUPRIMIDO',
                'MAE': f"MAE_DA_VITIMA_{id_cm}",
                'RG': f"{np.random.randint(1000000, 9999999)}",
                'TELEFONE': '99999-9999',
                'LOGRADOURO': 'ENDERECO SUPRIMIDO',
                'DATA_ENTRADA': row['DATA_HORA_FATO'],
                'DAT_OBITO': row['DATA_HORA_FATO'],
                'TIPO_EXAME': 'NECROPSIA',
                'DSC_UNIDADE_IML': 'IML MACEIO',
                'SEXO': np.random.choice(['M', 'F'], p=[0.8, 0.2]),
                'ETNIA': np.random.choice(['BRANCA', 'PRETA', 'PARDA', 'AMARELA'], p=[0.2, 0.1, 0.6, 0.1]),
                'NASCIMENTO': row['NASC_VITIMA']
            })
            
    df_iml_cad = pd.DataFrame(iml_cad_records)
    df_iml_cad.to_csv("data/mock/extracao_iml_cadaverico_2025.csv", index=False)
    print(f"  → Gerado extracao_iml_cadaverico_2025.csv ({len(df_iml_cad)} linhas)")
    print("============================================================")

if __name__ == "__main__":
    generate_mock_data()
