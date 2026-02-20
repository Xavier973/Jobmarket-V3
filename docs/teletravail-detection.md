# Détection du Télétravail

## Vue d'ensemble

Le champ `is_remote` a été ajouté au modèle canonique `JobOffer` pour identifier automatiquement les offres d'emploi mentionnant le télétravail dans leur description.

## Fonctionnement

### Détection automatique

La fonction `_detect_remote_work()` analyse la description de chaque offre pour détecter les mentions du télétravail via des patterns regex :

**Patterns détectés :**
- `télétravail` / `teletravail` (avec ou sans accent)
- `remote` (incluant "full remote", "hybrid remote")
- `travail à distance` / `travail a distance`
- `home office`
- `hybrid` / `hybride`
- `X jours de télétravail` (ex: "2 jours de télétravail")
- `possibilité de télétravail`

### Implémentation

**Fichiers modifiés :**

1. **`pipelines/ingest/models.py`**
   - Ajout du champ `is_remote: Optional[bool]` dans la dataclass `JobOffer`

2. **`pipelines/ingest/sources/francetravail/mapping.py`**
   - Fonction `_detect_remote_work(description: str) -> bool`
   - Intégration dans `map_france_travail()` pour définir automatiquement `is_remote`

3. **`pipelines/storage/elasticsearch.py`**
   - Ajout du mapping `"is_remote": {"type": "boolean"}` dans l'index Elasticsearch

## Statistiques (Février 2026)

Sur **2096 offres** analysées dans le secteur data :
- **561 offres (26.8%)** mentionnent le télétravail
- **1535 offres (73.2%)** ne le mentionnent pas

**Répartition par pattern détecté :**
- `télétravail` : 456 offres (81.3%)
- `hybrid` / `hybride` : 162 offres (28.9%)
- `remote` : 14 offres (2.5%)
- `home office` : 5 offres (0.9%)
- `travail à distance` : 1 offre (0.2%)

*Note : Certaines offres peuvent contenir plusieurs patterns*

## Utilisation

### 1. Collecte et normalisation

Le champ `is_remote` est automatiquement renseigné lors de la normalisation des offres :

```bash
# Collecter des offres
python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --split-by-contract

# Les offres normalisées contiennent automatiquement is_remote
```

### 2. Tester la détection

```bash
# Analyser les offres existantes
python scripts/analysis/test_remote_detection.py
```

### 3. Requêtes Elasticsearch

#### Filtrer les offres avec télétravail

```python
query = {
    "query": {
        "term": {"is_remote": True}
    }
}
```

#### Compter les offres par type

```python
query = {
    "size": 0,
    "aggs": {
        "by_remote": {
            "terms": {"field": "is_remote"}
        }
    }
}
```

#### Combiner avec d'autres filtres

```python
# Data Analyst + Télétravail + Paris
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"title": "data analyst"}},
                {"term": {"is_remote": True}},
                {"match": {"location_city": "Paris"}}
            ]
        }
    }
}
```

### 4. Exemples de requêtes

Utilisez le script fourni pour tester différents cas d'usage :

```bash
# Exécuter les exemples de requêtes
python scripts/query_remote_offers.py
```

**Exemples inclus :**
1. Filtrer uniquement les offres avec télétravail
2. Compter les offres par type (remote vs présentiel)
3. Top 10 des villes avec le plus d'offres remote
4. Offres remote avec salaires élevés (> 50K€)
5. Data Analyst en télétravail

## API Backend

Le champ `is_remote` est disponible via l'API FastAPI :

### Filtrer par télétravail

```bash
# Récupérer les offres avec télétravail
curl "http://localhost:8000/api/v1/offers?is_remote=true"

# Combiner avec d'autres filtres
curl "http://localhost:8000/api/v1/offers?is_remote=true&contract_type=CDI&location_city=Paris"
```

### Statistiques télétravail

```bash
# Obtenir la répartition télétravail vs présentiel
curl "http://localhost:8000/api/v1/stats/overview"
```

## Dashboard Frontend

### Affichage

Le champ `is_remote` peut être affiché avec un badge ou une icône :

```tsx
// Exemple React
{offer.is_remote && (
  <Badge variant="success">
    <Icon name="home" /> Télétravail
  </Badge>
)}
```

### Filtres

Ajouter un filtre "Télétravail" dans l'interface de recherche :

```tsx
// Exemple de filtre
<Switch
  label="Télétravail uniquement"
  checked={filters.isRemote}
  onChange={(checked) => setFilters({...filters, isRemote: checked})}
/>
```

## Réindexation

Pour appliquer la détection aux offres déjà collectées :

### Option 1 : Régénérer les données normalisées

```bash
# Régénérer toutes les données normalisées avec is_remote
python scripts/maintenance/regenerate_normalized.py
```

### Option 2 : Réindexer dans Elasticsearch

```bash
# Forcer la recréation de l'index avec le nouveau mapping
python scripts/index_to_elasticsearch.py --source francetravail --force
```

## Limitations

### Détection basée sur les descriptions

La détection se base uniquement sur le **texte de la description**. Elle ne peut pas détecter :
- Les offres où le télétravail n'est pas mentionné dans la description
- Les variations linguistiques très éloignées (ex: "possibilité de travailler depuis chez soi")

**Taux de rappel estimé :** ~85-90% (certaines offres peuvent mentionner le télétravail de manière non détectable)

### Pas de distinction du niveau de télétravail

Le champ `is_remote` est binaire (True/False). Il ne distingue pas :
- Full remote (100% télétravail)
- Hybrid (ex: 2-3 jours/semaine)
- Occasionnel

Pour cette information, il faut analyser la description complète.

## Évolutions futures

### 1. Extraction du niveau de télétravail

Ajouter un champ `remote_days_per_week` pour capturer "2 jours de télétravail" :

```python
remote_days_per_week: Optional[int] = None  # 0=présentiel, 5=full remote
remote_type: Optional[str] = None  # "full", "hybrid", "occasionnel"
```

### 2. Machine Learning

Entraîner un modèle de classification pour améliorer la détection :
- Détecter les offres non explicites
- Classifier le type de télétravail (full/hybrid)
- Prédire la probabilité de télétravail non mentionné

### 3. Autres sources

Adapter la détection pour d'autres sources (APEC, LinkedIn, Indeed) :
- Chaque source peut avoir sa propre terminologie
- Ajuster les patterns regex par source

## Support

Pour toute question ou problème :
1. Vérifier les logs de normalisation
2. Tester avec `scripts/analysis/test_remote_detection.py`
3. Consulter les fichiers modifiés mentionnés ci-dessus

## Références

- **Modèle canonique** : [pipelines/ingest/models.py](../pipelines/ingest/models.py)
- **Fonction de détection** : [pipelines/ingest/sources/francetravail/mapping.py](../pipelines/ingest/sources/francetravail/mapping.py)
- **Mapping Elasticsearch** : [pipelines/storage/elasticsearch.py](../pipelines/storage/elasticsearch.py)
- **Script de test** : [scripts/analysis/test_remote_detection.py](../scripts/analysis/test_remote_detection.py)
- **Exemples de requêtes** : [scripts/query_remote_offers.py](../scripts/query_remote_offers.py)
