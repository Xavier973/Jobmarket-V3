# Scripts de maintenance

Scripts utilitaires pour maintenance et optimisation des données du projet JobMarket.

## Scripts disponibles

### fix_line_endings.py

Nettoie les caractères de fin de ligne problématiques dans les fichiers JSONL.

**Problème résolu :** Les fichiers JSONL générés sur Windows peuvent contenir des caractères Line Separator (U+2028) et Paragraph Separator (U+2029) qui causent des avertissements dans VS Code.

**Usage :**
```bash
python scripts/maintenance/fix_line_endings.py
```

**Effet :** 
- Parcourt tous les fichiers `.jsonl` dans `data/raw/` et `data/normalized/`
- Remplace U+2028 et U+2029 par des espaces
- Affiche un rapport des fichiers nettoyés

---

### regenerate_normalized.py

Régénère les fichiers normalisés à partir des fichiers raw, sans stocker le champ `raw` pour éliminer la duplication.

**Problème résolu :** Les anciens fichiers normalisés contenaient un champ `raw` avec la réponse complète de l'API, dupliquant ainsi les données déjà présentes dans `data/raw/`. Cette duplication pouvait doubler la taille du stockage.

**Usage :**
```bash
python scripts/maintenance/regenerate_normalized.py
```

**Effet :**
- Lit tous les fichiers `data/raw/francetravail/*.jsonl`
- Normalise chaque offre via `normalize_offer()` 
- Sauvegarde dans `data/normalized/francetravail/` avec `raw=null`
- Affiche les statistiques de traitement

**Optimisation :**
- **Avant :** `data/raw/` (400 Ko) + `data/normalized/` avec champ raw (800 Ko) = 1.2 Mo total
- **Après :** `data/raw/` (400 Ko) + `data/normalized/` optimisé (400 Ko) = 800 Ko total
- **Gain :** ~33% de réduction de stockage

**Note :** Le champ `raw` reste disponible en option dans `map_france_travail(include_raw=True)` si nécessaire pour le débogage.

---

## Bonnes pratiques

- **Avant collecte massive :** Exécuter `fix_line_endings.py` si encodage problématique
- **Après modification du mapping :** Exécuter `regenerate_normalized.py` pour appliquer les changements
- **Avant indexation Elasticsearch :** Utiliser les fichiers normalisés optimisés (sans raw)
- **Pour audit/debug :** Les fichiers `data/raw/` conservent toujours les réponses complètes de l'API
