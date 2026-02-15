"""
Explore les filtres disponibles dans l'API France Travail pour découper davantage les résultats.
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

# Test avec CDI seulement pour "data engineer"
params = {
    "motsCles": "data engineer",
    "typeContrat": "CDI",
    "page": 0,
    "size": 50
}

print(f"🔍 Test avec: {params}\n")
response = client.search_offers(params)

# Analyser les filtres possibles
filtres = response.get("filtresPossibles", [])
print(f"📊 Filtres disponibles dans l'API:\n")

for filtre_group in filtres:
    filtre_name = filtre_group.get("filtre")
    agregations = filtre_group.get("agregation", [])
    
    print(f"  🔹 {filtre_name}:")
    
    # Trier par nombre de résultats décroissant
    agregations_sorted = sorted(agregations, key=lambda x: x.get("nbResultats", 0), reverse=True)
    
    for agr in agregations_sorted[:10]:  # Top 10
        valeur = agr.get("valeurPossible")
        nb = agr.get("nbResultats", 0)
        print(f"     - {valeur}: {nb} offres")
    
    if len(agregations) > 10:
        print(f"     ... et {len(agregations) - 10} autres valeurs")
    print()

# Nombre total de résultats pour CDI
resultats = response.get("resultats", [])
print(f"💡 Nombre de résultats retournés pour CDI: {len(resultats)}")
print(f"   (limité à 150 même s'il y en a plus)")
