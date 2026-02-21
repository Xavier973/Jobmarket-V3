"""
Service d'analytics et d'agrégations Elasticsearch
"""
from typing import Dict, Any, Optional, List
from app.services.elasticsearch import es_service
from app.models.filters import FilterRequest


class AnalyticsService:
    """Service pour les analyses et statistiques"""
    
    def __init__(self):
        self.es_service = es_service
        self.es = es_service.es
        self.index_name = es_service.index_name
    
    def get_salary_stats(
        self,
        group_by: Optional[str] = None,
        filters: Optional[FilterRequest] = None
    ) -> Dict[str, Any]:
        """
        Statistiques salariales
        
        Args:
            group_by: Champ de regroupement (experience_level, region, contract_type)
            filters: Filtres de recherche
            
        Returns:
            Statistiques salariales (min, max, avg, median)
        """
        query = self.es_service._build_query(filters)
        
        aggs = {
            "salary_stats": {
                "stats": {"field": "salary_min"}
            }
        }
        
        # Si regroupement demandé
        if group_by:
            aggs = {
                "grouped": {
                    "terms": {
                        "field": f"{group_by}.keyword" if group_by != "salary_min" else group_by,
                        "size": 50
                    },
                    "aggs": {
                        "salary_stats": {
                            "stats": {"field": "salary_min"}
                        }
                    }
                }
            }
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 0,
                    "aggs": aggs
                }
            )
            
            return response["aggregations"]
        except Exception as e:
            print(f"Erreur analytics salaire: {e}")
            return {}
    
    def get_top_skills(
        self,
        top: int = 20,
        filters: Optional[FilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """
        Top N compétences les plus demandées
        
        Args:
            top: Nombre de compétences à retourner
            filters: Filtres de recherche
            
        Returns:
            Liste des compétences avec leur nombre d'occurrences
        """
        query = self.es_service._build_query(filters)
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 0,
                    "aggs": {
                        "top_skills": {
                            "terms": {
                                "field": "skills",
                                "size": top
                            }
                        }
                    }
                }
            )
            
            buckets = response["aggregations"]["top_skills"]["buckets"]
            return [
                {"skill": b["key"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            print(f"Erreur analytics compétences: {e}")
            return []
    
    def get_contract_distribution(
        self,
        filters: Optional[FilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """Distribution des types de contrat"""
        query = self.es_service._build_query(filters)
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 0,
                    "aggs": {
                        "contracts": {
                            "terms": {
                                "field": "contract_type",
                                "size": 20
                            }
                        }
                    }
                }
            )
            
            buckets = response["aggregations"]["contracts"]["buckets"]
            return [
                {"contract_type": b["key"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            print(f"Erreur analytics contrats: {e}")
            return []
    
    def get_geography_stats(
        self,
        level: str = "region",
        filters: Optional[FilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """
        Statistiques géographiques
        
        Args:
            level: Niveau géographique (region, department, city)
            filters: Filtres de recherche
            
        Returns:
            Distribution géographique des offres
        """
        query = self.es_service._build_query(filters)
        
        field_mapping = {
            "region": "location_region",
            "department": "location_department",
            "city": "location_city"
        }
        
        field = field_mapping.get(level, "location_region")
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 0,
                    "aggs": {
                        "locations": {
                            "terms": {
                                "field": field,
                                "size": 50
                            }
                        }
                    }
                }
            )
            
            buckets = response["aggregations"]["locations"]["buckets"]
            return [
                {"location": b["key"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            print(f"Erreur analytics géographie: {e}")
            return []
    
    def get_timeline(
        self,
        interval: str = "week",
        filters: Optional[FilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """
        Évolution temporelle des publications
        
        Args:
            interval: Intervalle (day, week, month)
            filters: Filtres de recherche
            
        Returns:
            Timeline des publications
        """
        query = self.es_service._build_query(filters)
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 0,
                    "aggs": {
                        "timeline": {
                            "date_histogram": {
                                "field": "published_at",
                                "calendar_interval": interval
                            }
                        }
                    }
                }
            )
            
            buckets = response["aggregations"]["timeline"]["buckets"]
            return [
                {"date": b["key_as_string"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            print(f"Erreur analytics timeline: {e}")
            return []


# Instance singleton
analytics_service = AnalyticsService()
