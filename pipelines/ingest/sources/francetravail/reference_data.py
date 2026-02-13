"""
Référentiel des codes ROME et mots-clés pour identifier les métiers data.

Ce fichier centralise la classification des emplois liés à la data
pour faciliter le filtrage des offres France Travail.
"""

# Codes ROME prioritaires pour les métiers data
# ⚠️  CODES VALIDÉS depuis l'API France Travail (février 2026)
ROME_CODES_DATA = {
    # Data Analysis & Business Intelligence
    "M1419": "Data analyst",  # Code spécifique pour Data Analyst (71% des offres)
    
    # Data Engineering
    "M1811": "Data engineer",  # Code spécifique pour Data Engineer
    
    # Data Science & Machine Learning  
    "M1405": "Data scientist",  # Code spécifique pour Data Scientist
    
    # Codes génériques (moins précis, contiennent beaucoup de faux positifs)
    "M1403": "Études et prospective socio-économique",  # Chargé d'études (BTP, urbanisme) - PAS data !
    "M1805": "Études et développement informatique",  # Développeurs généralistes (Java, C#) - PAS data !  
    "M1806": "Conseil et maîtrise d'ouvrage en SI",  # Business analysts, consultants SI
}

# Mots-clés pour affiner la recherche dans les intitulés
KEYWORDS_DATA_JOBS = {
    # Analyst roles
    "analyst": [
        "data analyst",
        "analyste de données",
        "analyste données",
        "business analyst",
        "bi analyst",
        "analyste décisionnel",
    ],
    
    # Scientist roles
    "scientist": [
        "data scientist",
        "scientifique des données",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "nlp engineer",
    ],
    
    # Engineer roles
    "engineer": [
        "data engineer",
        "ingénieur données",
        "ingénieur data",
        "big data engineer",
        "etl developer",
        "pipeline engineer",
    ],
    
    # Architecture & Leadership
    "architecture": [
        "data architect",
        "architecte données",
        "architecte data",
        "chief data officer",
        "cdo",
        "data manager",
        "responsable data",
    ],
    
    # Visualization & BI
    "visualization": [
        "data visualization",
        "développeur bi",
        "power bi",
        "tableau developer",
        "qlik developer",
    ],
    
    # Database & Admin
    "database": [
        "dba",
        "database administrator",
        "administrateur base de données",
        "administrateur bdd",
    ],
}

# Compétences techniques clés à extraire
TECHNICAL_SKILLS_DATA = {
    # Langages de programmation
    "languages": [
        "python",
        "r",
        "sql",
        "scala",
        "java",
        "javascript",
        "julia",
    ],
    
    # Bases de données
    "databases": [
        "postgresql",
        "mysql",
        "mongodb",
        "elasticsearch",
        "cassandra",
        "redis",
        "oracle",
        "sql server",
    ],
    
    # Big Data & Cloud
    "bigdata_cloud": [
        "spark",
        "hadoop",
        "kafka",
        "airflow",
        "aws",
        "azure",
        "gcp",
        "databricks",
        "snowflake",
    ],
    
    # Machine Learning
    "ml_frameworks": [
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
        "xgboost",
        "lightgbm",
    ],
    
    # Outils BI
    "bi_tools": [
        "power bi",
        "tableau",
        "qlik",
        "looker",
        "metabase",
        "superset",
    ],
    
    # ETL & Orchestration
    "etl_tools": [
        "talend",
        "informatica",
        "ssis",
        "pentaho",
        "airflow",
        "prefect",
        "dagster",
    ],
}

# Secteurs d'activité prioritaires (codes NAF à affiner)
SECTORS_PRIORITY = {
    "tech": ["62", "63"],  # Programmation, activités informatiques
    "finance": ["64", "65", "66"],  # Banque, assurance
    "conseil": ["70.2"],  # Conseil de gestion
    "telecom": ["61"],  # Télécommunications
    "ecommerce": ["47.91"],  # Vente à distance
}

# Niveaux d'expérience (mapping pour normalisation)
EXPERIENCE_LEVELS = {
    "junior": ["débutant", "0 an", "1 an", "2 ans", "moins de 3 ans"],
    "confirmé": ["3 ans", "4 ans", "5 ans"],
    "senior": ["5 ans", "7 ans", "10 ans", "plus de 5 ans", "plus de 7 ans"],
    "expert": ["10 ans", "15 ans", "plus de 10 ans"],
}

# Niveaux de formation attendus
EDUCATION_LEVELS = {
    "bac+2": ["BTS", "DUT", "Bac+2"],
    "bac+3": ["Licence", "Bachelor", "Bac+3"],
    "bac+5": ["Master", "Ingénieur", "Bac+5", "M2"],
    "bac+8": ["Doctorat", "PhD", "Bac+8"],
}


def is_data_job(rome_code: str = None, title: str = None) -> bool:
    """
    Détermine si une offre correspond à un métier data.
    
    Args:
        rome_code: Code ROME de l'offre
        title: Intitulé du poste
    
    Returns:
        True si l'offre correspond à un métier data
    """
    # Vérifier le code ROME
    if rome_code and rome_code in ROME_CODES_DATA:
        return True
    
    # Vérifier les mots-clés dans le titre
    if title:
        title_lower = title.lower()
        for category, keywords in KEYWORDS_DATA_JOBS.items():
            if any(keyword in title_lower for keyword in keywords):
                return True
    
    return False


def extract_technical_skills(skills_list: list) -> dict:
    """
    Extrait et catégorise les compétences techniques data.
    
    Args:
        skills_list: Liste de compétences de l'offre
    
    Returns:
        Dictionnaire de compétences par catégorie
    """
    if not skills_list:
        return {}
    
    found_skills = {category: [] for category in TECHNICAL_SKILLS_DATA.keys()}
    
    for skill in skills_list:
        skill_label = skill.get("libelle", "").lower() if isinstance(skill, dict) else str(skill).lower()
        
        for category, tech_list in TECHNICAL_SKILLS_DATA.items():
            for tech in tech_list:
                if tech in skill_label:
                    found_skills[category].append(tech)
    
    # Retirer les catégories vides
    return {k: list(set(v)) for k, v in found_skills.items() if v}


def classify_experience_level(experience_str: str) -> str:
    """
    Classifie le niveau d'expérience demandé.
    
    Args:
        experience_str: Chaîne décrivant l'expérience requise
    
    Returns:
        Niveau normalisé (junior, confirmé, senior, expert)
    """
    if not experience_str:
        return "non spécifié"
    
    exp_lower = experience_str.lower()
    
    for level, patterns in EXPERIENCE_LEVELS.items():
        if any(pattern in exp_lower for pattern in patterns):
            return level
    
    return "confirmé"  # Valeur par défaut
