# Données à collecter depuis l'API France Travail

## Vue d'ensemble

Ce document analyse les données disponibles via l'API France Travail et propose une stratégie de collecte pour le projet JobMarket V3.

## Documentation officielle de l'API France Travail
https://francetravail.io/produits-partages/catalogue/offres-emploi/documentation#/api-reference/operations/recupererListeOffre


## État actuel

### Champs actuellement mappés
- `id` → identifiant de l'offre
- `title` → intitulé du poste
- `description` → description de l'offre
- `company_name` → nom de l'entreprise
- `location_city` → ville
- `location_department` → code postal
- `contract_type` → type de contrat
- `published_at` → date de publication
- `collected_at` → date de collecte
- `raw` → données brutes complètes

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

## Proposition d'enrichissement du modèle canonique

### Nouveaux champs à ajouter

```python
@dataclass
class JobOffer:
    # === Champs actuels ===
    id: str
    source: str
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    location_department: Optional[str] = None
    location_region: Optional[str] = None
    contract_type: Optional[str] = None
    contract_duration: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: Optional[str] = None
    skills: Optional[List[str]] = None
    published_at: Optional[str] = None
    collected_at: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    
    # === NOUVEAUX CHAMPS PRIORITAIRES ===
    
    # Classification métier
    rome_code: Optional[str] = None
    rome_label: Optional[str] = None
    job_category: Optional[str] = None
    naf_code: Optional[str] = None
    sector: Optional[str] = None
    
    # Localisation enrichie
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_commune_code: Optional[str] = None
    
    # Compétences détaillées
    skills_required: Optional[List[Dict[str, str]]] = None  # [{code, label, level}]
    skills_desired: Optional[List[Dict[str, str]]] = None
    soft_skills: Optional[List[str]] = None
    languages: Optional[List[Dict[str, str]]] = None
    
    # Rémunération enrichie
    salary_benefits: Optional[List[str]] = None  # Primes, avantages
    salary_comment: Optional[str] = None
    
    # Formation & Expérience
    education_level: Optional[str] = None  # Bac, Bac+2, Bac+5...
    experience_required: Optional[str] = None  # Débutant, 2 ans, 5 ans...
    experience_level: Optional[str] = None  # junior, confirmé, senior
    
    # Contrat & Organisation
    is_remote: Optional[bool] = None
    work_schedule: Optional[str] = None  # Temps plein, temps partiel
    weekly_hours: Optional[float] = None
    is_internship: Optional[bool] = None
    
    # Entreprise
    company_size: Optional[str] = None
    
    # Métadonnées
    positions_count: Optional[int] = None
    url: Optional[str] = None
    updated_at: Optional[str] = None
```

## Stratégie de collecte recommandée

### Phase 1 : Enrichissement immédiat
Ajouter les champs priorité HAUTE au mapping actuel :
- ✅ Codes ROME et secteur d'activité
- ✅ Compétences techniques
- ✅ Coordonnées GPS
- ✅ Données salariales extraites
- ✅ Niveau d'expérience

### Phase 2 : Analyse avancée
Intégrer les champs priorité MOYENNE :
- Formation requise
- Taille d'entreprise
- Contexte de travail

### Phase 3 : Complétion
Collecter les métadonnées optionnelles selon les besoins analytics.

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

### Parsing & Normalisation
Certains champs nécessitent du parsing :
- **Salaire** : Le champ `salaire.libelle` contient du texte libre ("Mensuel de 2500 à 3000 euros") → extraire min/max/unité
- **Horaires** : "35H/semaine" → extraire volume horaire
- **Expérience** : "2 An(s)" → normaliser en durée numérique

### Volumétrie
L'API France Travail retourne des documents JSON conséquents (~2-5 KB par offre).
- Stocker `raw` pour debug/audit
- Indexer uniquement les champs normalisés dans Elasticsearch

### Mise à jour
- `dateActualisation` permet de détecter les offres modifiées
- Stratégie : collecter quotidiennement les nouvelles + mises à jour

## Prochaines étapes

1. ✅ Mettre à jour `models.py` avec les nouveaux champs
2. ✅ Enrichir `mapping.py` pour extraire ces données
3. ⬜ Créer des fonctions de parsing pour salaire et horaires
4. ⬜ Tester sur l'échantillon existant
5. ⬜ Documenter les filtres ROME pour métiers data
6. ⬜ Définir index Elasticsearch avec mapping adapté

## Annexe : Codes ROME pertinents pour les métiers data

- **M1403** : Études et prospective socio-économique (Data Analyst)
- **M1805** : Études et développement informatique (Data Engineer, Data Scientist)
- **M1806** : Conseil et maîtrise d'ouvrage en systèmes d'information
- **M1810** : Production et exploitation de systèmes d'information

À affiner avec des recherches sur les intitulés (Data Scientist, Data Engineer, BI Analyst, etc.).
