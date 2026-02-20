"""
Test de la détection du télétravail dans les offres d'emploi.

Ce script teste la fonction de détection du télétravail sur les données
collectées depuis l'API France Travail.
"""

import json
from pathlib import Path
from collections import Counter

# Import de la fonction de détection
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from pipelines.ingest.sources.francetravail.mapping import _detect_remote_work, _extract_remote_type


def analyze_remote_work():
    """Analyse la présence du télétravail dans les offres collectées."""
    
    # Chemins des données
    data_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "francetravail"
    
    if not data_dir.exists():
        print(f"❌ Répertoire de données introuvable : {data_dir}")
        return
    
    # Lire toutes les offres
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
    
    # Analyse de la détection
    remote_count = 0
    non_remote_count = 0
    remote_examples = []
    
    for offer in all_offers:
        description = offer.get("description", "")
        is_remote = _detect_remote_work(description)
        
        if is_remote:
            remote_count += 1
            # Garder quelques exemples
            if len(remote_examples) < 5:
                title = offer.get("intitule", "Sans titre")
                # Extraire la partie pertinente de la description
                desc_lower = description.lower()
                snippet = ""
                for keyword in ["télétravail", "teletravail", "remote", "home office"]:
                    idx = desc_lower.find(keyword)
                    if idx != -1:
                        start = max(0, idx - 40)
                        end = min(len(description), idx + 60)
                        snippet = "..." + description[start:end] + "..."
                        break
                
                remote_examples.append({
                    "id": offer.get("id"),
                    "title": title,
                    "snippet": snippet
                })
        else:
            non_remote_count += 1
    
    # Affichage des résultats
    total = len(all_offers)
    remote_percent = (remote_count / total * 100) if total > 0 else 0
    
    print(f"✅ Offres avec télétravail détecté : {remote_count} ({remote_percent:.1f}%)")
    print(f"❌ Offres sans télétravail : {non_remote_count} ({100-remote_percent:.1f}%)")
    
    if remote_examples:
        print(f"\n📝 Exemples d'offres avec télétravail (5 premiers) :\n")
        for i, example in enumerate(remote_examples, 1):
            print(f"{i}. {example['title']} (ID: {example['id']})")
            print(f"   {example['snippet']}\n")
    
    # Statistiques par mot-clé
    print(f"\n🔍 Analyse des patterns détectés :\n")
    patterns_count = Counter()
    
    for offer in all_offers:
        description = offer.get("description", "")
        if _detect_remote_work(description):
            desc_lower = description.lower()
            if "télétravail" in desc_lower or "teletravail" in desc_lower:
                patterns_count["télétravail"] += 1
            if "remote" in desc_lower:
                patterns_count["remote"] += 1
            if "travail à distance" in desc_lower or "travail a distance" in desc_lower:
                patterns_count["travail à distance"] += 1
            if "home office" in desc_lower:
                patterns_count["home office"] += 1
            if "hybrid" in desc_lower:
                patterns_count["hybrid"] += 1
    
    for pattern, count in patterns_count.most_common():
        print(f"   {pattern:20} : {count} offres")
    
    # Analyse par type de télétravail
    print(f"\n📊 Répartition par type de télétravail :\n")
    type_count = Counter()
    type_examples = {"full_remote": [], "hybrid": [], "occasional": []}
    
    for offer in all_offers:
        description = offer.get("description", "")
        if _detect_remote_work(description):
            remote_type = _extract_remote_type(description)
            if remote_type:
                type_count[remote_type] += 1
                
                # Garder 2 exemples par type
                if len(type_examples.get(remote_type, [])) < 2:
                    title = offer.get("intitule", "Sans titre")
                    desc_lower = description.lower()
                    snippet = ""
                    keywords = ["télétravail", "remote", "hybrid", "jours"]
                    for keyword in keywords:
                        idx = desc_lower.find(keyword)
                        if idx != -1:
                            start = max(0, idx - 40)
                            end = min(len(description), idx + 60)
                            snippet = "..." + description[start:end] + "..."
                            break
                    
                    type_examples[remote_type].append({
                        "id": offer.get("id"),
                        "title": title,
                        "snippet": snippet
                    })
    
    # Affichage stats par type
    for remote_type, count in type_count.most_common():
        percentage = (count / remote_count * 100) if remote_count > 0 else 0
        type_label = {
            "full_remote": "🌍 Full Remote",
            "hybrid": "🏢 Hybride",
            "occasional": "📌 Occasionnel"
        }.get(remote_type, remote_type)
        print(f"   {type_label:<25} : {count:>4} offres ({percentage:>5.1f}%)")
    
    # Affichage exemples par type
    if any(type_examples.values()):
        print(f"\n📝 Exemples par type :\n")
        for remote_type in ["full_remote", "hybrid", "occasional"]:
            examples = type_examples.get(remote_type, [])
            if not examples:
                continue
            
            type_label = {
                "full_remote": "🌍 Full Remote",
                "hybrid": "🏢 Hybride",
                "occasional": "📌 Occasionnel"
            }.get(remote_type)
            
            print(f"{type_label} :")
            for example in examples:
                print(f"  • {example['title']}")
                if example['snippet']:
                    print(f"    {example['snippet']}")
            print()


if __name__ == "__main__":
    print("=" * 70)
    print("Test de détection du télétravail dans les offres d'emploi")
    print("=" * 70)
    print()
    
    analyze_remote_work()
    
    print("\n" + "=" * 70)
    print("✅ Analyse terminée")
    print("=" * 70)
