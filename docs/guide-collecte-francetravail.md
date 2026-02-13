# Guide de Collecte - France Travail API

## 🎯 Stratégies de recherche

### ✅ Méthode recommandée : Recherche par mots-clés

```bash
# Ciblage précis des métiers data
python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst" --limit 200
python -m pipelines.ingest.sources.francetravail.main --keywords "data engineer" --limit 200
python -m pipelines.ingest.sources.francetravail.main --keywords "data scientist" --limit 200
```

**Avantages :**
- ✅ Haute précision : 71% de pertinence sur "data analyst"
- ✅ Capture tous les codes ROME liés
- ✅ Flexible : combine plusieurs termes ("data analyst OR business intelligence")

**Résultats obtenus (testés février 2026) :**
- "data analyst" → 71% code M1419 (Data analyst)
- Salaires moyens : 36-42K€/an
- Titres cohérents : "Data analyst (H/F)" majoritaire

---

### ⚠️ Méthode à éviter : Codes ROME génériques

```bash
# ❌ NE PAS UTILISER - Trop génériques !
python -m pipelines.ingest.sources.francetravail.main --rome-codes M1403,M1805,M1806 --limit 200
```

**Pourquoi ?**
- ❌ M1403 = Chargé d'études (BTP, urbanisme, électricité) → **97% faux positifs**
- ❌ M1805 = Développeur généraliste (Java, C#, web) → **95% faux positifs**
- ❌ M1806 = Consultant SI / Business analyst → **70% faux positifs**

**Résultats obtenus :**
- 200 offres collectées → seulement **5 offres data** (2.5%)
- Majorité : Techniciens BE, développeurs web, consultants SI

---

### ✅ Codes ROME spécifiques validés

Si vous voulez absolument utiliser les codes ROME, utilisez les codes **spécifiques** :

```bash
# ✅ Codes ROME précis pour les métiers data
python -m pipelines.ingest.sources.francetravail.main --rome-codes M1419,M1811,M1405 --limit 200
```

**Codes validés (API France Travail 2026) :**
- **M1419** : Data analyst (71% des offres "data analyst")
- **M1811** : Data engineer (4% des offres "data analyst" - code mixte)
- **M1405** : Data scientist (3% des offres "data analyst")

---

## 📊 Stratégie de collecte complète

### Étape 1 : Collecte ciblée par mots-clés

```bash
# Data Analyst
python -m pipelines.ingest.sources.francetravail.main \
  --keywords "data analyst" \
  --limit 500

# Data Engineer  
python -m pipelines.ingest.sources.francetravail.main \
  --keywords "data engineer" \
  --limit 500

# Data Scientist
python -m pipelines.ingest.sources.francetravail.main \
  --keywords "data scientist" \
  --limit 500

# Business Intelligence
python -m pipelines.ingest.sources.francetravail.main \
  --keywords "business intelligence" \
  --limit 500
```

### Étape 2 : Validation des résultats

```bash
# Analyser la qualité des données collectées
python analyze_data_analyst.py
```

**Critères de qualité :**
- ✅ Titres cohérents (>70% mention "data")
- ✅ Codes ROME dominés par M1419, M1811, M1405
- ✅ Salaires cohérents (30-60K€/an)
- ✅ Compétences techniques : Python, SQL, BI tools

### Étape 3 : Normalisation et nettoyage

```bash
# Les fichiers normalisés sont créés automatiquement
# data/normalized/francetravail/offers_kw_data_analyst.jsonl
```

---

## 🔍 Combinaison mots-clés + filtres avancés

L'API France Travail permet de combiner plusieurs critères. Exemple pour les offres seniors :

```python
# Dans main.py, ajouter le paramètre experience
params = {
    "motsCles": "data analyst",
    "experience": "3"  # 3+ ans d'expérience
}
```

---

## 📈 Exemples de mots-clés pertinents

### Analytics & BI
- `data analyst`
- `business intelligence`
- `analyste données`
- `bi analyst`
- `power bi`
- `tableau analyst`

### Engineering & Architecture
- `data engineer`
- `ingénieur données`
- `data architect`
- `big data engineer`
- `etl developer`

### Science & ML
- `data scientist`
- `machine learning`
- `ml engineer`
- `ai engineer`
- `deep learning`

---

## ⚡ Bonnes pratiques

1. **Commencez petit** : `--limit 100` pour tester
2. **Vérifiez la qualité** : Analysez les 10 premiers titres
3. **Itérez** : Ajustez les mots-clés selon les résultats
4. **Combinez** : Utilisez plusieurs requêtes complémentaires
5. **Documentez** : Notez la date et les paramètres utilisés

---

## 🐛 Résolution de problèmes

### Problème : Trop de faux positifs

**Solution :** Utilisez des mots-clés plus spécifiques
```bash
# Au lieu de "analyst"
python -m pipelines.ingest.sources.francetravail.main --keywords "data analyst"

# Au lieu de "python"  
python -m pipelines.ingest.sources.francetravail.main --keywords "python data engineer"
```

### Problème : Pas assez de résultats

**Solution :** Élargissez avec plusieurs variantes
```bash
python -m pipelines.ingest.sources.francetravail.main --keywords "data engineer OR ingénieur données"
```

### Problème : Offres obsolètes

**Solution :** L'API retourne par défaut les offres récentes (dernières semaines)

---

## 📝 Logs et traçabilité

Chaque collecte génère :
- **Fichier raw** : `data/raw/francetravail/offers_kw_<keywords>.jsonl`
- **Fichier normalisé** : `data/normalized/francetravail/offers_kw_<keywords>.jsonl`
- **Statistiques** : Nombre d'offres, pages collectées

---

## 🔄 Mise à jour référentiel

Le fichier `reference_data.py` a été mis à jour avec les codes ROME validés :

```python
ROME_CODES_DATA = {
    "M1419": "Data analyst",      # ✅ Validé 71% pertinence
    "M1811": "Data engineer",     # ✅ Validé 4% pertinence  
    "M1405": "Data scientist",    # ✅ Validé 3% pertinence
}
```

---

**Date de validation :** Février 2026  
**Source :** API France Travail v2  
**Échantillon testé :** 100 offres "data analyst"
