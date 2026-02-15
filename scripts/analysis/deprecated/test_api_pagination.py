"""
Test de l'API France Travail pour voir les métadonnées de pagination.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
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

# Test avec "data engineer"
params = {"motsCles": "data engineer", "page": 0, "size": 50}
print(f"🔍 Test avec paramètres : {params}\n")

response = client.search_offers(params)

# Afficher les métadonnées
print("📊 Métadonnées de la réponse :")
print(f"   Clés disponibles : {list(response.keys())}\n")

# Nombre de résultats
resultats = response.get("resultats", [])
print(f"   Nombre de résultats : {len(resultats)}")

# Autres champs pertinents
for key in ["filtresPossibles", "contentRange", "range"]:
    if key in response:
        print(f"   {key} : {response[key]}")

# Vérifier s'il y a un champ de pagination
if "filtresPossibles" in response:
    print(f"\n📄 Filtres possibles : {response['filtresPossibles']}")

# Test page 1
print(f"\n🔍 Test page 1...")
params["page"] = 1
response2 = client.search_offers(params)
resultats2 = response2.get("resultats", [])
print(f"   Nombre de résultats page 1 : {len(resultats2)}")

# Comparer les IDs
ids_page0 = {r["id"] for r in resultats}
ids_page1 = {r["id"] for r in resultats2}
overlap = ids_page0 & ids_page1

print(f"\n🔄 Analyse des doublons :")
print(f"   IDs uniques page 0 : {len(ids_page0)}")
print(f"   IDs uniques page 1 : {len(ids_page1)}")
print(f"   IDs en commun : {len(overlap)}")
print(f"   Pourcentage de doublons : {len(overlap)/len(ids_page1)*100:.1f}%")
