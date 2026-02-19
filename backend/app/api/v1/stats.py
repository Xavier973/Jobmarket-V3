"""
Routes pour les statistiques globales
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query
from app.services.elasticsearch import es_service
from app.services.analytics import analytics_service
from app.models.filters import FilterRequest

router = APIRouter()


@router.get("/overview")
async def get_overview_stats() -> Dict[str, Any]:
    """
    Statistiques d'ensemble (KPIs principaux)
    """
    # Total d'offres
    total_offers = es_service.count_offers()
    
    # Salaires
    salary_stats_raw = analytics_service.get_salary_stats()
    salary_stats = salary_stats_raw.get("salary_stats", {})
    
    # Top 3 régions
    top_regions = analytics_service.get_geography_stats(level="region")[:3]
    
    # Top 3 compétences
    top_skills = analytics_service.get_top_skills(top=3)
    
    # Distribution contrats
    contracts = analytics_service.get_contract_distribution()
    total_with_contract = sum(c["count"] for c in contracts)
    cdi_count = next((c["count"] for c in contracts if "CDI" in c["contract_type"]), 0)
    cdi_percentage = (cdi_count / total_with_contract * 100) if total_with_contract > 0 else 0
    
    return {
        "total_offers": total_offers,
        "salary_median": salary_stats.get("avg", 0),  # ES stats n'a pas median, on utilise avg
        "salary_min": salary_stats.get("min", 0),
        "salary_max": salary_stats.get("max", 0),
        "top_regions": top_regions,
        "top_skills": top_skills,
        "cdi_percentage": round(cdi_percentage, 1),
        "contract_distribution": contracts
    }


@router.get("/kpis")
async def get_kpis(
    keywords: Optional[str] = Query(None),
    regions: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """
    KPIs avec filtres optionnels
    """
    filters = None
    if keywords or regions:
        filters = FilterRequest(
            keywords=keywords.split(",") if keywords else None,
            regions=regions.split(",") if regions else None,
        )
    
    total = es_service.count_offers(filters)
    salary_stats = analytics_service.get_salary_stats(filters=filters)
    
    return {
        "total_offers": total,
        "salary_stats": salary_stats.get("salary_stats", {}),
    }


@router.get("/timeline")
async def get_timeline(
    interval: str = Query("week", description="Intervalle : day, week, month"),
) -> Dict[str, Any]:
    """
    Évolution temporelle des publications d'offres
    """
    timeline_data = analytics_service.get_timeline(interval=interval)
    
    return {
        "interval": interval,
        "data": timeline_data
    }
