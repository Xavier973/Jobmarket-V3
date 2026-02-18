"""
Module de stockage pour JobMarket V3.
Gère l'indexation des données dans Elasticsearch.
"""

from .elasticsearch import ElasticsearchClient

__all__ = ["ElasticsearchClient"]
