import unicodedata
import re
from datetime import datetime

def remove_accents(text: str) -> str:
    """
    Remove acentos e diacríticos de uma string.
    """
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_text(text: str) -> str:
    """
    Remove acentos, converte para caixa alta, remove caracteres especiais e espaços extras.
    """
    if not text:
        return ""
    text = remove_accents(text).upper().strip()
    # Substitui múltiplos espaços por um único espaço
    text = re.sub(r'\s+', ' ', text)
    return text

def normalize_name(name: str) -> str:
    """
    Normalização específica para nomes de pessoas.
    """
    return normalize_text(name)

def normalize_sex(sex: str) -> str:
    """
    Padroniza sexo para M, F ou None.
    """
    if not sex:
        return None
    normalized = normalize_text(sex)
    if normalized in ["MASCULINO", "MASC", "M"]:
        return "M"
    elif normalized in ["FEMININO", "FEM", "F"]:
        return "F"
    return None

def normalize_race(race: str) -> str:
    """
    Padroniza cor/raça para as categorias oficiais.
    """
    if not race:
        return None
    normalized = normalize_text(race)
    # Trata sinônimos comuns
    if normalized in ["PRETA", "PRETO", "NEGRA", "NEGRO"]:
        return "PRETA"
    elif normalized in ["PARDA", "PARDO", "MORENA", "MORENO", "MULATA", "MULATO"]:
        return "PARDA"
    elif normalized in ["BRANCA", "BRANCO"]:
        return "BRANCA"
    elif normalized in ["AMARELA", "AMARELO"]:
        return "AMARELA"
    elif normalized in ["INDIGENA", "INDIO"]:
        return "INDIGENA"
    return normalized

def parse_date(date_val) -> datetime:
    """
    Tenta parsear um valor de data (seja string ou datetime) para objeto datetime.
    """
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    
    date_str = str(date_val).strip()
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y"
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def jaro_similarity(s1: str, s2: str) -> float:
    """
    Calcula a similaridade de Jaro entre duas strings.
    Retorna um valor entre 0.0 e 1.0.
    """
    if s1 == s2:
        return 1.0

    len1 = len(s1)
    len2 = len(s2)

    if len1 == 0 or len2 == 0:
        return 0.0

    # Limite máximo de distância para busca
    match_bound = max(0, max(len1, len2) // 2 - 1)

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    # Contar matches
    for i in range(len1):
        start = max(0, i - match_bound)
        end = min(len2, i + match_bound + 1)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    # Contar transposições
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions //= 2

    return (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0

def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Calcula a similaridade de Jaro-Winkler entre duas strings.
    Retorna um valor entre 0.0 e 1.0 (ou score 0-100 se multiplicado por 100).
    """
    jaro_sim = jaro_similarity(s1, s2)
    
    # Comprimento do prefixo comum (máximo de 4 caracteres)
    prefix_len = 0
    for i in range(min(4, min(len(s1), len(s2)))):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
            
    return jaro_sim + prefix_len * p * (1.0 - jaro_sim)

def jaro_winkler_score(s1: str, s2: str) -> float:
    """
    Retorna o score Jaro-Winkler escalado de 0 a 100.
    """
    if not s1 or not s2:
        return 0.0
    s1_norm = normalize_text(s1)
    s2_norm = normalize_text(s2)
    return round(jaro_winkler_similarity(s1_norm, s2_norm) * 100.0, 1)

def match_names(name1: str, name2: str, threshold: float = 88.0) -> tuple[bool, float]:
    """
    Compara dois nomes de acordo com as regras estabelecidas:
    - Mesma primeira letra (filtro de CPU/falso positivo)
    - Jaro-Winkler score >= threshold
    """
    if not name1 or not name2:
        return False, 0.0
        
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    
    if not n1 or not n2:
        return False, 0.0
        
    # Filtro da primeira letra
    if n1[0] != n2[0]:
        return False, 0.0
        
    score = jaro_winkler_score(n1, n2)
    return score >= threshold, score
