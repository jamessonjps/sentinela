from .text_normalizer import TextNormalizer

class CityMatcher:
    """
    Matches city names against the TRATAR_CIDADES standardized lookup.
    """
    def __init__(self, tratar_cidades_lookup: dict = None):
        self.lookup = {}
        if tratar_cidades_lookup:
            self.load_lookup(tratar_cidades_lookup)

    def load_lookup(self, lookup_dict: dict):
        """
        Loads the lookup table mapping raw or normalized names to standard city names.
        """
        self.lookup = {TextNormalizer.normalize(k): v for k, v in lookup_dict.items()}

    def match(self, city: str) -> str:
        """
        Returns the standardized city name or the original if not found.
        """
        norm = TextNormalizer.normalize(city)
        return self.lookup.get(norm, city)
