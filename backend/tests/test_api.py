"""
Tests pour l'API Backend
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test de l'endpoint root"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_check():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stats_overview():
    """Test des statistiques d'ensemble"""
    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_offers" in data
    # Note: peut échouer si ES n'est pas démarré


def test_list_offers():
    """Test de la liste des offres"""
    response = client.get("/api/v1/offers?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    # Note: peut échouer si ES n'est pas démarré


# TODO: Ajouter plus de tests unitaires et d'intégration
