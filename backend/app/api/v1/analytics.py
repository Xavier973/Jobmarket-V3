"""
Routes pour les analyses avancées
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from app.services.analytics import analytics_service
from app.models.filters import FilterRequest

router = APIRouter()


@router.get("/salary")
async def get_salary_analytics(
    group_by: Optional[str] = Query(None, description="Champ de regroupement"),
    keywords: Optional[str] = Query(None),
    regions: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """
    Analyses salariales avec regroupement optionnel
    
    Exemples:
    - /analytics/salary?group_by=experience_level
    - /analytics/salary?group_by=region
    - /analytics/salary?group_by=contract_type
    """
    filters = None
    if keywords or regions:
        filters = FilterRequest(
            keywords=keywords.split(",") if keywords else None,
            regions=regions.split(",") if regions else None,
        )
    
    result = analytics_service.get_salary_stats(
        group_by=group_by,
        filters=filters
    )
    
    return result


@router.get("/skills")
async def get_skills_analytics(
    top: int = Query(20, ge=1, le=100, description="Nombre de compétences"),
    keywords: Optional[str] = Query(None),
    regions: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Top N compétences les plus demandées
    """
    filters = None
    if keywords or regions:
        filters = FilterRequest(
            keywords=keywords.split(",") if keywords else None,
            regions=regions.split(",") if regions else None,
        )
    
    result = analytics_service.get_top_skills(top=top, filters=filters)
    
    return result


@router.get("/geography")
async def get_geography_analytics(
    level: str = Query("region", regex="^(region|department|city)$"),
    keywords: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Distribution géographique des offres
    
    Args:
        level: Niveau d'agrégation (region, department, city)
    """
    filters = None
    if keywords:
        filters = FilterRequest(keywords=keywords.split(","))
    
    result = analytics_service.get_geography_stats(
        level=level,
        filters=filters
    )
    
    return result


@router.get("/contracts")
async def get_contracts_analytics(
    keywords: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Distribution des types de contrat
    """
    filters = None
    if keywords:
        filters = FilterRequest(keywords=keywords.split(","))
    
    result = analytics_service.get_contract_distribution(filters=filters)
    
    return result


@router.get("/timeline")
async def get_timeline_analytics(
    interval: str = Query("week", regex="^(day|week|month)$"),
    keywords: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Évolution temporelle des publications
    
    Args:
        interval: Intervalle d'agrégation (day, week, month)
    """
    filters = None
    if keywords:
        filters = FilterRequest(keywords=keywords.split(","))
    
    result = analytics_service.get_timeline(
        interval=interval,
        filters=filters
    )
    
    return result
