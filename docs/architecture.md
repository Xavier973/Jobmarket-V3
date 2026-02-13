# Architecture V3

## Vue d'ensemble
Le systeme est decoupe en quatre blocs independants :

1. Ingestion multi-sources via des adapters.
2. Normalisation dans un schema canonique commun.
3. Indexation dans le moteur d'analyse (Elasticsearch par defaut).
4. Exposition via une API pour la couche dashboard.

## Flux de donnees
1. Source API (ex: France Travail) -> recuperation brute.
2. Donnees brutes -> normalisation (schema JobOffer).
3. Donnees normalisees -> indexation et agregations.
4. API -> lecture pour dashboard et analyses.

## Principes
- Adapters par source pour isoler la collecte.
- Schema canonique pour faciliter l'ajout de nouvelles sources.
- API independante pour changer la couche UI sans toucher au pipeline.
- Indexation versionnee pour evoluer sans casser les requetes existantes.
