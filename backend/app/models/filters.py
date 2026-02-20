"""
Modèles Pydantic pour les filtres de recherche
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class FilterRequest(BaseModel):
    """Requête de filtrage pour les offres"""
    keywords: Optional[List[str]] = Field(None, description="Mots-clés de recherche")
    regions: Optional[List[str]] = Field(None, description="Régions")
    departments: Optional[List[str]] = Field(None, description="Départements")
    cities: Optional[List[str]] = Field(None, description="Villes")
    contract_types: Optional[List[str]] = Field(None, description="Types de contrat")
    salary_min: Optional[float] = Field(None, description="Salaire minimum")
    salary_max: Optional[float] = Field(None, description="Salaire maximum")
    experience_levels: Optional[List[str]] = Field(None, description="Niveaux d'expérience")
    rome_codes: Optional[List[str]] = Field(None, description="Codes ROME")
    skills: Optional[List[str]] = Field(None, description="Compétences requises")
    is_remote: Optional[bool] = Field(None, description="Filtrer par télétravail (True=uniquement télétravail)")
    remote_types: Optional[List[str]] = Field(None, description="Types de télétravail (full_remote, hybrid, occasional)")
    date_from: Optional[str] = Field(None, description="Date de publication minimale (ISO)")
    date_to: Optional[str] = Field(None, description="Date de publication maximale (ISO)")


class FilterOptions(BaseModel):
    """Options disponibles pour les filtres"""
    regions: List[str] = Field(..., description="Liste des régions disponibles")
    departments: List[str] = Field(..., description="Liste des départements disponibles")
    contract_types: List[str] = Field(..., description="Liste des types de contrat")
    experience_levels: List[str] = Field(..., description="Liste des niveaux d'expérience")
    rome_codes: List[str] = Field(..., description="Liste des codes ROME")
    keywords: List[str] = Field(..., description="Liste des mots-clés disponibles")
