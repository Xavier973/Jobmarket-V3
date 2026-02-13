# Réorganisation du Projet - JobMarket V3

**Date :** 13 février 2026

## 🎯 Objectif

Organiser les fichiers du projet dans une structure logique et maintenable avec des dossiers dédiés pour les scripts d'analyse, de maintenance et les tests.

---

## 📁 Nouvelle Structure

### Avant
```
Jobmarket_V3/
├── analyze_data_analyst.py          # À la racine
├── examples_visualization.py        # À la racine
├── fix_line_endings.py              # À la racine
├── test_enriched_mapping.py         # À la racine
├── pipelines/
├── data/
├── docs/
└── config/
```

### Après
```
Jobmarket_V3/
├── scripts/                          # ✅ NOUVEAU
│   ├── README.md
│   ├── analysis/                     # Scripts d'analyse
│   │   ├── analyze_data_analyst.py
│   │   └── examples_visualization.py
│   └── maintenance/                  # Scripts de maintenance
│       └── fix_line_endings.py
│
├── tests/                            # ✅ NOUVEAU
│   ├── README.md
│   └── test_enriched_mapping.py
│
├── pipelines/
├── data/
├── docs/
└── config/
```

---

## 🔄 Fichiers Déplacés

### Scripts d'Analyse → `scripts/analysis/`
- ✅ `analyze_data_analyst.py`
  - Analyse statistique des offres Data Analyst collectées
  - Top titres, codes ROME, exemples de salaires
  
- ✅ `examples_visualization.py`
  - 5 exemples d'analyses : salaires, compétences, géographie, etc.
  - Démontre l'utilisation des champs enrichis

### Scripts de Maintenance → `scripts/maintenance/`
- ✅ `fix_line_endings.py`
  - Correction des caractères de fin de ligne inhabituels (LS/PS)
  - Nettoie les fichiers JSONL pour compatibilité Windows/VS Code

### Tests → `tests/`
- ✅ `test_enriched_mapping.py`
  - Validation du mapping enrichi
  - Analyse des taux de couverture (GPS, salaire, compétences)
  - Statistiques sur ROME, secteurs, départements

---

## 🛠️ Modifications Techniques

### 1. Gestion du PYTHONPATH

**Problème :** Scripts dans sous-dossiers ne peuvent plus importer depuis `pipelines/`

**Solution :** Ajout dynamique de la racine au sys.path

```python
import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

**Fichiers modifiés :**
- `tests/test_enriched_mapping.py`
- `scripts/analysis/examples_visualization.py`

---

### 2. Gestion de l'Encodage UTF-8 (Windows)

**Problème :** PowerShell ne gère pas bien les émojis (cp1252 par défaut)

**Solution :** Forcer l'encodage UTF-8 pour stdout/stderr

```python
import sys
import io

# Forcer l'encodage UTF-8 pour Windows PowerShell
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

**Fichiers modifiés :**
- `tests/test_enriched_mapping.py`
- `scripts/analysis/examples_visualization.py`

---

### 3. Correction du Bug d'Encodage JSONL

**Problème :** Caractères Line Separator (U+2028) dans les fichiers JSONL causant des erreurs VS Code

**Solution :** Ajout du paramètre `newline=""` dans `io.py`

```python
# Avant
with path.open("a", encoding="utf-8") as handle:

# Après
with path.open("a", encoding="utf-8", newline="") as handle:
```

**Fichier modifié :** `pipelines/ingest/io.py`

---

## 📚 Documentation Ajoutée

### `scripts/README.md`
- Description de chaque sous-dossier (`analysis/`, `maintenance/`)
- Guide d'utilisation des scripts
- Bonnes pratiques

### `tests/README.md`
- Description des tests existants
- Guide pour ajouter de nouveaux tests
- Recommandations pytest pour le futur

### Mise à jour `README.md` (racine)
- Nouvelle structure du projet avec arborescence visuelle
- Commandes pour l'analyse et la maintenance
- Exemples d'utilisation

---

## ✅ Validation

### Tests d'Exécution Réussis

```bash
# ✅ Script d'analyse
python scripts/analysis/analyze_data_analyst.py
→ 70/99 offres = Code ROME M1419 (Data analyst)

# ✅ Script de validation
python tests/test_enriched_mapping.py
→ 98% GPS coverage, 82% salary data

# ✅ Script de maintenance
python scripts/maintenance/fix_line_endings.py
→ 6 fichiers JSONL nettoyés (raw + normalized)
```

---

## 🎓 Bonnes Pratiques Établies

1. **Séparation des Responsabilités**
   - `scripts/analysis/` : Analyse et visualisation
   - `scripts/maintenance/` : Utilitaires de maintenance
   - `tests/` : Validation et tests

2. **Chemins Relatifs**
   - Tous les scripts utilisent des chemins relatifs depuis la racine
   - Exécution depuis `Jobmarket_V3/` : `python scripts/analysis/...`

3. **Documentation In-Code**
   - Docstrings en haut de chaque script
   - README dans chaque dossier important

4. **Portabilité Windows/Linux**
   - Gestion de l'encodage UTF-8
   - Fins de ligne standardisées (LF)
   - PYTHONPATH géré dynamiquement

---

## 🚀 Prochaines Étapes

### Court Terme
- [ ] Ajouter des tests unitaires avec pytest
- [ ] Créer un script `run_all_tests.py` pour exécuter tous les tests
- [ ] Ajouter un script de vérification de la qualité des données

### Moyen Terme
- [ ] Migrer vers pytest pour une meilleure structure de tests
- [ ] Ajouter des tests d'intégration du pipeline complet
- [ ] Créer un dossier `scripts/reporting/` pour les rapports automatisés

---

## 📊 Métriques de la Réorganisation

- **Fichiers déplacés :** 4
- **Dossiers créés :** 4 (`scripts/`, `scripts/analysis/`, `scripts/maintenance/`, `tests/`)
- **Documentation ajoutée :** 3 README
- **Bugs corrigés :** 2 (PYTHONPATH, encodage UTF-8)
- **Amélioration de lisibilité :** +++

---

**Status :** ✅ Réorganisation complète et validée
