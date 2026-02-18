# Guide Elasticsearch - JobMarket V3

## Vue d'ensemble

Elasticsearch est le moteur de stockage et d'analyse pour JobMarket V3. Il offre :
- **Recherche full-text** rapide et pertinente en français
- **Agrégations puissantes** pour l'analyse (salaires, compétences, tendances)
- **Filtrage multi-critères** (localisation, type de contrat, date, etc.)
- **Géolocalisation** pour la recherche par proximité
- **Kibana** intégré pour la visualisation

## Installation

### 1. Démarrer Elasticsearch et Kibana

```bash
# Démarrer les conteneurs
docker-compose up -d

# Vérifier que les services sont démarrés
docker-compose ps

# Voir les logs
docker-compose logs -f elasticsearch
docker-compose logs -f kibana
```

**URLs d'accès :**
- Elasticsearch : http://localhost:9200
- Kibana : http://localhost:5601

### 2. Installer les dépendances Python

```bash
# Dans votre environnement virtuel
pip install -r requirements.txt
```

## Configuration

Les variables d'environnement sont définies dans `config/.env` :

```env
ES_HOST=http://localhost:9200
ES_INDEX=jobmarket_v3
ES_BATCH_SIZE=500
```

## Indexation des données

### Indexer toutes les offres d'une source

```bash
# Indexer toutes les offres France Travail
python scripts/index_to_elasticsearch.py --source francetravail

# Forcer la recréation de l'index (supprime les données existantes)
python scripts/index_to_elasticsearch.py --source francetravail --force
```

### Indexer un fichier spécifique

```bash
# Indexer uniquement les offres "data engineer"
python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl
```

### Options avancées

```bash
# Personnaliser la taille des batches
python scripts/index_to_elasticsearch.py --source francetravail --batch-size 1000

# Utiliser un répertoire de données personnalisé
python scripts/index_to_elasticsearch.py --source francetravail --data-dir /chemin/vers/data
```

## Mapping de l'index

L'index `jobmarket_v3` utilise un mapping optimisé :

### Analyseur français
- **Tokenization** : découpage intelligent des mots
- **Elision** : gestion des apostrophes (l', d', qu', etc.)
- **Stop words** : exclusion des mots vides français
- **Stemming** : réduction des mots à leur racine (light_french)

### Champs principaux

| Champ | Type | Description |
|-------|------|-------------|
| `id` | keyword | Identifiant unique |
| `title` | text + keyword | Titre du poste (recherche + tri) |
| `description` | text | Description complète |
| `rome_code` | keyword | Code ROME |
| `location_city` | keyword | Ville |
| `location_region` | keyword | Région |
| `location_coordinates` | geo_point | Coordonnées GPS |
| `contract_type` | keyword | Type de contrat (CDI, CDD, etc.) |
| `salary_min` / `salary_max` | float | Fourchette salariale |
| `skills` | keyword | Compétences (format simple) |
| `skills_required` | nested | Compétences exigées (détaillées) |
| `published_at` | date | Date de publication |
| `experience_level` | keyword | Niveau d'expérience |

## Requêtes utiles

### Recherche simple

```python
from pipelines.storage.elasticsearch import ElasticsearchClient

es = ElasticsearchClient()

# Recherche full-text
query = {
    "query": {
        "match": {
            "title": "data engineer"
        }
    }
}

results = es.search(query)
```

### Filtrage par critères

```python
# Offres CDI à Paris avec salaire > 40k
query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"contract_type": "CDI"}},
                {"term": {"location_city": "Paris"}},
                {"range": {"salary_min": {"gte": 40000}}}
            ]
        }
    }
}

results = es.search(query, size=20)
```

### Agrégations

```python
# Top 10 des compétences les plus demandées
query = {
    "size": 0,
    "aggs": {
        "top_skills": {
            "terms": {
                "field": "skills",
                "size": 10
            }
        }
    }
}

results = es.search(query)
top_skills = results["aggregations"]["top_skills"]["buckets"]
```

### Recherche géographique

```python
# Offres dans un rayon de 50km autour de Paris
query = {
    "query": {
        "bool": {
            "filter": {
                "geo_distance": {
                    "distance": "50km",
                    "location_coordinates": {
                        "lat": 48.8566,
                        "lon": 2.3522
                    }
                }
            }
        }
    }
}

results = es.search(query)
```

## Kibana - Visualisation

### Accéder à Kibana

1. Ouvrir http://localhost:5601
2. Menu → **Analytics** → **Discover**
3. Créer un index pattern : `jobmarket_v3`

### Créer des visualisations

**Exemples de dashboards :**
- Répartition géographique des offres (carte)
- Évolution temporelle des publications (histogram)
- Top 10 des compétences (bar chart)
- Répartition par type de contrat (pie chart)
- Distribution des salaires (box plot)

### Requêtes KQL dans Kibana

```
# CDI à Paris
contract_type:"CDI" AND location_city:"Paris"

# Offres avec Python et salaire > 45k
skills:"Python" AND salary_min > 45000

# Publications récentes (derniers 7 jours)
published_at >= now-7d
```

## Maintenance

### Vérifier l'état du cluster

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### Statistiques de l'index

```bash
curl http://localhost:9200/jobmarket_v3/_stats?pretty
```

### Supprimer l'index

```bash
curl -X DELETE http://localhost:9200/jobmarket_v3
```

Ou via Python :
```python
from pipelines.storage.elasticsearch import ElasticsearchClient

es = ElasticsearchClient()
es.delete_index()
```

### Arrêter les services

```bash
# Arrêter sans supprimer les données
docker-compose stop

# Arrêter et supprimer les conteneurs (données préservées)
docker-compose down

# Arrêter et supprimer les données
docker-compose down -v
```

## Optimisations

### Taille des batches

Pour de gros volumes (>10k offres), augmentez la taille des batches :

```bash
python scripts/index_to_elasticsearch.py --batch-size 1000
```

### Mémoire Elasticsearch

Si vous avez des problèmes de performance, augmentez la mémoire dans `docker-compose.yml` :

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # au lieu de 512m
```

### Refresh interval

Pour accélérer l'indexation initiale, désactivez le refresh automatique :

```bash
curl -X PUT "http://localhost:9200/jobmarket_v3/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "-1"
  }
}'

# Réactiver après l'indexation
curl -X PUT "http://localhost:9200/jobmarket_v3/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "1s"
  }
}'
```

## Troubleshooting

### Elasticsearch ne démarre pas

```bash
# Vérifier les logs
docker-compose logs elasticsearch

# Problème de mémoire : augmenter la limite dans docker-compose.yml
# Problème de permissons : vérifier les droits sur le volume es_data
```

### Impossible de se connecter depuis Python

```python
# Vérifier la connectivité
import requests
response = requests.get("http://localhost:9200")
print(response.json())

# Vérifier les variables d'environnement
import os
print(os.getenv("ES_HOST"))
```

### Index non trouvé

```bash
# Lister les index existants
curl http://localhost:9200/_cat/indices?v
```

### Erreurs d'indexation

- **400 Bad Request** : problème de mapping (type de données incorrect)
- **429 Too Many Requests** : ralentir les requêtes
- **Connection timeout** : augmenter le timeout ou réduire la taille des batches

## Sécurité

⚠️ **Pour la production**, activez la sécurité Elasticsearch :

```yaml
environment:
  - xpack.security.enabled=true
  - ELASTIC_PASSWORD=votre_mot_de_passe
```

Et utilisez HTTPS + authentification.

## Ressources

- [Documentation Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/)
- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
