# GitHub Copilot Instructions

## Project context
- This repository is JobMarket V3, a modular data pipeline for job market analytics.
- Ingestion pulls from France Travail API using OAuth client credentials.
- Data is normalized into a canonical JobOffer schema before storage.

## Coding guidelines
- Keep modules small and focused (ingest, normalize, store, serve).
- Use environment variables for secrets and endpoints. Never hardcode secrets.
- Prefer simple, testable functions over complex classes.
- Keep ASCII-only text unless required by external data.

## Ingestion specifics
- Adapters live under pipelines/ingest/sources/.
- Each adapter maps to the canonical JobOffer model.
- Raw data should be saved in data/raw/<source>/.
- Normalized data should be saved in data/normalized/<source>/.

## API usage
- Token endpoint requires application/x-www-form-urlencoded.
- Scope must include api_offresdemploiv2 o2dsoffre for offres d'emploi.
- Handle rate limits (HTTP 429) using Retry-After.

## Testing
- Add or update tests when touching adapters or mappings.
- Prefer small unit tests for mapping functions.
