from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class JobOffer:
    # === Identification ===
    id: str
    source: str
    
    # === Informations de base ===
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    
    # === Classification métier ===
    rome_code: Optional[str] = None  # Code ROME du métier
    rome_label: Optional[str] = None  # Libellé du métier ROME
    job_category: Optional[str] = None  # Appellation précise du poste
    naf_code: Optional[str] = None  # Code NAF de l'entreprise
    sector: Optional[str] = None  # Secteur d'activité
    sector_label: Optional[str] = None  # Libellé du secteur
    
    # === Localisation ===
    location_city: Optional[str] = None
    location_department: Optional[str] = None
    location_region: Optional[str] = None
    location_latitude: Optional[float] = None  # Coordonnées GPS
    location_longitude: Optional[float] = None
    location_commune_code: Optional[str] = None  # Code INSEE commune
    
    # === Contrat ===
    contract_type: Optional[str] = None
    contract_duration: Optional[str] = None
    contract_nature: Optional[str] = None  # Nature du contrat
    work_schedule: Optional[str] = None  # Temps plein / temps partiel
    weekly_hours: Optional[float] = None  # Nombre d'heures hebdomadaires
    is_alternance: Optional[bool] = None  # Poste en alternance
    
    # === Rémunération ===
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None  # horaire, mensuel, annuel
    salary_comment: Optional[str] = None  # Commentaire sur le salaire
    salary_benefits: Optional[List[str]] = None  # Avantages (primes, mutuelle...)
    
    # === Compétences ===
    skills: Optional[List[str]] = None  # Liste simple (rétrocompatibilité)
    skills_required: Optional[List[Dict[str, str]]] = None  # Compétences exigées détaillées
    skills_desired: Optional[List[Dict[str, str]]] = None  # Compétences souhaitées
    soft_skills: Optional[List[str]] = None  # Qualités professionnelles
    languages: Optional[List[Dict[str, str]]] = None  # Langues requises
    
    # === Formation & Expérience ===
    education_level: Optional[str] = None  # Niveau de formation (Bac, Bac+2, Bac+5...)
    education_required: Optional[List[Dict[str, str]]] = None  # Formations détaillées
    experience_required: Optional[str] = None  # Expérience requise (ex: "2 An(s)")
    experience_level: Optional[str] = None  # junior, confirmé, senior, expert
    experience_code: Optional[str] = None  # Code expérience (D, E, S...)
    
    # === Entreprise ===
    company_size: Optional[str] = None  # Tranche d'effectif
    company_adapted: Optional[bool] = None  # Entreprise adaptée
    
    # === Conditions de travail ===
    work_context: Optional[List[str]] = None  # Horaires, conditions d'exercice
    permits_required: Optional[List[str]] = None  # Permis requis
    travel_frequency: Optional[str] = None  # Fréquence des déplacements
    accessible_handicap: Optional[bool] = None  # Accessible travailleurs handicapés
    
    # === Métadonnées ===
    published_at: Optional[str] = None
    updated_at: Optional[str] = None  # Date de dernière actualisation
    collected_at: Optional[str] = None
    positions_count: Optional[int] = None  # Nombre de postes à pourvoir
    qualification_code: Optional[str] = None  # Code qualification
    qualification_label: Optional[str] = None  # Libellé qualification
    url: Optional[str] = None  # URL de l'offre originale
    raw: Optional[Dict[str, Any]] = None  # Données brutes complètes

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
