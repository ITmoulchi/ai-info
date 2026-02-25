"""Analyse du contenu pour extraire idées clés, chiffres et structure."""
from .content_analyzer import analyze_content
from app.models import DocumentAnalysis

__all__ = ["analyze_content", "DocumentAnalysis"]
