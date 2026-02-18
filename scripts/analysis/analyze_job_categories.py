#!/usr/bin/env python3
"""
Analyse des catégories de poste (job_category) dans les offres normalisées France Travail.

Ce script parcourt les fichiers JSONL du dossier data/normalized/francetravail
et analyse la distribution des catégories de poste.
"""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any


def load_offers(file_path: Path) -> List[Dict[str, Any]]:
    """Charge les offres depuis un fichier JSONL."""
    offers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    return offers


def analyze_job_categories(data_dir: Path) -> None:
    """Analyse les catégories de poste dans tous les fichiers normalisés."""
    
    # Collecte des données
    all_job_categories = []
    stats_by_file = {}
    all_offers_by_id = {}  # Pour dédupliquer globalement par ID
    
    # Parcourir tous les fichiers JSONL
    jsonl_files = sorted([f for f in data_dir.glob("*.jsonl") if f.is_file()])
    
    if not jsonl_files:
        print(f"Aucun fichier JSONL trouvé dans {data_dir}")
        return
    
    print(f"=== Analyse des catégories de poste (job_category) ===\n")
    print(f"Dossier: {data_dir}")
    print(f"Fichiers trouvés: {len(jsonl_files)}\n")
    
    total_raw_offers = 0
    total_duplicates_in_files = 0
    
    for file_path in jsonl_files:
        offers = load_offers(file_path)
        total_raw_offers += len(offers)
        
        # Dédupliquer par ID dans le fichier
        file_offers_by_id = {}
        for offer in offers:
            offer_id = offer.get('id')
            if offer_id:
                file_offers_by_id[offer_id] = offer
        
        duplicates_in_file = len(offers) - len(file_offers_by_id)
        total_duplicates_in_files += duplicates_in_file
        
        # Collecter les catégories (après déduplication dans le fichier)
        file_job_categories = []
        for offer in file_offers_by_id.values():
            job_category = offer.get('job_category')
            
            if job_category:
                file_job_categories.append(job_category)
            
            # Conserver pour la déduplication globale
            offer_id = offer.get('id')
            if offer_id:
                all_offers_by_id[offer_id] = offer
        
        stats_by_file[file_path.name] = {
            'total_offers': len(offers),
            'unique_offers': len(file_offers_by_id),
            'duplicates': duplicates_in_file,
            'with_job_category': len(file_job_categories),
            'unique_job_categories': len(set(file_job_categories)),
            'job_categories': Counter(file_job_categories)
        }
    
    # Affichage des résultats par fichier
    print("=== Statistiques par fichier ===\n")
    for filename, stats in stats_by_file.items():
        print(f"📄 {filename}")
        print(f"   Total offres (brutes): {stats['total_offers']}")
        print(f"   Offres uniques: {stats['unique_offers']}")
        if stats['duplicates'] > 0:
            print(f"   ⚠️  Doublons détectés: {stats['duplicates']}")
        print(f"   Offres avec job_category: {stats['with_job_category']}")
        print(f"   Catégories uniques: {stats['unique_job_categories']}")
        
        if stats['job_categories']:
            print(f"   Top 10 catégories:")
            for category, count in stats['job_categories'].most_common(10):
                print(f"      • {category}: {count} offres")
        print()
    
    # Recompter avec les offres globalement dédupliquées
    all_job_categories = []
    for offer in all_offers_by_id.values():
        job_category = offer.get('job_category')
        if job_category:
            all_job_categories.append(job_category)
    
    # Statistiques globales
    print("\n=== Statistiques globales (après déduplication) ===\n")
    total_unique_offers = len(all_offers_by_id)
    total_duplicates_global = total_raw_offers - total_unique_offers
    offers_with_category = len(all_job_categories)
    all_categories_counter = Counter(all_job_categories)
    
    print(f"Total des offres (brutes): {total_raw_offers}")
    print(f"Doublons totaux: {total_duplicates_global}")
    print(f"Total des offres uniques: {total_unique_offers}")
    print(f"Offres avec job_category: {offers_with_category}")
    print(f"Taux de remplissage: {offers_with_category/total_unique_offers*100:.1f}%")
    print(f"Catégories uniques: {len(all_categories_counter)}")
    
    # Top 20 des catégories les plus fréquentes
    print("\n=== Top 20 des catégories les plus fréquentes ===\n")
    for i, (category, count) in enumerate(all_categories_counter.most_common(20), 1):
        percentage = (count / offers_with_category) * 100
        print(f"{i:2d}. {category}")
        print(f"    {count} offres ({percentage:.1f}%)")
    
    # Catégories rares (1-2 offres)
    rare_categories = [cat for cat, count in all_categories_counter.items() if count <= 2]
    if rare_categories:
        print(f"\n=== Catégories rares (≤ 2 offres) ===\n")
        print(f"Nombre: {len(rare_categories)}")
        print("\nExemples:")
        for cat in sorted(rare_categories)[:10]:
            count = all_categories_counter[cat]
            print(f"   • {cat} ({count} offre{'s' if count > 1 else ''})")
        if len(rare_categories) > 10:
            print(f"   ... et {len(rare_categories) - 10} autres")


def main():
    """Point d'entrée du script."""
    # Chemin vers le dossier des données normalisées
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "normalized" / "francetravail"
    
    if not data_dir.exists():
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas")
        return
    
    analyze_job_categories(data_dir)


if __name__ == "__main__":
    main()
