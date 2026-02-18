#!/usr/bin/env python3
"""
Analyse interactive d'un champ au choix dans les offres normalisées France Travail.

Ce script affiche un menu interactif permettant de choisir un champ à analyser.
"""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Optional


def load_offers(file_path: Path) -> List[Dict[str, Any]]:
    """Charge les offres depuis un fichier JSONL."""
    offers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    return offers


def get_available_fields() -> List[tuple[int, str, str]]:
    """Retourne la liste des champs disponibles avec leur description."""
    fields = [
        ("id", "Identifiant de l'offre"),
        ("source", "Source de l'offre"),
        ("title", "Titre du poste"),
        ("company_name", "Nom de l'entreprise"),
        ("rome_code", "Code ROME du métier"),
        ("rome_label", "Libellé du métier ROME"),
        ("job_category", "Appellation précise du poste"),
        ("naf_code", "Code NAF de l'entreprise"),
        ("sector", "Secteur d'activité"),
        ("sector_label", "Libellé du secteur"),
        ("location_city", "Ville"),
        ("location_department", "Département"),
        ("location_region", "Région"),
        ("location_commune_code", "Code INSEE commune"),
        ("contract_type", "Type de contrat"),
        ("contract_duration", "Durée du contrat"),
        ("contract_nature", "Nature du contrat"),
        ("work_schedule", "Temps plein/partiel"),
        ("weekly_hours", "Heures hebdomadaires"),
        ("is_alternance", "Poste en alternance"),
        ("salary_unit", "Unité de salaire"),
        ("education_level", "Niveau de formation"),
        ("experience_required", "Expérience requise"),
        ("experience_level", "Niveau d'expérience"),
        ("experience_code", "Code expérience"),
        ("company_size", "Taille de l'entreprise"),
        ("company_adapted", "Entreprise adaptée"),
        ("travel_frequency", "Fréquence des déplacements"),
        ("accessible_handicap", "Accessible handicapés"),
        ("positions_count", "Nombre de postes"),
        ("qualification_code", "Code qualification"),
        ("qualification_label", "Libellé qualification"),
    ]
    
    return [(i + 1, field, desc) for i, (field, desc) in enumerate(fields)]


def display_menu(fields: List[tuple[int, str, str]]) -> None:
    """Affiche le menu de sélection des champs."""
    print("\n" + "=" * 70)
    print("📊 ANALYSE DE CHAMP - Sélectionnez un champ à analyser")
    print("=" * 70 + "\n")
    
    for num, field_name, description in fields:
        print(f"  {num:2d}. {field_name:30s} - {description}")
    
    print("\n   0. Quitter")
    print("=" * 70)


def get_field_value(offer: Dict[str, Any], field_name: str) -> Optional[Any]:
    """Récupère la valeur d'un champ, même si c'est une liste ou dict."""
    value = offer.get(field_name)
    
    # Convertir les listes en chaîne pour l'analyse
    if isinstance(value, list):
        if value and isinstance(value[0], dict):
            # Extraire les labels si c'est une liste de dicts
            return ", ".join([str(item.get('label', item)) for item in value if item])
        else:
            return ", ".join([str(v) for v in value if v])
    elif isinstance(value, dict):
        # Convertir les dicts en string
        return str(value)
    
    return value


def analyze_field(data_dir: Path, field_name: str, field_description: str) -> None:
    """Analyse un champ spécifique dans tous les fichiers normalisés."""
    
    # Parcourir tous les fichiers JSONL
    jsonl_files = sorted([f for f in data_dir.glob("*.jsonl") if f.is_file()])
    
    if not jsonl_files:
        print(f"Aucun fichier JSONL trouvé dans {data_dir}")
        return
    
    print(f"\n{'=' * 70}")
    print(f"📈 Analyse du champ: {field_name}")
    print(f"   Description: {field_description}")
    print(f"{'=' * 70}\n")
    
    # Collecte des données avec déduplication
    all_offers_by_id = {}
    total_raw_offers = 0
    
    for file_path in jsonl_files:
        offers = load_offers(file_path)
        total_raw_offers += len(offers)
        
        for offer in offers:
            offer_id = offer.get('id')
            if offer_id:
                all_offers_by_id[offer_id] = offer
    
    # Analyse du champ sur les offres dédupliquées
    field_values = []
    null_count = 0
    
    for offer in all_offers_by_id.values():
        value = get_field_value(offer, field_name)
        
        if value is not None and value != "" and value != []:
            field_values.append(str(value))
        else:
            null_count += 1
    
    # Statistiques
    total_unique_offers = len(all_offers_by_id)
    total_duplicates = total_raw_offers - total_unique_offers
    values_with_data = len(field_values)
    unique_values = len(set(field_values))
    value_counter = Counter(field_values)
    
    print(f"📊 Statistiques globales:\n")
    print(f"   Total offres (brutes): {total_raw_offers}")
    print(f"   Doublons: {total_duplicates}")
    print(f"   Offres uniques: {total_unique_offers}")
    print(f"   Offres avec '{field_name}': {values_with_data}")
    print(f"   Offres sans valeur: {null_count}")
    print(f"   Taux de remplissage: {values_with_data/total_unique_offers*100:.1f}%")
    print(f"   Valeurs uniques: {unique_values}")
    
    if not field_values:
        print(f"\n⚠️  Aucune valeur trouvée pour le champ '{field_name}'")
        return
    
    # Top valeurs
    print(f"\n📈 Top 20 des valeurs les plus fréquentes:\n")
    for i, (value, count) in enumerate(value_counter.most_common(20), 1):
        percentage = (count / values_with_data) * 100
        # Tronquer les valeurs trop longues
        display_value = value[:60] + "..." if len(value) > 60 else value
        print(f"   {i:2d}. {display_value}")
        print(f"       {count} offres ({percentage:.1f}%)")
    
    # Valeurs rares
    rare_values = [val for val, count in value_counter.items() if count <= 2]
    if rare_values:
        print(f"\n📉 Valeurs rares (≤ 2 offres):\n")
        print(f"   Nombre: {len(rare_values)}")
        print(f"\n   Exemples:")
        for val in sorted(rare_values)[:10]:
            count = value_counter[val]
            display_val = val[:50] + "..." if len(val) > 50 else val
            print(f"      • {display_val} ({count} offre{'s' if count > 1 else ''})")
        if len(rare_values) > 10:
            print(f"      ... et {len(rare_values) - 10} autres")
    
    # Distribution pour les champs numériques
    if field_name in ['weekly_hours', 'positions_count', 'salary_min', 'salary_max']:
        try:
            numeric_values = [float(v) for v in field_values if v]
            if numeric_values:
                print(f"\n📊 Statistiques numériques:\n")
                print(f"   Minimum: {min(numeric_values)}")
                print(f"   Maximum: {max(numeric_values)}")
                print(f"   Moyenne: {sum(numeric_values)/len(numeric_values):.2f}")
        except (ValueError, TypeError):
            pass
    
    print("\n" + "=" * 70 + "\n")


def main():
    """Point d'entrée du script."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "normalized" / "francetravail"
    
    if not data_dir.exists():
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas")
        return
    
    fields = get_available_fields()
    
    while True:
        display_menu(fields)
        
        try:
            choice = input("\nVotre choix (numéro): ").strip()
            
            if choice == "0":
                print("\n👋 Au revoir !")
                break
            
            choice_num = int(choice)
            
            if choice_num < 1 or choice_num > len(fields):
                print(f"\n❌ Choix invalide. Veuillez entrer un numéro entre 1 et {len(fields)}")
                input("\nAppuyez sur Entrée pour continuer...")
                continue
            
            # Récupérer le champ sélectionné
            selected_field = [f for f in fields if f[0] == choice_num][0]
            _, field_name, field_description = selected_field
            
            # Analyser le champ
            analyze_field(data_dir, field_name, field_description)
            
            # Demander si l'utilisateur veut continuer
            continue_choice = input("\nAnalyser un autre champ ? (o/n): ").strip().lower()
            if continue_choice != 'o':
                print("\n👋 Au revoir !")
                break
                
        except ValueError:
            print("\n❌ Erreur: Veuillez entrer un numéro valide")
            input("\nAppuyez sur Entrée pour continuer...")
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break


if __name__ == "__main__":
    main()
