"""
Modèles Pydantic pour les offres d'emploi
Adaptés depuis pipelines/ingest/models.py
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JobOfferResponse(BaseModel):
    """Réponse API simplifiée pour liste d'offres"""
    id: str
    source: str
    title: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_region: Optional[str] = None
    contract_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None
    published_at: Optional[str] = None
    rome_code: Optional[str] = None
    rome_label: Optional[str] = None


class JobOfferDetail(BaseModel):
    """Réponse API détaillée pour une offre"""
    # Identification
    id: str
    source: str
    
    # Informations de base
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    
    # Classification métier
    rome_code: Optional[str] = None
    rome_label: Optional[str] = None
    job_category: Optional[str] = None
    naf_code: Optional[str] = None
    sector: Optional[str] = None
    sector_label: Optional[str] = None
    
    # Localisation
    location_city: Optional[str] = None
    location_department: Optional[str] = None
    location_region: Optional[str] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    
    # Contrat
    contract_type: Optional[str] = None
    contract_duration: Optional[str] = None
    contract_nature: Optional[str] = None
    work_schedule: Optional[str] = None
    weekly_hours: Optional[float] = None
    is_alternance: Optional[bool] = None
    
    # Rémunération
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None
    salary_comment: Optional[str] = None
    salary_benefits: Optional[List[str]] = None
    
    # Compétences
    skills: Optional[List[str]] = None
    skills_required: Optional[List[Dict[str, str]]] = None
    skills_desired: Optional[List[Dict[str, str]]] = None
    soft_skills: Optional[List[str]] = None
    languages: Optional[List[Dict[str, str]]] = None
    
    # Formation & Expérience
    education_level: Optional[str] = None
    education_required: Optional[List[Dict[str, str]]] = None
    experience_required: Optional[str] = None
    experience_level: Optional[str] = None
    
    # Entreprise
    company_size: Optional[str] = None
    
    # Conditions de travail
    work_context: Optional[List[str]] = None
    permits_required: Optional[List[str]] = None
    accessible_handicap: Optional[bool] = None
    
    # Métadonnées
    published_at: Optional[str] = None
    updated_at: Optional[str] = None
    collected_at: Optional[str] = None
    positions_count: Optional[int] = None
    url: Optional[str] = None


class JobOfferListResponse(BaseModel):
    """Réponse paginée pour liste d'offres"""
    total: int = Field(..., description="Nombre total d'offres")
    page: int = Field(..., description="Page courante")
    size: int = Field(..., description="Taille de la page")
    pages: int = Field(..., description="Nombre total de pages")
    items: List[JobOfferResponse] = Field(..., description="Liste des offres")
