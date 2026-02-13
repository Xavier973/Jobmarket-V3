# Schema canonique JobOffer

Ce schema est une base commune pour toutes les sources. Chaque adapter mappe ses champs vers ce format.

## Champs principaux
- id: identifiant unique global (source + id source).
- source: nom de la source (ex: francetravail).
- title: intitule du poste.
- description: description brute ou nettoyee.
- company_name: nom de l'entreprise.
- location_city: ville principale.
- location_department: code departement.
- location_region: region.
- contract_type: CDI, CDD, alternance, freelance, etc.
- contract_duration: duree si disponible.
- salary_min: salaire min.
- salary_max: salaire max.
- salary_unit: annee, mois, jour, heure.
- skills: liste de competences.
- published_at: date de publication.
- collected_at: date de collecte.
- raw: bloc JSON source brut (optionnel pour debug).

## Extensions
- Tout champ supplementaire doit rester dans raw ou dans un champ "source_fields".
- La logique de mapping se situe dans chaque adapter.
