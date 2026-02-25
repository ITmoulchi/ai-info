"""Génère une infographie HTML à partir d'une DocumentAnalysis."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.models import DocumentAnalysis
from app.design.theme import Theme, get_theme_for_analysis


def _safe_float(s: str) -> float:
    try:
        return float(str(s).replace(",", ".").replace(" ", ""))
    except (ValueError, TypeError):
        return 0.0


def generate_infographic_html(analysis: DocumentAnalysis, theme: Theme | None = None) -> str:
    """Produit le HTML complet de l'infographie."""
    if theme is None:
        theme = get_theme_for_analysis(analysis)
    
    # Données pour graphiques
    chart_data = analysis.categories_for_chart or {}
    chart_labels = list(chart_data.keys())
    chart_values = [_safe_float(v) for v in chart_data.values()]
    max_val = max(chart_values, default=1) or 1
    
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("infographic.html")
    
    return template.render(
        analysis=analysis,
        theme=theme,
        chart_labels=chart_labels,
        chart_values=chart_values,
        chart_max=max_val,
        chart_colors=theme.chart_colors,
    )
