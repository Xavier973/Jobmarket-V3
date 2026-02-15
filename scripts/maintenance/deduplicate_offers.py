"""
Script de déduplication des fichiers JSONL d'offres France Travail.

Ce script détecte et supprime les doublons dans les fichiers JSONL
basés sur le champ "id". Les fichiers dédupliqués sont sauvegardés
avec le suffixe "_deduplicate.jsonl".

Usage:
    python scripts/maintenance/deduplicate_offers.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set


def deduplicate_jsonl_file(input_path: Path, output_path: Path) -> Dict[str, int]:
    """
    Déduplique un fichier JSONL basé sur le champ 'id'.
    
    Args:
        input_path: Chemin du fichier source
        output_path: Chemin du fichier de sortie dédupliqué
    
    Returns:
        Dictionnaire avec les statistiques (total, unique, doublons)
    """
    seen_ids: Set[str] = set()
    unique_records: List[dict] = []
    total_count = 0
    duplicate_count = 0
    
    # Lecture et déduplication
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                total_count += 1
                
                record_id = record.get('id')
                if not record_id:
                    print(f"  ⚠️  Ligne {line_num}: pas d'ID trouvé, ignorée")
                    continue
                
                if record_id in seen_ids:
                    duplicate_count += 1
                else:
                    seen_ids.add(record_id)
                    unique_records.append(record)
            
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Ligne {line_num}: erreur JSON - {e}")
                continue
    
    # Écriture du fichier dédupliqué
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in unique_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    unique_count = len(unique_records)
    
    return {
        'total': total_count,
        'unique': unique_count,
        'duplicates': duplicate_count
    }


def process_directory(directory: Path) -> None:
    """
    Traite tous les fichiers JSONL d'un dossier.
    
    Args:
        directory: Chemin du dossier à traiter
    """
    if not directory.exists():
        print(f"❌ Dossier non trouvé: {directory}")
        return
    
    jsonl_files = list(directory.glob("*.jsonl"))
    
    if not jsonl_files:
        print(f"ℹ️  Aucun fichier JSONL trouvé dans {directory}")
        return
    
    print(f"\n📁 Traitement de: {directory}")
    print(f"   Fichiers trouvés: {len(jsonl_files)}")
    
    for input_file in jsonl_files:
        # Ignorer les fichiers déjà dédupliqués
        if "_deduplicate" in input_file.stem:
            print(f"  ⏭️  Ignoré (déjà dédupliqué): {input_file.name}")
            continue
        
        # Créer le nom du fichier de sortie
        output_file = input_file.parent / f"{input_file.stem}_deduplicate.jsonl"
        
        print(f"\n  🔍 {input_file.name}")
        
        stats = deduplicate_jsonl_file(input_file, output_file)
        
        print(f"     ✅ Total: {stats['total']}")
        print(f"     ✅ Unique: {stats['unique']}")
        print(f"     🗑️  Doublons supprimés: {stats['duplicates']}")
        print(f"     💾 Sauvegardé: {output_file.name}")


def main():
    """Point d'entrée principal du script."""
    print("=" * 70)
    print("🧹 Script de déduplication des offres France Travail")
    print("=" * 70)
    
    # Définir les chemins des dossiers
    base_path = Path(__file__).parent.parent.parent
    
    directories = [
        base_path / "data" / "raw" / "francetravail",
        base_path / "data" / "normalized" / "francetravail"
    ]
    
    # Traiter chaque dossier
    for directory in directories:
        process_directory(directory)
    
    print("\n" + "=" * 70)
    print("✅ Déduplication terminée!")
    print("=" * 70)


if __name__ == "__main__":
    main()
