"""
Routes pour les options de filtres
"""
import json
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter
from app.services.elasticsearch import es_service

router = APIRouter()

# Charger le référentiel des départements
DEPARTMENTS_FILE = Path(__file__).parent.parent.parent / "data" / "departments.json"
DEPARTMENTS_MAP = {}
try:
    with open(DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
        DEPARTMENTS_MAP = json.load(f)
except Exception as e:
    print(f"Erreur chargement référentiel départements: {e}")


def extract_department_code(postal_code: str) -> str:
    """Extrait le code département d'un code postal (2 ou 3 premiers caractères)"""
    if not postal_code:
        return ""
    
    # DOM-TOM (3 chiffres)
    if postal_code.startswith(("97", "98")):
        return postal_code[:3]
    
    # Corse (code spécial)
    if postal_code.startswith("20"):
        # Distinguer 2A et 2B (approximatif, basé sur le code postal)
        if postal_code[:5] in ["20000", "20090", "20100", "20110", "20137", "20140", "20150", "20166", "20167", "20200"]:
            return "2A"
        else:
            return "2B"
    
    # France métropolitaine (2 chiffres)
    return postal_code[:2]


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
async def get_departments(region: str = None) -> List[Dict[str, str]]:
    """Liste des départements disponibles avec leurs noms (optionnellement filtrés par région)"""
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
        
        # Extraire les codes départements uniques et les enrichir avec les noms
        departments_set = set()
        for bucket in buckets:
            postal_code = bucket["key"]
            if postal_code:
                dept_code = extract_department_code(postal_code)
                if dept_code:
                    departments_set.add(dept_code)
        
        # Créer la liste enrichie
        result = []
        for code in sorted(departments_set):
            name = DEPARTMENTS_MAP.get(code, code)
            result.append({
                "code": code,
                "name": name,
                "label": f"{name} ({code})"
            })
        
        return result
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


@router.get("/rome-labels")
async def get_rome_labels() -> List[str]:
    """Liste des métiers ROME disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "labels": {
                        "terms": {"field": "rome_label.keyword", "size": 100}
                    }
                }
            }
        )
        buckets = response["aggregations"]["labels"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération métiers ROME: {e}")
        return []


@router.get("/remote-types")
async def get_remote_types() -> List[str]:
    """Liste des types de télétravail disponibles"""
    try:
        response = es_service.es.search(
            index=es_service.index_name,
            body={
                "size": 0,
                "aggs": {
                    "types": {
                        "terms": {"field": "remote_type", "size": 10}
                    }
                }
            }
        )
        buckets = response["aggregations"]["types"]["buckets"]
        return [b["key"] for b in buckets if b["key"]]
    except Exception as e:
        print(f"Erreur récupération types de télétravail: {e}")
        return []
