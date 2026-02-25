"""Extracteur pour fichiers Word (.docx)."""
from pathlib import Path
from docx import Document as DocxDocument
from app.models import ExtractedContent
from .base import BaseExtractor


class DocxExtractor(BaseExtractor):
    """Extrait le texte et la structure des fichiers Word."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return [".docx", ".doc"]
    
    def extract(self, path: Path) -> ExtractedContent:
        doc = DocxDocument(str(path))
        sections = []
        current_section = None
        text_parts = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = para.style.name if para.style else ""
            if "Heading" in style or "Titre" in style:
                if current_section:
                    sections.append(current_section)
                current_section = {"title": text, "content": []}
            else:
                if current_section:
                    current_section["content"].append(text)
                text_parts.append(text)
        
        if current_section:
            sections.append(current_section)
        
        title = doc.core_properties.title or (sections[0]["title"] if sections else None)
        raw_text = "\n\n".join(text_parts)
        return ExtractedContent(raw_text=raw_text, title=title, sections=sections)
