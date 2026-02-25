"""Extracteur pour fichiers PDF."""
from pathlib import Path
from pypdf import PdfReader
from app.models import ExtractedContent
from .base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extrait le texte des fichiers PDF."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]
    
    def extract(self, path: Path) -> ExtractedContent:
        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        raw_text = "\n\n".join(text_parts).strip()
        title = reader.metadata.get("/Title") or reader.metadata.get("/Subject") or None
        if title is not None:
            if isinstance(title, bytes):
                title = title.decode("utf-8", errors="ignore")
            title = (title or "").strip() or None
        return ExtractedContent(raw_text=raw_text, title=title, sections=[])
