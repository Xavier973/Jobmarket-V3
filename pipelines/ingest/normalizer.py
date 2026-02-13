from typing import Any, Dict

from pipelines.ingest.models import JobOffer
from pipelines.ingest.sources.francetravail.mapping import map_france_travail


def normalize_offer(raw: Dict[str, Any], source: str) -> JobOffer:
    if source == "francetravail":
        return map_france_travail(raw)
    raise ValueError(f"Unsupported source: {source}")
