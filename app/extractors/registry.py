"""Registre des extracteurs et fonction d'extraction unifiée."""
from pathlib import Path
from app.models import ExtractedContent
from .base import BaseExtractor
from .pdf_extractor import PDFExtractor
from .docx_extractor import DocxExtractor
from .pptx_extractor import PptxExtractor
from .text_extractor import TextExtractor


_EXTRACTORS: list[BaseExtractor] = [
    PDFExtractor(),
    DocxExtractor(),
    PptxExtractor(),
    TextExtractor(),
]


def get_extractor(path: Path) -> BaseExtractor | None:
    """Retourne l'extracteur approprié pour le fichier."""
    for ext in _EXTRACTORS:
        if ext.can_handle(path):
            return ext
    return None


def extract_from_file(path: Path) -> ExtractedContent:
    """Extrait le contenu d'un fichier avec l'extracteur adapté."""
    ext = get_extractor(path)
    if ext is None:
        raise ValueError(f"Format non supporté: {path.suffix}. Utilisez PDF, DOCX, PPTX ou TXT.")
    return ext.extract(path)
