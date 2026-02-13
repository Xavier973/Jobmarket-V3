from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pipelines.ingest.models import JobOffer


def _get_nested(data: Dict[str, Any], path: str) -> Optional[Any]:
    current: Any = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def map_france_travail(raw: Dict[str, Any]) -> JobOffer:
    source_id = raw.get("id") or raw.get("id_offre") or "unknown"
    title = raw.get("intitule") or raw.get("title")
    description = raw.get("description")
    company_name = _get_nested(raw, "entreprise.nom") or raw.get("entreprise")
    location_city = _get_nested(raw, "lieuTravail.libelle") or raw.get("lieu")
    location_department = _get_nested(raw, "lieuTravail.codePostal")
    contract_type = raw.get("typeContratLibelle") or raw.get("typeContrat")
    published_at = raw.get("dateCreation") or raw.get("datePublication")

    return JobOffer(
        id=f"francetravail:{source_id}",
        source="francetravail",
        title=title,
        description=description,
        company_name=company_name,
        location_city=location_city,
        location_department=location_department,
        contract_type=contract_type,
        published_at=published_at,
        collected_at=datetime.now(timezone.utc).isoformat(),
        raw=raw,
    )
