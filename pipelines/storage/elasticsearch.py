"""
Client Elasticsearch pour l'indexation des offres d'emploi.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from elasticsearch import Elasticsearch, helpers
    from elasticsearch.exceptions import RequestError, ConnectionError as ESConnectionError
except ImportError:
    raise ImportError(
        "Le package 'elasticsearch' n'est pas installé. "
        "Installez-le avec: pip install elasticsearch>=8.0.0"
    )


class ElasticsearchClient:
    """Client pour gérer l'indexation des offres dans Elasticsearch."""
    
    def __init__(self, host: str = None, index_name: str = None):
        """
        Initialise le client Elasticsearch.
        
        Args:
            host: URL du serveur Elasticsearch (défaut: depuis ES_HOST env var)
            index_name: Nom de l'index (défaut: depuis ES_INDEX env var)
        """
        self.host = host or os.getenv("ES_HOST", "http://localhost:9200")
        self.index_name = index_name or os.getenv("ES_INDEX", "jobmarket_v3")
        
        self.client = Elasticsearch([self.host])
        
        # Vérifier la connexion
        if not self.client.ping():
            raise ESConnectionError(
                f"Impossible de se connecter à Elasticsearch sur {self.host}. "
                "Assurez-vous que le service est démarré (docker-compose up -d)."
            )
        
        print(f"✓ Connecté à Elasticsearch sur {self.host}")
    
    def create_index(self, force: bool = False) -> bool:
        """
        Crée l'index avec le mapping optimisé pour les offres d'emploi.
        
        Args:
            force: Si True, supprime l'index existant avant de le recréer
            
        Returns:
            True si l'index a été créé, False s'il existait déjà
        """
        if self.client.indices.exists(index=self.index_name):
            if force:
                print(f"⚠ Suppression de l'index existant '{self.index_name}'...")
                self.client.indices.delete(index=self.index_name)
            else:
                print(f"✓ L'index '{self.index_name}' existe déjà")
                return False
        
        # Mapping optimisé pour les offres d'emploi
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "french_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "french_elision", "french_stop", "french_stemmer"]
                        }
                    },
                    "filter": {
                        "french_elision": {
                            "type": "elision",
                            "articles_case": True,
                            "articles": ["l", "m", "t", "qu", "n", "s", "j", "d", "c", "jusqu", "quoiqu", "lorsqu", "puisqu"]
                        },
                        "french_stop": {
                            "type": "stop",
                            "stopwords": "_french_"
                        },
                        "french_stemmer": {
                            "type": "stemmer",
                            "language": "light_french"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    # Identification
                    "id": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    
                    # Informations de base (recherche full-text)
                    "title": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "french_analyzer"
                    },
                    "company_name": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    
                    # Classification métier
                    "rome_code": {"type": "keyword"},
                    "rome_label": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "job_category": {"type": "keyword"},
                    "naf_code": {"type": "keyword"},
                    "sector": {"type": "keyword"},
                    "sector_label": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    
                    # Localisation
                    "location_city": {"type": "keyword"},
                    "location_department": {"type": "keyword"},
                    "location_region": {"type": "keyword"},
                    "location_coordinates": {"type": "geo_point"},
                    "location_commune_code": {"type": "keyword"},
                    
                    # Contrat
                    "contract_type": {"type": "keyword"},
                    "contract_duration": {"type": "keyword"},
                    "contract_nature": {"type": "keyword"},
                    "work_schedule": {"type": "keyword"},
                    "weekly_hours": {"type": "float"},
                    "is_alternance": {"type": "boolean"},
                    
                    # Rémunération
                    "salary_min": {"type": "float"},
                    "salary_max": {"type": "float"},
                    "salary_unit": {"type": "keyword"},
                    "salary_comment": {"type": "text", "analyzer": "french_analyzer"},
                    "salary_benefits": {"type": "keyword"},
                    
                    # Compétences
                    "skills": {"type": "keyword"},
                    "skills_required": {"type": "nested"},
                    "skills_desired": {"type": "nested"},
                    "soft_skills": {"type": "keyword"},
                    "languages": {"type": "nested"},
                    
                    # Formation & Expérience
                    "education_level": {"type": "keyword"},
                    "education_required": {"type": "nested"},
                    "experience_required": {"type": "keyword"},
                    "experience_level": {"type": "keyword"},
                    "experience_code": {"type": "keyword"},
                    
                    # Entreprise
                    "company_size": {"type": "keyword"},
                    "company_adapted": {"type": "boolean"},
                    
                    # Conditions de travail
                    "work_context": {"type": "keyword"},
                    "permits_required": {"type": "keyword"},
                    "travel_frequency": {"type": "keyword"},
                    "accessible_handicap": {"type": "boolean"},
                    "is_remote": {"type": "boolean"},
                    "remote_type": {"type": "keyword"},
                    
                    # Métadonnées
                    "published_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "collected_at": {"type": "date"},
                    "positions_count": {"type": "integer"},
                    "qualification_code": {"type": "keyword"},
                    "qualification_label": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "url": {"type": "keyword"},
                    "raw": {"type": "object", "enabled": False}
                }
            }
        }
        
        try:
            self.client.indices.create(index=self.index_name, body=mapping)
            print(f"✓ Index '{self.index_name}' créé avec succès")
            return True
        except RequestError as e:
            print(f"❌ Erreur lors de la création de l'index: {e}")
            raise
    
    def index_offer(self, offer: Dict[str, Any]) -> bool:
        """
        Indexe une offre d'emploi unique.
        
        Args:
            offer: Dictionnaire représentant une offre d'emploi
            
        Returns:
            True si l'indexation a réussi
        """
        # Préparer le document pour l'indexation
        doc = self._prepare_document(offer)
        
        try:
            self.client.index(
                index=self.index_name,
                id=offer["id"],
                document=doc
            )
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation de l'offre {offer.get('id')}: {e}")
            return False
    
    def bulk_index_offers(self, offers: List[Dict[str, Any]], batch_size: int = 500, verbose: bool = False) -> Dict[str, int]:
        """
        Indexe plusieurs offres en batch pour de meilleures performances.
        
        Args:
            offers: Liste d'offres d'emploi
            batch_size: Taille des batches pour l'indexation
            verbose: Si True, affiche les détails des erreurs
            
        Returns:
            Dictionnaire avec le nombre d'offres indexées, doublons et erreurs
        """
        actions = []
        for offer in offers:
            doc = self._prepare_document(offer)
            actions.append({
                "_index": self.index_name,
                "_id": offer["id"],
                "_source": doc
            })
        
        try:
            success, errors = helpers.bulk(
                self.client,
                actions,
                chunk_size=batch_size,
                raise_on_error=False,
                stats_only=False
            )
            
            # Analyser les types d'erreurs
            duplicates = 0
            real_errors = 0
            error_details = {}
            
            if errors:
                for error in errors:
                    error_info = error.get('index', {}).get('error', {})
                    error_type = error_info.get('type', '')
                    
                    if error_type == 'version_conflict_engine_exception':
                        duplicates += 1
                    else:
                        real_errors += 1
                        # Compter les types d'erreurs
                        error_details[error_type] = error_details.get(error_type, 0) + 1
                        
                        # Afficher le détail en mode verbose
                        if verbose:
                            doc_id = error.get('index', {}).get('_id', 'unknown')
                            reason = error_info.get('reason', 'No reason provided')
                            print(f"      ⚠ {doc_id}: {error_type} - {reason[:100]}")
            
            result = {
                "indexed": success,
                "duplicates": duplicates,
                "errors": real_errors,
                "error_details": error_details,
                "total": len(offers)
            }
            
            return result
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation en batch: {e}")
            return {"indexed": 0, "duplicates": 0, "errors": len(offers), "error_details": {}, "total": len(offers)}
    
    def _prepare_document(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prépare un document pour l'indexation (conversion des coordonnées GPS, dates, etc.).
        
        Args:
            offer: Offre d'emploi brute
            
        Returns:
            Document prêt pour l'indexation
        """
        doc = offer.copy()
        
        # Corriger company_name si c'est un objet (bug du normalizer)
        if isinstance(doc.get("company_name"), dict):
            # Extraire le nom ou la description
            company_info = doc["company_name"]
            doc["company_name"] = company_info.get("nom") or company_info.get("description", "")[:200] or None
        
        # Convertir les coordonnées GPS en format geo_point
        if offer.get("location_latitude") and offer.get("location_longitude"):
            doc["location_coordinates"] = {
                "lat": offer["location_latitude"],
                "lon": offer["location_longitude"]
            }
            # Supprimer les champs séparés (optionnel, pour éviter la duplication)
            doc.pop("location_latitude", None)
            doc.pop("location_longitude", None)
        
        # S'assurer que les dates sont au bon format
        for date_field in ["published_at", "updated_at", "collected_at"]:
            if doc.get(date_field):
                # Elasticsearch accepte ISO 8601
                if isinstance(doc[date_field], str):
                    try:
                        # Valider le format de date
                        datetime.fromisoformat(doc[date_field].replace("Z", "+00:00"))
                    except ValueError:
                        doc[date_field] = None
        
        return doc
    
    def search(self, query: Dict[str, Any], size: int = 10) -> Dict[str, Any]:
        """
        Effectue une recherche dans l'index.
        
        Args:
            query: Requête Elasticsearch DSL
            size: Nombre de résultats à retourner
            
        Returns:
            Résultats de la recherche
        """
        try:
            # Ajouter size au body si pas déjà présent
            if "size" not in query:
                query["size"] = size
            return self.client.search(index=self.index_name, body=query)
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            raise
    
    def count(self) -> int:
        """
        Compte le nombre de documents dans l'index.
        
        Returns:
            Nombre de documents
        """
        try:
            result = self.client.count(index=self.index_name)
            return result["count"]
        except Exception:
            return 0
    
    def delete_index(self) -> bool:
        """
        Supprime l'index.
        
        Returns:
            True si la suppression a réussi
        """
        if self.client.indices.exists(index=self.index_name):
            self.client.indices.delete(index=self.index_name)
            print(f"✓ Index '{self.index_name}' supprimé")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur l'index.
        
        Returns:
            Dictionnaire de statistiques
        """
        stats = self.client.indices.stats(index=self.index_name)
        return {
            "total_documents": self.count(),
            "size_in_bytes": stats["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
            "index_name": self.index_name
        }
