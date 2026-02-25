"""Point d'entrée FastAPI — plateforme infographie intelligente."""
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.extractors import extract_from_file
from app.analyzer import analyze_content
from app.generator import generate_infographic_html
from app.design import get_theme_for_analysis
from app.models import DocumentAnalysis


app = FastAPI(
    title="Plateforme Infographie Intelligente",
    description="Génération automatique d'infographies à partir de documents PDF, Word, PowerPoint ou texte.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_dirs():
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md"}

# Servir les images du dossier projet (6.png, 7.png) sous /images
PROJECT_ROOT = Path(__file__).resolve().parent.parent
app.mount("/images", StaticFiles(directory=str(PROJECT_ROOT), html=True), name="images")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec formulaire d'upload."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Infographie</title></head>
    <body><h1>Plateforme Infographie</h1>
    <p>Utilisez <code>POST /generate</code> avec un fichier pour générer une infographie.</p>
    </body></html>
    """


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Enregistre le fichier, extrait le texte et le renvoie (pour analyse par Puter côté frontend).
    """
    _ensure_dirs()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            detail=f"Format non supporté. Utilisez: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    file_id = str(uuid.uuid4())
    settings = get_settings()
    upload_path = settings.upload_dir / f"{file_id}{suffix}"
    try:
        content = await file.read()
        upload_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur lors de l'enregistrement: {e}")
    try:
        extracted = extract_from_file(upload_path)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur d'extraction: {e}")
    return {
        "file_id": file_id,
        "filename": file.filename or "document",
        "text": extracted.raw_text,
    }


@app.post("/generate-from-analysis")
async def generate_from_analysis(body: dict = Body(...)):
    """
    Génère l'infographie à partir d'une analyse fournie (ex. retour Puter.ai.chat).
    Body: { "file_id": "...", "filename": "...", "analysis": { ... } }
    """
    _ensure_dirs()
    file_id = body.get("file_id")
    filename = body.get("filename") or "document"
    analysis = body.get("analysis") or {}
    if not file_id:
        raise HTTPException(400, detail="file_id requis.")
    settings = get_settings()
    candidates = list(settings.upload_dir.glob(f"{file_id}.*"))
    if not candidates:
        raise HTTPException(400, detail="Fichier introuvable. Uploadez d'abord via /extract-text.")
    try:
        doc_analysis = DocumentAnalysis.model_validate(_normalize_analysis(analysis))
    except Exception as e:
        raise HTTPException(400, detail=f"Format d'analyse invalide: {e}")
    fallback_title = Path(filename).stem or "Infographie"
    if not doc_analysis.title or not str(doc_analysis.title).strip():
        doc_analysis.title = fallback_title
    theme = get_theme_for_analysis(doc_analysis)
    output_path = settings.output_dir / f"{file_id}.html"
    html = generate_infographic_html(doc_analysis, theme)
    output_path.write_text(html, encoding="utf-8")
    return {
        "id": file_id,
        "title": doc_analysis.title or fallback_title,
        "preview_url": f"/infographic/{file_id}",
        "download_url": f"/download/{file_id}",
    }


def _normalize_analysis(data: dict) -> dict:
    """Adapte le JSON Puter/frontend au format DocumentAnalysis."""
    key_ideas = []
    for i in data.get("key_ideas") or []:
        if isinstance(i, dict):
            key_ideas.append({"text": i.get("text", ""), "importance": i.get("importance", "medium")})
        else:
            key_ideas.append({"text": str(i), "importance": "medium"})
    key_figures = []
    for f in data.get("key_figures") or []:
        if isinstance(f, dict):
            key_figures.append({
                "label": f.get("label", ""),
                "value": str(f.get("value", "")),
                "unit": f.get("unit"),
            })
        else:
            key_figures.append({"label": "Statistique", "value": str(f)})
    timeline = []
    for t in data.get("timeline") or []:
        if isinstance(t, dict):
            timeline.append({
                "date_or_step": t.get("date_or_step", ""),
                "description": t.get("description", ""),
            })
        else:
            timeline.append({"date_or_step": "", "description": str(t)})
    return {
        "title": data.get("title"),
        "summary": data.get("summary"),
        "key_ideas": key_ideas,
        "key_figures": key_figures,
        "timeline": timeline,
        "structure": data.get("structure") or [],
        "categories_for_chart": data.get("categories_for_chart"),
        "raw_text": data.get("raw_text", ""),
    }


@app.post("/generate")
async def generate_infographic(file: UploadFile = File(...)):
    """
    Upload un document (PDF, Word, PowerPoint, texte) et renvoie l'infographie en HTML.
    """
    _ensure_dirs()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            detail=f"Format non supporté. Utilisez: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_id = str(uuid.uuid4())
    settings = get_settings()
    upload_path = settings.upload_dir / f"{file_id}{suffix}"
    output_path = settings.output_dir / f"{file_id}.html"

    try:
        content = await file.read()
        upload_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur lors de l'enregistrement: {e}")

    try:
        extracted = extract_from_file(upload_path)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur d'extraction: {e}")

    try:
        analysis = await analyze_content(extracted)
        # Titre de repli : nom du fichier sans extension
        fallback_title = Path(file.filename or "").stem or "Infographie"
        if not analysis.title or not analysis.title.strip():
            analysis.title = fallback_title
        theme = get_theme_for_analysis(analysis)
        html = generate_infographic_html(analysis, theme)
        output_path.write_text(html, encoding="utf-8")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=f"Erreur lors de l'analyse ou génération: {str(e)}")

    return {
        "id": file_id,
        "title": analysis.title or fallback_title,
        "preview_url": f"/infographic/{file_id}",
        "download_url": f"/download-pdf/{file_id}",
    }


@app.get("/infographic/{file_id}", response_class=HTMLResponse)
async def view_infographic(file_id: str):
    """Affiche l'infographie générée dans le navigateur."""
    settings = get_settings()
    path = settings.output_dir / f"{file_id}.html"
    if not path.is_file():
        raise HTTPException(404, detail="Infographie introuvable.")
    return path.read_text(encoding="utf-8")


@app.get("/download/{file_id}")
async def download_infographic(file_id: str):
    """Télécharge l'infographie en fichier HTML (pour l'instant, PDF à venir)."""
    settings = get_settings()
    path = settings.output_dir / f"{file_id}.html"
    if not path.is_file():
        raise HTTPException(404, detail="Infographie introuvable.")
    return FileResponse(
        path,
        media_type="text/html",
        filename=f"infographic_{file_id}.html",
    )


@app.get("/download-pdf/{file_id}")
async def download_infographic_pdf(file_id: str):
    """Génère et télécharge l'infographie en PDF via WeasyPrint."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise HTTPException(500, detail="WeasyPrint non installé. Impossible de générer le PDF.")

    settings = get_settings()
    html_path = settings.output_dir / f"{file_id}.html"
    
    if not html_path.is_file():
        raise HTTPException(404, detail="Infographie HTML introuvable.")

    pdf_path = settings.output_dir / f"{file_id}.pdf"
    
    # Générer le PDF s'il n'existe pas encore ou le régénérer à la demande
    try:
        # On lit le HTML
        html_content = html_path.read_text(encoding="utf-8")
        
        # On peut injecter du CSS spécifique pour l'impression ici si nécessaire
        print_css = CSS(string="@page { size: A4; margin: 0; } body { -webkit-print-color-adjust: exact; }")
        
        # Génération WeasyPrint
        # base_url est important pour charger les images locales (ex: /images/6.png)
        HTML(string=html_content, base_url=str(PROJECT_ROOT)).write_pdf(
            target=pdf_path, 
            stylesheets=[print_css]
        )
    except Exception as e:
        print(f"Erreur WeasyPrint: {e}")
        raise HTTPException(500, detail=f"Erreur lors de la génération du PDF: {e}")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"infographic_{file_id}.pdf",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
