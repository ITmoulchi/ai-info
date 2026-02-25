# Plateforme Infographie Intelligente

Génération automatique d'**infographies professionnelles** à partir d'un document (PDF, Word, PowerPoint ou texte). La plateforme analyse le contenu, extrait les idées clés, les chiffres importants et la structure, puis produit une infographie avec graphiques, chronologie et mise en page harmonieuse.

## Fonctionnalités

- **Formats supportés** : PDF, Word (.docx), PowerPoint (.pptx), fichier texte (.txt, .md)
- **Extraction** : texte, titres, sections
- **Analyse** : idées clés, statistiques, chronologie (années), structure
- **Infographie** : chiffres mis en avant, graphiques en barres, timeline, cartes d'idées
- **Design** : thèmes automatiques (couleurs, typographie) selon le contenu
- **Optionnel** : clé API OpenAI pour une extraction plus fine des idées et chiffres

## Installation

```bash
cd infographic-platform
python -m venv venv
venv\Scripts\activate   # Windows
# ou: source venv/bin/activate  # Linux / macOS
pip install -r requirements.txt
```

### Option : meilleure analyse avec OpenAI

Copiez `.env.example` en `.env` à la racine du projet puis renseignez votre clé :

```
OPENAI_API_KEY=votre_cle_api_openai
```

Sans clé, une analyse heuristique (regex, structure) est utilisée.

## Lancement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Puis ouvrez **http://localhost:8000** dans le navigateur.

## Utilisation

1. Sur la page d'accueil : glissez-déposez un fichier ou cliquez pour choisir (PDF, Word, PowerPoint, texte).
2. Cliquez sur **Générer l'infographie**.
3. Consultez l'infographie dans le navigateur ou téléchargez le fichier HTML.

L'infographie contient notamment :

- Un **titre** et un **résumé**
- Des **chiffres clés** mis en évidence
- Un **graphique en barres** si des données numériques sont détectées
- Les **idées clés** en cartes
- Une **chronologie** si des années sont présentes dans le document

## Structure du projet

```
infographic-platform/
├── app/
│   ├── main.py           # API FastAPI
│   ├── config.py         # Configuration
│   ├── models.py         # Modèles de données
│   ├── extractors/       # PDF, Word, PPTX, texte
│   ├── analyzer/         # Analyse du contenu (heuristique + option OpenAI)
│   ├── design/           # Thèmes (couleurs, typo)
│   ├── generator/        # Génération HTML de l'infographie
│   └── static/           # Page d'accueil
├── requirements.txt
├── .env.example
└── README.md
```

## API

- `GET /` — Page d'accueil avec formulaire d'upload
- `POST /generate` — Envoi d'un fichier, retourne l'ID et les URLs de l'infographie
- `GET /infographic/{id}` — Affichage de l'infographie (HTML)
- `GET /download/{id}` — Téléchargement de l'infographie en HTML

## Licence

Projet à usage éducatif / démonstration.
