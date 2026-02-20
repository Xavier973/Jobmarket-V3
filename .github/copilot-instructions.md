# GitHub Copilot Instructions

## Project context
- **JobMarket V3** : Plateforme d'analyse du marché de l'emploi data en France
- **Architecture** : Pipeline d'ingestion modulaire + API FastAPI + Dashboard React/Next.js
- **Stack principale** : Python 3.9+, Elasticsearch 8.x, FastAPI, Next.js 14, React 18, TypeScript
- **Déploiement** : Docker Compose (4 services : Elasticsearch, Kibana, Backend, Frontend)
- **Source de données** : API France Travail (OAuth client credentials)
- **Modèle de données** : Schéma canonique JobOffer pour multi-sources (France Travail, APEC, WTTJ prévu)

## Architecture overview
```
pipelines/          → Ingestion & normalisation (sources/francetravail/*, models.py, normalizer.py)
├── ingest/         → Adapters par source (francetravail actuellement)
└── storage/        → Client Elasticsearch (indexation, mappings)

backend/            → API REST FastAPI
├── app/main.py     → Point d'entrée (CORS, routes)
├── app/config.py   → Settings (Pydantic BaseSettings)
├── app/models/     → Modèles Pydantic (filters, job_offer)
├── app/services/   → ElasticsearchService, AnalyticsService
└── app/api/v1/     → Routes (offers, stats, analytics, filters)

frontend/           → Dashboard React + Next.js 14
├── src/app/        → Pages Next.js (/, /dashboard, /dashboard/offers, /analytics, /map)
├── src/lib/        → Client API (axios), utilitaires
├── src/types/      → Types TypeScript
└── package.json    → Deps: Next.js 14, React Query, Zustand, Recharts, Leaflet

scripts/            → Outils CLI
├── collect_keywords_batch.py   → Collecte par mots-clés
├── index_to_elasticsearch.py   → Indexation
├── query_elasticsearch.py      → Requêtes de test
├── analysis/                   → Scripts d'analyse
└── maintenance/                → Scripts de maintenance

data/
├── raw/<source>/        → Données brutes (JSONL)
└── normalized/<source>/ → Données normalisées (JSONL)
```

## Coding guidelines

### Général
- **Modules courts et focalisés** : Séparer ingestion, normalisation, stockage, API, visualisation
- **Variables d'environnement** : Jamais de secrets hardcodés (use .env via BaseSettings)
- **Fonctions simples et testables** : Préférer fonctions pures > classes complexes
- **Encodage** : UTF-8, mais éviter caractères spéciaux dans code (sauf données externes)
- **Format** : Suivre PEP 8 (Python), ESLint (TypeScript)

### Python backend (FastAPI)
- **Config** : Utiliser `app.config.Settings` (Pydantic BaseSettings)
- **Services** : Logique métier dans `app/services/` (ElasticsearchService, AnalyticsService)
- **Routes** : Organiser par ressource dans `app/api/v1/` (offers.py, stats.py, analytics.py, filters.py)
- **Modèles** : Pydantic pour validation (app/models/)
- **CORS** : Configurer dans main.py via `settings.cors_origins_list`
- **Health checks** : Endpoints `/` et `/health` obligatoires pour Docker healthcheck

### Frontend (Next.js 14 + React 18)
- **App Router** : Utiliser Next.js App Router (src/app/)
- **'use client'** : Ajouter directive pour composants avec hooks/interactivité
- **State management** : Zustand pour état global, React Query pour cache API
- **Styling** : Tailwind CSS (configuration dans tailwind.config.js)
- **Fetching** : Utiliser axios + React Query (src/lib/)
- **Types** : Définir interfaces TypeScript dans src/types/
- **Composants** : Préférer composants fonctionnels + hooks

### Elasticsearch
- **Client** : Utiliser `pipelines.storage.elasticsearch.ElasticsearchClient`
- **Index** : `jobmarket_v3` (configurable via ELASTICSEARCH_INDEX)
- **Mapping** : Enrichi avec geo_point, keyword, text, nested (voir storage/elasticsearch.py)
- **Agrégations** : Utiliser termes, stats, date_histogram pour analytics
- **Pagination** : from/size ou search_after pour gros volumes

## Data pipeline specifics

### Ingestion
- **Adapters** : Un dossier par source dans `pipelines/ingest/sources/` (ex: francetravail/)
- **Modèle canonique** : Mapper vers `JobOffer` (pipelines/ingest/models.py)
- **Flux** : API source → raw JSONL (data/raw/) → normalisation → normalized JSONL (data/normalized/)
- **Champs principaux JobOffer** :
  - Identification : id, source
  - Base : title, description, company_name
  - Classification : rome_code, rome_label, job_category, naf_code, sector
  - Localisation : city, department, region, latitude/longitude, commune_code
  - Contrat : contract_type, duration, nature, work_schedule, weekly_hours, is_alternance
  - Rémunération : salary_min/max, unit, comment, benefits
  - Compétences : skills, skills_required (nested), skills_desired, soft_skills, languages
  - Formation : education_level, education_required, experience_required/level/code
  - Entreprise : company_size, company_adapted
  - Conditions : work_context, permits_required, travel_frequency, accessible_handicap
  - Métadonnées : published_at, updated_at, collected_at, positions_count, url, raw

### France Travail API specifics
- **Authentication** : OAuth2 client credentials (application/x-www-form-urlencoded)
- **Scopes** : `api_offresdemploiv2 o2dsoffre` pour offres d'emploi
- **Pagination** : Paramètre `range` (format "0-149", "150-299"), max 1150 offres
- **Rate limiting** : Respecter HTTP 429 + Retry-After header
- **Contournement limite 150** : Option `--split-by-contract` pour subdiviser recherches
- **URL token** : https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire
- **URL search** : https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search

### Normalisation
- **Fichier** : `pipelines/ingest/normalizer.py`
- **Principe** : Transformer données brutes source → JobOffer canonique
- **Géolocalisation** : Extraire latitude/longitude, codes INSEE si disponibles
- **Compétences** : Séparer exigées/souhaitées, extraire niveau/code
- **Dates** : Normaliser en ISO 8601
- **Préserver raw** : Garder données originales dans champ `raw` pour debug

### Stockage & Indexation
- **Script** : `scripts/index_to_elasticsearch.py`
- **Options** : --source, --file, --force (recréer index)
- **Mapping** : Défini dans `pipelines/storage/elasticsearch.py`
- **Bulk indexing** : Utiliser helpers.bulk() pour performance
- **Dédoublonnage** : Basé sur champ `id` (unique par source)

## API backend (FastAPI)

### Routes disponibles
```
GET /                           → Health check + infos API
GET /health                     → Healthcheck pour Docker
GET /api/v1/offers              → Liste offres (pagination, filtres)
GET /api/v1/offers/{id}         → Détail offre
GET /api/v1/stats/overview      → KPIs globaux
GET /api/v1/stats/top-skills    → Top compétences
GET /api/v1/stats/salaries      → Distribution salaires
GET /api/v1/analytics/...       → Analyses avancées
GET /api/v1/filters/values      → Valeurs possibles pour filtres
```

### Services
- **ElasticsearchService** (`app/services/elasticsearch.py`) :
  - search_offers() : Recherche avec filtres
  - get_offer_by_id() : Récupération par ID
  - get_aggregations() : Agrégations génériques
  - build_query() : Construction requêtes Elasticsearch
  
- **AnalyticsService** (`app/services/analytics.py`) :
  - get_overview_stats() : KPIs (total, par contrat, par région)
  - get_top_skills() : Top N compétences
  - get_salary_distribution() : Stats salaires
  - get_temporal_trends() : Évolution temporelle

### Modèles Pydantic
- **FilterRequest** (`app/models/filters.py`) : Filtres de recherche
- **JobOfferResponse** (`app/models/job_offer.py`) : Schéma réponse API

### Configuration
- **Fichier** : `backend/app/config.py`
- **Variables** :
  - ELASTICSEARCH_URL (default: http://localhost:9200)
  - ELASTICSEARCH_INDEX (default: jobmarket_v3)
  - CORS_ORIGINS (liste séparée virgules)
  - API_V1_PREFIX (default: /api/v1)
  - DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

## Frontend dashboard

### Technologies
- **Framework** : Next.js 14 (App Router)
- **UI** : React 18 + TypeScript + Tailwind CSS
- **État** : Zustand (global state), React Query (cache API/mutations)
- **Charts** : Recharts (graphiques)
- **Cartes** : Leaflet + react-leaflet
- **Icônes** : Lucide React
- **Dates** : date-fns

### Pages disponibles
- `/` : Landing page
- `/dashboard` : Vue d'ensemble (KPIs, statistiques)
- `/dashboard/offers` : Liste offres avec filtres
- `/dashboard/analytics` : Analyses avancées (en développement)
- `/dashboard/map` : Carte interactive (en développement)

### Règles frontend
- **Client components** : Ajouter 'use client' pour hooks/interactivité
- **API calls** : Via axios dans src/lib/, wrapped par React Query
- **Typage** : Définir types dans src/types/, synchro avec backend
- **Responsive** : Mobile-first avec Tailwind breakpoints
- **Performance** : Utiliser React Query pour cache, prefetch, optimistic updates

## Scripts & maintenance

### Collecte
```bash
# Collecte complète avec contournement limite API
python -m pipelines.ingest.sources.francetravail.main --keywords "data engineer" --split-by-contract

# Collecte simple (max 150 offres)
python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst"

# Collecte limitée
python -m pipelines.ingest.sources.francetravail.main --keywords "data scientist" --limit 200

# Collecte par codes ROME
python -m pipelines.ingest.sources.francetravail.main --rome-codes M1419,M1811

# Mode échantillon (test rapide)
python -m pipelines.ingest.sources.francetravail.main --sample
```

### Indexation
```bash
# Indexer toutes les offres France Travail
python scripts/index_to_elasticsearch.py --source francetravail

# Indexer fichier spécifique
python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl

# Forcer recréation index
python scripts/index_to_elasticsearch.py --source francetravail --force
```

### Analyse
```bash
# Analyser offres Data Analyst
python scripts/analysis/analyze_data_analyst.py

# Analyser champ spécifique (menu interactif)
python scripts/analysis/analyze_field.py

# Exemples visualisations
python scripts/analysis/examples_visualization.py
```

### Maintenance
```bash
# Corriger fins de ligne JSONL
python scripts/maintenance/fix_line_endings.py

# Régénérer données normalisées
python scripts/maintenance/regenerate_normalized.py

# Dédoublonner offres
python scripts/maintenance/deduplicate_offers.py
```

## Docker & deployment

### Services
```yaml
elasticsearch:9200  → Moteur recherche/agrégations
kibana:5601         → Interface Elasticsearch
backend:8000        → API FastAPI
frontend:3000       → Dashboard Next.js
```

### Commandes
```bash
# Démarrer tous les services
docker-compose up -d

# Rebuilder un service
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Arrêter
docker-compose down

# Arrêter + supprimer volumes
docker-compose down -v
```

### Health checks
- Elasticsearch : `curl http://localhost:9200/_cluster/health`
- Kibana : `curl http://localhost:5601/api/status`
- Backend : `curl http://localhost:8000/health`
- Frontend : `curl http://localhost:3000`

## Testing

### Règles générales
- **Ajouter tests** pour tout adapter/mapping/service modifié
- **Tests unitaires** : Préférer petits tests pour fonctions mapping
- **Tests intégration** : Valider pipeline complet (raw → normalized → indexed)
- **Tests API** : Utiliser pytest + TestClient FastAPI (backend/tests/)
- **Mocking** : Mocker Elasticsearch pour tests rapides

### Commandes
```bash
# Tests backend
cd backend
pytest tests/

# Tests pipeline
pytest tests/test_enriched_mapping.py

# Type checking frontend
cd frontend
npm run type-check

# Linting
npm run lint
```

## Documentation
- **Architecture** : docs/architecture.md
- **Modèle données** : docs/data-model.md
- **Elasticsearch** : docs/elasticsearch.md, docs/elasticsearch-quickstart.md
- **Dashboard** : docs/dashboard-architecture.md, docs/dashboard-eval.md
- **Guide collecte** : docs/guide-collecte-francetravail.md
- **Ops** : docs/ops.md

## Common patterns

### Ajouter une nouvelle source d'ingestion
1. Créer `pipelines/ingest/sources/<source>/`
2. Implémenter adapter avec méthodes fetch() et parse()
3. Mapper vers JobOffer canonique dans normalizer
4. Sauvegarder raw → data/raw/<source>/
5. Sauvegarder normalized → data/normalized/<source>/
6. Ajouter tests dans tests/

### Ajouter un endpoint API
1. Créer route dans `backend/app/api/v1/`
2. Ajouter service method si logique complexe
3. Définir modèles Pydantic pour request/response
4. Documenter avec docstrings (auto OpenAPI)
5. Ajouter tests dans backend/tests/

### Ajouter une page dashboard
1. Créer page dans `frontend/src/app/dashboard/<page>/page.tsx`
2. Ajouter 'use client' si interactivité
3. Définir types dans src/types/
4. Créer hooks API dans src/lib/
5. Utiliser React Query pour fetch
6. Styliser avec Tailwind

## Troubleshooting

### API France Travail
- **401 Unauthorized** : Vérifier CLIENT_ID, CLIENT_SECRET, SCOPE
- **400 Bad Request** : Vérifier TOKEN_URL et Content-Type (x-www-form-urlencoded)
- **429 Rate Limit** : Respecter Retry-After, limiter requêtes/sec
- **Aucun résultat** : Tester paramètres en mode sandbox
- **Limite 150** : Utiliser --split-by-contract ou subdiviser par dates

### Elasticsearch
- **Connection refused** : Vérifier `docker-compose ps`, attendre healthcheck
- **Index not found** : Lancer `scripts/index_to_elasticsearch.py`
- **Mapping conflict** : Forcer recréation avec --force
- **Out of memory** : Augmenter ES_JAVA_OPTS dans docker-compose.yml

### Backend API
- **CORS error** : Vérifier CORS_ORIGINS dans config
- **Import error** : Vérifier PYTHONPATH et structure modules
- **500 Internal** : Checker logs `docker-compose logs backend`

### Frontend
- **Module not found** : `cd frontend && npm install`
- **Hydration error** : Vérifier 'use client' sur composants avec state
- **Build error** : `npm run type-check` pour erreurs TypeScript
- **API call fail** : Vérifier NEXT_PUBLIC_API_URL
