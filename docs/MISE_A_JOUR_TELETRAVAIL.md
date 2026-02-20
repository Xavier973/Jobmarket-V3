# Guide de mise à jour - Détection du télétravail

## Modifications effectuées

✅ **Ajout du champ `is_remote`** au modèle canonique JobOffer
✅ **Fonction de détection automatique** basée sur des patterns regex
✅ **Intégration dans le pipeline** de normalisation France Travail
✅ **Mapping Elasticsearch** mis à jour
✅ **Scripts de test et d'exemples** créés
✅ **Documentation complète** ajoutée

## Pour utiliser la nouvelle fonctionnalité

### 1. Nouvelles collectes (recommandé)

Les nouvelles offres collectées incluront automatiquement le champ `is_remote` :

```bash
# Collecter de nouvelles offres
python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --split-by-contract

# Indexer dans Elasticsearch
python scripts/index_to_elasticsearch.py --source francetravail
```

### 2. Mettre à jour les données existantes

Si vous voulez ajouter `is_remote` aux offres déjà collectées :

#### Option A : Régénérer les données normalisées

```bash
# Régénère les fichiers normalized/*.jsonl à partir des fichiers raw/*.jsonl
python scripts/maintenance/regenerate_normalized.py
```

#### Option B : Réindexer dans Elasticsearch avec force

```bash
# Supprime et recrée l'index avec les nouvelles données
python scripts/index_to_elasticsearch.py --source francetravail --force
```

**⚠️ Attention :** `--force` supprime l'index existant et toutes ses données !

### 3. Tester la détection

```bash
# Analyser les offres pour voir combien mentionnent le télétravail
python scripts/analysis/test_remote_detection.py
```

**Résultats attendus :**
- Environ 26.8% des offres détectées avec télétravail
- Patterns les plus fréquents : "télétravail", "hybrid", "remote"

### 4. Requêter les offres avec télétravail

```bash
# Exemples de requêtes Elasticsearch
python scripts/query_remote_offers.py
```

## Fichiers modifiés

### Code
- `pipelines/ingest/models.py` - Modèle canonique JobOffer
- `pipelines/ingest/sources/francetravail/mapping.py` - Fonction de détection + intégration
- `pipelines/storage/elasticsearch.py` - Mapping Elasticsearch

### Scripts
- `scripts/analysis/test_remote_detection.py` - Test de détection
- `scripts/query_remote_offers.py` - Exemples de requêtes

### Documentation
- `docs/teletravail-detection.md` - Documentation complète
- `README.md` - Mise à jour avec nouvelle fonctionnalité

## Exemples d'utilisation

### API Elasticsearch directe

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Filtrer les offres avec télétravail
query = {
    "query": {
        "term": {"is_remote": True}
    }
}

response = es.search(index="jobmarket_v3", body=query)
print(f"{response['hits']['total']['value']} offres avec télétravail")
```

### API Backend FastAPI (à implémenter)

```bash
# Récupérer les offres avec télétravail
curl "http://localhost:8000/api/v1/offers?is_remote=true"

# Combiner avec d'autres filtres
curl "http://localhost:8000/api/v1/offers?is_remote=true&contract_type=CDI&location_city=Paris"
```

### Dashboard Frontend (à implémenter)

```tsx
// Ajouter un filtre dans l'interface
<Switch
  label="Télétravail uniquement"
  checked={filters.isRemote}
  onChange={(checked) => setFilters({...filters, isRemote: checked})}
/>

// Afficher un badge
{offer.is_remote && (
  <Badge variant="success">
    <HomeIcon /> Télétravail
  </Badge>
)}
```

## Vérifications

Avant de déployer en production :

- [ ] Tester la détection sur un échantillon d'offres
- [ ] Vérifier que l'index Elasticsearch contient le champ `is_remote`
- [ ] Valider que les nouvelles collectes incluent `is_remote`
- [ ] Mettre à jour l'API backend pour filtrer par `is_remote`
- [ ] Mettre à jour le frontend pour afficher et filtrer par `is_remote`

## Troubleshooting

### Le champ `is_remote` n'apparaît pas dans Elasticsearch

**Cause :** L'index a été créé avant l'ajout du mapping.

**Solution :**
```bash
python scripts/index_to_elasticsearch.py --source francetravail --force
```

### Les anciennes offres n'ont pas `is_remote`

**Cause :** Les fichiers normalized ont été créés avant l'implémentation.

**Solution :**
```bash
python scripts/maintenance/regenerate_normalized.py
python scripts/index_to_elasticsearch.py --source francetravail --force
```

### La détection ne fonctionne pas bien

**Cause :** Patterns regex incomplets ou variations linguistiques.

**Solution :** 
1. Analyser les faux négatifs avec `test_remote_detection.py`
2. Ajouter de nouveaux patterns dans `_detect_remote_work()`
3. Régénérer les données normalisées

## Support

Pour toute question :
1. Consulter [docs/teletravail-detection.md](../docs/teletravail-detection.md)
2. Tester avec les scripts fournis
3. Vérifier les logs de normalisation

## Prochaines étapes

### Améliorations futures

1. **Extraction du niveau de télétravail**
   - Ajouter `remote_days_per_week: int` (0-5)
   - Classifier en "full", "hybrid", "occasionnel"

2. **Machine Learning**
   - Entraîner un modèle de classification
   - Détecter les offres non explicites

3. **API Backend**
   - Ajouter le filtre `is_remote` dans les endpoints
   - Créer des agrégations par type de télétravail

4. **Dashboard Frontend**
   - Ajouter un toggle "Télétravail uniquement"
   - Afficher des badges/icônes pour les offres remote
   - Graphiques : évolution du télétravail par région/métier

## Date de mise à jour

**19 février 2026** - Implémentation initiale de la détection du télétravail
