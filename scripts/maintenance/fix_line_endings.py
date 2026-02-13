"""
Script pour corriger les fins de ligne inhabituelles dans les fichiers JSONL.
"""
import json
from pathlib import Path

def fix_jsonl_line_endings(file_path: Path) -> None:
    """Relit un fichier JSONL et le réécrit avec des fins de ligne standard."""
    if not file_path.exists():
        print(f"Fichier introuvable : {file_path}")
        return
    
    # Lire toutes les lignes
    print(f"📖 Lecture de {file_path.name}...")
    content = file_path.read_text(encoding="utf-8")
    
    # Compter les caractères inhabituels
    ls_count = content.count('\u2028')  # Line Separator
    ps_count = content.count('\u2029')  # Paragraph Separator
    
    if ls_count > 0 or ps_count > 0:
        print(f"⚠️  Caractères inhabituels détectés :")
        print(f"   - Line Separator (LS): {ls_count}")
        print(f"   - Paragraph Separator (PS): {ps_count}")
        
        # Nettoyer
        content = content.replace('\u2028', '\n').replace('\u2029', '\n')
    
    # Parser et réécrire proprement
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    offers = []
    
    for line in lines:
        try:
            offers.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"⚠️  Ligne JSON invalide ignorée : {e}")
    
    print(f"✅ {len(offers)} offres valides trouvées")
    
    # Réécrire avec fins de ligne standard
    print(f"✍️  Réécriture avec fins de ligne standard...")
    with file_path.open("w", encoding="utf-8", newline="") as f:
        for offer in offers:
            f.write(json.dumps(offer, ensure_ascii=False))
            f.write("\n")
    
    print(f"✅ Fichier corrigé : {file_path}")

if __name__ == "__main__":
    # Corriger tous les fichiers JSONL
    raw_dir = Path("data/raw/francetravail")
    normalized_dir = Path("data/normalized/francetravail")
    
    all_files = list(raw_dir.glob("*.jsonl")) + list(normalized_dir.glob("*.jsonl"))
    
    print(f"🔍 {len(all_files)} fichiers JSONL trouvés\n")
    
    for file_path in all_files:
        fix_jsonl_line_endings(file_path)
        print()
