from .text_normalizer import TextNormalizer

class NeighborhoodMatcher:
    """
    Matches neighborhood names against the TRATAR_BAIRROS standardized lookup.
    """
    def __init__(self, tratar_bairros_lookup: dict = None):
        self.lookup = {}
        if tratar_bairros_lookup:
            self.load_lookup(tratar_bairros_lookup)

    def load_lookup(self, lookup_dict: dict):
        """
        Loads the lookup table mapping raw or normalized names to standard neighborhood names.
        """
        self.lookup = {TextNormalizer.normalize(k): v for k, v in lookup_dict.items()}

    def match(self, neighborhood: str) -> str:
        """
        Returns the standardized neighborhood name or the original if not found.
        """
        norm = TextNormalizer.normalize(neighborhood)
        return self.lookup.get(norm, neighborhood)
