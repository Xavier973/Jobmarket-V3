"""
Routes pour les offres d'emploi
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.job_offer import JobOfferListResponse, JobOfferDetail
from app.models.filters import FilterRequest
from app.services.elasticsearch import es_service
from app.config import settings

router = APIRouter()


@router.get("", response_model=JobOfferListResponse)
async def list_offers(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE, description="Taille de la page"),
    sort_by: str = Query("published_at", description="Champ de tri"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Ordre de tri"),
    # Filtres query params
    keywords: Optional[str] = Query(None, description="Mots-clés (séparés par virgule)"),
    regions: Optional[str] = Query(None, description="Régions (séparées par virgule)"),
    departments: Optional[str] = Query(None, description="Départements (séparés par virgule)"),
    contract_types: Optional[str] = Query(None, description="Types de contrat (séparés par virgule)"),
    salary_min: Optional[float] = Query(None, description="Salaire minimum"),
    salary_max: Optional[float] = Query(None, description="Salaire maximum"),
):
    """
    Liste paginée des offres d'emploi avec filtres optionnels
    """
    # Construire l'objet FilterRequest depuis les query params
    filters = None
    if any([keywords, regions, departments, contract_types, salary_min, salary_max]):
        filters = FilterRequest(
            keywords=keywords.split(",") if keywords else None,
            regions=regions.split(",") if regions else None,
            departments=departments.split(",") if departments else None,
            contract_types=contract_types.split(",") if contract_types else None,
            salary_min=salary_min,
            salary_max=salary_max,
        )
    
    result = es_service.search_offers(
        filters=filters,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return result


@router.post("/search", response_model=JobOfferListResponse)
async def search_offers(
    filters: FilterRequest,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    sort_by: str = Query("published_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    Recherche d'offres avec filtres avancés (POST body)
    """
    result = es_service.search_offers(
        filters=filters,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return result


@router.get("/{offer_id}", response_model=JobOfferDetail)
async def get_offer(offer_id: str):
    """
    Récupère une offre par son ID
    """
    offer = es_service.get_offer_by_id(offer_id)
    
    if not offer:
        raise HTTPException(status_code=404, detail=f"Offre {offer_id} non trouvée")
    
    return offer


@router.get("/count/total")
async def count_offers(
    keywords: Optional[str] = Query(None),
    regions: Optional[str] = Query(None),
    departments: Optional[str] = Query(None),
    contract_types: Optional[str] = Query(None),
):
    """
    Compte le nombre d'offres correspondant aux filtres
    """
    filters = None
    if any([keywords, regions, departments, contract_types]):
        filters = FilterRequest(
            keywords=keywords.split(",") if keywords else None,
            regions=regions.split(",") if regions else None,
            departments=departments.split(",") if departments else None,
            contract_types=contract_types.split(",") if contract_types else None,
        )
    
    count = es_service.count_offers(filters)
    
    return {"count": count}
