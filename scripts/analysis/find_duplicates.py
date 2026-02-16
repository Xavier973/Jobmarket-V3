"""
Script de détection des doublons dans les fichiers JSONL d'offres France Travail.

Ce script analyse les fichiers JSONL normalisés et identifie les offres en doublons
basées sur le champ "id". Affiche un rapport détaillé sans modifier les fichiers.

Usage:
    python scripts/analysis/find_duplicates.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


def find_duplicates_in_file(file_path: Path) -> Dict:
    """
    Identifie les doublons dans un fichier JSONL.
    
    Args:
        file_path: Chemin du fichier à analyser
    
    Returns:
        Dictionnaire avec les statistiques et détails des doublons
    """
    seen_ids: Dict[str, List[int]] = defaultdict(list)
    all_offers: List[dict] = []
    total_count = 0
    
    # Lecture du fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                total_count += 1
                all_offers.append(record)
                
                record_id = record.get('id')
                if not record_id:
                    print(f"  ⚠️  Ligne {line_num}: pas d'ID trouvé")
                    continue
                
                # Enregistrer la ligne où cet ID apparaît
                seen_ids[record_id].append(line_num)
            
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Ligne {line_num}: erreur JSON - {e}")
                continue
    
    # Identifier les IDs en doublons (apparaissent plus d'une fois)
    duplicates = {
        offer_id: line_nums 
        for offer_id, line_nums in seen_ids.items() 
        if len(line_nums) > 1
    }
    
    # Créer un rapport détaillé pour chaque doublon
    duplicate_details = []
    for offer_id, line_nums in duplicates.items():
        # Trouver les offres correspondantes
        matching_offers = [
            offer for offer in all_offers 
            if offer.get('id') == offer_id
        ]
        
        if matching_offers:
            detail = {
                'id': offer_id,
                'occurrences': len(line_nums),
                'line_numbers': line_nums,
                'title': matching_offers[0].get('title', 'N/A'),
                'company': matching_offers[0].get('company_name', 'N/A')
            }
            duplicate_details.append(detail)
    
    unique_count = len(seen_ids)
    duplicate_count = sum(len(line_nums) - 1 for line_nums in duplicates.values())
    
    return {
        'total': total_count,
        'unique': unique_count,
        'duplicates': duplicate_count,
        'duplicate_ids': len(duplicates),
        'details': duplicate_details
    }


def analyze_directory(directory: Path, show_details: bool = True) -> Dict:
    """
    Analyse tous les fichiers JSONL d'un dossier.
    
    Args:
        directory: Chemin du dossier à analyser
        show_details: Afficher les détails de chaque doublon
    
    Returns:
        Statistiques globales
    """
    if not directory.exists():
        print(f"❌ Dossier non trouvé: {directory}")
        return {}
    
    jsonl_files = [
        f for f in directory.glob("*.jsonl")
        if not f.stem.endswith('_deduplicate')  # Ignorer les fichiers dédupliqués
    ]
    
    if not jsonl_files:
        print(f"ℹ️  Aucun fichier JSONL trouvé dans {directory}")
        return {}
    
    print(f"\n📁 Analyse du dossier: {directory.relative_to(Path.cwd())}")
    print(f"   Fichiers à analyser: {len(jsonl_files)}\n")
    
    global_stats = {
        'total_files': len(jsonl_files),
        'total_offers': 0,
        'total_duplicates': 0,
        'files_with_duplicates': 0
    }
    
    for file_path in sorted(jsonl_files):
        print(f"  🔍 {file_path.name}")
        
        stats = find_duplicates_in_file(file_path)
        
        global_stats['total_offers'] += stats['total']
        global_stats['total_duplicates'] += stats['duplicates']
        
        print(f"     📊 Total d'offres: {stats['total']}")
        print(f"     ✅ IDs uniques: {stats['unique']}")
        
        if stats['duplicates'] > 0:
            global_stats['files_with_duplicates'] += 1
            print(f"     ⚠️  Doublons trouvés: {stats['duplicates']} (dans {stats['duplicate_ids']} IDs)")
            
            if show_details and stats['details']:
                print(f"\n     📋 Détails des doublons:")
                for detail in stats['details'][:5]:  # Limiter à 5 premiers pour lisibilité
                    print(f"        • ID: {detail['id']}")
                    print(f"          Titre: {detail['title'][:70]}...")
                    print(f"          Occurrences: {detail['occurrences']} (lignes {detail['line_numbers']})")
                
                if len(stats['details']) > 5:
                    print(f"        ... et {len(stats['details']) - 5} autres doublons")
                print()
        else:
            print(f"     ✅ Aucun doublon trouvé")
        
        print()
    
    return global_stats


def main():
    """Point d'entrée principal du script."""
    print("=" * 80)
    print(" 🔍 Détection des doublons dans les offres France Travail")
    print("=" * 80)
    
    # Définir le chemin du dossier normalisé
    base_path = Path(__file__).parent.parent.parent
    normalized_dir = base_path / "data" / "normalized" / "francetravail"
    
    # Analyser le dossier
    stats = analyze_directory(normalized_dir, show_details=True)
    
    # Afficher le résumé global
    if stats:
        print("=" * 80)
        print(" 📊 RÉSUMÉ GLOBAL")
        print("=" * 80)
        print(f"  Fichiers analysés: {stats['total_files']}")
        print(f"  Offres totales: {stats['total_offers']}")
        print(f"  Doublons détectés: {stats['total_duplicates']}")
        print(f"  Fichiers avec doublons: {stats['files_with_duplicates']}")
        
        if stats['total_duplicates'] > 0:
            duplicate_rate = (stats['total_duplicates'] / stats['total_offers']) * 100
            print(f"  Taux de duplication: {duplicate_rate:.2f}%")
            print("\n  💡 Pour nettoyer les doublons, utilisez:")
            print("     python scripts/maintenance/deduplicate_offers.py")
        else:
            print("\n  ✅ Aucun doublon trouvé dans les fichiers !")
        
        print("=" * 80)


if __name__ == "__main__":
    main()
