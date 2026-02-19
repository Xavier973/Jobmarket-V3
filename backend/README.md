# Backend API - JobMarket V3

API FastAPI pour exposer les données du marché de l'emploi data en France.

## Architecture

```
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration
│   ├── models/              # Modèles Pydantic
│   ├── services/            # Logique métier (ES, analytics)
│   └── api/v1/              # Routes API
├── tests/                   # Tests unitaires
└── requirements.txt
```

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

L'API utilise le fichier `config/.env` à la racine du projet.

Variables principales :
- `ELASTICSEARCH_URL` : URL Elasticsearch (défaut: http://localhost:9200)
- `ELASTICSEARCH_INDEX` : Nom de l'index (défaut: job_offers)
- `CORS_ORIGINS` : Origines autorisées pour CORS

## Démarrage

### Mode développement

```bash
# Depuis le dossier backend/
uvicorn app.main:app --reload --port 8000

# Ou depuis la racine du projet
cd backend
python -m app.main
```

### Mode production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Accès

- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

## Endpoints principaux

### Statistiques
- `GET /api/v1/stats/overview` - KPIs globaux
- `GET /api/v1/stats/kpis` - KPIs avec filtres

### Offres
- `GET /api/v1/offers` - Liste paginée des offres
- `POST /api/v1/offers/search` - Recherche avec filtres avancés
- `GET /api/v1/offers/{id}` - Détail d'une offre
- `GET /api/v1/offers/count/total` - Comptage avec filtres

### Analytics
- `GET /api/v1/analytics/salary` - Statistiques salariales
- `GET /api/v1/analytics/skills` - Top compétences
- `GET /api/v1/analytics/geography` - Distribution géographique
- `GET /api/v1/analytics/contracts` - Types de contrat
- `GET /api/v1/analytics/timeline` - Évolution temporelle

### Filtres
- `GET /api/v1/filters/regions` - Liste des régions
- `GET /api/v1/filters/departments` - Liste des départements
- `GET /api/v1/filters/cities` - Liste des villes
- `GET /api/v1/filters/contracts` - Types de contrat
- `GET /api/v1/filters/experience-levels` - Niveaux d'expérience
- `GET /api/v1/filters/rome-codes` - Codes ROME

## Exemples de requêtes

### Récupérer les offres

```bash
# Toutes les offres (paginées)
curl http://localhost:8000/api/v1/offers

# Offres avec filtres
curl "http://localhost:8000/api/v1/offers?keywords=python,data&regions=Île-de-France&page=1&size=20"

# Recherche avancée (POST)
curl -X POST http://localhost:8000/api/v1/offers/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["python", "data"],
    "regions": ["Île-de-France"],
    "salary_min": 35000,
    "contract_types": ["CDI"]
  }'
```

### Analytics

```bash
# Statistiques salariales par expérience
curl "http://localhost:8000/api/v1/analytics/salary?group_by=experience_level"

# Top 20 compétences
curl "http://localhost:8000/api/v1/analytics/skills?top=20"

# Distribution géographique par région
curl "http://localhost:8000/api/v1/analytics/geography?level=region"

# Timeline hebdomadaire
curl "http://localhost:8000/api/v1/analytics/timeline?interval=week"
```

## Tests

```bash
pytest tests/ -v
```

## Déploiement

Voir `docker-compose.yml` à la racine du projet pour le déploiement avec Docker.
