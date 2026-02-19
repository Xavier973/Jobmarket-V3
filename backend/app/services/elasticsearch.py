"""
Service Elasticsearch
Réutilise et étend pipelines/storage/elasticsearch.py
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch

# Ajouter le répertoire parent au path pour importer depuis pipelines
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from pipelines.storage.elasticsearch import ElasticsearchClient
from app.config import settings
from app.models.filters import FilterRequest


class ElasticsearchService:
    """Service pour interroger Elasticsearch"""
    
    def __init__(self):
        """Initialise le client Elasticsearch"""
        self.client = ElasticsearchClient(
            host=settings.ELASTICSEARCH_URL,
            index_name=settings.ELASTICSEARCH_INDEX
        )
        self.es = self.client.client  # Accès au client ES natif
        self.index_name = self.client.index_name
    
    def search_offers(
        self,
        filters: Optional[FilterRequest] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "published_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Recherche des offres avec filtres
        
        Args:
            filters: Filtres de recherche
            page: Numéro de page (1-based)
            size: Nombre de résultats par page
            sort_by: Champ de tri
            sort_order: Ordre de tri (asc/desc)
            
        Returns:
            Dict avec total, offres, et métadonnées de pagination
        """
        # Construction de la requête
        query = self._build_query(filters)
        
        # Calcul de l'offset
        from_offset = (page - 1) * size
        
        # Recherche
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "from": from_offset,
                    "size": size,
                    "sort": [{sort_by: {"order": sort_order}}]
                }
            )
            
            total = response["hits"]["total"]["value"]
            hits = response["hits"]["hits"]
            
            # Extraire les documents source
            offers = [hit["_source"] for hit in hits]
            
            return {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,  # Arrondi supérieur
                "items": offers
            }
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return {
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0,
                "items": []
            }
    
    def get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une offre par son ID"""
        try:
            response = self.es.get(index=self.index_name, id=offer_id)
            return response["_source"]
        except Exception as e:
            print(f"Offre {offer_id} non trouvée: {e}")
            return None
    
    def count_offers(self, filters: Optional[FilterRequest] = None) -> int:
        """Compte le nombre d'offres correspondant aux filtres"""
        query = self._build_query(filters)
        try:
            response = self.es.count(index=self.index_name, body={"query": query})
            return response["count"]
        except Exception as e:
            print(f"Erreur lors du comptage: {e}")
            return 0
    
    def _build_query(self, filters: Optional[FilterRequest]) -> Dict[str, Any]:
        """
        Construit la requête Elasticsearch à partir des filtres
        
        Returns:
            Query DSL Elasticsearch
        """
        if not filters:
            return {"match_all": {}}
        
        must_clauses = []
        
        # Filtres textuels (keywords)
        if filters.keywords:
            should_clauses = []
            for keyword in filters.keywords:
                should_clauses.extend([
                    {"match": {"title": keyword}},
                    {"match": {"description": keyword}},
                    {"match": {"skills": keyword}}
                ])
            must_clauses.append({"bool": {"should": should_clauses, "minimum_should_match": 1}})
        
        # Filtres géographiques
        if filters.regions:
            must_clauses.append({"terms": {"location_region": filters.regions}})
        
        if filters.departments:
            must_clauses.append({"terms": {"location_department": filters.departments}})
        
        if filters.cities:
            must_clauses.append({"terms": {"location_city.keyword": filters.cities}})
        
        # Filtres contrat
        if filters.contract_types:
            must_clauses.append({"terms": {"contract_type": filters.contract_types}})
        
        # Filtres salaire
        if filters.salary_min is not None or filters.salary_max is not None:
            range_query = {}
            if filters.salary_min is not None:
                range_query["gte"] = filters.salary_min
            if filters.salary_max is not None:
                range_query["lte"] = filters.salary_max
            must_clauses.append({"range": {"salary_min": range_query}})
        
        # Filtres expérience
        if filters.experience_levels:
            must_clauses.append({"terms": {"experience_level": filters.experience_levels}})
        
        # Filtres ROME
        if filters.rome_codes:
            must_clauses.append({"terms": {"rome_code": filters.rome_codes}})
        
        # Filtres compétences
        if filters.skills:
            must_clauses.append({"terms": {"skills": filters.skills}})
        
        # Filtres dates
        if filters.date_from or filters.date_to:
            range_query = {}
            if filters.date_from:
                range_query["gte"] = filters.date_from
            if filters.date_to:
                range_query["lte"] = filters.date_to
            must_clauses.append({"range": {"published_at": range_query}})
        
        # Construire la requête bool
        if not must_clauses:
            return {"match_all": {}}
        
        return {
            "bool": {
                "must": must_clauses
            }
        }


# Instance singleton
es_service = ElasticsearchService()
