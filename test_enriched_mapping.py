"""
Script de test pour valider le mapping enrichi des données France Travail.
Analyse l'échantillon existant et affiche les statistiques des nouveaux champs.
"""

import json
from pathlib import Path
from collections import Counter
from pipelines.ingest.sources.francetravail.mapping import map_france_travail


def load_sample_data():
    """Charge l'échantillon de données brutes."""
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    
    if not sample_path.exists():
        print(f"❌ Fichier échantillon introuvable : {sample_path}")
        return []
    
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    print(f"✅ Chargé {len(offers)} offres depuis l'échantillon")
    return offers


def analyze_mapped_data(offers):
    """Analyse les données mappées et affiche les statistiques."""
    
    if not offers:
        print("⚠️  Aucune donnée à analyser")
        return
    
    # Mapper toutes les offres
    mapped = [map_france_travail(offer) for offer in offers]
    
    print("\n" + "="*80)
    print("📊 ANALYSE DES DONNÉES ENRICHIES")
    print("="*80)
    
    # === Classification métier ===
    print("\n🏷️  CLASSIFICATION MÉTIER")
    print("-" * 80)
    rome_codes = Counter(m.rome_code for m in mapped if m.rome_code)
    print(f"Codes ROME distincts : {len(rome_codes)}")
    print("Top 5 codes ROME :")
    for code, count in rome_codes.most_common(5):
        label = next((m.rome_label for m in mapped if m.rome_code == code), "")
        print(f"  • {code} - {label}: {count} offres")
    
    sectors = Counter(m.sector_label for m in mapped if m.sector_label)
    print(f"\nSecteurs d'activité distincts : {len(sectors)}")
    print("Top 5 secteurs :")
    for sector, count in sectors.most_common(5):
        print(f"  • {sector}: {count} offres")
    
    # === Localisation ===
    print("\n📍 LOCALISATION")
    print("-" * 80)
    with_gps = sum(1 for m in mapped if m.location_latitude and m.location_longitude)
    print(f"Offres avec coordonnées GPS : {with_gps}/{len(mapped)} ({with_gps/len(mapped)*100:.1f}%)")
    
    departments = Counter(m.location_department for m in mapped if m.location_department)
    print(f"Départements distincts : {len(departments)}")
    print("Top 5 départements :")
    for dept, count in departments.most_common(5):
        print(f"  • {dept}: {count} offres")
    
    # === Rémunération ===
    print("\n💰 RÉMUNÉRATION")
    print("-" * 80)
    with_salary = sum(1 for m in mapped if m.salary_min or m.salary_max)
    print(f"Offres avec info salariale : {with_salary}/{len(mapped)} ({with_salary/len(mapped)*100:.1f}%)")
    
    salary_units = Counter(m.salary_unit for m in mapped if m.salary_unit)
    print("Unités salariales :")
    for unit, count in salary_units.items():
        print(f"  • {unit}: {count}")
    
    if with_salary > 0:
        salaries = [(m.salary_min, m.salary_max, m.salary_unit) for m in mapped 
                    if m.salary_min or m.salary_max]
        # Afficher quelques exemples
        print("\nExemples de salaires :")
        for i, (min_sal, max_sal, unit) in enumerate(salaries[:3]):
            if min_sal and max_sal:
                print(f"  • {min_sal} - {max_sal} € ({unit})")
            elif min_sal:
                print(f"  • À partir de {min_sal} € ({unit})")
    
    with_benefits = sum(1 for m in mapped if m.salary_benefits)
    print(f"\nOffres avec avantages : {with_benefits}/{len(mapped)}")
    if with_benefits > 0:
        all_benefits = []
        for m in mapped:
            if m.salary_benefits:
                all_benefits.extend(m.salary_benefits)
        benefits = Counter(all_benefits)
        print("Top avantages :")
        for benefit, count in benefits.most_common(5):
            print(f"  • {benefit}: {count}")
    
    # === Compétences ===
    print("\n🎯 COMPÉTENCES")
    print("-" * 80)
    with_skills_req = sum(1 for m in mapped if m.skills_required)
    with_skills_des = sum(1 for m in mapped if m.skills_desired)
    with_soft = sum(1 for m in mapped if m.soft_skills)
    with_lang = sum(1 for m in mapped if m.languages)
    
    print(f"Offres avec compétences exigées : {with_skills_req}/{len(mapped)}")
    print(f"Offres avec compétences souhaitées : {with_skills_des}/{len(mapped)}")
    print(f"Offres avec soft skills : {with_soft}/{len(mapped)}")
    print(f"Offres avec langues : {with_lang}/{len(mapped)}")
    
    # Compter les compétences les plus demandées
    all_skills = []
    for m in mapped:
        if m.skills_required:
            all_skills.extend([s['label'] for s in m.skills_required])
        if m.skills_desired:
            all_skills.extend([s['label'] for s in m.skills_desired])
    
    if all_skills:
        skills_counter = Counter(all_skills)
        print("\nTop 10 compétences demandées :")
        for skill, count in skills_counter.most_common(10):
            print(f"  • {skill}: {count}")
    
    # === Formation & Expérience ===
    print("\n🎓 FORMATION & EXPÉRIENCE")
    print("-" * 80)
    with_education = sum(1 for m in mapped if m.education_level)
    print(f"Offres avec niveau de formation : {with_education}/{len(mapped)}")
    
    education_levels = Counter(m.education_level for m in mapped if m.education_level)
    print("Niveaux de formation :")
    for level, count in education_levels.most_common(5):
        print(f"  • {level}: {count}")
    
    experience_required = Counter(m.experience_required for m in mapped if m.experience_required)
    print(f"\nExpérience requise (top 5) :")
    for exp, count in experience_required.most_common(5):
        print(f"  • {exp}: {count}")
    
    # === Contrat ===
    print("\n📋 TYPE DE CONTRAT")
    print("-" * 80)
    contracts = Counter(m.contract_type for m in mapped if m.contract_type)
    print("Types de contrat :")
    for contract, count in contracts.most_common(5):
        print(f"  • {contract}: {count}")
    
    work_schedules = Counter(m.work_schedule for m in mapped if m.work_schedule)
    print("\nRégime de travail :")
    for schedule, count in work_schedules.items():
        print(f"  • {schedule}: {count}")
    
    alternance_count = sum(1 for m in mapped if m.is_alternance)
    print(f"\nOffres en alternance : {alternance_count}/{len(mapped)}")
    
    # === Entreprise ===
    print("\n🏢 ENTREPRISE")
    print("-" * 80)
    with_size = sum(1 for m in mapped if m.company_size)
    print(f"Offres avec taille entreprise : {with_size}/{len(mapped)}")
    
    sizes = Counter(m.company_size for m in mapped if m.company_size)
    print("Tailles d'entreprise :")
    for size, count in sizes.most_common(5):
        print(f"  • {size}: {count}")
    
    # === Métadonnées ===
    print("\n📌 MÉTADONNÉES")
    print("-" * 80)
    with_url = sum(1 for m in mapped if m.url)
    with_positions = sum(1 for m in mapped if m.positions_count and m.positions_count > 1)
    
    print(f"Offres avec URL : {with_url}/{len(mapped)}")
    print(f"Offres avec plusieurs postes : {with_positions}/{len(mapped)}")
    
    total_positions = sum(m.positions_count or 1 for m in mapped)
    print(f"Total de postes à pourvoir : {total_positions}")
    
    print("\n" + "="*80)
    print("✅ Analyse terminée")
    print("="*80)


def main():
    """Point d'entrée principal."""
    print("🔍 Test du mapping enrichi France Travail\n")
    
    # Charger les données
    offers = load_sample_data()
    
    if not offers:
        return
    
    # Analyser
    analyze_mapped_data(offers)
    
    print("\n💡 Suggestions :")
    print("  • Vérifiez que les champs importants sont bien extraits")
    print("  • Identifiez les codes ROME pertinents pour les métiers data")
    print("  • Validez les fourchettes salariales parsées")
    print("  • Explorez les compétences techniques les plus demandées")


if __name__ == "__main__":
    main()
