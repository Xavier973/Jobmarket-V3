# JobMarket — Data Job Market Analytics (V3)

## Aperçu
JobMarket V3 repart sur une architecture modulaire pour analyser le marche de l'emploi data en France. La collecte d'offres se fait via l'API France Travail, puis les donnees sont normalisees dans un schema commun pour faciliter l'ajout d'autres sources (APEC, Welcome to the Jungle, Indeed, LinkedIn).

## Objectifs
- Remplacer le scraping par l'API France Travail.
- Decoupler l'ingestion, le stockage et la visualisation.
- Garder un schema canonique pour accueillir plusieurs sources.
- Choisir une nouvelle solution de dashboard (etude en cours).

## Architecture cible
- **Ingestion** : pipeline multi-sources (adapters par source) -> donnees brutes -> normalisees.
- **Stockage** : moteur d'analyse (Elasticsearch par defaut) et indexation optimisee.
- **API** : service de lecture pour exposer les donnees au dashboard.
- **Dashboard** : front-end a definir, connecte a l'API.

## Stack technique (base)
- Python 3.9+
- Elasticsearch 8.x (par defaut)
- Docker + Docker Compose

## Structure du projet (V3)
```
Jobmarket_V3/
├── pipelines/           # Pipeline d'ingestion et normalisation
│   └── ingest/
│       ├── sources/     # Adapters par source (francetravail, apec, etc.)
│       ├── models.py    # Schéma canonique JobOffer
│       ├── normalizer.py
│       └── io.py
│
├── scripts/             # Scripts utilitaires
│   ├── analysis/        # Scripts d'analyse des données
│   │   ├── analyze_data_analyst.py
│   │   └── examples_visualization.py
│   └── maintenance/     # Scripts de maintenance
│       └── fix_line_endings.py
│
├── tests/               # Tests de validation
│   └── test_enriched_mapping.py
│
├── data/                # Données brutes et normalisées
│   ├── raw/francetravail/
│   └── normalized/francetravail/
│
├── docs/                # Documentation
│   ├── architecture.md
│   ├── data-model.md
│   ├── guide-collecte-francetravail.md
│   └── ops.md
│
└── config/              # Configuration
    └── .env.example
```

## Configuration
Exemple d'environnement : [config/.env.example](config/.env.example)

Variables principales :
- FT_API_BASE_URL=https://api.francetravail.io/partenaire/offresdemploi
- FT_API_TOKEN_URL=https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire
- FT_API_CLIENT_ID=
- FT_API_CLIENT_SECRET=
- FT_API_SEARCH_URL=https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
- FT_API_SCOPE=api_offresdemploiv2 o2dsoffre
- INGEST_OUTPUT_DIR=./data

## Démarrage rapide (ingestion France Travail)
1. Copier l'environnement :
   ```bash
   copy config/.env.example config/.env
   ```
2. Renseigner les variables France Travail.
3. Lancer l'ingestion :
   ```bash
   # Collecte par mots-clés (recommandé)
   python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --limit 200
   
   # Collecte par codes ROME (moins précis)
   python -m pipelines.ingest.sources.francetravail.main --rome-codes M1419,M1811,M1405 --limit 200
   
   # Mode échantillon (test)
   python -m pipelines.ingest.sources.francetravail.main --sample
   ```

## Analyse des données collectées
```bash
# Analyser les offres Data Analyst
python scripts/analysis/analyze_data_analyst.py

# Exemples de visualisations (salaires, compétences, etc.)
python scripts/analysis/examples_visualization.py

# Valider le mapping enrichi
python tests/test_enriched_mapping.py
```

## Maintenance
```bash
# Corriger les fins de ligne des fichiers JSONL
python scripts/maintenance/fix_line_endings.py
```

## Roadmap courte
- Etude comparative du dashboard (voir [docs/dashboard-eval.md](docs/dashboard-eval.md)).
- Mise en place du service API.
- Indexation ElasticSearch et tests d'aggregations.
- Ajout d'une 2eme source (APEC ou WTTJ) pour valider l'extensibilite.

## Troubleshooting API France Travail
- Erreur 401: verifier `FT_API_CLIENT_ID`, `FT_API_CLIENT_SECRET` et `FT_API_SCOPE`.
- Erreur 400: verifier `FT_API_TOKEN_URL` et le format `application/x-www-form-urlencoded`.
- Erreur 429: respecter `Retry-After` et limiter le nombre d'appels par seconde.
- Aucun resultat: verifier les parametres de recherche et tester en mode bac a sable.

## Licence
Projet interne / usage prive.