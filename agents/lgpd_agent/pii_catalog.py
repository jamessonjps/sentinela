"""
Catalog of PII fields and allowed fields according to SENTINELA LGPD rules.
"""

# Campos a Mascarar (Supressão/Pseudonimização)
PII_CATALOG = {
    "NOME_VITIMA": "SUPPRESS", # Pode virar VITIMA_<ID>
    "MAE_VITIMA": "SUPPRESS",
    "NASC_VITIMA": "DATE_MASK", # Ex: Ano apenas ou 01/01/Ano
    "ENDERECO": "SUPPRESS",
    "NOME_AUTOR": "SUPPRESS",
    "CPF_AUTOR": "MASK_CPF",
    "ALCUNHA_AUTOR": "SUPPRESS",
    "RELATO_HISTORICO": "TEXT_MASK", # DAAS
    "NOM_VITIMA": "SUPPRESS", # SGOU
    "RG": "MASK_RG" # SGOU
}

# Campos Liberados (Chaves e Território)
ALLOWED_FIELDS = [
    # Chaves Universais
    "NIC",
    "BO_PC",
    "CAD",
    "ID_CONTROLE_MORTE",
    "ID_FATO",
    # Território
    "AISP",
    "RISP",
    "BAIRRO",
    "BAIRRO_FATO",
    "LATITUDE",
    "LONGITUDE",
    # Tipificações e Outros
    "SUBJETIVIDADE",
    "MOTIVACAO",
    "INSTRUMENTO_UTILIZADO",
    "DATA_HORA_FATO",
    "DATA_ENTRADA",
    "DT_HORA_REGISTRO",
    "DS_GRUPO_NATUREZA",
    "TIPO_EXAME",
    "QTD_AUTORES"
]
