"""Classe de base pour les extracteurs de documents."""
from pathlib import Path
from app.models import ExtractedContent


class BaseExtractor:
    """Extracteur abstrait pour un type de document."""
    
    @property
    def supported_extensions(self) -> list[str]:
        raise NotImplementedError
    
    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_extensions
    
    def extract(self, path: Path) -> ExtractedContent:
        raise NotImplementedError
