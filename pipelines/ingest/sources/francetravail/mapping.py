from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import re

from pipelines.ingest.models import JobOffer


def _get_nested(data: Dict[str, Any], path: str) -> Optional[Any]:
    """Récupère une valeur dans un dictionnaire imbriqué via un chemin point-séparé."""
    current: Any = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _parse_salary(salary_data: Dict[str, Any]) -> tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """Parse les données de salaire France Travail.
    
    Returns:
        Tuple (salary_min, salary_max, salary_unit, salary_comment)
    """
    if not salary_data:
        return None, None, None, None
    
    salary_min = None
    salary_max = None
    salary_unit = None
    salary_comment = salary_data.get("commentaire")
    
    # Parser le libellé (ex: "Mensuel de 2500.0 Euros à 3000.0 Euros")
    libelle = salary_data.get("libelle", "")
    if libelle:
        # Extraire l'unité (Horaire, Mensuel, Annuel)
        if "Horaire" in libelle or "horaire" in libelle:
            salary_unit = "hourly"
        elif "Mensuel" in libelle or "mensuel" in libelle:
            salary_unit = "monthly"
        elif "Annuel" in libelle or "annuel" in libelle:
            salary_unit = "yearly"
        
        # Extraire les montants
        numbers = re.findall(r'\d+\.?\d*', libelle)
        if len(numbers) >= 2:
            try:
                salary_min = float(numbers[0])
                salary_max = float(numbers[1])
            except (ValueError, IndexError):
                pass
        elif len(numbers) == 1:
            try:
                salary_min = float(numbers[0])
            except ValueError:
                pass
    
    return salary_min, salary_max, salary_unit, salary_comment


def _extract_benefits(salary_data: Dict[str, Any]) -> Optional[List[str]]:
    """Extrait la liste des avantages (primes, mutuelle, etc.)."""
    if not salary_data:
        return None
    
    complements = salary_data.get("listeComplements", [])
    if not complements:
        return None
    
    return [comp.get("libelle") for comp in complements if comp.get("libelle")]


def _extract_skills(competences: List[Dict[str, Any]], exigence_filter: str = None) -> Optional[List[Dict[str, str]]]:
    """Extrait et structure les compétences.
    
    Args:
        competences: Liste des compétences brutes
        exigence_filter: Filtre par niveau d'exigence (E=Exigé, S=Souhaité)
    
    Returns:
        Liste de dictionnaires {code, label, level}
    """
    if not competences:
        return None
    
    skills = []
    for comp in competences:
        if exigence_filter and comp.get("exigence") != exigence_filter:
            continue
        
        skill = {
            "code": comp.get("code", ""),
            "label": comp.get("libelle", ""),
            "level": comp.get("exigence", "")
        }
        skills.append(skill)
    
    return skills if skills else None


def _extract_soft_skills(qualites: List[Dict[str, Any]]) -> Optional[List[str]]:
    """Extrait les qualités professionnelles (soft skills)."""
    if not qualites:
        return None
    
    return [q.get("libelle") for q in qualites if q.get("libelle")]


def _extract_languages(langues: List[Dict[str, Any]]) -> Optional[List[Dict[str, str]]]:
    """Extrait les langues requises."""
    if not langues:
        return None
    
    return [
        {
            "language": lang.get("libelle", ""),
            "level": lang.get("exigence", "")
        }
        for lang in langues
    ]


def _extract_formations(formations: List[Dict[str, Any]]) -> Optional[List[Dict[str, str]]]:
    """Extrait les formations requises."""
    if not formations:
        return None
    
    return [
        {
            "code": form.get("codeFormation", ""),
            "domain": form.get("domaineLibelle", ""),
            "level": form.get("niveauLibelle", ""),
            "required": form.get("exigence", "")
        }
        for form in formations
    ]


def _extract_permits(permis: List[Dict[str, Any]]) -> Optional[List[str]]:
    """Extrait les permis requis."""
    if not permis:
        return None
    
    return [p.get("libelle") for p in permis if p.get("libelle")]


def _extract_work_context(context: Dict[str, Any]) -> Optional[List[str]]:
    """Extrait le contexte de travail (horaires, conditions)."""
    if not context:
        return None
    
    contexts = []
    
    # Horaires
    horaires = context.get("horaires", [])
    if horaires:
        contexts.extend(horaires)
    
    # Conditions d'exercice
    conditions = context.get("conditionsExercice", [])
    if conditions:
        contexts.extend(conditions)
    
    return contexts if contexts else None


def _parse_weekly_hours(duree_travail: str) -> Optional[float]:
    """Parse le nombre d'heures hebdomadaires.
    
    Ex: "35H/semaine" -> 35.0
    """
    if not duree_travail:
        return None
    
    match = re.search(r'(\d+\.?\d*)H', duree_travail)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    
    return None


def map_france_travail(raw: Dict[str, Any]) -> JobOffer:
    """Mappe les données brutes France Travail vers le modèle JobOffer enrichi."""
    
    # === Identification ===
    source_id = raw.get("id") or raw.get("id_offre") or "unknown"
    
    # === Informations de base ===
    title = raw.get("intitule") or raw.get("title")
    description = raw.get("description")
    company_name = _get_nested(raw, "entreprise.nom") or raw.get("entreprise")
    
    # === Classification métier ===
    rome_code = raw.get("romeCode")
    rome_label = raw.get("romeLibelle")
    job_category = raw.get("appellationlibelle")
    naf_code = raw.get("codeNAF")
    sector = raw.get("secteurActivite")
    sector_label = raw.get("secteurActiviteLibelle")
    
    # === Localisation ===
    location_city = _get_nested(raw, "lieuTravail.libelle") or raw.get("lieu")
    location_department = _get_nested(raw, "lieuTravail.codePostal")
    location_latitude = _get_nested(raw, "lieuTravail.latitude")
    location_longitude = _get_nested(raw, "lieuTravail.longitude")
    location_commune_code = _get_nested(raw, "lieuTravail.commune")
    
    # === Contrat ===
    contract_type = raw.get("typeContratLibelle") or raw.get("typeContrat")
    contract_nature = raw.get("natureContrat")
    work_schedule = raw.get("dureeTravailLibelleConverti")  # Temps plein/partiel
    duree_travail = raw.get("dureeTravailLibelle")
    weekly_hours = _parse_weekly_hours(duree_travail) if duree_travail else None
    is_alternance = raw.get("alternance")
    
    # === Rémunération ===
    salary_data = raw.get("salaire", {})
    salary_min, salary_max, salary_unit, salary_comment = _parse_salary(salary_data)
    salary_benefits = _extract_benefits(salary_data)
    
    # === Compétences ===
    competences = raw.get("competences", [])
    skills_required = _extract_skills(competences, exigence_filter="E")  # Exigées
    skills_desired = _extract_skills(competences, exigence_filter="S")  # Souhaitées
    
    # Liste simple pour rétrocompatibilité
    all_skills = _extract_skills(competences)
    skills = [s["label"] for s in all_skills] if all_skills else None
    
    soft_skills = _extract_soft_skills(raw.get("qualitesProfessionnelles", []))
    languages = _extract_languages(raw.get("langues", []))
    
    # === Formation & Expérience ===
    formations = raw.get("formations", [])
    education_required = _extract_formations(formations)
    # Prendre le niveau le plus élevé comme niveau principal
    education_level = formations[0].get("niveauLibelle") if formations else None
    
    experience_required = raw.get("experienceLibelle")
    experience_code = raw.get("experienceExige")
    # TODO: classifier experience_level (junior/confirmé/senior) via reference_data
    
    # === Entreprise ===
    company_size = raw.get("trancheEffectifEtab")
    company_adapted = raw.get("entrepriseAdaptee")
    
    # === Conditions de travail ===
    work_context = _extract_work_context(raw.get("contexteTravail", {}))
    permits_required = _extract_permits(raw.get("permis", []))
    travel_frequency = raw.get("deplacementLibelle")
    accessible_handicap = raw.get("accessibleTH")
    
    # === Métadonnées ===
    published_at = raw.get("dateCreation") or raw.get("datePublication")
    updated_at = raw.get("dateActualisation")
    positions_count = raw.get("nombrePostes")
    qualification_code = raw.get("qualificationCode")
    qualification_label = raw.get("qualificationLibelle")
    url = _get_nested(raw, "origineOffre.urlOrigine")
    
    return JobOffer(
        # Identification
        id=f"francetravail:{source_id}",
        source="francetravail",
        
        # Informations de base
        title=title,
        description=description,
        company_name=company_name,
        
        # Classification métier
        rome_code=rome_code,
        rome_label=rome_label,
        job_category=job_category,
        naf_code=naf_code,
        sector=sector,
        sector_label=sector_label,
        
        # Localisation
        location_city=location_city,
        location_department=location_department,
        location_latitude=location_latitude,
        location_longitude=location_longitude,
        location_commune_code=location_commune_code,
        
        # Contrat
        contract_type=contract_type,
        contract_nature=contract_nature,
        work_schedule=work_schedule,
        weekly_hours=weekly_hours,
        is_alternance=is_alternance,
        
        # Rémunération
        salary_min=salary_min,
        salary_max=salary_max,
        salary_unit=salary_unit,
        salary_comment=salary_comment,
        salary_benefits=salary_benefits,
        
        # Compétences
        skills=skills,
        skills_required=skills_required,
        skills_desired=skills_desired,
        soft_skills=soft_skills,
        languages=languages,
        
        # Formation & Expérience
        education_level=education_level,
        education_required=education_required,
        experience_required=experience_required,
        experience_code=experience_code,
        
        # Entreprise
        company_size=company_size,
        company_adapted=company_adapted,
        
        # Conditions de travail
        work_context=work_context,
        permits_required=permits_required,
        travel_frequency=travel_frequency,
        accessible_handicap=accessible_handicap,
        
        # Métadonnées
        published_at=published_at,
        updated_at=updated_at,
        collected_at=datetime.now(timezone.utc).isoformat(),
        positions_count=positions_count,
        qualification_code=qualification_code,
        qualification_label=qualification_label,
        url=url,
        raw=raw,
    )
