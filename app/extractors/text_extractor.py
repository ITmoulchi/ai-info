"""Extracteur pour fichiers texte."""
from pathlib import Path
from app.models import ExtractedContent
from .base import BaseExtractor


class TextExtractor(BaseExtractor):
    """Extrait le contenu des fichiers texte."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return [".txt", ".md", ".rst", ".log", ""]
    
    def can_handle(self, path: Path) -> bool:
        ext = path.suffix.lower()
        return ext in self.supported_extensions or (ext == "" and path.is_file())
    
    def extract(self, path: Path) -> ExtractedContent:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            raw = path.read_text(encoding="latin-1", errors="replace")
        
        lines = raw.strip().split("\n")
        sections = []
        current_title = None
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if line.startswith("#") or (len(stripped) < 80 and stripped.endswith(":") and not current_title):
                if current_title is not None and current_content:
                    sections.append({"title": current_title, "content": current_content})
                current_title = stripped.lstrip("#").strip().rstrip(":")
                current_content = []
            else:
                current_content.append(stripped)
        
        if current_title is not None and current_content:
            sections.append({"title": current_title, "content": current_content})
        
        title = lines[0].strip().lstrip("#").strip() if lines else None
        return ExtractedContent(raw_text=raw.strip(), title=title, sections=sections)
