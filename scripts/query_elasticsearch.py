#!/usr/bin/env python3
"""
Exemples de requêtes Elasticsearch pour analyser le marché de l'emploi.

Usage:
    python scripts/query_elasticsearch.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.storage.elasticsearch import ElasticsearchClient


def example_full_text_search(es_client: ElasticsearchClient):
    """Exemple 1 : Recherche full-text sur le titre."""
    print("\n" + "="*60)
    print("1. RECHERCHE FULL-TEXT : 'data engineer'")
    print("="*60)
    
    query = {
        "query": {
            "match": {
                "title": "data engineer"
            }
        }
    }
    
    results = es_client.search(query, size=5)
    total = results["hits"]["total"]["value"]
    print(f"\nRésultats trouvés : {total}")
    
    for hit in results["hits"]["hits"]:
        source = hit["_source"]
        print(f"\n- {source['title']}")
        print(f"  Entreprise: {source.get('company_name', 'N/A')}")
        print(f"  Lieu: {source.get('location_city', 'N/A')}")
        print(f"  Contrat: {source.get('contract_type', 'N/A')}")


def example_filtered_search(es_client: ElasticsearchClient):
    """Exemple 2 : Filtrage par critères multiples."""
    print("\n" + "="*60)
    print("2. FILTRAGE : CDI à Paris")
    print("="*60)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"contract_type": "CDI"}},
                    {"term": {"location_city": "Paris"}}
                ]
            }
        }
    }
    
    results = es_client.search(query, size=5)
    total = results["hits"]["total"]["value"]
    print(f"\nOffres CDI à Paris : {total}")
    
    for hit in results["hits"]["hits"]:
        source = hit["_source"]
        print(f"\n- {source['title']}")
        print(f"  Entreprise: {source.get('company_name', 'N/A')}")


def example_salary_range(es_client: ElasticsearchClient):
    """Exemple 3 : Filtrage par fourchette salariale."""
    print("\n" + "="*60)
    print("3. SALAIRES : > 40 000 €/an")
    print("="*60)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "salary_min"}},
                    {"range": {"salary_min": {"gte": 40000}}}
                ]
            }
        },
        "sort": [
            {"salary_min": {"order": "desc"}}
        ]
    }
    
    results = es_client.search(query, size=5)
    total = results["hits"]["total"]["value"]
    print(f"\nOffres avec salaire ≥ 40 000 € : {total}")
    
    for hit in results["hits"]["hits"]:
        source = hit["_source"]
        salary_min = source.get("salary_min", 0)
        salary_max = source.get("salary_max", 0)
        print(f"\n- {source['title']}")
        print(f"  Salaire: {salary_min:,.0f} € - {salary_max:,.0f} €")
        print(f"  Lieu: {source.get('location_city', 'N/A')}")


def example_aggregation_skills(es_client: ElasticsearchClient):
    """Exemple 4 : Top 10 des compétences."""
    print("\n" + "="*60)
    print("4. TOP 10 DES COMPÉTENCES")
    print("="*60)
    
    query = {
        "size": 0,
        "aggs": {
            "top_skills": {
                "terms": {
                    "field": "skills",
                    "size": 10
                }
            }
        }
    }
    
    results = es_client.search(query)
    buckets = results["aggregations"]["top_skills"]["buckets"]
    
    print(f"\n{'Rang':<6} {'Compétence':<30} {'Offres':<10}")
    print("-" * 50)
    
    for i, bucket in enumerate(buckets, 1):
        print(f"{i:<6} {bucket['key']:<30} {bucket['doc_count']:<10}")


def example_aggregation_contract_types(es_client: ElasticsearchClient):
    """Exemple 5 : Répartition par type de contrat."""
    print("\n" + "="*60)
    print("5. RÉPARTITION PAR TYPE DE CONTRAT")
    print("="*60)
    
    query = {
        "size": 0,
        "aggs": {
            "contract_types": {
                "terms": {
                    "field": "contract_type",
                    "size": 10
                }
            }
        }
    }
    
    results = es_client.search(query)
    buckets = results["aggregations"]["contract_types"]["buckets"]
    total = sum(b["doc_count"] for b in buckets)
    
    print(f"\n{'Type':<20} {'Offres':<10} {'%':<10}")
    print("-" * 40)
    
    for bucket in buckets:
        percentage = (bucket["doc_count"] / total) * 100
        print(f"{bucket['key']:<20} {bucket['doc_count']:<10} {percentage:>6.1f}%")


def example_aggregation_locations(es_client: ElasticsearchClient):
    """Exemple 6 : Top 10 des villes."""
    print("\n" + "="*60)
    print("6. TOP 10 DES VILLES")
    print("="*60)
    
    query = {
        "size": 0,
        "aggs": {
            "top_cities": {
                "terms": {
                    "field": "location_city",
                    "size": 10
                }
            }
        }
    }
    
    results = es_client.search(query)
    buckets = results["aggregations"]["top_cities"]["buckets"]
    
    print(f"\n{'Rang':<6} {'Ville':<30} {'Offres':<10}")
    print("-" * 50)
    
    for i, bucket in enumerate(buckets, 1):
        print(f"{i:<6} {bucket['key']:<30} {bucket['doc_count']:<10}")


def example_aggregation_experience(es_client: ElasticsearchClient):
    """Exemple 7 : Répartition par niveau d'expérience."""
    print("\n" + "="*60)
    print("7. RÉPARTITION PAR NIVEAU D'EXPÉRIENCE")
    print("="*60)
    
    query = {
        "size": 0,
        "aggs": {
            "experience_levels": {
                "terms": {
                    "field": "experience_level",
                    "size": 10
                }
            }
        }
    }
    
    results = es_client.search(query)
    buckets = results["aggregations"]["experience_levels"]["buckets"]
    
    print(f"\n{'Niveau':<20} {'Offres':<10}")
    print("-" * 30)
    
    for bucket in buckets:
        level = bucket["key"] if bucket["key"] else "Non spécifié"
        print(f"{level:<20} {bucket['doc_count']:<10}")


def example_stats_salary(es_client: ElasticsearchClient):
    """Exemple 8 : Statistiques sur les salaires."""
    print("\n" + "="*60)
    print("8. STATISTIQUES SALARIALES")
    print("="*60)
    
    query = {
        "size": 0,
        "query": {
            "exists": {"field": "salary_min"}
        },
        "aggs": {
            "salary_stats": {
                "stats": {
                    "field": "salary_min"
                }
            }
        }
    }
    
    results = es_client.search(query)
    stats = results["aggregations"]["salary_stats"]
    
    print(f"\nOffres avec salaire communiqué : {stats['count']}")
    print(f"Salaire minimum : {stats['min']:,.0f} €")
    print(f"Salaire moyen   : {stats['avg']:,.0f} €")
    print(f"Salaire médian  : (à calculer avec percentiles)")
    print(f"Salaire maximum : {stats['max']:,.0f} €")


def main():
    """Point d'entrée principal."""
    # Charger les variables d'environnement
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    # Se connecter à Elasticsearch
    try:
        print("🔌 Connexion à Elasticsearch...")
        es_client = ElasticsearchClient()
        
        # Afficher les statistiques de l'index
        count = es_client.count()
        print(f"✓ Index '{es_client.index_name}' : {count:,} offres")
        
        if count == 0:
            print("\n⚠ L'index est vide. Indexez d'abord des données :")
            print("   python scripts/index_to_elasticsearch.py --source francetravail")
            return
        
        # Exécuter les exemples
        example_full_text_search(es_client)
        example_filtered_search(es_client)
        example_salary_range(es_client)
        example_aggregation_skills(es_client)
        example_aggregation_contract_types(es_client)
        example_aggregation_locations(es_client)
        example_aggregation_experience(es_client)
        example_stats_salary(es_client)
        
        print("\n" + "="*60)
        print("✅ Exemples terminés !")
        print("="*60)
        print(f"\n💡 Accès Kibana : http://localhost:5601")
        print(f"💡 Documentation : docs/elasticsearch.md")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        print("\nAssurez-vous que Elasticsearch est démarré :")
        print("   docker-compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    main()
