"""
Script de détection des doublons inter-fichiers dans les offres France Travail.

Ce script identifie les offres qui apparaissent dans plusieurs fichiers différents
du dossier data/normalized/francetravail.

Usage:
    python scripts/analysis/find_cross_file_duplicates.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


def load_offers_from_file(file_path: Path) -> Dict[str, dict]:
    """
    Charge toutes les offres d'un fichier JSONL.
    
    Args:
        file_path: Chemin du fichier à charger
    
    Returns:
        Dictionnaire {id: offer_data}
    """
    offers = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                offer_id = record.get('id')
                
                if offer_id:
                    offers[offer_id] = record
                else:
                    print(f"  ⚠️  {file_path.name} ligne {line_num}: pas d'ID trouvé")
            
            except json.JSONDecodeError as e:
                print(f"  ⚠️  {file_path.name} ligne {line_num}: erreur JSON - {e}")
    
    return offers


def find_cross_file_duplicates(directory: Path) -> Dict:
    """
    Identifie les offres présentes dans plusieurs fichiers.
    
    Args:
        directory: Dossier contenant les fichiers JSONL
    
    Returns:
        Dictionnaire avec les statistiques et détails
    """
    # Récupérer tous les fichiers JSONL (hors dédupliqués)
    jsonl_files = [
        f for f in directory.glob("*.jsonl")
        if not f.stem.endswith('_deduplicate')
    ]
    
    if not jsonl_files:
        print(f"ℹ️  Aucun fichier JSONL trouvé dans {directory}")
        return {}
    
    # Tracker dans quels fichiers chaque ID apparaît
    id_to_files: Dict[str, List[str]] = defaultdict(list)
    file_offers: Dict[str, Dict[str, dict]] = {}
    
    print(f"📁 Chargement des fichiers depuis: {directory.relative_to(Path.cwd())}\n")
    
    # Charger tous les fichiers
    for file_path in sorted(jsonl_files):
        print(f"  📄 Chargement: {file_path.name}")
        offers = load_offers_from_file(file_path)
        file_offers[file_path.name] = offers
        
        print(f"     Offres chargées: {len(offers)}")
        
        # Enregistrer dans quels fichiers chaque ID apparaît
        for offer_id in offers.keys():
            id_to_files[offer_id].append(file_path.name)
    
    print()
    
    # Identifier les IDs présents dans plusieurs fichiers
    cross_file_duplicates = {
        offer_id: files
        for offer_id, files in id_to_files.items()
        if len(files) > 1
    }
    
    # Créer un rapport détaillé
    duplicate_details = []
    for offer_id, files in sorted(cross_file_duplicates.items(), 
                                   key=lambda x: len(x[1]), 
                                   reverse=True):
        # Prendre les infos de la première occurrence
        first_file = files[0]
        offer_data = file_offers[first_file][offer_id]
        
        detail = {
            'id': offer_id,
            'title': offer_data.get('title', 'N/A'),
            'company': offer_data.get('company_name', 'N/A'),
            'files': files,
            'occurrences': len(files)
        }
        duplicate_details.append(detail)
    
    # Statistiques globales
    total_unique_ids = len(id_to_files)
    total_offers = sum(len(offers) for offers in file_offers.values())
    duplicate_ids = len(cross_file_duplicates)
    duplicate_offers = sum(len(files) - 1 for files in cross_file_duplicates.values())
    
    return {
        'total_files': len(jsonl_files),
        'total_offers': total_offers,
        'total_unique_ids': total_unique_ids,
        'duplicate_ids': duplicate_ids,
        'duplicate_offers': duplicate_offers,
        'details': duplicate_details,
        'file_offers': file_offers
    }


def print_detailed_report(stats: Dict, show_all: bool = False):
    """
    Affiche un rapport détaillé des doublons inter-fichiers.
    
    Args:
        stats: Statistiques retournées par find_cross_file_duplicates
        show_all: Afficher tous les doublons (sinon limité à 10)
    """
    print("=" * 80)
    print(" 📊 RÉSULTATS DE L'ANALYSE")
    print("=" * 80)
    print(f"  Fichiers analysés: {stats['total_files']}")
    print(f"  Offres totales: {stats['total_offers']}")
    print(f"  IDs uniques: {stats['total_unique_ids']}")
    print(f"  IDs en doublon entre fichiers: {stats['duplicate_ids']}")
    print(f"  Offres redondantes: {stats['duplicate_offers']}")
    
    if stats['duplicate_offers'] > 0:
        redundancy_rate = (stats['duplicate_offers'] / stats['total_offers']) * 100
        print(f"  Taux de redondance: {redundancy_rate:.2f}%")
    
    print()
    
    if stats['details']:
        print("=" * 80)
        print(" 📋 DÉTAILS DES DOUBLONS INTER-FICHIERS")
        print("=" * 80)
        
        limit = None if show_all else 10
        details_to_show = stats['details'][:limit] if limit else stats['details']
        
        for i, detail in enumerate(details_to_show, 1):
            print(f"\n{i}. ID: {detail['id']}")
            print(f"   Titre: {detail['title'][:70]}...")
            if isinstance(detail['company'], str):
                print(f"   Entreprise: {detail['company'][:50]}...")
            print(f"   Présent dans {detail['occurrences']} fichiers:")
            for file_name in detail['files']:
                print(f"      • {file_name}")
        
        if limit and len(stats['details']) > limit:
            print(f"\n... et {len(stats['details']) - limit} autres offres en doublon")
            print(f"\n💡 Pour voir tous les doublons, modifiez show_all=True dans le script")
    
    # Matrice de chevauchement
    print("\n" + "=" * 80)
    print(" 🔀 MATRICE DE CHEVAUCHEMENT ENTRE FICHIERS")
    print("=" * 80)
    
    file_names = sorted(stats['file_offers'].keys())
    overlap_matrix = {}
    
    for file1 in file_names:
        overlap_matrix[file1] = {}
        ids1 = set(stats['file_offers'][file1].keys())
        
        for file2 in file_names:
            if file1 == file2:
                overlap_matrix[file1][file2] = len(ids1)
            else:
                ids2 = set(stats['file_offers'][file2].keys())
                overlap = len(ids1 & ids2)
                overlap_matrix[file1][file2] = overlap
    
    # Afficher la matrice
    print("\nNombre d'offres communes entre fichiers:")
    print()
    
    # Raccourcir les noms de fichiers pour l'affichage
    short_names = {name: name.replace('offers_kw_', '').replace('.jsonl', '') 
                   for name in file_names}
    
    for file1 in file_names:
        print(f"\n{short_names[file1]}:")
        for file2 in file_names:
            if file1 != file2:
                overlap = overlap_matrix[file1][file2]
                if overlap > 0:
                    total1 = overlap_matrix[file1][file1]
                    percentage = (overlap / total1) * 100
                    print(f"  ↔ {short_names[file2]}: {overlap} offres ({percentage:.1f}%)")


def main():
    """Point d'entrée principal du script."""
    print("=" * 80)
    print(" 🔍 Détection des doublons INTER-FICHIERS")
    print("=" * 80)
    print()
    
    # Définir le chemin du dossier normalisé
    base_path = Path(__file__).parent.parent.parent
    normalized_dir = base_path / "data" / "normalized" / "francetravail"
    
    # Analyser les fichiers
    stats = find_cross_file_duplicates(normalized_dir)
    
    if stats:
        # Afficher le rapport détaillé
        print_detailed_report(stats, show_all=False)
        
        if stats['duplicate_ids'] > 0:
            print("\n" + "=" * 80)
            print(" 💡 RECOMMANDATIONS")
            print("=" * 80)
            print("\nLes offres apparaissent dans plusieurs fichiers car elles correspondent")
            print("à plusieurs mots-clés de recherche différents.")
            print("\nCeci est normal et attendu. Pour une analyse globale, vous pouvez:")
            print("  • Fusionner tous les fichiers en supprimant les doublons")
            print("  • Ou analyser chaque fichier indépendamment selon vos besoins")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
