"""Thèmes de couleurs et typographie pour infographies."""
import hashlib
from dataclasses import dataclass
from app.models import DocumentAnalysis


@dataclass
class Theme:
    """Palette et typo pour une infographie."""
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    text_light: str
    font_heading: str
    font_body: str
    chart_colors: list[str]
    # Nouveaux champs pour un design premium
    gradient_start: str = ""
    gradient_end: str = ""
    card_bg: str = "#ffffff"
    is_dark: bool = False

    def __post_init__(self):
        if not self.gradient_start:
            self.gradient_start = self.primary
        if not self.gradient_end:
            self.gradient_end = self.secondary


THEMES: list[Theme] = [
    Theme(
        name="Ocean Deep",
        primary="#0d47a1",
        secondary="#1565c0",
        accent="#00e5ff",
        background="#f0f4f8",
        text="#102a43",
        text_light="#627d98",
        font_heading="'Montserrat', sans-serif",
        font_body="'Open Sans', sans-serif",
        chart_colors=["#0d47a1", "#1976d2", "#2196f3", "#64b5f6", "#90caf9", "#bbdefb"],
        gradient_start="#0d47a1",
        gradient_end="#1565c0"
    ),
    Theme(
        name="Forest Pro",
        primary="#1b5e20",
        secondary="#2e7d32",
        accent="#00e676",
        background="#f1f8e9",
        text="#1b5e20",
        text_light="#558b2f",
        font_heading="'Playfair Display', serif",
        font_body="'Source Sans 3', sans-serif",
        chart_colors=["#1b5e20", "#388e3c", "#4caf50", "#81c784", "#a5d6a7", "#c8e6c9"],
        gradient_start="#1b5e20",
        gradient_end="#43a047"
    ),
    Theme(
        name="Corporate Slate",
        primary="#263238",
        secondary="#455a64",
        accent="#ff3d00", # Orange vif pour contraste
        background="#f5f7fa",
        text="#263238",
        text_light="#546e7a",
        font_heading="'Roboto Slab', serif",
        font_body="'Roboto', sans-serif",
        chart_colors=["#263238", "#37474f", "#546e7a", "#78909c", "#b0bec5", "#cfd8dc"],
        gradient_start="#37474f",
        gradient_end="#263238"
    ),
    Theme(
        name="Tech Dark",
        primary="#6200ea",
        secondary="#651fff",
        accent="#00b0ff",
        background="#121212", # Mode sombre
        text="#f5f5f5",
        text_light="#bdbdbd",
        font_heading="'Space Grotesk', sans-serif",
        font_body="'Inter', sans-serif",
        chart_colors=["#6200ea", "#7c4dff", "#b388ff", "#00b0ff", "#40c4ff", "#80d8ff"],
        card_bg="#1e1e1e",
        is_dark=True,
        gradient_start="#311b92",
        gradient_end="#6200ea"
    ),
    Theme(
        name="Luxury Gold",
        primary="#bf360c",
        secondary="#d84315",
        accent="#ffd700",
        background="#fff8e1",
        text="#3e2723",
        text_light="#795548",
        font_heading="'Cinzel', serif",
        font_body="'Lato', sans-serif",
        chart_colors=["#bf360c", "#d84315", "#f4511e", "#ff7043", "#ff8a65", "#ffab91"],
        gradient_start="#bf360c",
        gradient_end="#d84315"
    ),
    Theme(
        name="Modern Berry",
        primary="#880e4f",
        secondary="#ad1457",
        accent="#ff4081",
        background="#fce4ec",
        text="#4a148c",
        text_light="#880e4f",
        font_heading="'Raleway', sans-serif",
        font_body="'Nunito', sans-serif",
        chart_colors=["#880e4f", "#c2185b", "#e91e63", "#f06292", "#f48fb1", "#f8bbd0"],
        gradient_start="#880e4f",
        gradient_end="#c2185b"
    ),
]


def get_theme_for_analysis(analysis: DocumentAnalysis) -> Theme:
    """Choisit un thème de façon déterministe à partir du contenu."""
    seed = (analysis.title or "") + (analysis.summary or "")[:200]
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return THEMES[h % len(THEMES)]
