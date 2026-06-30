import unicodedata
import re

class TextNormalizer:
    """
    Normalizes text for standardized comparison and storage.
    """
    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        # Remove accents
        text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
        # Convert to uppercase
        text = text.upper()
        # Remove non-alphanumeric characters except spaces
        text = re.sub(r'[^A-Z0-9\s]', '', text)
        # Collapse multiple spaces into one
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
