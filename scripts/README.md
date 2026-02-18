# Scripts

Ce dossier contient les scripts utilitaires du projet JobMarket V3.

## Structure

### � Elasticsearch
Scripts pour l'indexation et l'interrogation des données.

**Fichiers :**
- `index_to_elasticsearch.py` : Indexation des offres dans Elasticsearch
- `query_elasticsearch.py` : Exemples de requêtes et analyses avec Elasticsearch

**Utilisation :**
```bash
# Indexer toutes les offres France Travail
python scripts/index_to_elasticsearch.py --source francetravail

# Indexer un fichier spécifique
python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl

# Forcer la recréation de l'index
python scripts/index_to_elasticsearch.py --source francetravail --force

# Exécuter des exemples de requêtes
python scripts/query_elasticsearch.py
```

---

### �📊 `analysis/`
Scripts d'analyse et de visualisation des données collectées.

**Fichiers :**
- `analyze_data_analyst.py` : Analyse statistique des offres Data Analyst
- `examples_visualization.py` : Exemples d'analyses (salaires, compétences, géographie, etc.)

**Utilisation :**
```bash
# Analyser les offres Data Analyst collectées
python scripts/analysis/analyze_data_analyst.py

# Exécuter les exemples d'analyses
python scripts/analysis/examples_visualization.py
```

---

### 🔧 `maintenance/`
Scripts de maintenance et correction des données.

**Fichiers :**
- `fix_line_endings.py` : Correction des caractères de fin de ligne inhabituels dans les fichiers JSONL

**Utilisation :**
```bash
# Corriger les fins de ligne des fichiers JSONL
python scripts/maintenance/fix_line_endings.py
```

---

## Bonnes pratiques

1. **Nommage** : Utilisez des noms descriptifs avec des underscores (snake_case)
2. **Documentation** : Ajoutez un docstring en haut de chaque script
3. **Dépendances** : Listez les imports au début du fichier
4. **Exécution** : Les scripts doivent être exécutables depuis la racine du projet
5. **Logs** : Utilisez des prints clairs avec des émojis pour la lisibilité

---

## Ajouter un nouveau script

1. Placez-le dans le sous-dossier approprié (`analysis/` ou `maintenance/`)
2. Ajoutez un docstring descriptif
3. Testez l'exécution depuis la racine : `python scripts/<category>/<script>.py`
4. Mettez à jour ce README si le script est important
