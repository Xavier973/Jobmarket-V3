# Dashboard React + FastAPI - Architecture & Guide

## Vue d'ensemble

Le dashboard JobMarket V3 suit une architecture **React (Next.js) + FastAPI** séparée en deux services distincts mais intégrés au monorepo.

```
Jobmarket_V3/
├── backend/          # API FastAPI (Python)
├── frontend/         # Dashboard Next.js (TypeScript/React)
├── pipelines/        # Pipeline d'ingestion (existant)
├── data/             # Données brutes et normalisées
└── docker-compose.yml
```

## Flux de données

```
[API France Travail] 
    ↓
[pipelines/ingest] → data/raw/ → data/normalized/
    ↓
[scripts/index_to_elasticsearch.py] → [Elasticsearch]
    ↓
[backend/FastAPI] ← HTTP ← [frontend/React]
    ↓
[Visualisation dans le navigateur]
```

## Architecture Backend (FastAPI)

### Structure

```
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI + CORS
│   ├── config.py            # Configuration (charge .env)
│   ├── models/              # Modèles Pydantic
│   │   ├── job_offer.py     # Adapté depuis pipelines/ingest/models.py
│   │   └── filters.py       # Modèles de filtres
│   ├── services/            # Logique métier
│   │   ├── elasticsearch.py # Client ES + queries (réutilise pipelines/storage)
│   │   └── analytics.py     # Agrégations ES
│   └── api/v1/              # Routes API
│       ├── offers.py        # CRUD offres
│       ├── stats.py         # Statistiques globales
│       ├── analytics.py     # Analyses avancées
│       └── filters.py       # Options de filtres
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

### Endpoints API

#### **Base URL** : `http://localhost:8000/api/v1`

**Statistiques**
- `GET /stats/overview` - KPIs globaux
- `GET /stats/kpis?filters={...}` - KPIs avec filtres

**Offres**
- `GET /offers` - Liste paginée
- `POST /offers/search` - Recherche avancée
- `GET /offers/{id}` - Détail
- `GET /offers/count/total` - Comptage

**Analytics**
- `GET /analytics/salary?group_by=experience_level` - Stats salariales
- `GET /analytics/skills?top=20` - Top compétences
- `GET /analytics/geography?level=region` - Distribution géo
- `GET /analytics/contracts` - Types de contrat
- `GET /analytics/timeline?interval=week` - Évolution temporelle

**Filtres (options dynamiques)**
- `GET /filters/regions`
- `GET /filters/departments?region=xxx`
- `GET /filters/cities?department=xxx`
- `GET /filters/contracts`
- `GET /filters/experience-levels`
- `GET /filters/rome-codes`

### Réutilisation du code existant

Le backend **réutilise** les modules existants :

```python
# backend/app/services/elasticsearch.py
from pipelines.storage.elasticsearch import ElasticsearchClient

# backend/app/models/job_offer.py
# S'appuie sur pipelines/ingest/models.py
```

## Architecture Frontend (Next.js)

### Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router (pages)
│   │   ├── layout.tsx        # Layout global
│   │   ├── page.tsx          # Landing page
│   │   └── dashboard/
│   │       ├── page.tsx      # Vue d'ensemble (KPIs)
│   │       ├── offers/       # Liste détaillée offres
│   │       ├── analytics/    # Analyses approfondies
│   │       └── map/          # Carte géographique
│   ├── components/           # Composants React
│   │   ├── ui/               # Composants UI génériques (Button, Card, etc.)
│   │   ├── charts/           # Graphiques (Recharts)
│   │   ├── filters/          # Composants filtres
│   │   ├── map/              # Carte Leaflet
│   │   └── layout/           # Header, Sidebar, Footer
│   ├── lib/                  # Utilitaires
│   │   ├── api.ts            # Client API (axios)
│   │   └── formatters.ts     # Formatage données
│   ├── hooks/                # Custom React hooks
│   │   ├── useOffers.ts      # Hook pour récupérer offres
│   │   ├── useFilters.ts     # Hook pour gérer filtres
│   │   └── useStats.ts       # Hook pour stats
│   ├── types/                # Types TypeScript
│   │   ├── offer.ts
│   │   ├── filters.ts
│   │   └── stats.ts
│   └── styles/
│       └── globals.css       # Styles Tailwind
├── public/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
└── Dockerfile
```

### Pages principales

**1. Landing Page** (`/`)
- Hero section portfolio
- Présentation du projet
- CTA vers le dashboard

**2. Vue d'ensemble** (`/dashboard`)
- ✅ **Implémenté** : KPI cards (total offres, salaire moyen, % CDI, régions)
- ✅ **Implémenté** : Top 3 régions et compétences
- ✅ **Implémenté** : Distribution des contrats
- 🚧 **TODO** : Graphiques interactifs (salaires, timeline)
- 🚧 **TODO** : Filtres latéraux

**3. Liste des offres** (`/dashboard/offers`) - 🚧 **À implémenter**
- Table paginée avec tri
- Filtres (région, contrat, salaire, etc.)
- Modal de détail d'offre
- Export CSV

**4. Analytics avancées** (`/dashboard/analytics`) - 🚧 **À implémenter**
Sections à onglets :
- Analyse salariale (box plot par expérience)
- Compétences (bar chart, heatmap co-occurrence)
- Géographie (treemap, carte choroplèthe)
- Tendances temporelles (line chart, calendar heatmap)

**5. Carte interactive** (`/dashboard/map`) - 🚧 **À implémenter**
- Leaflet avec markers clusterisés
- Popup détail offre au clic
- Filtres contextuels

### Stack technique

**Core**
- Next.js 14 (App Router)
- React 18
- TypeScript 5

**Styling**
- TailwindCSS 3+
- Lucide React (icônes)

**Data fetching**
- Axios (HTTP client)
- Tanstack Query (cache + mutations) - à intégrer

**Visualisation**
- Recharts (graphiques) - à intégrer
- Leaflet (carte) - à intégrer

**State management**
- Zustand (state léger) - optionnel

## Déploiement local

### Option 1 : Docker Compose (recommandé)

```bash
# Tout démarrer (ES + Kibana + Backend + Frontend)
docker-compose up -d

# Accès :
# - Elasticsearch : http://localhost:9200
# - Kibana : http://localhost:5601
# - Backend API : http://localhost:8000 (docs: /docs)
# - Frontend : http://localhost:3000
```

### Option 2 : Développement manuel

**Terminal 1 : Elasticsearch**
```bash
docker-compose up elasticsearch kibana
```

**Terminal 2 : Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 : Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Backend

Fichier : `config/.env` (ou variables d'environnement Docker)

```env
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=job_offers
CORS_ORIGINS=http://localhost:3000
```

### Frontend

Fichier : `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Workflow de développement

### 1. Collecte de données (pipeline existant)

```bash
# Collecter des offres
python -m pipelines.ingest.sources.francetravail.main --keywords "data engineer" --split-by-contract

# Indexer dans Elasticsearch
python scripts/index_to_elasticsearch.py --source francetravail
```

### 2. Développement backend

```bash
cd backend
uvicorn app.main:app --reload
# Test : curl http://localhost:8000/api/v1/stats/overview
```

### 3. Développement frontend

```bash
cd frontend
npm run dev
# Accès : http://localhost:3000
```

## Tests

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm run test        # Tests unitaires (à configurer)
npm run test:e2e    # Tests E2E (à configurer)
```

## Roadmap d'implémentation

### Phase 1 : Fondations ✅ (Complété)
- [x] Structure backend FastAPI
- [x] Structure frontend Next.js
- [x] Configuration Docker Compose
- [x] API endpoints de base (stats, offers, analytics, filters)
- [x] Page landing + dashboard overview

### Phase 2 : Features Core 🚧 (En cours)
- [ ] Système de filtres complet (composants réutilisables)
- [ ] Page liste des offres avec pagination
- [ ] Graphiques interactifs (Recharts)
- [ ] Intégration React Query (cache)

### Phase 3 : Features Avancées 📅 (Planifié)
- [ ] Page analytics avancées
- [ ] Carte interactive Leaflet
- [ ] Export de données (CSV, PDF)
- [ ] Mode comparaison (2 mots-clés côte à côte)

### Phase 4 : Finition & Production 📅
- [ ] Mode sombre
- [ ] Responsive mobile
- [ ] Tests E2E
- [ ] Optimisations performances
- [ ] CI/CD GitHub Actions
- [ ] Déploiement VPS

## Exemples de développement

### Ajouter un nouveau endpoint API

**1. Créer la route dans `backend/app/api/v1/`**
```python
# backend/app/api/v1/custom.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom-stat")
async def get_custom_stat():
    return {"result": "data"}
```

**2. Enregistrer dans `main.py`**
```python
from app.api.v1 import custom
app.include_router(custom.router, prefix="/api/v1/custom", tags=["Custom"])
```

**3. Appeler depuis le frontend**
```typescript
// frontend/src/lib/api.ts
export const customApi = {
  getStat: async () => {
    const response = await apiClient.get('/custom/custom-stat');
    return response.data;
  }
};
```

### Créer un nouveau graphique

**1. Créer le composant**
```typescript
// frontend/src/components/charts/CustomChart.tsx
'use client'

import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export function CustomChart({ data }: { data: any[] }) {
  return (
    <BarChart width={600} height={300} data={data}>
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" fill="#0ea5e9" />
    </BarChart>
  );
}
```

**2. Utiliser dans une page**
```typescript
// frontend/src/app/dashboard/page.tsx
import { CustomChart } from '@/components/charts/CustomChart';

// Dans le composant
<CustomChart data={statsData} />
```

## Troubleshooting

### Erreur CORS

**Symptôme** : `Access-Control-Allow-Origin` error dans la console navigateur

**Solution** : Vérifier `backend/app/config.py`
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",  # Doit correspondre à l'URL frontend
]
```

### Backend ne se connecte pas à Elasticsearch

**Symptôme** : `ConnectionError: Connection to elasticsearch:9200 refused`

**Solution** :
1. Vérifier qu'Elasticsearch tourne : `curl http://localhost:9200`
2. Si Docker : utiliser le nom du service (`elasticsearch` pas `localhost`)
3. Si local : `ELASTICSEARCH_URL=http://localhost:9200`

### Frontend affiche "Impossible de charger les statistiques"

**Checklist** :
1. Backend tourne ? → `curl http://localhost:8000/health`
2. Elasticsearch tourne ? → `curl http://localhost:9200`
3. Données indexées ? → `curl http://localhost:9200/job_offers/_count`
4. CORS configuré ? → Vérifier dans Network DevTools

## Ressources

- **Backend** : [backend/README.md](../backend/README.md)
- **Frontend** : [frontend/README.md](../frontend/README.md)
- **API Docs** : http://localhost:8000/docs (Swagger interactif)
- **Elasticsearch** : [docs/elasticsearch.md](elasticsearch.md)

## Support

Pour toute question sur l'architecture du dashboard, se référer à ce document ou consulter le code dans `backend/` et `frontend/`.
