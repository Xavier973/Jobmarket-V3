# Scripts d'analyse dépréciés

Ce dossier contient les scripts créés lors de l'investigation du problème de pagination de l'API France Travail (15 février 2026).

## Contexte historique

**Problème initial** : L'API France Travail ne retournait que 150 offres maximum malgré la pagination avec `page=0`, `page=1`, etc.

**Solution finale** : Utilisation du paramètre `range` (format `"0-149"`, `"150-299"`, etc.) au lieu de `page`/`size`, permettant d'accéder jusqu'à 1150 offres par recherche.

## Scripts archivés

### test_api_pagination.py
**Objectif** : Tester si `page=1` retournait de nouvelles offres par rapport à `page=0`.

**Résultat** : Prouvé que `page=0` et `page=1` retournaient les 150 mêmes offres (100% de doublons). La pagination `page` ne fonctionnait pas.

**Status** : ✅ Obsolète - Remplacé par pagination `range`

---

### test_offres_partenaires.py
**Objectif** : Tester si le paramètre `offresPartenaires=true` (visible sur le site France Travail) permettait d'accéder aux offres partenaires (Indeed, Monster, LinkedIn).

**Résultat** : Le paramètre est accepté par l'API mais n'augmente pas le nombre de résultats. Les offres partenaires ne sont pas accessibles via l'API publique.

**Status** : ✅ Concluant - Les 1337 offres du site vs 353 de l'API s'expliquent par les offres partenaires inaccessibles

---

### explore_api_filters.py
**Objectif** : Analyser les métadonnées `filtresPossibles` de l'API pour découvrir des filtres supplémentaires permettant de subdiviser les recherches.

**Résultat** : Découverte du filtre `experience` avec codes 0-4, ayant permis de créer la stratégie multi-filtres (contrat × expérience = 30 combinaisons).

**Status** : ✅ Mission accomplie - Stratégie multi-filtres implémentée, mais devenue moins critique avec pagination `range`

## Documentation de référence

Voir [docs/api-range-parameter-discovery.md](../../../docs/api-range-parameter-discovery.md) pour le détail complet de l'investigation et de la solution.

## Pourquoi conserver ces scripts ?

Ces scripts constituent la **trace historique** du processus de résolution de problème :
1. Identification du symptôme (pagination cassée)
2. Tests systématiques des hypothèses
3. Découverte de la vraie cause (mauvais paramètre)
4. Recherche de la solution (repository tiers, documentation)

Ils peuvent servir de référence pour de futurs problèmes d'API similaires.
