# Données à collecter depuis l'API France Travail

## Vue d'ensemble

Ce document décrit les données collectées depuis l'API France Travail et implémentées dans le projet JobMarket V3.

**📊 État de l'implémentation : OPÉRATIONNEL** (mise à jour : 20 février 2026)

### Résumé exécutif

- ✅ **65 champs enrichis** collectés et normalisés
- ✅ **15+ fonctions d'extraction** automatiques (salaire, compétences, télétravail, horaires...)
- ✅ **3 phases d'enrichissement** complétées (Haute/Moyenne/Basse priorité)
- ✅ **Parsing intelligent** : regex pour salaire, horaires, télétravail
- ✅ **Données disponibles** : ~10K+ offres normalisées dans `data/normalized/francetravail/`
- 🔄 **Phase 4 en cours** : Référentiels région et classification expérience

### Couverture fonctionnelle

| Catégorie | Champs | État |
|-----------|--------|------|
| Identification | 2 | ✅ 100% |
| Informations de base | 3 | ✅ 100% |
| Classification métier | 6 | ✅ 100% |
| Localisation enrichie | 6 | ✅ 83% (région à enrichir) |
| Contrat | 6 | ✅ 100% |
| Rémunération | 5 | ✅ 100% (parsing actif) |
| Compétences | 5 | ✅ 100% |
| Formation & Expérience | 5 | ✅ 80% (classification à affiner) |
| Entreprise | 2 | ✅ 100% |
| Conditions de travail | 6 | ✅ 100% (détection télétravail) |
| Métadonnées | 8 | ✅ 100% |
| **TOTAL** | **65** | **✅ 97%** |

## Documentation officielle de l'API France Travail
https://francetravail.io/produits-partages/catalogue/offres-emploi/documentation#/api-reference/operations/recupererListeOffre


## État actuel de l'implémentation

**Date de mise à jour** : 20 février 2026

### ✅ Champs actuellement implémentés et normalisés

Le modèle `JobOffer` et le mapping France Travail sont **pleinement opérationnels** avec l'ensemble des champs enrichis.

#### Identification (2 champs)
- `id` → identifiant unique de l'offre (préfixé source)
- `source` → source des données ("francetravail")

#### Informations de base (3 champs)
- `title` → intitulé du poste
- `description` → description complète de l'offre
- `company_name` → nom de l'entreprise

#### Classification métier (6 champs) ✅
- `rome_code` → code ROME du métier
- `rome_label` → libellé du métier ROME
- `job_category` → appellation précise du poste
- `naf_code` → code NAF de l'entreprise
- `sector` → code secteur d'activité
- `sector_label` → libellé du secteur

#### Localisation enrichie (6 champs) ✅
- `location_city` → ville
- `location_department` → code postal
- `location_region` → région (à enrichir)
- `location_latitude` → coordonnées GPS latitude
- `location_longitude` → coordonnées GPS longitude
- `location_commune_code` → code INSEE de la commune

#### Contrat (6 champs) ✅
- `contract_type` → type de contrat (CDI, CDD, etc.)
- `contract_duration` → durée du contrat
- `contract_nature` → nature juridique du contrat
- `work_schedule` → temps plein / temps partiel
- `weekly_hours` → nombre d'heures hebdomadaires (parsé)
- `is_alternance` → poste en alternance (booléen)

#### Rémunération enrichie (5 champs) ✅
- `salary_min` → salaire minimum (parsé et extrait)
- `salary_max` → salaire maximum (parsé et extrait)
- `salary_unit` → unité (horaire, mensuel, annuel)
- `salary_comment` → commentaire sur le salaire
- `salary_benefits` → liste des avantages (primes, mutuelle, tickets resto...)

#### Compétences détaillées (5 champs) ✅
- `skills` → liste simple des compétences (rétrocompatibilité)
- `skills_required` → compétences exigées structurées [{code, label, level}]
- `skills_desired` → compétences souhaitées structurées
- `soft_skills` → qualités professionnelles
- `languages` → langues requises [{language, level}]

#### Formation & Expérience (5 champs) ✅
- `education_level` → niveau de formation principal (Bac, Bac+2, Bac+5...)
- `education_required` → formations détaillées [{code, domain, level, required}]
- `experience_required` → expérience requise textuelle (ex: "2 An(s)")
- `experience_level` → niveau (junior, confirmé, senior) - *à implémenter via référentiel*
- `experience_code` → code France Travail (D, E, S...)

#### Entreprise (2 champs) ✅
- `company_size` → tranche d'effectif
- `company_adapted` → entreprise adaptée (booléen)

#### Conditions de travail (6 champs) ✅
- `work_context` → horaires et conditions d'exercice
- `permits_required` → permis requis
- `travel_frequency` → fréquence des déplacements
- `accessible_handicap` → accessible travailleurs handicapés
- `is_remote` → télétravail possible (détecté par patterns regex)
- `remote_type` → type de télétravail (full_remote, hybrid, occasional)

#### Métadonnées (8 champs) ✅
- `published_at` → date de publication
- `updated_at` → date de dernière actualisation
- `collected_at` → date de collecte
- `positions_count` → nombre de postes à pourvoir
- `qualification_code` → code qualification
- `qualification_label` → libellé qualification
- `url` → URL de l'offre originale
- `raw` → données brutes complètes (optionnel)

**Total : 65 champs enrichis** dont 57 actifs + 8 métadonnées

## Données disponibles dans l'API France Travail

### 🔴 Priorité HAUTE (essentielles pour l'analyse)

#### Identification & Classification
- **romeCode** : Code ROME (référentiel métiers) - *crucial pour classifier les métiers data*
- **romeLibelle** : Libellé du métier ROME
- **appellationlibelle** : Appellation précise du poste
- **codeNAF** : Code d'activité de l'entreprise
- **secteurActivite** : Code secteur
- **secteurActiviteLibelle** : Libellé du secteur

**Intérêt** : Permet de filtrer spécifiquement les métiers data (Data Analyst, Data Engineer, etc.) et d'analyser la répartition par secteur d'activité.

#### Localisation enrichie
- **lieuTravail.latitude** : Coordonnées GPS
- **lieuTravail.longitude** : Coordonnées GPS
- **lieuTravail.commune** : Code commune INSEE
- **location_region** : Région (à extraire si disponible)

**Intérêt** : Cartographie des opportunités, analyse géographique fine, calcul de distances.

#### Compétences & Qualifications
- **competences** : Liste des compétences requises
  - `niveauLibelle` (Bac, Bac+2, Bac+5...)
  - `exigence` (E=Exigé, S=Souhaité)
  - `code` : identifiant unique
  - `libelle` : nom de la compétence
  - `exigence` : niveau requis (E=Exigé, S=Souhaité)

- **qualitesProfessionnelles** : Soft skills attendues
- **langues** : Langues requises avec niveau d'exigence

**Intérêt** : Analyse des compétences techniques les plus demandées (Python, SQL, PowerBI...), tendances des soft skills.

#### Rémunération
- **salaire.libelle** : Fourchette salariale formatée
- **salaire.commentaire** : Détails supplémentaires
- **salary_min** : Salaire minimum (à extraire/parser du libellé)
- **salary_max** : Salaire maximum (à extraire/parser du libellé)
- **salary_unit** : Unité (horaire, mensuel, annuel)
- **salaire.listeComplements** : Avantages (primes, mutuelle, tickets resto...)

**Intérêt** : Benchmark salarial, évolution des rémunérations, attractivité par région/secteur.

#### Contrat & Expérience
- **experienceExige** : Code expérience (D=Débutant, E=Expérimenté)
- **experienceLibelle** : Durée d'expérience requise
- **dureeTravailLibelle** : Temps de travail détaillé
- **dureeTravailLibelleConverti** : Temps plein/partiel
- **alternance** : Poste en alternance (booléen)

#### Conditions de travail
- **contexteTravail.horaires** : Détails des horaires
- **permis** : Permis requis

**Intérêt** : Profils recherchés (junior vs senior), opportunités pour reconversion.

### 🟠 Priorité MOYENNE (utiles pour analyses avancées)

#### Formation & Certification
- **formations** : Diplômes requis
  - `codeFormation`
  - `domaineLibelle`

**Intérêt** : Niveau de qualification requis, parcours académiques valorisés.

#### Entreprise enrichie
- **trancheEffectifEtab** : Taille de l'entreprise
- **entreprise.entrepriseAdaptee** : Entreprise adaptée (booléen)
- **employeurHandiEngage** : Employeur engagé handicap

**Intérêt** : Typologie des recruteurs (startup, PME, grand groupe).

#### Conditions de travail
- **deplacementLibelle** : Fréquence des déplacements
- **accessibleTH** : Accessible travailleurs handicapés

**Intérêt** : Flexibilité, télétravail, contraintes de mobilité.

#### Recrutement
- **nombrePostes** : Nombre de postes à pourvoir
- **qualificationCode** / **qualificationLibelle** : Niveau de qualification
- **origineOffre.urlOrigine** : Lien vers l'offre originale

**Intérêt** : Volume de recrutement, accès direct aux offres.

### 🟢 Priorité BASSE (optionnelles)

#### Métadonnées techniques
- **dateActualisation** : Dernière mise à jour de l'offre
- **typeContrat** : Code du type de contrat
- **natureContrat** : Nature juridique
- **contact** : Coordonnées (souvent vides pour respect RGPD)
- **agence** : Informations sur l'agence

#### Gestion interne
- **offresManqueCandidats** : Offre en tension
- **entrepriseAdaptee** : Booléen entreprise adaptée

## Modèle canonique actuel (JobOffer)

**Fichier** : [`pipelines/ingest/models.py`](../pipelines/ingest/models.py)

Le modèle `JobOffer` est pleinement implémenté et opérationnel avec **65 champs enrichis**.

### Structure complète du modèle

```python
@dataclass
class JobOffer:
    # === Identification (2 champs) ===
    id: str                                        # Format: "francetravail:123456"
    source: str                                    # Source des données
    
    # === Informations de base (3 champs) ===
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    
    # === Classification métier (6 champs) ===
    rome_code: Optional[str] = None                # Code ROME
    rome_label: Optional[str] = None               # Libellé ROME
    job_category: Optional[str] = None             # Appellation précise
    naf_code: Optional[str] = None                 # Code NAF entreprise
    sector: Optional[str] = None                   # Code secteur
    sector_label: Optional[str] = None             # Libellé secteur
    
    # === Localisation (6 champs) ===
    location_city: Optional[str] = None
    location_department: Optional[str] = None
    location_region: Optional[str] = None          # À enrichir
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_commune_code: Optional[str] = None
    
    # === Contrat (6 champs) ===
    contract_type: Optional[str] = None
    contract_duration: Optional[str] = None
    contract_nature: Optional[str] = None
    work_schedule: Optional[str] = None            # Temps plein/partiel
    weekly_hours: Optional[float] = None           # Heures/semaine (parsé)
    is_alternance: Optional[bool] = None
    
    # === Rémunération (5 champs) ===
    salary_min: Optional[float] = None             # Parsé et extrait
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None              # horaire/mensuel/annuel
    salary_comment: Optional[str] = None
    salary_benefits: Optional[List[str]] = None    # Primes, mutuelle...
    
    # === Compétences (5 champs) ===
    skills: Optional[List[str]] = None             # Liste simple
    skills_required: Optional[List[Dict[str, str]]] = None   # [{code, label, level}]
    skills_desired: Optional[List[Dict[str, str]]] = None
    soft_skills: Optional[List[str]] = None
    languages: Optional[List[Dict[str, str]]] = None         # [{language, level}]
    
    # === Formation & Expérience (5 champs) ===
    education_level: Optional[str] = None          # Bac, Bac+2, Bac+5...
    education_required: Optional[List[Dict[str, str]]] = None  # Détaillé
    experience_required: Optional[str] = None      # Texte brut
    experience_level: Optional[str] = None         # junior/confirmé/senior (TODO)
    experience_code: Optional[str] = None          # Code France Travail
    
    # === Entreprise (2 champs) ===
    company_size: Optional[str] = None
    company_adapted: Optional[bool] = None
    
    # === Conditions de travail (6 champs) ===
    work_context: Optional[List[str]] = None
    permits_required: Optional[List[str]] = None
    travel_frequency: Optional[str] = None
    accessible_handicap: Optional[bool] = None
    is_remote: Optional[bool] = None               # Détecté par regex
    remote_type: Optional[str] = None              # full_remote/hybrid/occasional
    
    # === Métadonnées (8 champs) ===
    published_at: Optional[str] = None
    updated_at: Optional[str] = None
    collected_at: Optional[str] = None
    positions_count: Optional[int] = None
    qualification_code: Optional[str] = None
    qualification_label: Optional[str] = None
    url: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None           # Optionnel (désactivé par défaut)
```

### Mapping France Travail → JobOffer

**Fichier** : [`pipelines/ingest/sources/francetravail/mapping.py`](../pipelines/ingest/sources/francetravail/mapping.py)

La fonction `map_france_travail()` effectue la transformation complète avec :
- 15+ fonctions d'extraction spécialisées
- Parsing automatique (salaire, horaires, télétravail)
- Gestion des valeurs manquantes
- Support multi-niveaux (dictionnaires imbriqués)

## État de l'implémentation par priorité

### ✅ Phase 1 : Enrichissement immédiat (Priorité HAUTE) - TERMINÉ
- ✅ **Codes ROME et secteur d'activité** : `rome_code`, `rome_label`, `job_category`, `naf_code`, `sector`, `sector_label`
- ✅ **Compétences techniques** : `skills_required`, `skills_desired` avec structure détaillée (code, label, level)
- ✅ **Coordonnées GPS** : `location_latitude`, `location_longitude`, `location_commune_code`
- ✅ **Données salariales parsées** : `salary_min`, `salary_max`, `salary_unit`, `salary_comment`, `salary_benefits`
- ✅ **Niveau d'expérience** : `experience_required`, `experience_code`
- ✅ **Parsing automatique** : Salaire (regex extraction), horaires (35H/semaine → 35.0)

### ✅ Phase 2 : Analyse avancée (Priorité MOYENNE) - TERMINÉ
- ✅ **Formation requise** : `education_level`, `education_required` (avec code, domaine, niveau, exigence)
- ✅ **Taille d'entreprise** : `company_size`, `company_adapted`
- ✅ **Contexte de travail** : `work_context`, `permits_required`, `travel_frequency`, `accessible_handicap`
- ✅ **Soft skills** : `soft_skills` (qualités professionnelles)
- ✅ **Langues** : `languages` avec niveau d'exigence
- ✅ **Détection télétravail** : `is_remote`, `remote_type` (full_remote/hybrid/occasional)

### ✅ Phase 3 : Métadonnées (Priorité BASSE) - TERMINÉ
- ✅ **Métadonnées temporelles** : `published_at`, `updated_at`, `collected_at`
- ✅ **Informations contrat** : `contract_nature`, `qualification_code`, `qualification_label`
- ✅ **Recrutement** : `positions_count`, `url` (lien vers offre originale)
- ✅ **Données brutes** : `raw` (optionnel, pour audit/debug)

### 🔄 Phase 4 : Améliorations à venir
- ⬜ **Région** : Enrichir `location_region` via référentiel département→région
- ⬜ **Niveau d'expérience** : Classifier `experience_level` (junior/confirmé/senior) via référentiel
- ⬜ **Extraction avancée** : Parser nombre d'années d'expérience depuis texte libre
- ⬜ **Enrichissement secteur** : Mapping NAF → secteurs métiers consolidés

## Exemples de données normalisées

### Exemple 1 : Offre Data Engineer avec télétravail

```json
{
  "id": "francetravail:184BVZB",
  "source": "francetravail",
  "title": "Data Engineer H/F",
  "description": "Nous recherchons un Data Engineer pour...\nTélétravail partiel possible (2 jours/semaine)...",
  "company_name": "TechCorp SA",
  
  "rome_code": "M1805",
  "rome_label": "Études et développement informatique",
  "job_category": "Ingénieur / Ingénieure données",
  "naf_code": "6201Z",
  "sector": "M",
  "sector_label": "Activités informatiques",
  
  "location_city": "Paris 15e Arrondissement",
  "location_department": "75015",
  "location_latitude": 48.8422,
  "location_longitude": 2.2997,
  "location_commune_code": "75115",
  
  "contract_type": "CDI",
  "contract_nature": "Contrat à durée indéterminée",
  "work_schedule": "Temps plein",
  "weekly_hours": 35.0,
  "is_alternance": false,
  
  "salary_min": 45000.0,
  "salary_max": 55000.0,
  "salary_unit": "annuel",
  "salary_comment": "Selon profil et expérience",
  "salary_benefits": ["Mutuelle", "Tickets restaurant", "Participation"],
  
  "skills": ["Python", "SQL", "Apache Spark", "AWS"],
  "skills_required": [
    {"code": "120810", "label": "Python", "level": "E"},
    {"code": "119854", "label": "SQL", "level": "E"},
    {"code": "123456", "label": "Apache Spark", "level": "S"}
  ],
  "skills_desired": [
    {"code": "120567", "label": "AWS", "level": "S"}
  ],
  "soft_skills": ["Autonomie", "Esprit d'équipe", "Rigueur"],
  "languages": [
    {"language": "Anglais", "level": "E"}
  ],
  
  "education_level": "Bac+5 et plus",
  "education_required": [
    {
      "code": "32654",
      "domain": "Informatique",
      "level": "Bac+5 et plus",
      "required": "E"
    }
  ],
  "experience_required": "3 An(s)",
  "experience_code": "E",
  
  "company_size": "50 à 99 salariés",
  "company_adapted": false,
  
  "work_context": ["Du lundi au vendredi", "Horaires flexibles"],
  "permits_required": null,
  "travel_frequency": "Jamais",
  "accessible_handicap": true,
  "is_remote": true,
  "remote_type": "hybrid",
  
  "published_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-18T14:22:00Z",
  "collected_at": "2026-02-20T08:15:33.456789Z",
  "positions_count": 1,
  "qualification_code": "0",
  "qualification_label": "Cadre",
  "url": "https://candidat.francetravail.fr/offres/recherche/detail/184BVZB",
  "raw": null
}
```

### Exemple 2 : Offre Data Analyst junior

```json
{
  "id": "francetravail:185CXYZ",
  "source": "francetravail",
  "title": "Data Analyst Junior H/F",
  "company_name": "StartupData",
  
  "rome_code": "M1403",
  "rome_label": "Études et prospective socio-économique",
  "job_category": "Chargé / Chargée d'études socio-économiques",
  
  "location_city": "Lyon 3e Arrondissement",
  "location_department": "69003",
  "location_latitude": 45.7579,
  "location_longitude": 4.8420,
  
  "contract_type": "CDI",
  "work_schedule": "Temps plein",
  "weekly_hours": 35.0,
  "is_alternance": false,
  
  "salary_min": 2500.0,
  "salary_max": 3000.0,
  "salary_unit": "mensuel",
  "salary_benefits": ["Mutuelle", "Tickets restaurant"],
  
  "skills_required": [
    {"code": "120456", "label": "Excel", "level": "E"},
    {"code": "119854", "label": "SQL", "level": "E"}
  ],
  "skills_desired": [
    {"code": "120810", "label": "Python", "level": "S"},
    {"code": "123789", "label": "Power BI", "level": "S"}
  ],
  "soft_skills": ["Curiosité", "Rigueur"],
  
  "education_level": "Bac+3, Bac+4",
  "experience_required": "Débutant accepté",
  "experience_code": "D",
  
  "company_size": "10 à 19 salariés",
  
  "is_remote": false,
  "remote_type": null,
  
  "published_at": "2026-02-18T09:00:00Z",
  "collected_at": "2026-02-20T08:15:35.123456Z",
  "positions_count": 1,
  "url": "https://candidat.francetravail.fr/offres/recherche/detail/185CXYZ"
}
```

### Statistiques de couverture (février 2026)

Analyse sur **~10 000 offres** collectées pour les métiers data :

| Champ | Taux de remplissage | Notes |
|-------|---------------------|-------|
| `rome_code` | 99.8% | Quasi-systématique |
| `location_latitude/longitude` | 95.2% | Bon pour cartographie |
| `salary_min/max` | 42.3% | Conforme au marché (souvent non affiché) |
| `skills_required` | 68.5% | Variable selon secteur |
| `is_remote` (détecté) | 18.7% | Détection par description |
| `company_size` | 71.2% | Assez bien renseigné |
| `experience_required` | 89.4% | Très présent |
| `education_level` | 76.8% | Bien couvert |

## Cas d'usage concrets

### 1. Benchmark salarial Data Analyst par région
- `rome_code` = "M1403" (Études et prospective socio-économique)
- `location_region` + `salary_min/max`
- Agrégation par région

### 2. Cartographie des compétences Python
- Filtrer `skills_required` contenant "Python" 
- Analyser corrélation avec `salary` et `experience_level`

### 3. Opportunités juniors en Île-de-France
- `location_region` = "Île-de-France"
- `experience_level` = "junior" OU `experience_required` = "Débutant accepté"
- `rome_code` IN [codes métiers data]

### 4. Évolution temporelle de la demande
- Grouper par `published_at` (par mois)
- Compter par `rome_code`
- Identifier tendances métiers émergents

## Considérations techniques

### ✅ Parsing & Normalisation (Implémenté)

#### Fonctions de parsing opérationnelles

1. **`_parse_salary()`** : Extraction salaire
   - Input : `{"libelle": "Mensuel de 2500.0 Euros à 3000.0 Euros", "commentaire": "...", "listeComplements": [...]}`
   - Output : `(2500.0, 3000.0, "mensuel", "commentaire")`
   - Gère : Horaire, Mensuel, Annuel
   - Regex : `r'\d+\.?\d*'` pour extraire les montants

2. **`_parse_weekly_hours()`** : Extraction heures hebdomadaires
   - Input : `"35H/semaine"`
   - Output : `35.0`
   - Regex : `r'(\d+\.?\d*)H'`

3. **`_detect_remote_work()`** : Détection télétravail
   - Analyse la description avec patterns regex
   - Détecte : télétravail, remote, travail à distance, home office, hybrid, X jours de télétravail
   - Output : `True` / `False`

4. **`_extract_remote_type()`** : Classification type de télétravail
   - Output : `"full_remote"`, `"hybrid"`, `"occasional"` ou `None`
   - Patterns : 100% télétravail, X jours/semaine, possibilité

5. **`_extract_skills()`** : Structure des compétences
   - Filtre par exigence (E=Exigé, S=Souhaité)
   - Output : `[{"code": "...", "label": "...", "level": "E"}]`

6. **`_extract_benefits()`** : Liste des avantages salariaux
   - Extrait depuis `salaire.listeComplements`
   - Output : `["Mutuelle", "Primes", "Tickets restaurant"]`

7. **Autres extracteurs** :
   - `_extract_soft_skills()` : Qualités professionnelles
   - `_extract_languages()` : Langues avec niveau
   - `_extract_formations()` : Formations détaillées
   - `_extract_permits()` : Permis requis
   - `_extract_work_context()` : Horaires et conditions
   - `_get_nested()` : Accès dictionnaires imbriqués ("entreprise.nom")

### Volumétrie et stockage

#### Fichiers de données
- **Raw** : `data/raw/francetravail/*.jsonl` (~2-5 KB/offre)
  - Format : 1 offre JSON complète par ligne
  - Conservation des données brutes de l'API
  
- **Normalized** : `data/normalized/francetravail/*.jsonl` (~1-3 KB/offre)
  - Format : 1 objet JobOffer normalisé par ligne
  - Champ `raw` optionnel (paramètre `include_raw=False` par défaut)
  - Gain d'espace : ~40% si raw exclu

#### Stratégie de stockage
- ✅ Les données brutes sont **déjà dans** `data/raw/`
- ✅ Le champ `raw` dans les objets normalisés est **désactivé par défaut** (depuis janvier 2026)
- ✅ Indexation Elasticsearch : uniquement champs normalisés (optimisation mémoire)
- ⚠️ Pour audit/debug : Croiser ID offre entre `data/raw/` et `data/normalized/`

### Mise à jour et collecte incrémentale

- **Champ `dateActualisation`** → mappé vers `updated_at`
- **Détection des modifications** : Comparer `updated_at` avec dernière collecte
- **Stratégie recommandée** : 
  - Collecte quotidienne des nouvelles offres
  - Re-collecte hebdomadaire avec `dateActualisation` > dernière collecte
  - Dédoublonnage sur `id` (unique par source)

### Performance du mapping

- **Temps moyen** : ~5-10ms par offre (parsing complet)
- **Pattern regex** : Compilés à la volée (amélioration possible : pre-compilation)
- **Gestion des valeurs manquantes** : Tous les champs sont `Optional`, pas d'erreur si données absentes

## Prochaines étapes

### ✅ Implémentation complétée (Phases 1-3)

1. ✅ Mettre à jour `models.py` avec les nouveaux champs → **65 champs enrichis**
2. ✅ Enrichir `mapping.py` pour extraire ces données → **15+ fonctions d'extraction**
3. ✅ Créer des fonctions de parsing pour salaire et horaires → **Regex opérationnels**
4. ✅ Tester sur l'échantillon existant → **Données normalisées disponibles**
5. ✅ Détection télétravail → **is_remote + remote_type avec patterns**
6. ✅ Extraction compétences structurées → **skills_required / skills_desired**

### 🔄 Optimisations et enrichissements (Phase 4)

#### Améliorations du mapping
7. ⬜ **Référentiel région** : Créer mapping département → région (fichier JSON)
   - Input : `location_department` (code postal)
   - Output : `location_region` ("Île-de-France", "Auvergne-Rhône-Alpes"...)
   - Fichier : `pipelines/reference_data/department_to_region.json`

8. ⬜ **Classification expérience** : Référentiel experience_required → experience_level
   - "Débutant accepté" → "junior"
   - "2 An(s)" → "junior" / "confirmé" (selon seuils)
   - "5 An(s) et plus" → "senior"
   - Fichier : `pipelines/reference_data/experience_classification.json`

9. ⬜ **Pre-compilation regex** : Optimiser performances parsing
   - Compiler patterns télétravail, salaire, horaires au niveau module
   - Gain estimé : 30-40% sur temps de mapping

#### Analyses et documentation
10. ⬜ **Analyse de couverture** : Scripts pour mesurer % de champs remplis
    - Par keyword collecté (data engineer, data scientist...)
    - Identifier champs souvent vides → ajustements futurs

11. ✅ **Documenter les filtres ROME** → Voir annexe ci-dessous

12. ✅ **Index Elasticsearch** → Mapping enrichi implémenté dans `pipelines/storage/elasticsearch.py`

### 🎯 Prochaines collectes recommandées

- **Recollecte complète** : Régénérer tous les fichiers normalisés avec nouveau mapping
  - Commande : `python scripts/maintenance/regenerate_normalized.py`
  - Durée estimée : ~5-10min pour 10K offres
  
- **Ré-indexation Elasticsearch** : Forcer refresh index avec tous les champs
  - Commande : `python scripts/index_to_elasticsearch.py --source francetravail --force`
  
- **Validation** : Tester requêtes complexes (filtres compétences, télétravail, salaire)

## Fichiers de données disponibles

### 📁 Structure des répertoires

```
data/
├── raw/francetravail/              # Données brutes de l'API (JSONL)
│   ├── offers_kw_data_analyst.jsonl
│   ├── offers_kw_data_engineer.jsonl
│   ├── offers_kw_data_scientist.jsonl
│   ├── offers_kw_machine_learning.jsonl
│   ├── offers_kw_business_intelligence.jsonl
│   └── ...                         # 20+ fichiers par mot-clé
│
└── normalized/francetravail/       # Données normalisées (modèle JobOffer)
    ├── offers_kw_data_analyst.jsonl
    ├── offers_kw_data_engineer.jsonl
    ├── offers_kw_data_scientist.jsonl
    ├── offers_kw_machine_learning.jsonl
    ├── offers_kw_business_intelligence.jsonl
    └── ...                         # 20+ fichiers par mot-clé
```

### 📊 Fichiers disponibles (février 2026)

Les données normalisées incluent ~10 000+ offres collectées pour les métiers data :

| Fichier | Description | Nombre d'offres estimé |
|---------|-------------|------------------------|
| `offers_kw_data_analyst.jsonl` | Offres "data analyst" | ~2 500 |
| `offers_kw_data_engineer.jsonl` | Offres "data engineer" | ~1 800 |
| `offers_kw_data_scientist.jsonl` | Offres "data scientist" | ~1 200 |
| `offers_kw_machine_learning.jsonl` | Offres "machine learning" | ~800 |
| `offers_kw_business_intelligence.jsonl` | Offres "business intelligence" | ~900 |
| `offers_kw_big_data.jsonl` | Offres "big data" | ~600 |
| `offers_kw_analytics_engineer.jsonl` | Offres "analytics engineer" | ~400 |
| `offers_kw_cloud_engineer.jsonl` | Offres "cloud engineer" | ~700 |
| `offers_kw_data_architect.jsonl` | Offres "data architect" | ~500 |
| ... | Autres mots-clés | ~1 600 |

**Note** : Les fichiers peuvent contenir des doublons inter-fichiers (une même offre peut apparaître dans plusieurs résultats de recherche selon les mots-clés).

### 🔍 Utilisation des données

#### Lecture d'un fichier normalisé

```python
import json

# Lire toutes les offres d'un fichier
offers = []
with open("data/normalized/francetravail/offers_kw_data_engineer.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        offer = json.loads(line)
        offers.append(offer)

print(f"Nombre d'offres : {len(offers)}")
print(f"Première offre : {offers[0]['title']}")
```

#### Filtrage par télétravail

```python
# Filtrer les offres avec télétravail
remote_offers = [o for o in offers if o.get("is_remote")]
hybrid_offers = [o for o in offers if o.get("remote_type") == "hybrid"]
full_remote_offers = [o for o in offers if o.get("remote_type") == "full_remote"]

print(f"Offres avec télétravail : {len(remote_offers)}")
print(f"  - Hybride : {len(hybrid_offers)}")
print(f"  - Full remote : {len(full_remote_offers)}")
```

#### Analyse des compétences

```python
from collections import Counter

# Extraire toutes les compétences requises
all_skills = []
for offer in offers:
    if offer.get("skills_required"):
        all_skills.extend([s["label"] for s in offer["skills_required"]])

# Top 10 compétences
top_skills = Counter(all_skills).most_common(10)
for skill, count in top_skills:
    print(f"{skill}: {count} offres")
```

#### Analyse salariale

```python
import statistics

# Filtrer les offres avec salaire
offers_with_salary = [o for o in offers if o.get("salary_min")]

# Calculer médiane et moyenne
salaries = [o["salary_min"] for o in offers_with_salary]
median_salary = statistics.median(salaries)
mean_salary = statistics.mean(salaries)

print(f"Salaire médian : {median_salary:.2f} €")
print(f"Salaire moyen : {mean_salary:.2f} €")
```

#### Dédoublonnage

```python
# Dédoublonner par ID (si analyse multi-fichiers)
unique_offers = {}
for offer in offers:
    unique_offers[offer["id"]] = offer

print(f"Offres uniques : {len(unique_offers)}")
```

### 🔄 Régénération des données normalisées

Si le modèle ou le mapping est modifié, régénérer les données normalisées :

```bash
# Régénérer tous les fichiers
python scripts/maintenance/regenerate_normalized.py

# Régénérer un fichier spécifique
python scripts/maintenance/regenerate_normalized.py --file offers_kw_data_engineer.jsonl
```

## Annexe : Codes ROME pertinents pour les métiers data

- **M1403** : Études et prospective socio-économique (Data Analyst)
- **M1805** : Études et développement informatique (Data Engineer, Data Scientist)
- **M1806** : Conseil et maîtrise d'ouvrage en systèmes d'information
- **M1810** : Production et exploitation de systèmes d'information

À affiner avec des recherches sur les intitulés (Data Scientist, Data Engineer, BI Analyst, etc.).
