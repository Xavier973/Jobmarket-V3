#!/usr/bin/env python3
"""
Script d'indexation des offres d'emploi dans Elasticsearch.

Usage:
    python scripts/index_to_elasticsearch.py --source francetravail
    python scripts/index_to_elasticsearch.py --source francetravail --file offers_kw_data_engineer.jsonl
    python scripts/index_to_elasticsearch.py --source francetravail --force
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.storage.elasticsearch import ElasticsearchClient


def load_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Charge un fichier JSONL et retourne une liste d'offres.
    
    Args:
        file_path: Chemin vers le fichier JSONL
        
    Returns:
        Liste d'offres d'emploi
    """
    offers = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                offer = json.loads(line)
                offers.append(offer)
            except json.JSONDecodeError as e:
                print(f"⚠ Erreur ligne {line_num} dans {file_path.name}: {e}")
    return offers


def get_normalized_files(source: str, data_dir: Path, specific_file: str = None) -> List[Path]:
    """
    Récupère la liste des fichiers normalisés à indexer.
    
    Args:
        source: Nom de la source (francetravail, apec, etc.)
        data_dir: Répertoire racine des données
        specific_file: Nom d'un fichier spécifique (optionnel)
        
    Returns:
        Liste des chemins de fichiers JSONL
    """
    normalized_dir = data_dir / "normalized" / source
    
    if not normalized_dir.exists():
        print(f"❌ Le répertoire {normalized_dir} n'existe pas")
        return []
    
    if specific_file:
        file_path = normalized_dir / specific_file
        if file_path.exists():
            return [file_path]
        else:
            print(f"❌ Le fichier {file_path} n'existe pas")
            return []
    
    # Récupérer tous les fichiers JSONL (exclure le dossier old)
    files = [f for f in normalized_dir.glob("*.jsonl") if f.is_file()]
    return sorted(files)


def index_files(
    es_client: ElasticsearchClient,
    files: List[Path],
    batch_size: int = 500,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Indexe tous les fichiers dans Elasticsearch.
    
    Args:
        es_client: Client Elasticsearch
        files: Liste des fichiers à indexer
        batch_size: Taille des batches d'indexation
        verbose: Si True, affiche les détails des erreurs
        
    Returns:
        Statistiques d'indexation
    """
    total_stats = {
        "total_offers": 0,
        "indexed": 0,
        "duplicates": 0,
        "errors": 0,
        "files_processed": 0,
        "error_details": {}
    }
    
    for file_path in files:
        print(f"\n📄 Traitement de {file_path.name}...")
        
        offers = load_jsonl_file(file_path)
        if not offers:
            print(f"⚠ Aucune offre trouvée dans {file_path.name}")
            continue
        
        print(f"   → {len(offers)} offres chargées")
        
        # Indexer en batch
        stats = es_client.bulk_index_offers(offers, batch_size=batch_size, verbose=verbose)
        
        if stats['duplicates'] > 0:
            print(f"   ✓ {stats['indexed']} indexées, {stats['duplicates']} doublons, {stats['errors']} erreurs")
        else:
            print(f"   ✓ {stats['indexed']} indexées, {stats['errors']} erreurs")
        
        total_stats["total_offers"] += len(offers)
        total_stats["indexed"] += stats["indexed"]
        total_stats["duplicates"] += stats.get("duplicates", 0)
        total_stats["errors"] += stats["errors"]
        total_stats["files_processed"] += 1
        
        # Accumuler les types d'erreurs
        for error_type, count in stats.get("error_details", {}).items():
            total_stats["error_details"][error_type] = total_stats["error_details"].get(error_type, 0) + count
    
    return total_stats


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Indexe les offres d'emploi normalisées dans Elasticsearch"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="francetravail",
        help="Source des données (francetravail, apec, etc.)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Nom d'un fichier spécifique à indexer (optionnel)"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data"),
        help="Répertoire racine des données"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recrée l'index (supprime les données existantes)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Taille des batches d'indexation"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche les détails des erreurs"
    )
    
    args = parser.parse_args()
    
    # Charger les variables d'environnement
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Variables d'environnement chargées depuis {env_path}")
    else:
        print(f"⚠ Fichier .env non trouvé ({env_path}). Utilisation des valeurs par défaut.")
    
    # Initialiser le client Elasticsearch
    try:
        print(f"\n🔌 Connexion à Elasticsearch...")
        es_client = ElasticsearchClient()
    except Exception as e:
        print(f"\n❌ Impossible de se connecter à Elasticsearch: {e}")
        print("\nAssurez-vous que Elasticsearch est démarré:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    # Créer l'index
    print(f"\n📑 Configuration de l'index...")
    try:
        es_client.create_index(force=args.force)
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de l'index: {e}")
        sys.exit(1)
    
    # Récupérer les fichiers à indexer
    print(f"\n📂 Recherche des fichiers à indexer...")
    files = get_normalized_files(args.source, args.data_dir, args.file)
    
    if not files:
        print("❌ Aucun fichier à indexer")
        sys.exit(1)
    
    print(f"✓ {len(files)} fichier(s) trouvé(s)")
    
    # Indexer les fichiers
    print(f"\n🚀 Indexation en cours...")
    stats = index_files(es_client, files, batch_size=args.batch_size, verbose=args.verbose)
    
    # Forcer le refresh de l'index pour que les stats soient à jour
    es_client.client.indices.refresh(index=es_client.index_name)
    
    # Afficher le résumé
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ DE L'INDEXATION")
    print(f"{'='*60}")
    print(f"Fichiers traités    : {stats['files_processed']}")
    print(f"Offres totales      : {stats['total_offers']}")
    print(f"Offres indexées     : {stats['indexed']}")
    print(f"Doublons ignorés    : {stats['duplicates']}")
    print(f"Erreurs             : {stats['errors']}")
    if stats['total_offers'] > 0:
        success_rate = (stats['indexed'] / stats['total_offers']) * 100
        print(f"Taux de succès      : {success_rate:.1f}%")
    
    # Afficher le détail des types d'erreurs s'il y en a
    if stats.get('error_details'):
        print(f"\n📋 Types d'erreurs:")
        for error_type, count in sorted(stats['error_details'].items(), key=lambda x: x[1], reverse=True):
            print(f"   - {error_type}: {count}")
    
    print(f"{'='*60}")
    
    # Afficher les statistiques de l'index
    try:
        index_stats = es_client.get_stats()
        print(f"\n📈 Statistiques de l'index '{index_stats['index_name']}':")
        print(f"Documents totaux    : {index_stats['total_documents']}")
        print(f"Taille              : {index_stats['size_in_bytes'] / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"⚠ Impossible de récupérer les statistiques: {e}")
    
    print(f"\n✅ Indexation terminée!")
    print(f"\n💡 Accès:")
    print(f"   - Elasticsearch: {es_client.host}")
    print(f"   - Kibana: http://localhost:5601")
    print(f"   - Index: {es_client.index_name}")


if __name__ == "__main__":
    main()
