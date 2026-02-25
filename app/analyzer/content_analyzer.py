"""Analyse du contenu : idées clés, chiffres, chronologie, structure."""
import re
from app.models import (
    DocumentAnalysis,
    KeyIdea,
    KeyFigure,
    TimelineItem,
    ExtractedContent,
)
from app.config import get_settings


# Patterns pour extraction heuristique
PATTERN_NUMBER = re.compile(
    r"(?:^|\s)([0-9]+(?:\s*[.,]\s*[0-9]+)*)\s*%?(?:\s*(?:millions?|milliards?|M|k|K|€|\$|euros?|dollars?))?(?=\s|$|[.,;:])",
    re.IGNORECASE,
)
PATTERN_PERCENT = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
PATTERN_YEAR = re.compile(r"\b(19|20)\d{2}\b")
PATTERN_BULLET = re.compile(r"^[\s]*[-*•▪]\s+(.+)$", re.MULTILINE)
PATTERN_HEADING = re.compile(r"^#+\s*(.+)$", re.MULTILINE)
PATTERN_NUMBER_LABEL = re.compile(
    r"([A-Za-zÀ-ÿ\s]+?)\s*[:\-]\s*(\d+(?:[.,]\d+)?)\s*%?(?:\s*(?:M|k|€|\$|%))?",
    re.IGNORECASE,
)


def _extract_key_figures(text: str) -> list[KeyFigure]:
    """Extrait chiffres et statistiques du texte."""
    figures: list[KeyFigure] = []
    seen: set[tuple[str, str]] = set()
    
    # Pourcentages
    for m in PATTERN_PERCENT.finditer(text):
        val = m.group(1).replace(",", ".")
        key = ("%", val)
        if key not in seen:
            seen.add(key)
            context = text[max(0, m.start() - 60) : m.end() + 40].strip()
            figures.append(KeyFigure(label="Statistique", value=f"{val}%", unit="%", context=context[:80]))
    
    # Paires "label : valeur"
    for m in PATTERN_NUMBER_LABEL.finditer(text):
        label, value = m.group(1).strip(), m.group(2)
        if len(label) > 2 and len(label) < 60:
            key = (label[:30], value)
            if key not in seen:
                seen.add(key)
                figures.append(KeyFigure(label=label, value=value))
    
    return figures[:15]  # Limiter pour l'infographie


def _extract_timeline(text: str) -> list[TimelineItem]:
    """Extrait des éléments de chronologie (années + phrase complète)."""
    items: list[TimelineItem] = []
    seen_dates = set()

    # Regex simplifiée pour éviter les crashs sur textes complexes
    # On cherche juste l'année et les mots autour, sans essayer de matcher toute la phrase parfaitement
    regex_sentence = re.compile(r"(.{0,100}\b(19|20)\d{2}\b.{0,100})", re.MULTILINE)

    for m in regex_sentence.finditer(text):
        sentence = m.group(1).strip()
        
        # Trouver l'année précise dans la phrase pour l'utiliser comme label
        year_match = PATTERN_YEAR.search(sentence)
        if not year_match:
            continue
            
        year = year_match.group(0)
        
        # Nettoyage de la phrase
        clean_desc = re.sub(r'\s+', ' ', sentence).strip()
        
        # Si la phrase est trop courte (juste l'année) ou trop longue, on ignore ou on tronque proprement
        if len(clean_desc) < 10: 
            continue
            
        if year not in seen_dates:
            seen_dates.add(year)
            items.append(TimelineItem(date_or_step=year, description=clean_desc[:150]))
            
    # Tri par année
    items.sort(key=lambda x: x.date_or_step)
    return items[:10]


def _get_icon_for_idea(text: str) -> str:
    """Retourne une icône (emoji) appropriée selon le contenu de l'idée."""
    text_lower = text.lower()
    
    mapping = {
        "finance": ["euro", "dollar", "coût", "budget", "prix", "chiffre d'affaire", "bénéfice", "invest", "banque", "argent"],
        "croissance": ["croissance", "hausse", "augmentation", "progression", "développement", "boost", "succès"],
        "temps": ["année", "date", "période", "durée", "temps", "deadline", "échéance", "202", "199"],
        "techno": ["tech", "logiciel", "digital", "numérique", "web", "app", "système", "donnée", "data", "ia", "intelligence"],
        "équipe": ["équipe", "staff", "employé", "personnel", "rh", "humain", "collaborateur", "social"],
        "danger": ["risque", "menace", "problème", "crise", "erreur", "faille", "attention"],
        "objectif": ["objectif", "but", "mission", "vision", "stratégie", "plan", "cible"],
        "monde": ["international", "monde", "global", "pays", "europe", "étranger", "export"],
        "juridique": ["loi", "règle", "norme", "juridique", "légal", "contrat", "droit"],
    }
    
    icons = {
        "finance": "💰",
        "croissance": "🚀",
        "temps": "📅",
        "techno": "💻",
        "équipe": "👥",
        "danger": "⚠️",
        "objectif": "🎯",
        "monde": "🌍",
        "juridique": "⚖️",
    }
    
    for category, keywords in mapping.items():
        if any(k in text_lower for k in keywords):
            return icons[category]
            
    return "💡"  # Défaut


def _extract_key_ideas(text: str, sections: list) -> list[KeyIdea]:
    """Extrait les idées clés (titres de sections, puces)."""
    ideas: list[KeyIdea] = []
    seen: set[str] = set()
    
    for sec in sections:
        title = sec.get("title", "").strip()
        if title and len(title) > 3 and title.lower() not in seen:
            seen.add(title.lower())
            icon = _get_icon_for_idea(title)
            ideas.append(KeyIdea(text=title, importance="high", icon=icon))
    
    for m in PATTERN_BULLET.finditer(text):
        idea_text = m.group(1).strip()
        if 10 < len(idea_text) < 150 and idea_text.lower() not in seen:
            seen.add(idea_text.lower())
            icon = _get_icon_for_idea(idea_text)
            ideas.append(KeyIdea(text=idea_text, importance="medium", icon=icon))
    
    for m in PATTERN_HEADING.finditer(text):
        idea_text = m.group(1).strip()
        if idea_text and idea_text.lower() not in seen:
            seen.add(idea_text.lower())
            icon = _get_icon_for_idea(idea_text)
            ideas.append(KeyIdea(text=idea_text, importance="high", icon=icon))
    
    return ideas[:12]


def _extract_structure(sections: list) -> list[str]:
    """Liste la structure (titres de sections)."""
    return [s.get("title", "").strip() for s in sections if s.get("title")]


def _build_chart_data(key_figures: list[KeyFigure]) -> dict | None:
    """Construit des données pour graphiques à partir des chiffres clés."""
    if not key_figures:
        return None
    return {f.label[:30]: f.value.replace(",", ".") for f in key_figures[:8]}


def _extract_summary(text: str, sections: list) -> str:
    """Génère un résumé en prenant le début des sections principales."""
    summary_parts = []
    
    # Première phrase du texte (souvent le chapeau)
    first_para = text.split('\n\n')[0].strip()
    if len(first_para) > 30:
        summary_parts.append(first_para[:250])
        
    # Premières phrases des sections importantes
    for sec in sections[:2]:
        content = sec.get("content", "")
        if isinstance(content, list):
            content = " ".join(content)
        content = str(content).strip()
        
        if content:
            first_sent = content.split('.')[0] + "."
            if 20 < len(first_sent) < 200:
                summary_parts.append(first_sent)
                
    final_summary = " ".join(summary_parts)
    if len(final_summary) > 400:
        final_summary = final_summary[:397] + "..."
        
    return final_summary or (text[:300] + "...")


def _analyze_heuristic(content: ExtractedContent) -> DocumentAnalysis:
    """Analyse heuristique améliorée sans API externe."""
    text = content.raw_text.strip()
    sections = content.sections or []
    
    # Titre intelligent
    title = (content.title or "").strip()
    if not title and sections:
        # Si pas de métadonnée titre, on prend le premier titre de section s'il est court
        first_sec_title = sections[0].get("title", "").strip()
        if first_sec_title and len(first_sec_title) < 60:
            title = first_sec_title
            
    # Résumé intelligent
    summary = _extract_summary(text, sections)

    return DocumentAnalysis(
        title=title or None,
        summary=summary,
        key_ideas=_extract_key_ideas(text, sections),
        key_figures=_extract_key_figures(text),
        timeline=_extract_timeline(text),
        structure=_extract_structure(sections),
        categories_for_chart=_build_chart_data(_extract_key_figures(text)),
        raw_text=text,
    )


async def _analyze_with_openai(content: ExtractedContent) -> DocumentAnalysis | None:
    """Analyse avec OpenAI si la clé API est configurée."""
    settings = get_settings()
    if not settings.openai_api_key or len(content.raw_text) < 50:
        return None
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        prompt = """Tu es un expert en synthèse de documents. À partir du texte suivant, extrais :
1. Un titre court (si évident)
2. Un résumé en 2-3 phrases
3. Une liste d'idées clés (phrases courtes, une par ligne, préfixe "IDEE:")
4. Une liste de chiffres/statistiques (format "LABEL: VALEUR", une par ligne, préfixe "CHIFFRE:")
5. Une chronologie si des dates sont présentes (format "DATE: description", préfixe "DATE:")

Réponds UNIQUEMENT avec ces lignes, sans autre texte.

TEXTE:
"""
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt + content.raw_text[:8000]}],
            max_tokens=1500,
        )
        reply = (response.choices[0].message.content or "").strip()
        return _parse_openai_reply(reply, content)
    except Exception:
        return None


def _parse_openai_reply(reply: str, content: ExtractedContent) -> DocumentAnalysis:
    """Parse la réponse OpenAI en DocumentAnalysis."""
    ideas: list[KeyIdea] = []
    figures: list[KeyFigure] = []
    timeline: list[TimelineItem] = []
    title = content.title
    summary = None
    
    for line in reply.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("IDEE:"):
            ideas.append(KeyIdea(text=line[5:].strip(), importance="medium"))
        elif line.upper().startswith("CHIFFRE:"):
            part = line[8:].strip()
            if ":" in part:
                label, _, value = part.partition(":")
                figures.append(KeyFigure(label=label.strip(), value=value.strip()))
        elif line.upper().startswith("DATE:"):
            part = line[5:].strip()
            if ":" in part:
                date, _, desc = part.partition(":")
                timeline.append(TimelineItem(date_or_step=date.strip(), description=desc.strip()))
            else:
                timeline.append(TimelineItem(date_or_step="", description=part))
        elif "résumé" in line.lower() or len(line) > 80:
            summary = line
    
    return DocumentAnalysis(
        title=title,
        summary=summary or content.raw_text[:400],
        key_ideas=ideas[:12],
        key_figures=figures[:15],
        timeline=timeline[:10],
        structure=[i.text for i in ideas[:8]],
        categories_for_chart={f.label[:30]: f.value for f in figures[:8]} if figures else None,
        raw_text=content.raw_text,
    )


async def analyze_content(content: ExtractedContent) -> DocumentAnalysis:
    """Analyse le contenu extrait (avec OpenAI si dispo, sinon heuristique)."""
    analysis = await _analyze_with_openai(content)
    if analysis is not None:
        return analysis
    return _analyze_heuristic(content)
