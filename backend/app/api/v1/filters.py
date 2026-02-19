"""
Routes pour les options de filtres
"""
from typing import List
from fastapi import APIRouter
from app.services.elasticsearch import es_service

router = APIRouter()


@router.get("/regions")
async def get_regions() -> List[str]:
    """Liste des régions disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "regions": {
                        "terms": {"field": "location_region", "size": 50}
                    }
                }
            }
        )
        buckets = response["aggregations"]["regions"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération régions: {e}")
        return []


@router.get("/departments")
async def get_departments(region: str = None) -> List[str]:
    """Liste des départements disponibles (optionnellement filtrés par région)"""
    query = {"match_all": {}}
    if region:
        query = {"term": {"location_region": region}}
    
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "query": query,
                "size": 0,
                "aggs": {
                    "departments": {
                        "terms": {"field": "location_department", "size": 150}
                    }
                }
            }
        )
        buckets = response["aggregations"]["departments"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération départements: {e}")
        return []


@router.get("/cities")
async def get_cities(department: str = None) -> List[str]:
    """Liste des villes disponibles (optionnellement filtrées par département)"""
    query = {"match_all": {}}
    if department:
        query = {"term": {"location_department": department}}
    
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "query": query,
                "size": 0,
                "aggs": {
                    "cities": {
                        "terms": {"field": "location_city.keyword", "size": 200}
                    }
                }
            }
        )
        buckets = response["aggregations"]["cities"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération villes: {e}")
        return []


@router.get("/contracts")
async def get_contract_types() -> List[str]:
    """Liste des types de contrat disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "contracts": {
                        "terms": {"field": "contract_type.keyword", "size": 50}
                    }
                }
            }
        )
        buckets = response["aggregations"]["contracts"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération contrats: {e}")
        return []


@router.get("/experience-levels")
async def get_experience_levels() -> List[str]:
    """Liste des niveaux d'expérience disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "levels": {
                        "terms": {"field": "experience_level.keyword", "size": 20}
                    }
                }
            }
        )
        buckets = response["aggregations"]["levels"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération niveaux d'expérience: {e}")
        return []


@router.get("/rome-codes")
async def get_rome_codes() -> List[str]:
    """Liste des codes ROME disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "codes": {
                        "terms": {"field": "rome_code", "size": 100}
                    }
                }
            }
        )
        buckets = response["aggregations"]["codes"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération codes ROME: {e}")
        return []
