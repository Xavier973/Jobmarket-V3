import argparse
import os
from pathlib import Path
from typing import Any, Dict, List

from pipelines.ingest.io import write_jsonl
from pipelines.ingest.normalizer import normalize_offer
from pipelines.ingest.sources.francetravail.client import FranceTravailClient


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        return int(value)
    except ValueError:
        return default


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def run(sample: bool = False, rome_codes: List[str] = None, keywords: str = None, limit: int = None) -> None:
    """
    Lance la collecte d'offres depuis l'API France Travail.
    
    Args:
        sample: Mode échantillon (1 page, max 5 résultats)
        rome_codes: Liste de codes ROME pour filtrer (ex: ["M1403", "M1805"])
        keywords: Mots-clés pour la recherche (ex: "data analyst")
        limit: Nombre maximum d'offres à collecter
    """
    _load_env_file(Path("config/.env"))
    output_dir = Path(os.getenv("INGEST_OUTPUT_DIR", "./data"))
    max_pages = _int_env("INGEST_MAX_PAGES", 5)
    page_size = _int_env("INGEST_PAGE_SIZE", 50)

    if sample:
        max_pages = 1
        page_size = min(page_size, 5)

    # Déterminer le nom de fichier selon le contexte
    if keywords:
        kw_str = keywords.replace(" ", "_").replace(",", "_")[:50]
        filename = f"offers_kw_{kw_str}.jsonl"
    elif rome_codes:
        rome_str = "_".join(rome_codes)
        filename = f"offers_rome_{rome_str}.jsonl"
    elif sample:
        filename = "offers_sample.jsonl"
    else:
        filename = "offers.jsonl"
    
    raw_path = output_dir / "raw" / "francetravail" / filename
    normalized_path = output_dir / "normalized" / "francetravail" / filename

    client = FranceTravailClient()
    
    total_collected = 0
    print(f"🔍 Collecte d'offres France Travail")
    if keywords:
        print(f"   Mots-clés : {keywords}")
    if rome_codes:
        print(f"   Codes ROME : {', '.join(rome_codes)}")
    if limit:
        print(f"   Limite : {limit} offres")
    print(f"   Fichier : {filename}\n")

    for page in range(0, max_pages):
        # Construire les paramètres de recherche
        params = {"page": page, "size": page_size}
        
        # Ajouter le filtre par mots-clés si spécifié
        if keywords:
            params["motsCles"] = keywords
        
        # Ajouter le filtre ROME si spécifié
        if rome_codes:
            # L'API France Travail accepte plusieurs codes ROME séparés par des virgules
            params["codeROME"] = ",".join(rome_codes)
        
        payload = client.search_offers(params)
        offers: List[Dict[str, Any]] = payload.get("resultats", [])
        
        if not offers:
            print(f"   Page {page}: Aucune offre trouvée")
            break

        # Appliquer la limite si spécifiée
        if limit and total_collected + len(offers) > limit:
            offers = offers[:limit - total_collected]
        
        print(f"   Page {page}: {len(offers)} offres collectées")
        
        write_jsonl(raw_path, offers)
        normalized = [normalize_offer(raw, "francetravail").to_dict() for raw in offers]
        write_jsonl(normalized_path, normalized)
        
        total_collected += len(offers)
        
        # Arrêter si la limite est atteinte
        if limit and total_collected >= limit:
            print(f"\n✅ Limite atteinte : {total_collected} offres collectées")
            break
    
    print(f"\n✅ Collecte terminée : {total_collected} offres au total")
    print(f"   Brutes      : {raw_path}")
    print(f"   Normalisées : {normalized_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecte d'offres d'emploi France Travail")
    parser.add_argument(
        "--sample", 
        action="store_true", 
        help="Mode échantillon : collecte 1 page de 5 offres maximum"
    )
    parser.add_argument(
        "--rome-codes",
        type=str,
        help="Codes ROME pour filtrer les offres (séparés par des virgules, ex: M1403,M1805,M1806)"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        help="Mots-clés pour la recherche (ex: 'data analyst', 'data engineer')"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Nombre maximum d'offres à collecter"
    )
    
    args = parser.parse_args()
    
    # Parser les codes ROME
    rome_codes = None
    if args.rome_codes:
        rome_codes = [code.strip() for code in args.rome_codes.split(",")]
    
    run(sample=args.sample, rome_codes=rome_codes, keywords=args.keywords, limit=args.limit)
