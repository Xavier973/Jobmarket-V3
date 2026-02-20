# JobMarket — Data Job Market Analytics (V3)

## Aperçu
JobMarket V3 repart sur une architecture modulaire pour analyser le marche de l'emploi data en France. La collecte d'offres se fait via l'API France Travail, puis les donnees sont normalisees dans un schema commun pour faciliter l'ajout d'autres sources (APEC, Welcome to the Jungle, Indeed, LinkedIn).

## Objectifs
- Remplacer le scraping par l'API France Travail.
- Decoupler l'ingestion, le stockage et la visualisation.
- Garder un schema canonique pour accueillir plusieurs sources.
- Choisir une nouvelle solution de dashboard (etude en cours).

## Fonctionnalités clés
- ✅ Collecte automatisée via API France Travail
- ✅ Normalisation multi-sources (schéma canonique)
- ✅ **Détection automatique du télétravail** (26.8% des offres)
- ✅ Indexation Elasticsearch avec géolocalisation
- ✅ API REST FastAPI pour requêtes et analyses
- ✅ Dashboard React/Next.js (en développement)

## Architecture cible
- **Ingestion** : pipeline multi-sources (adapters par source) -> donnees brutes -> normalisees.
- **Stockage** : moteur d'analyse (Elasticsearch par defaut) et indexation optimisee.
- **API** : service de lecture FastAPI pour exposer les donnees au dashboard.
- **Dashboard** : interface React + Next.js connectee a l'API.

## Stack technique (base)
- Python 3.9+
- Elasticsearch 8.x (par defaut)
- FastAPI (API backend)
- Next.js 14 + React 18 + TypeScript (Dashboard frontend)
- Docker + Docker Compose

## Structure du projet (V3)
```
Jobmarket_V3/
├── pipelines/           # Pipeline d'ingestion et normalisation
│   ├── ingest/
│   │   ├── sources/     # Adapters par source (francetravail, apec, etc.)
│   │   ├── models.py    # Schéma canonique JobOffer
│   │   ├── normalizer.py
│   │   └── io.py
│   └── storage/         # Module de stockage Elasticsearch
│       ├── elasticsearch.py
│   backend/             # API FastAPI
│   ├── app/
│   │   ├── main.py      # Point d'entrée API
│   │   ├── config.py    # Configuration
│   │   ├── models/      # Modèles Pydantic
│   │   ├── services/    # Logique métier (ES, analytics)
│   │   └── api/v1/      # Routes API
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/            # Dashboard React + Next.js
│   ├── src/
│   │   ├── app/         # Pages Next.js
│   │   ├── components/  # Composants React
│   │   ├── lib/         # Client API, utilitaires
│   │   ├── hooks/       # Custom hooks
│   │   └── types/       # Types TypeScript
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
│
├── scripts/             # Scripts utilitaires
│   ├── index_to_elasticsearch.py  # Indexation dans Elasticsearch
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
│   ├── elasticsearch.md
│   ├── dashboard-architecture.md
│   ├── guide-collecte-francetravail.md
│   └── ops.md
│
├── config/              # Configuration
│   └── .env.example
│
├── docker-compose.yml   # Elasticsearch + Kibana + Backend + Frontend
│
├── docker-compose.yml   # Elasticsearch + Kibana
└── requirements.txt     # Dépendances Python
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
   # Collecte complète avec découpage automatique (contourne la limite de 150)
   python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --split-by-contract
   python -m pipelines.ingest.sources.francetravail.main --keywords "data engineer" --split-by-contract
   
   # Collecte simple (limitée à 150 offres par l'API)
   python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst"
   
   # Collecte limitée (nombre d'offres spécifique)
   python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --limit 200
   
   # Collecte par codes ROME
   python -m pipelines.ingest.sources.francetravail.main --rome-codes M1419,M1811,M1405
   
   # Mode échantillon (test rapide)
   python -m pipelines.ingest.sources.francetravail.main --sample
   ```

## Démarrage Elasticsearch et indexation
1. Démarrer Elasticsearch et Kibana :
   ```bash
   # Démarrer les conteneurs Docker
   docker-compose up -d
   
   # Vérifier que les services sont démarrés
   - **Backend API** : http://localhost:8000 (docs: http://localhost:8000/docs)
   - **Dashboard** : http://localhost:3000
   docker-compose ps
   ```

2. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Indexer les données dans Elasticsearch :
   ```bash
   # Indexer toutes les offres France Travail
   python scripts/index_to_elasticsearch.py --source francetravail
   
   # Indexer un fichier spécifique
   

## Dashboard (React + FastAPI)

### Démarrage complet avec Docker

```bash
# Tout démarrer (Elasticsearch + Backend + Frontend)
docker-compose up -d

# Accès :
# - API : http://localhost:8000/docs
# - Dashboard : http://localhost:3000
```

### Développement manuel

**Terminal 1 : Elasticsearch**
```bash
docker-compose up elasticsearch kibana
```

**Terminal 2 : Backend API**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 : Frontend**
```bash
cd frontend
np✅ Choix dashboard : React + FastAPI (voir [docs/dashboard-eval.md](docs/dashboard-eval.md)).
- ✅ Mise en place du service API FastAPI.
- ✅ Indexation ElasticSearch et tests d'aggregations.
- ✅ Structure frontend Next.js + pages de base.
- 🚧 Développement features dashboard (filtres, graphiques, carte).
- 📅
### Pages disponibles

- `/` - Landing page
- `/dashboard` - Vue d'ensemble (KPIs, statistiques)
- `/dashboard/offers` - Liste des offres (en développement)
- `/dashboard/analytics` - Analyses avancées (en développement)
- `/dashboard/map` - Carte interactive (en développement)

📖 Documentation détaillée : [docs/dashboard-architecture.md](docs/dashboard-architecture.md)python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl
   
   # Forcer la recréation de l'index (supprime les données existantes)
   python scripts/index_to_elasticsearch.py --source francetravail --force
   ```

4. Accéder aux interfaces :
   - **Elasticsearch** : http://localhost:9200
   - **Kibana** : http://localhost:5601

📖 Pour plus de détails, voir [docs/elasticsearch.md](docs/elasticsearch.md)

## Analyse des données collectées
```bash
# Analyser les offres Data Analyst
python scripts/analysis/analyze_data_analyst.py

# Analyser un champs spécifique - menu interactif
python scripts/analysis/analyze_field.py

# Exemples de visualisations (salaires, compétences, etc.)
python scripts/analysis/examples_visualization.py

# Tester la détection du télétravail
python scripts/analysis/test_remote_detection.py

# Valider le mapping enrichi
python tests/test_enriched_mapping.py
```

## Filtrer les offres avec télétravail

Le système détecte automatiquement les mentions du télétravail dans les descriptions d'offres.

**Statistiques :** 26.8% des offres (561 sur 2096) mentionnent le télétravail.

```bash
# Exemples de requêtes Elasticsearch pour filtrer par télétravail
python scripts/query_remote_offers.py

# Tester la détection sur les données collectées
python scripts/analysis/test_remote_detection.py
```

**Documentation complète :** [docs/teletravail-detection.md](docs/teletravail-detection.md)

## Maintenance
```bash
# Corriger les fins de ligne des fichiers JSONL
python scripts/maintenance/fix_line_endings.py
```

## Roadmap courte
- Etude comparative du dashboard (voir [docs/dashboard-eval.md](docs/dashboard-eval.md)).
- Mise en place du service API.
- ✅ Indexation ElasticSearch et tests d'aggregations.
- Ajout d'une 2eme source (APEC ou WTTJ) pour valider l'extensibilite.

##  Troubleshooting API France Travail
- Erreur 401: verifier `FT_API_CLIENT_ID`, `FT_API_CLIENT_SECRET` et `FT_API_SCOPE`.
- Erreur 400: verifier `FT_API_TOKEN_URL` et le format `application/x-www-form-urlencoded`.
- Erreur 429: respecter `Retry-After` et limiter le nombre d'appels par seconde.
- Aucun resultat: verifier les parametres de recherche et tester en mode bac a sable.
- **Pagination avec le paramètre `range`**: L'API utilise le paramètre `range` (format `"0-149"`, `"150-299"`) au lieu de `page`/`size`. Maximum 1150 offres par recherche (range 0-149 + 150-299 + ... + 1000-1149). Pour aller au-delà, utiliser `--split-by-contract` ou subdiviser par dates (`minCreationDate`/`maxCreationDate`).
- **Écart avec le site web**: Le site France Travail affiche beaucoup plus d'offres (ex: 1337 pour "data engineer" vs 353 via l'API). **Raison principale** : le site utilise une recherche floue qui renvoie des résultats peu pertinents (ex: "Développeur COBOL" apparaît pour "data engineer"). L'API est plus stricte et ne renvoie que les offres vraiment pertinentes. **Conclusion** : Les 353 offres API sont de meilleure qualité que les 1337 du site (moins de bruit). Le site inclut aussi quelques offres partenaires (Indeed, Monster, LinkedIn) non accessibles via l'API publique.

## Licence
Projet interne / usage prive.