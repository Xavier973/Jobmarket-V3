# JobMarket — Data Job Market Analytics (V3)

## Aperçu
JobMarket V3 repart sur une architecture modulaire pour analyser le marche de l'emploi data en France. La collecte d'offres se fait via l'API France Travail, puis les donnees sont normalisees dans un schema commun pour faciliter l'ajout d'autres sources (APEC, Welcome to the Jungle, Indeed, LinkedIn).

## Objectifs
- Remplacer le scraping par l'API France Travail.
- Decoupler l'ingestion, le stockage et la visualisation.
- Garder un schema canonique pour accueillir plusieurs sources.
- Choisir une nouvelle solution de dashboard (etude en cours).

## Architecture cible
- **Ingestion** : pipeline multi-sources (adapters par source) -> donnees brutes -> normalisees.
- **Stockage** : moteur d'analyse (Elasticsearch par defaut) et indexation optimisee.
- **API** : service de lecture pour exposer les donnees au dashboard.
- **Dashboard** : front-end a definir, connecte a l'API.

## Stack technique (base)
- Python 3.9+
- Elasticsearch 8.x (par defaut)
- Docker + Docker Compose

## Structure du projet (V3)
- pipelines/ingest/ : pipeline d'ingestion et normalisation.
- pipelines/ingest/sources/ : adapters par source.
- storage/elasticsearch/ : index templates et helpers.
- services/api/ : service d'API pour le dashboard.
- apps/ : application de dashboard (a definir).
- config/ : configuration et exemples d'environnement.
- docs/ : documentation d'architecture, schema, operations.
- data/ : donnees brutes et normalisees.

## Configuration
Exemple d'environnement : [config/.env.example](config/.env.example)

Variables principales :
- FT_API_BASE_URL=
- FT_API_TOKEN_URL=
- FT_API_CLIENT_ID=
- FT_API_CLIENT_SECRET=
- FT_API_SEARCH_URL=
- INGEST_OUTPUT_DIR=./data

## Demarrage rapide (ingestion France Travail)
1. Copier l'environnement :
   - copy config/.env.example .env
2. Renseigner les variables France Travail.
3. Lancer l'ingestion :
   - python -m pipelines.ingest.sources.francetravail.main

## Roadmap courte
- Etude comparative du dashboard (voir [docs/dashboard-eval.md](docs/dashboard-eval.md)).
- Mise en place du service API.
- Indexation ElasticSearch et tests d'aggregations.
- Ajout d'une 2eme source (APEC ou WTTJ) pour valider l'extensibilite.

## Licence
Projet interne / usage prive.