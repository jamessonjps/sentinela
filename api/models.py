from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class SentinelaFilaAlertas(Base):
    __tablename__ = "SENTINELA_FILA_ALERTAS"
    
    ID_ALERTA = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_CONTROLE_MORTE = Column(Integer, index=True)
    NIC = Column(String(100), nullable=True)
    BO_PC = Column(String(100), nullable=True)
    CAD = Column(String(100), nullable=True)
    STATUS = Column(String(50), default="Novo")  # Novo, Em Tratativa, Resolvido
    PRIORIDADE = Column(Integer, default=1)       # 1, 2, 3
    TIPO_ALERTA = Column(String(255), nullable=False)
    DT_CRIACAO = Column(DateTime, default=func.now())
    DT_ATUALIZACAO = Column(DateTime, default=func.now(), onupdate=func.now())

class VwSentinelaCasoCompleto(Base):
    __tablename__ = "VW_SENTINELA_CASO_COMPLETO"
    
    ID_CONTROLE_MORTE = Column(Integer, primary_key=True, index=True)
    SUBJETIVIDADE = Column(String(255))
    TIPO_MVI = Column(String(100))
    EH_MVI = Column(Boolean, default=False)
    BO_PC = Column(String(100))
    CAD = Column(String(100))
    NIC = Column(String(100))
    BAIRRO_FATO = Column(String(255))
    CIDADE_FATO = Column(String(255))
    DATA_HORA_FATO = Column(String(100)) # Datetime em string ISO
    INSTRUMENTO_UTILIZADO = Column(String(255))
    MOTIV_INICIAL = Column(Text)
    AISP = Column(String(100))
    RISP = Column(String(100))
    STATUS = Column(String(100))
    NOME_VITIMA = Column(String(255), nullable=True)
    SEXO_VITIMA = Column(String(50), nullable=True)
    MAE_VITIMA = Column(String(255), nullable=True)
    NASC_VITIMA = Column(String(100), nullable=True)
    COR_RACA_VITIMA = Column(String(50), nullable=True)
    NOM_VITIMA_IML = Column(String(255), nullable=True)

    
    # Flags de Alerta
    ALERTA_BO_INEXISTENTE = Column(String(50))
    ALERTA_NATUREZA_DIVERGENTE = Column(String(50))
    ALERTA_CAD_FALTANTE = Column(String(50))
    ALERTA_DO_IML_VAZIA = Column(String(50))
    ALERTA_NIC_FALTANTE = Column(String(50))
    ALERTA_NOME_DIVERGENTE = Column(String(50), nullable=True)
    
    # Polícia Civil complementar
    NUM_BO = Column(String(100))
    NO_NATUREZA_OCORRENCIA = Column(Text)
    DS_GRUPO_NATUREZA = Column(Text)
    ED_BAIRRO = Column(String(255))
    NO_MUNICIPIO = Column(String(255))
    DT_OCORRENCIA = Column(String(100))
    SN_TENTATIVA = Column(Integer)
    SN_MARIA_DA_PENHA = Column(Integer)
    IN_SITUACAO_ATUAL = Column(String(50))

    
    # Polícia Militar (CAD) complementar
    ID_OCOR = Column(String(100))
    DS_NATUREZA_ATEND = Column(Text)
    DS_GRUPO_CRIME_ATEND = Column(Text)
    NR_COOR_LATD = Column(Float)
    NR_COOR_LONG = Column(Float)
    
    # IML complementar
    NIC_IML = Column(String(100))
    TIPO_MORTE = Column(String(255))
    NR_DECLARACAO_OBITO = Column(String(255))
    SEXO = Column(String(10))
    ETNIA = Column(String(50))
    NASCIMENTO = Column(String(100))
    STATUS_IML = Column(String(100))
    MAE_IML = Column(String(255))
    IML_ENTRADA = Column(String(100))
    ORGAO_REQUERENTE = Column(String(255))
    REQUERENTE_OUTROS = Column(String(255))






class SentinelaRadarCAD(Base):
    """
    Radar de Ocorrências CAD (190 PM).
    Armazena ocorrências CVLI-like detectadas no despacho 190
    que ainda não possuem vínculo na CONTROLE_MORTE.
    
    ⚠️ PROTEÇÃO: Esta tabela é alimentada apenas pelo script
    radar_cad.py em modo READ ONLY das bases fonte.
    """
    __tablename__ = "SENTINELA_RADAR_CAD"
    
    ID_RADAR = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_OCOR = Column(Integer, index=True, unique=True)  # ID da ocorrência no CAD PM
    DS_NATUREZA_ATEND = Column(String(500))              # Natureza do atendimento
    DS_GRUPO_CRIME_ATEND = Column(String(255))           # Grupo de crime
    DT_OCOR = Column(String(100))                        # Data da ocorrência
    TURNO = Column(String(50), nullable=True)             # Turno operacional (T1 a T6)
    CIDADE = Column(String(255), index=True)             # Cidade
    BAIRRO = Column(String(255))                         # Bairro
    NR_COOR_LATD = Column(Float, nullable=True)          # Latitude GPS
    NR_COOR_LONG = Column(Float, nullable=True)          # Longitude GPS
    TEM_GPS = Column(Boolean, default=False)             # Flag de disponibilidade GPS
    DS_STATUS = Column(String(100))                      # Status CAD (FINALIZADA, etc)
    DS_OCOR = Column(Text, nullable=True)                # Descrição/despacho da ocorrência
    
    # Classificação do Radar
    PRIORIDADE_RADAR = Column(Integer, default=1)        # 1=Baixa, 2=Média, 3=Alta
    CLASSIFICACAO_RADAR = Column(String(50))              # CVLI_CONFIRMADO, CVLI_PROVAVEL, A_ESCLARECER
    NIVEL_RADAR = Column(String(20))                     # ALTA, MEDIA, BAIXA
    
    # Workflow de validação
    STATUS_RADAR = Column(String(50), default="Novo")    # Novo, Validado, Descartado
    DT_DETECCAO = Column(DateTime, default=func.now())   # Quando o radar detectou
    DT_VALIDACAO = Column(DateTime, nullable=True)       # Quando o analista validou/descartou


class SentinelaReconciliacaoLog(Base):
    """
    Tabela de logs de reconciliação e divergências campo-a-campo.
    Registra inconsistências entre a Controle Morte e fontes externas
    ou sugestões de correlação probabilística (ex: CAD ↔ PPE).
    """
    __tablename__ = "SENTINELA_RECONCILIACAO_LOG"
    
    ID_RECONCILIACAO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_CONTROLE_MORTE = Column(Integer, index=True)
    FONTE = Column(String(20), index=True)               # IML, CAD, PPE
    CAMPO_MESTRA = Column(String(100))                  # ex: NOME_VITIMA
    VALOR_MESTRA = Column(String(4000), nullable=True)
    CAMPO_FONTE = Column(String(100))                   # ex: NOM_VITIMA
    VALOR_FONTE = Column(String(4000), nullable=True)
    TIPO_DIVERGENCIA = Column(String(50))                # VALOR_DIFERENTE, CAMPO_VAZIO_MESTRA, CORRELACAO_PROBABILISTICA
    SCORE_SIMILARIDADE = Column(Float, nullable=True)   # Score calculado (Jaro-Winkler ou correlação)
    DT_DETECCAO = Column(DateTime, default=func.now())
    STATUS = Column(String(30), default="Pendente", index=True) # Pendente, Confirmado, Ignorado
    DT_RESOLUCAO = Column(DateTime, nullable=True)


class SentinelaEvolucaoPendente(Base):
    __tablename__ = "SENTINELA_EVOLUCAO_PENDENTE"
    
    ID_EVOLUCAO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_CONTROLE_MORTE = Column(Integer, index=True, nullable=False)
    NIC_IML = Column(String(100), nullable=True)
    BO_PC = Column(String(100), nullable=True)
    DATA_OBITO = Column(DateTime, nullable=True)
    STATUS = Column(String(30), default="Pendente", index=True) # Pendente, Aprovada, Rejeitada
    MOTIVO = Column(String(4000), nullable=True)
    TIPO_EVOLUCAO = Column(String(100), default="Tentativa -> Óbito")
    AUTOR_PROPOSTA = Column(String(100), nullable=True)
    DT_CRIACAO = Column(DateTime, default=func.now())
    DT_ATUALIZACAO = Column(DateTime, default=func.now(), onupdate=func.now())


class SentinelaNotificacaoIML(Base):
    __tablename__ = "SENTINELA_NOTIFICACAO_IML"
    
    ID_NOTIFICACAO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    NIC = Column(String(100), nullable=False, index=True)
    NOME_VITIMA = Column(String(255), nullable=True)
    STATUS_IML = Column(String(100), nullable=True)
    TIPO_MENSAGEM = Column(String(255), nullable=False)
    DT_EVENTO = Column(DateTime, default=func.now())
    LIDO = Column(Integer, default=0, index=True) # 0 ou 1


class SentinelaGeoBairro(Base):
    __tablename__ = "SENTINELA_GEO_BAIRRO"
    
    ID_BAIRRO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    NOME_BAIRRO = Column(String(150), nullable=False)
    NOME_MUNICIPIO = Column(String(150), nullable=False)
    CENTRO_LATITUDE = Column(Float, nullable=False)
    CENTRO_LONGITUDE = Column(Float, nullable=False)
    RAIO_KM = Column(Float, default=1.5)


class SentinelaEstabelecimentoSaude(Base):
    __tablename__ = "SENTINELA_ESTABELECIMENTO_SAUDE"
    
    ID_ESTABELECIMENTO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    NOME = Column(String(255), nullable=False)
    LATITUDE = Column(Float, nullable=False)
    LONGITUDE = Column(Float, nullable=False)
    RAIO_METROS = Column(Float, default=150.0)
    TIPO = Column(String(50), default="SAUDE")




