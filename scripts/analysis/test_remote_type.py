"""
Test de l'extraction du type de télétravail dans les offres d'emploi.

Ce script teste la fonction d'extraction du type de télétravail sur les données
collectées depuis l'API France Travail.
"""

import json
from pathlib import Path
from collections import Counter

# Import des fonctions
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from pipelines.ingest.sources.francetravail.mapping import _extract_remote_type


def analyze_remote_types():
    """Analyse la répartition des types de télétravail dans les offres collectées."""
    
    # Chemins des données
    data_dir = Path(__file__).parent.parent.parent / "data" / "normalized" / "francetravail"
    
    if not data_dir.exists():
        print(f"❌ Répertoire de données introuvable : {data_dir}")
        return
    
    # Lire toutes les offres normalisées
    all_offers = []
    for file in data_dir.glob("*.jsonl"):
        print(f"📂 Lecture de {file.name}...")
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    offer = json.loads(line.strip())
                    all_offers.append(offer)
                except json.JSONDecodeError:
                    continue
    
    if not all_offers:
        print("❌ Aucune offre trouvée")
        return
    
    print(f"\n📊 Analyse de {len(all_offers)} offres\n")
    
    # Comptage par type
    type_counter = Counter()
    examples_by_type = {
        "full_remote": [],
        "hybrid": [],
        "occasional": []
    }
    
    for offer in all_offers:
        remote_type = offer.get("remote_type")
        is_remote = offer.get("is_remote")
        
        if remote_type:
            type_counter[remote_type] += 1
            
            # Garder quelques exemples
            if len(examples_by_type.get(remote_type, [])) < 3:
                title = offer.get("title", "Sans titre")
                description = offer.get("description", "")
                
                # Extraire un snippet pertinent
                desc_lower = description.lower()
                snippet = ""
                keywords = ["télétravail", "remote", "hybrid", "jours"]
                for keyword in keywords:
                    idx = desc_lower.find(keyword)
                    if idx != -1:
                        start = max(0, idx - 50)
                        end = min(len(description), idx + 100)
                        snippet = "..." + description[start:end] + "..."
                        break
                
                examples_by_type[remote_type].append({
                    "id": offer.get("id"),
                    "title": title,
                    "snippet": snippet
                })
        elif is_remote:
            type_counter["none_detected"] += 1
    
    # Comptage des offres sans télétravail
    no_remote_count = sum(1 for o in all_offers if not o.get("is_remote"))
    
    # Affichage des résultats
    total = len(all_offers)
    remote_total = sum(type_counter.values())
    
    print(f"{'='*70}")
    print(f"📊 RÉPARTITION PAR TYPE DE TÉLÉTRAVAIL")
    print(f"{'='*70}\n")
    
    print(f"Total offres analysées        : {total}")
    print(f"Offres SANS télétravail      : {no_remote_count} ({no_remote_count/total*100:.1f}%)")
    print(f"Offres AVEC télétravail      : {remote_total} ({remote_total/total*100:.1f}%)\n")
    
    print(f"{'Type':<20} {'Nombre':<10} {'%':<10}")
    print(f"{'-'*40}")
    
    for remote_type, count in type_counter.most_common():
        percentage = (count / remote_total * 100) if remote_total > 0 else 0
        
        type_label = {
            "full_remote": "🌍 Full Remote",
            "hybrid": "🏢 Hybride",
            "occasional": "📌 Occasionnel",
            "none_detected": "❓ Type non détecté"
        }.get(remote_type, remote_type)
        
        print(f"{type_label:<20} {count:<10} {percentage:>6.1f}%")
    
    # Exemples détaillés
    print(f"\n{'='*70}")
    print(f"📝 EXEMPLES PAR TYPE")
    print(f"{'='*70}\n")
    
    for remote_type in ["full_remote", "hybrid", "occasional"]:
        examples = examples_by_type.get(remote_type, [])
        if not examples:
            continue
        
        type_label = {
            "full_remote": "🌍 Full Remote (100% télétravail)",
            "hybrid": "🏢 Hybride (X jours/semaine)",
            "occasional": "📌 Occasionnel (possibilité)"
        }.get(remote_type)
        
        print(f"\n{type_label}")
        print(f"{'-'*70}\n")
        
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example['title']} (ID: {example['id']})")
            if example['snippet']:
                print(f"   {example['snippet']}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("Test d'extraction du type de télétravail")
    print("=" * 70)
    print()
    
    analyze_remote_types()
    
    print("\n" + "=" * 70)
    print("✅ Analyse terminée")
    print("=" * 70)
