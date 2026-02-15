import argparse
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from pipelines.ingest.io import write_jsonl
from pipelines.ingest.normalizer import normalize_offer
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


def run(sample: bool = False, rome_codes: List[str] = None, keywords: str = None, limit: int = None, split_by_contract: bool = False) -> None:
    """
    Lance la collecte d'offres depuis l'API France Travail.
    
    Args:
        sample: Mode échantillon (1 requête uniquement, max 150 offres)
        rome_codes: Liste de codes ROME pour filtrer (ex: ["M1403", "M1805"])
        keywords: Mots-clés pour la recherche (ex: "data analyst")
        limit: Nombre maximum d'offres à collecter (optionnel)
               Si non spécifié, collecte jusqu'à 1150 offres par recherche (limite API)
        split_by_contract: Si True, découpe par contrat + expérience pour dépasser 1150 offres
                          (utile uniquement si > 1150 résultats disponibles)
    """
    _load_env_file(Path("config/.env"))
    output_dir = Path(os.getenv("INGEST_OUTPUT_DIR", "./data"))
    
    # Filtres pour découper la recherche si nécessaire
    # Découpage par type de contrat ET niveau d'expérience pour maximiser les résultats
    if split_by_contract:
        contract_types = ["CDI", "CDD", "MIS", "CCE", "LIB"]
        experience_codes = ["0", "1", "2", "3", "4"]  # Codes d'expérience de l'API
        # Créer toutes les combinaisons contrat × expérience
        filter_combinations = [(ct, exp) for ct in contract_types for exp in experience_codes]
        # Ajouter aussi sans filtre d'expérience pour capturer les offres sans ce critère
        filter_combinations.extend([(ct, None) for ct in contract_types])
    else:
        filter_combinations = [(None, None)]

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
    seen_ids = set()  # Détecter les doublons entre tous les filtres
    
    print(f"🔍 Collecte d'offres France Travail")
    if keywords:
        print(f"   Mots-clés : {keywords}")
    if rome_codes:
        print(f"   Codes ROME : {', '.join(rome_codes)}")
    if limit:
        print(f"   Limite : {limit} offres")
    elif sample:
        print(f"   Mode : échantillon (1 requête, max 150 offres)")
    else:
        print(f"   Mode : collecte complète (max 1150 offres par recherche)")
    if split_by_contract:
        print(f"   ⚙️  Mode multi-filtres : découpage par contrat + expérience (pour > 1150 offres)")
    print(f"   Fichier : {filename}\n")
    
    # Boucle sur les filtres (contrat × expérience ou une seule itération si pas de split)
    for contract_filter, experience_filter in filter_combinations:
        if contract_filter and split_by_contract:
            label = f"Contrat={contract_filter}"
            if experience_filter:
                label += f", Experience={experience_filter}"
            print(f"\n📋 Collecte : {label}")
        
        range_start = 0
        range_size = 150  # API limite à 150 résultats par requête

        while True:
            # Mode sample : s'arrêter après 1 requête
            if sample and range_start > 0:
                break
            
            # Limite API : range max est 1000-1149 (voir doc France Travail)
            # Au-delà de 1149, il faut subdiviser par dates ou autres filtres
            if range_start >= 1150:
                print(f"\n⚠️  Limite API atteinte (1150 offres max par filtre)")
                print(f"   Pour aller au-delà, subdiviser par dates de création")
                break
            
            # Construire le paramètre range au format "start-end"
            range_end = min(range_start + range_size - 1, 1149)
            params = {"range": f"{range_start}-{range_end}"}
            
            # Ajouter le filtre par mots-clés si spécifié
            if keywords:
                params["motsCles"] = keywords
            
            # Ajouter le filtre ROME si spécifié
            if rome_codes:
                # L'API France Travail accepte plusieurs codes ROME séparés par des virgules
                params["codeROME"] = ",".join(rome_codes)
            
            # Ajouter le filtre de type de contrat si split_by_contract activé
            if contract_filter:
                params["typeContrat"] = contract_filter
            
            # Ajouter le filtre d'expérience si spécifié
            if experience_filter:
                params["experience"] = experience_filter
            
            try:
                payload = client.search_offers(params)
                offers: List[Dict[str, Any]] = payload.get("resultats", [])
            except Exception as e:
                # Certains filtres peuvent ne renvoyer aucun résultat ou causer des erreurs API
                filter_label = f"{contract_filter or 'sans filtre'}"
                if experience_filter:
                    filter_label += f" + exp={experience_filter}"
                print(f"   ⚠️  Erreur API pour {filter_label}: {e}")
                break
            
            if not offers:
                print(f"   Range {range_start}-{range_end}: Aucune offre trouvée (fin de la collecte)")
                break
            
            # Filtrer les doublons (l'API peut renvoyer les mêmes offres)
            new_offers = []
            duplicates = 0
            for offer in offers:
                offer_id = offer.get("id")
                if offer_id and offer_id not in seen_ids:
                    seen_ids.add(offer_id)
                    new_offers.append(offer)
                else:
                    duplicates += 1
            
            # Si toutes les offres sont des doublons, on a fait le tour
            if not new_offers:
                filter_label = contract_filter or "ce filtre"
                if experience_filter:
                    filter_label += f" + exp={experience_filter}"
                if split_by_contract:
                    print(f"   Range {range_start}-{range_end}: Toutes les offres sont des doublons pour {filter_label} (fin)")
                else:
                    print(f"   Range {range_start}-{range_end}: Toutes les offres sont des doublons (fin de la collecte)")
                break

            # Appliquer la limite si spécifiée
            if limit and total_collected + len(new_offers) > limit:
                new_offers = new_offers[:limit - total_collected]
            
            status_msg = f"   Range {range_start}-{range_end}: {len(new_offers)} offres collectées"
            if duplicates > 0:
                status_msg += f" ({duplicates} doublons ignorés)"
            print(status_msg)
            
            write_jsonl(raw_path, new_offers)
            normalized = [normalize_offer(raw, "francetravail").to_dict() for raw in new_offers]
            write_jsonl(normalized_path, normalized)
            
            total_collected += len(new_offers)
            
            # Arrêter si la limite est atteinte
            if limit and total_collected >= limit:
                print(f"\n✅ Limite atteinte : {total_collected} offres collectées")
                return  # Sortir complètement de la fonction
            
            # Passer au range suivant
            range_start += range_size
    print(f"\n✅ Collecte terminée : {total_collected} offres au total")
    print(f"   Brutes      : {raw_path}")
    print(f"   Normalisées : {normalized_path}")


if __name__ == "__main__":
    # Configuration du logging pour voir les détails des appels API
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    
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
        help="Nombre maximum d'offres à collecter (optionnel, par défaut : jusqu'à 1150 offres max)"
    )
    parser.add_argument(
        "--split-by-contract",
        action="store_true",
        help="Découper la collecte par contrat + expérience (utile uniquement si > 1150 offres disponibles)"
    )
    
    args = parser.parse_args()
    
    # Parser les codes ROME
    rome_codes = None
    if args.rome_codes:
        rome_codes = [code.strip() for code in args.rome_codes.split(",")]
    
    run(
        sample=args.sample, 
        rome_codes=rome_codes, 
        keywords=args.keywords, 
        limit=args.limit,
        split_by_contract=args.split_by_contract
    )
