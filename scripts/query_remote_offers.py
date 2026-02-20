"""
Exemples de requêtes Elasticsearch pour filtrer les offres avec télétravail.

Ce script montre comment :
1. Filtrer uniquement les offres avec télétravail
2. Compter les offres par type (remote vs présentiel)
3. Analyser les offres remote par région
4. Trouver les offres remote avec salaires élevés
5. Filtrer par type de télétravail (full_remote, hybrid, occasional)
"""

import os
from elasticsearch import Elasticsearch
from pprint import pprint


def connect_elasticsearch():
    """Connexion à Elasticsearch."""
    es_host = os.getenv("ES_HOST", "http://localhost:9200")
    client = Elasticsearch([es_host])
    
    if not client.ping():
        raise ConnectionError(f"Impossible de se connecter à Elasticsearch sur {es_host}")
    
    print(f"✓ Connecté à Elasticsearch\n")
    return client


def example_1_filter_remote_offers(client, index="jobmarket_v3"):
    """Exemple 1 : Récupérer uniquement les offres avec télétravail."""
    print("=" * 70)
    print("Exemple 1 : Offres avec télétravail (10 premiers résultats)")
    print("=" * 70)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"is_remote": True}}
                ]
            }
        },
        "size": 10,
        "_source": ["id", "title", "company_name", "location_city", "contract_type", "is_remote"]
    }
    
    response = client.search(index=index, body=query)
    hits = response["hits"]["hits"]
    
    print(f"\n{response['hits']['total']['value']} offres trouvées\n")
    
    for i, hit in enumerate(hits, 1):
        source = hit["_source"]
        print(f"{i}. {source.get('title', 'Sans titre')}")
        print(f"   Entreprise : {source.get('company_name', 'N/A')}")
        print(f"   Lieu : {source.get('location_city', 'N/A')}")
        print(f"   Contrat : {source.get('contract_type', 'N/A')}")
        print(f"   Télétravail : {'✓' if source.get('is_remote') else '✗'}\n")


def example_2_count_by_remote(client, index="jobmarket_v3"):
    """Exemple 2 : Compter les offres par type (remote vs présentiel)."""
    print("=" * 70)
    print("Exemple 2 : Répartition télétravail vs présentiel")
    print("=" * 70)
    
    query = {
        "size": 0,
        "aggs": {
            "by_remote": {
                "terms": {
                    "field": "is_remote",
                    "missing": False  # Traiter les valeurs manquantes comme False
                }
            }
        }
    }
    
    response = client.search(index=index, body=query)
    buckets = response["aggregations"]["by_remote"]["buckets"]
    total = response["hits"]["total"]["value"]
    
    print(f"\nTotal : {total} offres\n")
    
    for bucket in buckets:
        is_remote = bucket["key"]
        count = bucket["doc_count"]
        percent = (count / total * 100) if total > 0 else 0
        label = "Avec télétravail" if is_remote else "Sans télétravail"
        print(f"{label:20} : {count:5} offres ({percent:5.1f}%)")


def example_2b_count_by_remote_type(client, index="jobmarket_v3"):
    """Exemple 2b : Compter les offres par type de télétravail."""
    print("\n" + "=" * 70)
    print("Exemple 2b : Répartition par type de télétravail")
    print("=" * 70)
    
    query = {
        "size": 0,
        "query": {
            "term": {"is_remote": True}
        },
        "aggs": {
            "by_type": {
                "terms": {
                    "field": "remote_type",
                    "size": 10
                }
            }
        }
    }
    
    response = client.search(index=index, body=query)
    buckets = response["aggregations"]["by_type"]["buckets"]
    total = response["hits"]["total"]["value"]
    
    print(f"\nTotal offres avec télétravail : {total}\n")
    
    type_labels = {
        "full_remote": "🌍 Full Remote (100%)",
        "hybrid": "🏢 Hybride (X jours/semaine)",
        "occasional": "📌 Occasionnel (possible)"
    }
    
    for bucket in buckets:
        remote_type = bucket["key"]
        count = bucket["doc_count"]
        percent = (count / total * 100) if total > 0 else 0
        label = type_labels.get(remote_type, remote_type)
        print(f"{label:35} : {count:4} offres ({percent:5.1f}%)")


def example_3_remote_by_region(client, index="jobmarket_v3"):
    """Exemple 3 : Analyser les offres remote par région."""
    print("\n" + "=" * 70)
    print("Exemple 3 : Top 10 villes avec le plus d'offres en télétravail")
    print("=" * 70)
    
    query = {
        "size": 0,
        "query": {
            "term": {"is_remote": True}
        },
        "aggs": {
            "by_city": {
                "terms": {
                    "field": "location_city",
                    "size": 10,
                    "order": {"_count": "desc"}
                }
            }
        }
    }
    
    response = client.search(index=index, body=query)
    buckets = response["aggregations"]["by_city"]["buckets"]
    
    print()
    for i, bucket in enumerate(buckets, 1):
        city = bucket["key"]
        count = bucket["doc_count"]
        print(f"{i:2}. {city:30} : {count:4} offres")


def example_3b_full_remote_offers(client, index="jobmarket_v3"):
    """Exemple 3b : Offres 100% télétravail uniquement."""
    print("\n" + "=" * 70)
    print("Exemple 3b : Offres 100% Full Remote (5 exemples)")
    print("=" * 70)
    
    query = {
        "query": {
            "term": {"remote_type": "full_remote"}
        },
        "size": 5,
        "_source": ["id", "title", "company_name", "location_city", "contract_type", "remote_type"]
    }
    
    response = client.search(index=index, body=query)
    hits = response["hits"]["hits"]
    
    print(f"\n{response['hits']['total']['value']} offres trouvées\n")
    
    for i, hit in enumerate(hits, 1):
        source = hit["_source"]
        print(f"{i}. {source.get('title', 'Sans titre')}")
        print(f"   Entreprise : {source.get('company_name', 'N/A')}")
        print(f"   Lieu : {source.get('location_city', 'N/A')}")
        print(f"   Contrat : {source.get('contract_type', 'N/A')}")
        print(f"   Type : 🌍 Full Remote\n")


def example_4_remote_high_salary(client, index="jobmarket_v3"):
    """Exemple 4 : Offres remote avec salaires élevés (> 50K€)."""
    print("\n" + "=" * 70)
    print("Exemple 4 : Offres en télétravail avec salaire > 50K€/an")
    print("=" * 70)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"is_remote": True}},
                    {"term": {"salary_unit": "yearly"}},
                    {"range": {"salary_min": {"gte": 50000}}}
                ]
            }
        },
        "size": 5,
        "_source": ["id", "title", "company_name", "salary_min", "salary_max", "location_city"],
        "sort": [{"salary_min": "desc"}]
    }
    
    response = client.search(index=index, body=query)
    hits = response["hits"]["hits"]
    
    print(f"\n{response['hits']['total']['value']} offres trouvées\n")
    
    for i, hit in enumerate(hits, 1):
        source = hit["_source"]
        salary_range = f"{source.get('salary_min', 0):.0f}€"
        if source.get('salary_max'):
            salary_range += f" - {source.get('salary_max', 0):.0f}€"
        salary_range += "/an"
        
        print(f"{i}. {source.get('title', 'Sans titre')}")
        print(f"   Entreprise : {source.get('company_name', 'N/A')}")
        print(f"   Salaire : {salary_range}")
        print(f"   Lieu : {source.get('location_city', 'N/A')}\n")


def example_5_data_analyst_remote(client, index="jobmarket_v3"):
    """Exemple 5 : Data Analyst en télétravail."""
    print("=" * 70)
    print("Exemple 5 : Poste 'Data Analyst' avec télétravail")
    print("=" * 70)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": "data analyst"}},
                    {"term": {"is_remote": True}}
                ]
            }
        },
        "size": 5,
        "_source": ["id", "title", "company_name", "location_city", "contract_type", "salary_min", "salary_max"]
    }
    
    response = client.search(index=index, body=query)
    hits = response["hits"]["hits"]
    
    print(f"\n{response['hits']['total']['value']} offres trouvées\n")
    
    for i, hit in enumerate(hits, 1):
        source = hit["_source"]
        salary = "Non communiqué"
        if source.get('salary_min'):
            salary = f"{source.get('salary_min', 0):.0f}€"
            if source.get('salary_max'):
                salary += f" - {source.get('salary_max', 0):.0f}€"
        
        print(f"{i}. {source.get('title', 'Sans titre')}")
        print(f"   Entreprise : {source.get('company_name', 'N/A')}")
        print(f"   Lieu : {source.get('location_city', 'N/A')}")
        print(f"   Contrat : {source.get('contract_type', 'N/A')}")
        print(f"   Salaire : {salary}\n")


if __name__ == "__main__":
    try:
        client = connect_elasticsearch()
        
        # Exécuter tous les exemples
        example_1_filter_remote_offers(client)
        example_2_count_by_remote(client)
        example_2b_count_by_remote_type(client)
        example_3_remote_by_region(client)
        example_3b_full_remote_offers(client)
        example_4_remote_high_salary(client)
        example_5_data_analyst_remote(client)
        
        print("\n" + "=" * 70)
        print("✅ Tous les exemples ont été exécutés avec succès")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("\nAssurez-vous que :")
        print("1. Elasticsearch est démarré (docker-compose up -d)")
        print("2. Les données sont indexées (python scripts/index_to_elasticsearch.py)")
