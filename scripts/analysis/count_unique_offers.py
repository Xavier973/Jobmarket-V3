"""
Compte le nombre d'offres uniques dans un fichier JSONL.
Détecte les doublons par ID.

Usage:
    python scripts/analysis/count_unique_offers.py data/raw/francetravail/offers_kw_data_analyst.jsonl
"""
import json
import sys
from pathlib import Path
from collections import Counter

def count_unique_offers(filepath: Path):
    """Compte les offres uniques et détecte les doublons."""
    
    if not filepath.exists():
        print(f"❌ Fichier introuvable : {filepath}")
        return
    
    seen_ids = set()
    duplicate_count = 0
    id_frequencies = Counter()
    total_lines = 0
    
    print(f"📊 Analyse de {filepath.name}...\n")
    
    with filepath.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            
            try:
                offer = json.loads(line)
                offer_id = offer.get("id")
                
                if offer_id:
                    id_frequencies[offer_id] += 1
                    if offer_id in seen_ids:
                        duplicate_count += 1
                    else:
                        seen_ids.add(offer_id)
                        
            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur ligne {line_num}: {e}")
    
    unique_count = len(seen_ids)
    
    print(f"📈 Résultats :")
    print(f"   Total de lignes      : {total_lines:,}")
    print(f"   Offres uniques       : {unique_count:,}")
    print(f"   Doublons détectés    : {duplicate_count:,}")
    print(f"   Taux de duplication  : {(duplicate_count/total_lines*100):.1f}%\n")
    
    # Top des IDs les plus dupliqués
    most_common = id_frequencies.most_common(10)
    if any(count > 1 for _, count in most_common):
        print(f"🔁 Top 10 des offres les plus dupliquées :")
        for offer_id, count in most_common:
            if count > 1:
                print(f"   {offer_id}: {count} fois")
    
    # Taille du fichier
    file_size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"\n💾 Taille du fichier : {file_size_mb:.2f} Mo")
    print(f"   Taille estimée sans doublons : {file_size_mb * unique_count / total_lines:.2f} Mo")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/analysis/count_unique_offers.py <chemin_fichier.jsonl>")
        print("\nExemple:")
        print("  python scripts/analysis/count_unique_offers.py data/raw/francetravail/offers_kw_data_analyst.jsonl")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    count_unique_offers(filepath)
