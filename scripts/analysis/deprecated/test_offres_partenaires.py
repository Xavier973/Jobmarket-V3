"""
Test pour voir si l'API supporte le paramètre offresPartenaires.
"""
import os
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from pipelines.ingest.sources.francetravail.client import FranceTravailClient

def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

_load_env_file(Path("config/.env"))
client = FranceTravailClient()

# Test SANS offres partenaires
params1 = {"motsCles": "data engineer", "page": 0, "size": 50}
print("Test 1: SANS offresPartenaires")
print(f"Paramètres: {params1}")
response1 = client.search_offers(params1)
count1 = len(response1.get("resultats", []))
print(f"Résultats: {count1} offres\n")

# Test AVEC offres partenaires
params2 = {"motsCles": "data engineer", "page": 0, "size": 50, "offresPartenaires": "true"}
print("Test 2: AVEC offresPartenaires=true")
print(f"Paramètres: {params2}")
try:
    response2 = client.search_offers(params2)
    count2 = len(response2.get("resultats", []))
    print(f"Résultats: {count2} offres")
    
    # Analyser les métadonnées
    filtres2 = response2.get("filtresPossibles", [])
    for filtre in filtres2:
        if filtre.get("filtre") == "typeContrat":
            print(f"\nTypes de contrat avec partenaires:")
            for agr in filtre.get("agregation", []):
                print(f"  - {agr.get('valeurPossible')}: {agr.get('nbResultats')} offres")
except Exception as e:
    print(f"Erreur: {e}")
    print("Le paramètre 'offresPartenaires' n'est peut-être pas supporté par l'API")
