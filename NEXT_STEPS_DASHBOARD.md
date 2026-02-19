# Prochaines étapes - Dashboard JobMarket V3

## ✅ Ce qui a été créé

### 1. Backend FastAPI (dans `backend/`)
- ✅ Structure complète avec API REST
- ✅ Endpoints pour offres, statistiques, analytics, filtres
- ✅ Intégration avec Elasticsearch
- ✅ Réutilisation des modules existants (`pipelines/storage/elasticsearch.py`)
- ✅ Documentation Swagger automatique
- ✅ Docker support

### 2. Frontend Next.js (dans `frontend/`)
- ✅ Structure Next.js 14 avec App Router
- ✅ Configuration TypeScript + TailwindCSS
- ✅ Client API (axios)
- ✅ Types TypeScript complets
- ✅ Landing page attractive
- ✅ Page dashboard avec KPIs de base
- ✅ Docker support

### 3. Infrastructure
- ✅ Docker Compose mis à jour (ES + Kibana + Backend + Frontend)
- ✅ `.gitignore` complété pour Node.js
- ✅ Documentation architecture détaillée
- ✅ README principal mis à jour

## 🚀 Pour démarrer maintenant

### Étape 1 : Installer les dépendances

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ..\frontend
npm install
```

### Étape 2 : Vérifier Elasticsearch

```powershell
# Si pas déjà lancé
docker-compose up -d elasticsearch kibana

# Vérifier
curl http://localhost:9200
```

### Étape 3 : Démarrer le backend

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Tester : http://localhost:8000/docs

### Étape 4 : Démarrer le frontend

```powershell
cd frontend
npm run dev
```

Accès : http://localhost:3000

## 🎯 Prochaines étapes de développement

### Phase 1 : Finaliser la page Dashboard (1-2 jours)

**Fichier** : `frontend/src/app/dashboard/page.tsx`

✅ **Déjà fait** :
- KPI cards (total offres, salaire moyen, % CDI, régions)
- Top 3 régions et compétences
- Distribution des contrats

🚧 **À ajouter** :
1. **Graphiques interactifs** (Recharts)
   ```typescript
   import { BarChart, LineChart, PieChart } from 'recharts';
   ```
   - Distribution salariale (histogramme)
   - Évolution temporelle (line chart)
   - Types de contrat (pie chart)

2. **Panneau de filtres latéral**
   - Composant `FilterPanel.tsx`
   - Sélection multiple (régions, contrats, etc.)
   - Range slider salaire
   - Appliquer les filtres aux graphiques

### Phase 2 : Page Liste des offres (2-3 jours)

**Créer** : `frontend/src/app/dashboard/offers/page.tsx`

Fonctionnalités :
- Table avec pagination (20 offres par page)
- Tri par colonne (salaire, date, région)
- Filtres en colonnes
- Modal de détail au clic
- Export CSV (bouton export)

Composants à créer :
- `components/OffersTable.tsx`
- `components/OfferDetailModal.tsx`
- `components/Pagination.tsx`

### Phase 3 : Page Analytics (3-4 jours)

**Créer** : `frontend/src/app/dashboard/analytics/page.tsx`

Sections à onglets :
1. **Analyse salariale**
   - Salaire par expérience (box plot)
   - Salaire par région (carte choroplèthe)
   - Distribution (violin plot)

2. **Compétences**
   - Top 20 (bar chart horizontal)
   - Co-occurrence (heatmap)
   - Évolution temporelle (multi-line)

3. **Géographie**
   - Concentration par région (treemap)
   - Top villes (bar chart)

4. **Tendances**
   - Publications par semaine (area chart)
   - Saisonnalité (calendar heatmap)

### Phase 4 : Carte interactive (2-3 jours)

**Créer** : `frontend/src/app/dashboard/map/page.tsx`

Utiliser Leaflet :
```typescript
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
```

Fonctionnalités :
- Markers clusterisés (MarkerClusterGroup)
- Popup détail offre au clic
- Filtres contextuels (même que dashboard)
- Légende par type de contrat

### Phase 5 : Optimisations (1-2 jours)

1. **React Query** (cache + invalidation)
   ```typescript
   import { useQuery, useMutation } from '@tanstack/react-query';
   ```

2. **Mode sombre**
   - Toggle dans Header
   - Classes Tailwind dark:

3. **Responsive mobile**
   - Breakpoints Tailwind
   - Menu hamburger mobile

4. **Tests**
   - Jest + React Testing Library
   - Tests E2E avec Playwright

## 📚 Ressources utiles

### Documentation créée
- [docs/dashboard-architecture.md](docs/dashboard-architecture.md) - Architecture complète
- [backend/README.md](backend/README.md) - Guide backend
- [frontend/README.md](frontend/README.md) - Guide frontend
- [docs/dashboard-eval.md](docs/dashboard-eval.md) - Choix technologiques

### API Endpoints
Swagger interactif : http://localhost:8000/docs

Endpoints principaux :
- `GET /api/v1/stats/overview` - KPIs
- `GET /api/v1/offers?page=1&size=20` - Liste offres
- `GET /api/v1/analytics/salary?group_by=experience_level` - Stats salaires
- `GET /api/v1/analytics/skills?top=20` - Top compétences
- `GET /api/v1/filters/regions` - Liste régions

### Bibliothèques à explorer

**Recharts** (graphiques)
```bash
npm install recharts
```
Docs : https://recharts.org/

**Leaflet** (carte)
```bash
npm install leaflet react-leaflet
npm install -D @types/leaflet
```
Docs : https://react-leaflet.js.org/

**React Query** (data fetching)
```bash
npm install @tanstack/react-query
```
Docs : https://tanstack.com/query/latest

**shadcn/ui** (composants UI)
```bash
npx shadcn-ui@latest init
```
Docs : https://ui.shadcn.com/

## 🐛 Dépannage rapide

### Backend ne démarre pas
```powershell
# Vérifier que le virtualenv est activé
.venv\Scripts\Activate.ps1

# Réinstaller les dépendances
pip install -r backend/requirements.txt
```

### Frontend ne démarre pas
```powershell
# Supprimer node_modules et réinstaller
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### Erreur CORS
Vérifier dans `backend/app/config.py` :
```python
CORS_ORIGINS = ["http://localhost:3000"]
```

### Pas de données dans le dashboard
```powershell
# 1. Vérifier ES
curl http://localhost:9200/job_offers/_count

# 2. Réindexer si nécessaire
python scripts/index_to_elasticsearch.py --source francetravail --force
```

## 💡 Conseils de développement

1. **Développer page par page** : Ne pas tout faire en même temps
2. **Tester régulièrement** : Vérifier dans le navigateur après chaque modif
3. **Utiliser les DevTools** : Network tab pour déboguer les appels API
4. **Commiter souvent** : Petits commits atomiques
5. **Documentation API** : Swagger est votre ami (http://localhost:8000/docs)

## 🎨 Design inspiration

Pour le design des graphiques et de l'interface :
- Kibana (http://localhost:5601) - Dashboard Elastic
- Tableau Public - Dashboards data
- Observable - Visualisations interactives
- Recharts Examples - Exemples de graphiques

## ✅ Checklist avant de continuer

- [ ] Backend démarre sans erreur (port 8000)
- [ ] Frontend démarre sans erreur (port 3000)
- [ ] Page dashboard affiche les KPIs
- [ ] Pas d'erreurs dans la console navigateur
- [ ] API endpoint `/api/v1/stats/overview` retourne des données
- [ ] Elasticsearch contient des offres (`curl http://localhost:9200/job_offers/_count`)

---

**Prêt à développer !** 🚀

Commencez par l'une des phases ci-dessus selon vos priorités.

Pour toute question, référez-vous à la documentation dans `docs/dashboard-architecture.md`.
