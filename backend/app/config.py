"""
Configuration de l'application
Charge les variables d'environnement
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "jobmarket_v3"
    
    # CORS - peut être une string séparée par des virgules
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Cache (optionnel)
    CACHE_ENABLED: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convertit CORS_ORIGINS en liste"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
    
    class Config:
        # Ne pas charger de fichier .env en production (utiliser variables d'environnement)
        env_file = None
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instance globale des settings
settings = Settings()
