from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class JobOffer:
    id: str
    source: str
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_department: Optional[str] = None
    location_region: Optional[str] = None
    contract_type: Optional[str] = None
    contract_duration: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None
    skills: Optional[List[str]] = None
    published_at: Optional[str] = None
    collected_at: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
