# Démarrage rapide - Elasticsearch

Guide pour démarrer rapidement avec Elasticsearch sur JobMarket V3.

## Étape 1 : Installation

### A. Installer Docker Desktop
Si ce n'est pas déjà fait, installez [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### B. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

## Étape 2 : Démarrer Elasticsearch

```bash
# Démarrer les conteneurs (Elasticsearch + Kibana)
docker-compose up -d

# Vérifier que les services sont démarrés
docker-compose ps

# Attendre ~30 secondes que les services soient prêts
```

**Vérification :**
- Elasticsearch : http://localhost:9200 (doit afficher un JSON)
- Kibana : http://localhost:5601 (doit afficher l'interface)

## Étape 3 : Indexer des données

### Option 1 : Indexer toutes les offres France Travail
```bash
python scripts/index_to_elasticsearch.py --source francetravail
```

### Option 2 : Indexer un fichier spécifique
```bash
python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl
```

**Résultat attendu :**
```
✓ Connecté à Elasticsearch sur http://localhost:9200
✓ Index 'jobmarket_v3' créé avec succès

📄 Traitement de offers_kw_data_engineer.jsonl...
   → 350 offres chargées
   ✓ 350 indexées, 0 erreurs

============================================================
📊 RÉSUMÉ DE L'INDEXATION
============================================================
Fichiers traités    : 1
Offres totales      : 350
Offres indexées     : 350
Erreurs             : 0
Taux de succès      : 100.0%
============================================================
```

## Étape 4 : Tester les requêtes

```bash
# Exécuter des exemples de requêtes
python scripts/query_elasticsearch.py
```

Cela affichera :
- Recherche full-text : "data engineer"
- Filtrage : CDI à Paris
- Salaires > 40 000 €
- Top 10 des compétences
- Répartition par type de contrat
- Top 10 des villes
- Statistiques salariales

## Étape 5 : Utiliser Kibana

1. Ouvrir http://localhost:5601
2. Menu → **Analytics** → **Discover**
3. Créer un index pattern :
   - Index pattern : `jobmarket_v3`
   - Time field : `published_at`
4. Explorer les données !

### Requêtes KQL utiles :
```
# CDI à Paris
contract_type:"CDI" AND location_city:"Paris"

# Python et salaire > 45k
skills:"Python" AND salary_min > 45000

# Offres récentes (7 derniers jours)
published_at >= now-7d
```

## Commandes utiles

### Docker
```bash
# Arrêter les services
docker-compose stop

# Redémarrer les services
docker-compose restart

# Voir les logs
docker-compose logs -f elasticsearch

# Supprimer tout (données comprises)
docker-compose down -v
```

### Elasticsearch
```bash
# Compter les documents
curl http://localhost:9200/jobmarket_v3/_count

# Voir la santé du cluster
curl http://localhost:9200/_cluster/health?pretty

# Supprimer l'index
curl -X DELETE http://localhost:9200/jobmarket_v3
```

## Troubleshooting

### Elasticsearch ne démarre pas
```bash
# Voir les logs
docker-compose logs elasticsearch

# Vérifier les ressources disponibles (RAM, disque)
docker stats
```

### Impossible de se connecter
```bash
# Vérifier que le service écoute
curl http://localhost:9200

# Vérifier que le conteneur tourne
docker ps

# Redémarrer le conteneur
docker-compose restart elasticsearch
```

### Erreur d'indexation
```bash
# Vérifier que l'index existe
curl http://localhost:9200/_cat/indices?v

# Recréer l'index
python scripts/index_to_elasticsearch.py --source francetravail --force
```

## Next steps

1. 📖 Lire la [documentation complète](elasticsearch.md)
2. 🎨 Créer des visualisations dans Kibana
3. 🔍 Tester des requêtes personnalisées
4. 📊 Analyser les tendances du marché

**Besoin d'aide ?** Consultez [docs/elasticsearch.md](elasticsearch.md)
