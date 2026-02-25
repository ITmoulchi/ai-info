"""Modèles de données pour l'extraction et la génération d'infographies."""
from typing import Optional
from pydantic import BaseModel, Field


class ExtractedContent(BaseModel):
    """Contenu extrait d'un document."""
    raw_text: str = Field(description="Texte brut complet")
    title: Optional[str] = Field(None, description="Titre du document")
    sections: list[dict] = Field(default_factory=list, description="Sections avec titres et contenu")


class KeyIdea(BaseModel):
    """Idée clé extraite."""
    text: str
    importance: str = "medium"  # low, medium, high
    icon: str = "💡"  # Emoji ou classe d'icône


class KeyFigure(BaseModel):
    """Chiffre ou statistique importante."""
    label: str
    value: str
    unit: Optional[str] = None
    context: Optional[str] = None


class TimelineItem(BaseModel):
    """Élément de chronologie."""
    date_or_step: str
    description: str
    detail: Optional[str] = None


class DocumentAnalysis(BaseModel):
    """Résultat de l'analyse du document."""
    title: Optional[str] = None
    summary: Optional[str] = None
    key_ideas: list[KeyIdea] = Field(default_factory=list)
    key_figures: list[KeyFigure] = Field(default_factory=list)
    timeline: list[TimelineItem] = Field(default_factory=list)
    structure: list[str] = Field(default_factory=list)
    categories_for_chart: Optional[dict] = None  # {label: value} pour graphiques
    raw_text: str = ""
