#!/usr/bin/env python3
"""
Analyse des codes ROME dans les offres normalisées France Travail.

Ce script parcourt les fichiers JSONL du dossier data/normalized/francetravail
et analyse la distribution des codes ROME (rome_code et rome_label).
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


def analyze_rome_codes(data_dir: Path) -> None:
    """Analyse les codes ROME dans tous les fichiers normalisés."""
    
    # Collecte des données
    all_rome_codes = []
    all_rome_labels = []
    rome_code_to_label = {}
    stats_by_file = {}
    
    # Parcourir tous les fichiers JSONL
    jsonl_files = sorted([f for f in data_dir.glob("*.jsonl") if f.is_file()])
    
    if not jsonl_files:
        print(f"Aucun fichier JSONL trouvé dans {data_dir}")
        return
    
    print(f"=== Analyse des codes ROME ===\n")
    print(f"Dossier: {data_dir}")
    print(f"Fichiers trouvés: {len(jsonl_files)}\n")
    
    for file_path in jsonl_files:
        offers = load_offers(file_path)
        
        file_rome_codes = []
        for offer in offers:
            rome_code = offer.get('rome_code')
            rome_label = offer.get('rome_label')
            
            if rome_code:
                file_rome_codes.append(rome_code)
                all_rome_codes.append(rome_code)
                
                if rome_label:
                    all_rome_labels.append(rome_label)
                    rome_code_to_label[rome_code] = rome_label
        
        stats_by_file[file_path.name] = {
            'total_offers': len(offers),
            'with_rome_code': len(file_rome_codes),
            'unique_rome_codes': len(set(file_rome_codes)),
            'rome_codes': Counter(file_rome_codes)
        }
    
    # Affichage des résultats par fichier
    print("=== Statistiques par fichier ===\n")
    for filename, stats in stats_by_file.items():
        print(f"📄 {filename}")
        print(f"   Total offres: {stats['total_offers']}")
        print(f"   Offres avec code ROME: {stats['with_rome_code']}")
        print(f"   Codes ROME uniques: {stats['unique_rome_codes']}")
        
        if stats['rome_codes']:
            print(f"   Distribution:")
            for rome_code, count in stats['rome_codes'].most_common():
                label = rome_code_to_label.get(rome_code, 'N/A')
                print(f"      • {rome_code} ({label}): {count} offres")
        print()
    
    # Statistiques globales
    print("=== Statistiques globales ===\n")
    total_offers = sum(s['total_offers'] for s in stats_by_file.values())
    total_with_rome = len(all_rome_codes)
    unique_rome_codes = len(set(all_rome_codes))
    
    print(f"Total d'offres: {total_offers}")
    print(f"Offres avec code ROME: {total_with_rome} ({100*total_with_rome/total_offers:.1f}%)")
    print(f"Codes ROME uniques: {unique_rome_codes}\n")
    
    # Distribution globale des codes ROME
    print("=== Distribution globale des codes ROME ===\n")
    rome_counter = Counter(all_rome_codes)
    
    for rome_code, count in rome_counter.most_common():
        label = rome_code_to_label.get(rome_code, 'N/A')
        percentage = 100 * count / total_with_rome
        print(f"{rome_code} - {label}")
        print(f"   {count} offres ({percentage:.1f}%)")
        print()
    
    # Mapping code -> libellé
    if rome_code_to_label:
        print("=== Mapping Code ROME -> Libellé ===\n")
        for code in sorted(rome_code_to_label.keys()):
            print(f"{code}: {rome_code_to_label[code]}")


def main():
    """Point d'entrée principal."""
    # Chemin relatif au script
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    data_dir = project_root / "data" / "normalized" / "francetravail"
    
    if not data_dir.exists():
        print(f"Erreur: Le dossier {data_dir} n'existe pas.")
        return
    
    analyze_rome_codes(data_dir)


if __name__ == "__main__":
    main()
