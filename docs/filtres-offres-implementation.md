# Implémentation des filtres sur la page des offres

**Date** : 20 février 2026  
**Fonctionnalité** : Ajout de 3 nouveaux filtres sur `/dashboard/offers`

## Résumé

Ajout de filtres interactifs permettant de filtrer les offres d'emploi par :
- **Métier ROME** (`rome_label`) : Ex: "Études et développement informatique"
- **Département** (`location_department`) : Ex: "75", "69", etc.
- **Type de télétravail** (`remote_type`) : "full_remote", "hybrid", "occasional"

## Architecture des changements

### 📁 Backend - API Endpoints

#### 1. Nouveaux endpoints de filtres (`backend/app/api/v1/filters.py`)

```python
@router.get("/rome-labels")
async def get_rome_labels() -> List[str]:
    """Liste des métiers ROME disponibles (utilise rome_label.keyword)"""

@router.get("/remote-types")
async def get_remote_types() -> List[str]:
    """Liste des types de télétravail disponibles"""
```

#### 2. Mise à jour du modèle de filtres (`backend/app/models/filters.py`)

Ajout dans `FilterRequest` :
```python
rome_labels: Optional[List[str]] = Field(None, description="Métiers ROME")
```

#### 3. Mise à jour du service Elasticsearch (`backend/app/services/elasticsearch.py`)

Ajout dans `_build_query()` :
```python
if filters.rome_labels:
    must_clauses.append({"terms": {"rome_label.keyword": filters.rome_labels}})
```

Utilise le champ **`rome_label.keyword`** (multi-field créé précédemment) pour des agrégations et filtres performants.

#### 4. Mise à jour de la route des offres (`backend/app/api/v1/offers.py`)

Ajout de paramètres dans `list_offers()` :
```python
rome_labels: Optional[str] = Query(None, description="Métiers ROME (séparés par virgule)")
remote_types: Optional[str] = Query(None, description="Types de télétravail (séparés par virgule)")
```

### 📁 Frontend - Interface utilisateur

#### 1. Types TypeScript (`frontend/src/types/filters.ts`)

Ajout dans `FilterRequest` :
```typescript
rome_labels?: string[];
remote_types?: string[];
is_remote?: boolean;
```

#### 2. Client API (`frontend/src/lib/api.ts`)

Nouveaux endpoints dans `filtersApi` :
```typescript
romeLabels: async (): Promise<string[]>
remoteTypes: async (): Promise<string[]>
```

Ajout de paramètres dans `offersApi.list()` :
```typescript
rome_labels?: string;
remote_types?: string;
```

#### 3. Page des offres (`frontend/src/app/dashboard/offers/page.tsx`)

**Nouvelles fonctionnalités** :
- 3 dropdowns (select) pour les filtres
- Chargement automatique des options depuis l'API au montage du composant
- Rechargement des offres lors du changement de filtre
- Bouton "Réinitialiser" pour effacer tous les filtres
- Affichage "Aucune offre ne correspond" si liste vide
- Labels traduits pour `remote_type` :
  - `full_remote` → "100% Télétravail"
  - `hybrid` → "Hybride"
  - `occasional` → "Occasionnel"

**États React** :
```typescript
const [selectedRomeLabel, setSelectedRomeLabel] = useState<string>('');
const [selectedDepartment, setSelectedDepartment] = useState<string>('');
const [selectedRemoteType, setSelectedRemoteType] = useState<string>('');

const [romeLabels, setRomeLabels] = useState<string[]>([]);
const [departments, setDepartments] = useState<string[]>([]);
const [remoteTypes, setRemoteTypes] = useState<string[]>([]);
```

**Flux de données** :
1. `loadFilterOptions()` → Charge les valeurs possibles (appelé au montage)
2. `fetchOffers()` → Charge les offres avec filtres actifs (appelé à chaque changement)
3. `handleResetFilters()` → Réinitialise tous les états

## Mapping Elasticsearch utilisé

Ces filtres exploitent le **mapping enrichi** créé précédemment :

```json
{
  "rome_label": {
    "type": "text",
    "analyzer": "french_analyzer",
    "fields": {
      "keyword": {"type": "keyword"}  // ← Utilisé pour filtres
    }
  },
  "location_department": {"type": "keyword"},
  "remote_type": {"type": "keyword"}
}
```

### Avantages du multi-field `rome_label.keyword`

- **Agrégations performantes** : Compte exact des métiers sans tokenisation
- **Filtres exacts** : Match parfait "Études et développement informatique"
- **Tri efficace** : Ordre alphabétique correct
- **Compatibilité** : Garde la recherche full-text sur `rome_label`

## Exemples d'utilisation

### 1. Requête API avec filtres

```bash
GET /api/v1/offers?rome_labels=Études%20et%20développement%20informatique&departments=75&remote_types=hybrid&page=1&size=20
```

### 2. Requête Elasticsearch générée

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "terms": {
            "rome_label.keyword": ["Études et développement informatique"]
          }
        },
        {
          "terms": {
            "location_department": ["75"]
          }
        },
        {
          "terms": {
            "remote_type": ["hybrid"]
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 20,
  "sort": [{"published_at": {"order": "desc"}}]
}
```

### 3. Interface frontend

**Avant filtrage** : 1 565 offres  
**Après filtrage** (Data Engineer + Paris + Hybride) : ~25 offres

## Tests effectués

### ✅ Backend

```bash
# Imports Python OK
python -c "from app.api.v1 import filters, offers; print('OK')"
```

### ✅ Frontend

```bash
# Type-check TypeScript OK
npm run type-check
```

### ✅ Elasticsearch

```bash
# Index avec nouveau mapping OK
python scripts/index_to_elasticsearch.py --source francetravail --force
# → 1 565 offres indexées, 100% succès
```

## Prochaines étapes possibles

### 🔧 Améliorations UX

1. **Compteur de résultats** par filtre
   - Afficher "(25)" à côté de chaque option
   - Endpoint : `GET /filters/rome-labels?with_count=true`

2. **Filtres multiples**
   - Permettre sélection de plusieurs métiers/départements
   - Remplacer `<select>` par composants multi-select

3. **Recherche textuelle** dans les filtres
   - Input avec autocomplete pour métiers
   - Utile avec 100+ métiers possibles

4. **Sauvegarde des filtres**
   - URL params : `/offers?rome_label=...&dept=...`
   - LocalStorage pour préférences utilisateur

### 🚀 Filtres additionnels

5. **Compétences** (`skills`)
6. **Type de contrat** (`contract_type`)
7. **Fourchette salariale** (sliders min/max)
8. **Niveau d'expérience** (`experience_level`)
9. **Taille d'entreprise** (`company_size`)

### 📊 Analytics

10. **Statistiques des filtres**
    - Quels filtres sont les plus utilisés ?
    - Combinaisons de filtres populaires

## Fichiers modifiés

### Backend (5 fichiers)

```
backend/app/api/v1/filters.py           # +42 lignes (2 endpoints)
backend/app/api/v1/offers.py            # +4 lignes (2 paramètres)
backend/app/models/filters.py           # +1 ligne (rome_labels)
backend/app/services/elasticsearch.py   # +3 lignes (filtre rome_labels)
pipelines/storage/elasticsearch.py      # Modifié précédemment (multi-field)
```

### Frontend (3 fichiers)

```
frontend/src/types/filters.ts           # +3 lignes (nouveaux champs)
frontend/src/lib/api.ts                 # +12 lignes (2 endpoints, 2 params)
frontend/src/app/dashboard/offers/page.tsx  # +150 lignes (filtres UI)
```

## Commandes de déploiement

### Backend

```bash
# Si changements backend uniquement
docker-compose up -d --build backend
```

### Frontend

```bash
# Si changements frontend uniquement
docker-compose up -d --build frontend
```

### Complet

```bash
# Rebuild complet avec nouveau mapping
docker-compose down
docker-compose up -d --build

# Ré-indexer si mapping Elasticsearch modifié
python scripts/index_to_elasticsearch.py --source francetravail --force
```

## Notes de compatibilité

- **Elasticsearch 8.x** : Supporte multi-field nativement
- **Next.js 14** : App Router avec 'use client'
- **React 18** : Hooks (useState, useEffect)
- **FastAPI** : Query params avec `Optional[str]`
- **Python 3.9+** : Type hints avec `List[str]`

## Références

- [Elasticsearch Multi-fields](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-fields.html)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [React Hooks](https://react.dev/reference/react)
- [Next.js App Router](https://nextjs.org/docs/app)
