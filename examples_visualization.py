"""
Exemple de visualisation des données enrichies France Travail.
Démontre l'utilisation des nouveaux champs pour l'analyse de marché.
"""

import json
from pathlib import Path
from collections import Counter
from pipelines.ingest.sources.francetravail.mapping import map_france_travail


def example_1_salary_by_experience():
    """Exemple 1 : Analyse salariale par niveau d'expérience."""
    print("\n" + "="*80)
    print("📊 EXEMPLE 1 : SALAIRE PAR NIVEAU D'EXPÉRIENCE")
    print("="*80)
    
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    mapped = [map_france_travail(offer) for offer in offers]
    
    # Grouper par expérience
    by_experience = {}
    for offer in mapped:
        if not offer.experience_required or not offer.salary_min:
            continue
        
        exp = offer.experience_required
        if exp not in by_experience:
            by_experience[exp] = []
        
        # Convertir en mensuel si horaire
        salary = offer.salary_min
        if offer.salary_unit == "hourly":
            salary = salary * 35 * 4.33  # Approximation mensuel
        elif offer.salary_unit == "yearly":
            salary = salary / 12
        
        by_experience[exp].append(salary)
    
    # Calculer les moyennes
    print("\nSalaire mensuel moyen par expérience requise :\n")
    for exp, salaries in sorted(by_experience.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
        avg = sum(salaries) / len(salaries)
        print(f"  {exp:20s} : {avg:7.0f} € ({len(salaries):3d} offres)")


def example_2_skills_by_sector():
    """Exemple 2 : Compétences les plus demandées par secteur."""
    print("\n" + "="*80)
    print("🎯 EXEMPLE 2 : COMPÉTENCES PAR SECTEUR")
    print("="*80)
    
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    mapped = [map_france_travail(offer) for offer in offers]
    
    # Grouper par secteur
    by_sector = {}
    for offer in mapped:
        if not offer.sector_label or not offer.skills_required:
            continue
        
        sector = offer.sector_label
        if sector not in by_sector:
            by_sector[sector] = []
        
        skills = [s['label'] for s in offer.skills_required]
        by_sector[sector].extend(skills)
    
    # Top compétences par secteur
    print("\nTop 3 compétences par secteur :\n")
    for sector, skills in sorted(by_sector.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        skill_counts = Counter(skills)
        print(f"📍 {sector}")
        for skill, count in skill_counts.most_common(3):
            print(f"   • {skill[:60]}: {count}")
        print()


def example_3_geographic_distribution():
    """Exemple 3 : Répartition géographique avec GPS."""
    print("\n" + "="*80)
    print("🗺️  EXEMPLE 3 : RÉPARTITION GÉOGRAPHIQUE")
    print("="*80)
    
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    mapped = [map_france_travail(offer) for offer in offers]
    
    # Offres avec GPS
    with_gps = [o for o in mapped if o.location_latitude and o.location_longitude]
    
    print(f"\nOffres géolocalisées : {len(with_gps)}/{len(mapped)}")
    print("\nCentroïdes par département (approximatif) :\n")
    
    # Grouper par département
    by_dept = {}
    for offer in with_gps:
        dept = offer.location_department[:2] if offer.location_department else "??"
        if dept not in by_dept:
            by_dept[dept] = {"lats": [], "lons": [], "count": 0}
        
        by_dept[dept]["lats"].append(offer.location_latitude)
        by_dept[dept]["lons"].append(offer.location_longitude)
        by_dept[dept]["count"] += 1
    
    # Calculer centroïdes
    for dept, data in sorted(by_dept.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
        avg_lat = sum(data["lats"]) / len(data["lats"])
        avg_lon = sum(data["lons"]) / len(data["lons"])
        print(f"  Dept {dept} : {data['count']:3d} offres → Centre : {avg_lat:.4f}, {avg_lon:.4f}")


def example_4_contract_benefits():
    """Exemple 4 : Analyse des avantages par type de contrat."""
    print("\n" + "="*80)
    print("🎁 EXEMPLE 4 : AVANTAGES PAR TYPE DE CONTRAT")
    print("="*80)
    
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    mapped = [map_france_travail(offer) for offer in offers]
    
    # Grouper par type de contrat
    by_contract = {}
    for offer in mapped:
        if not offer.contract_type or not offer.salary_benefits:
            continue
        
        contract = offer.contract_type
        if contract not in by_contract:
            by_contract[contract] = []
        
        by_contract[contract].extend(offer.salary_benefits)
    
    # Top avantages par contrat
    print("\nAvantages les plus fréquents par type de contrat :\n")
    for contract, benefits in sorted(by_contract.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        benefit_counts = Counter(benefits)
        print(f"📋 {contract}")
        for benefit, count in benefit_counts.most_common(3):
            print(f"   • {benefit}: {count}")
        print()


def example_5_company_size_analysis():
    """Exemple 5 : Analyse par taille d'entreprise."""
    print("\n" + "="*80)
    print("🏢 EXEMPLE 5 : PROFIL DES RECRUTEURS PAR TAILLE")
    print("="*80)
    
    sample_path = Path("data/raw/francetravail/offers_sample.jsonl")
    offers = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                offers.append(json.loads(line))
    
    mapped = [map_france_travail(offer) for offer in offers]
    
    # Grouper par taille
    by_size = {}
    for offer in mapped:
        if not offer.company_size:
            continue
        
        size = offer.company_size
        if size not in by_size:
            by_size[size] = {
                "count": 0,
                "total_positions": 0,
                "with_salary": 0,
                "avg_salary": []
            }
        
        by_size[size]["count"] += 1
        by_size[size]["total_positions"] += offer.positions_count or 1
        
        if offer.salary_min:
            by_size[size]["with_salary"] += 1
            salary = offer.salary_min
            if offer.salary_unit == "hourly":
                salary = salary * 35 * 4.33
            elif offer.salary_unit == "yearly":
                salary = salary / 12
            by_size[size]["avg_salary"].append(salary)
    
    # Afficher les stats
    print("\nStatistiques par taille d'entreprise :\n")
    for size, stats in sorted(by_size.items(), key=lambda x: x[1]["count"], reverse=True)[:8]:
        avg_sal = sum(stats["avg_salary"]) / len(stats["avg_salary"]) if stats["avg_salary"] else 0
        print(f"📊 {size}")
        print(f"   Offres : {stats['count']}")
        print(f"   Postes totaux : {stats['total_positions']}")
        print(f"   Avec salaire : {stats['with_salary']} ({stats['with_salary']/stats['count']*100:.0f}%)")
        if avg_sal > 0:
            print(f"   Salaire moyen : {avg_sal:.0f} €/mois")
        print()


def main():
    """Exécute tous les exemples."""
    print("\n" + "="*80)
    print("🔍 EXEMPLES DE VISUALISATION - DONNÉES ENRICHIES")
    print("="*80)
    
    example_1_salary_by_experience()
    example_2_skills_by_sector()
    example_3_geographic_distribution()
    example_4_contract_benefits()
    example_5_company_size_analysis()
    
    print("\n" + "="*80)
    print("✅ Tous les exemples exécutés avec succès")
    print("="*80)
    print("\n💡 Ces exemples démontrent le potentiel des données enrichies.")
    print("   Avec une collecte ciblée sur les métiers data (codes ROME M1403, M1805),")
    print("   vous pourrez analyser : benchmark salarial, compétences tech demandées,")
    print("   zones géographiques porteuses, profils d'entreprises qui recrutent, etc.")
    print()


if __name__ == "__main__":
    main()
