"""
Script pour régénérer les fichiers normalisés sans le champ raw.
Élimine la duplication entre data/raw/ et data/normalized/.

Usage:
    python scripts/maintenance/regenerate_normalized.py
"""
import json
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from pipelines.ingest.normalizer import normalize_offer


def regenerate_normalized_files():
    """Régénère tous les fichiers normalisés à partir des fichiers raw."""
    
    raw_dir = root_dir / "data" / "raw" / "francetravail"
    normalized_dir = root_dir / "data" / "normalized" / "francetravail"
    
    if not raw_dir.exists():
        print(f"❌ Aucun dossier raw trouvé : {raw_dir}")
        return
    
    raw_files = list(raw_dir.glob("*.jsonl"))
    if not raw_files:
        print(f"❌ Aucun fichier JSONL trouvé dans {raw_dir}")
        return
    
    print(f"📁 Fichiers raw trouvés : {len(raw_files)}")
    
    for raw_path in raw_files:
        print(f"\n🔄 Traitement de {raw_path.name}...")
        
        # Lire les offres brutes
        raw_offers = []
        with raw_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    offer = json.loads(line)
                    raw_offers.append(offer)
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Erreur ligne {line_num}: {e}")
        
        print(f"   ✓ {len(raw_offers)} offres brutes lues")
        
        # Normaliser sans le champ raw
        normalized_offers = []
        for offer in raw_offers:
            try:
                normalized = normalize_offer(offer, "francetravail")
                normalized_offers.append(normalized.to_dict())
            except Exception as e:
                print(f"   ⚠️  Erreur de normalisation: {e}")
                continue
        
        print(f"   ✓ {len(normalized_offers)} offres normalisées")
        
        # Écrire le fichier normalisé
        normalized_path = normalized_dir / raw_path.name
        normalized_dir.mkdir(parents=True, exist_ok=True)
        
        with normalized_path.open("w", encoding="utf-8", newline="") as f:
            for offer in normalized_offers:
                json.dump(offer, f, ensure_ascii=False)
                f.write("\n")
        
        # Calculer la réduction de taille
        raw_size = raw_path.stat().st_size
        normalized_size = normalized_path.stat().st_size
        reduction_pct = (1 - normalized_size / raw_size) * 100 if raw_size > 0 else 0
        
        print(f"   ✓ Fichier normalisé sauvegardé : {normalized_path.name}")
        print(f"   📊 Taille brute     : {raw_size:,} octets")
        print(f"   📊 Taille normalisée: {normalized_size:,} octets")
        print(f"   📊 Réduction        : {reduction_pct:.1f}%")
    
    print(f"\n✅ Régénération terminée !")
    print(f"\n💡 Le champ 'raw' a été supprimé des fichiers normalisés.")
    print(f"   Les données complètes restent disponibles dans data/raw/")


if __name__ == "__main__":
    regenerate_normalized_files()
