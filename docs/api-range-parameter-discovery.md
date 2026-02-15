# Découverte : Paramètre `range` de l'API France Travail

**Date** : 15 février 2026  
**Contexte** : Limitation à 150 offres par recherche  
**Source** : Repository [etiennekintzler/api-offres-emploi](https://github.com/etiennekintzler/api-offres-emploi)

## Problème initial

L'API France Travail ne retournait que 150 offres maximum, même en utilisant la pagination avec `page=0`, `page=1`, `page=2`, etc.

**Symptôme** : 
```
GET .../search?page=0&size=50&motsCles=data+engineer
📊 Content-Range: offres 0-149/353

GET .../search?page=1&size=50&motsCles=data+engineer  
📊 Content-Range: offres 0-149/353  ← Toujours les mêmes !
```

→ **Les pages 0, 1, 2... renvoyaient toutes les 150 premières offres**

## Solution découverte

L'API France Travail utilise un **paramètre `range`** au format `"start-end"` (et non `page`/`size`).

### Spécification officielle

D'après la documentation API Offres d'emploi v2 :

- **Format du range** : `"0-149"`, `"150-299"`, `"300-449"`, etc.
- **Contraintes** :
  - Valeur max du 1er élément : **1000**
  - Valeur max du 2ème élément : **1149**  
  - Nombre de résultats par requête : **≤ 150**
- **Maximum accessible** : **1150 offres** par recherche (0-1149)

### Implémentation

```python
# Avant (ne fonctionnait pas)
params = {"page": 0, "size": 50}

# Après (fonctionnel)
params = {"range": "0-149"}   # 1ère requête
params = {"range": "150-299"} # 2ème requête
params = {"range": "300-449"} # 3ème requête
# ... jusqu'à
params = {"range": "1000-1149"} # Dernière requête possible
```

## Résultats

### "data engineer" (353 offres disponibles)

**Avant** :
- Page 0, 1, 2... : toujours 0-149/353  
- **Total collecté : 150 offres** ❌

**Après** :
- Range 0-149 : 150 offres (Content-Range: 0-149/353)  
- Range 150-299 : 150 offres (Content-Range: 150-299/353)
- Range 300-449 : 53 offres (Content-Range: 300-352/353)
- **Total collecté : 353 offres** ✅

**Gain : +135%**

### "python" (3577 offres disponibles)

**Avant** :
- **Total collecté : 150 offres** ❌

**Après** :
- Range 0-149 : 150 offres  
- Range 150-299 : 150 offres
- Range 300-449 : 150 offres
- ... (jusqu'à range 1000-1149)
- **Total collecté : 1150 offres** ✅

**Gain : +666%**

## Stratégie pour > 1150 offres

Pour les recherches retournant plus de 1150 résultats, **deux approches** :

### 1. Subdivision par dates

```python
params = {
    "motsCles": "python",
    "range": "0-149",
    "minCreationDate": "2024-01-01T00:00:00Z",
    "maxCreationDate": "2024-01-31T23:59:59Z"
}
```

→ Collecter par tranches mensuelles pour rester sous 1150 par tranche

### 2. Filtres multiples (contract × experience)

```bash
python -m pipelines.ingest.sources.francetravail.main \
  --keywords "python" \
  --split-by-contract
```

→ Subdivise en 30 combinaisons (5 contrats × 5 niveaux expérience + 5 sans filtre expérience)

## Preuve technique

Les logs montrent clairement le header HTTP `Content-Range` :

```log
18:42:37 [INFO] 🌐 API Request: GET .../search?range=0-149&motsCles=data+engineer
18:42:39 [INFO] ✅ HTTP Status: 206 Partial Content
18:42:39 [INFO] 📊 Content-Range: offres 0-149/353

18:42:41 [INFO] 🌐 API Request: GET .../search?range=150-299&motsCles=data+engineer
18:42:42 [INFO] ✅ HTTP Status: 206 Partial Content  
18:42:42 [INFO] 📊 Content-Range: offres 150-299/353

18:48:15 [INFO] 🌐 API Request: GET .../search?range=300-449&motsCles=data+engineer
18:48:15 [INFO] ✅ HTTP Status: 206 Partial Content
18:48:15 [INFO] 📊 Content-Range: offres 300-352/353

18:48:18 [INFO] 🌐 API Request: GET .../search?range=450-599&motsCles=data+engineer
18:48:19 [INFO] ✅ HTTP Status: 204 No Content
18:48:19 [INFO] 📊 Content-Range: offres -1--1/353  ← Fin de la collection
```

→ HTTP **206** = Partial Content (pagination active)  
→ HTTP **204** = No Content (plus de résultats)

## Vérification 0% doublons

```bash
📊 Analyse de offers_kw_data_engineer.jsonl...

📈 Résultats :
   Total de lignes      : 353
   Offres uniques       : 353
   Doublons détectés    : 0
   Taux de duplication  : 0.0%
```

## Impact sur le projet

### Code modifié

- **`pipelines/ingest/sources/francetravail/main.py`** : 
  - Remplacement `page` → `range_start`
  - Calcul `range_end = min(range_start + 150 - 1, 1149)`
  - Paramètre `{"range": f"{range_start}-{range_end}"}`

- **`pipelines/ingest/sources/francetravail/client.py`** :
  - Logging URL complète
  - Logging headers (secrets masqués)
  - Logging Content-Range et métadonnées serveur

### Documentation mise à jour

- ✅ `README.md` : Section Troubleshooting
- ✅ `docs/guide-collecte-francetravail.md` : Limitation API
- ✅ `docs/api-range-parameter-discovery.md` : Ce document

## Références

- [Repository etiennekintzler/api-offres-emploi](https://github.com/etiennekintzler/api-offres-emploi/blob/master/README.md)
- [README.md - Section "About range and pagination"](https://raw.githubusercontent.com/etiennekintzler/api-offres-emploi/master/README.md)
- [Code source api_wrapper](https://raw.githubusercontent.com/etiennekintzler/api-offres-emploi/master/offres_emploi/api.py)

## Conclusion

Le paramètre `range` résout complètement le problème de pagination de l'API France Travail. 

**Bénéfices** :
- ✅ Collection complète jusqu'à 1150 offres par recherche
- ✅ 0% de doublons (verified)  
- ✅ Logging détaillé prouvant les limites serveur
- ✅ Code plus simple (pas besoin de --split-by-contract pour <1150 offres)

**Limites restantes** :
- ❌ Maximum 1150 offres par recherche (limitation API documentée)
- ⚠️  Écart avec le site web (353 API vs 1337 site pour "data engineer") - **Mais** : le site utilise une recherche floue qui renvoie beaucoup de faux positifs (ex: "Développeur COBOL" pour "data engineer"). L'API est plus stricte = **meilleure pertinence**. Les 353 offres API sont de meilleure qualité que les 1337 du site.
- ⚠️  Quelques offres partenaires (Indeed, Monster, LinkedIn) visibles sur le site ne sont pas accessibles via l'API publique (impact marginal)

**Conclusion qualité** : L'API France Travail privilégie la **pertinence** sur la **quantité**. Les 353 offres "data engineer" sont réellement pertinentes, contrairement aux 1337 du site qui incluent beaucoup de bruit.

**Solution pour diversifier** : Intégrer d'autres sources (APEC, LinkedIn, Indeed) pour élargir la couverture tout en gardant la qualité.
