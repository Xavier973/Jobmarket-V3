# Tests

Ce dossier contient les tests du projet JobMarket V3.

## Fichiers

### `test_enriched_mapping.py`
Test de validation du mapping enrichi des offres France Travail.

**Objectif :**
- Valider la qualité des données collectées
- Analyser les taux de couverture des champs enrichis
- Vérifier le bon fonctionnement du mapping

**Métriques analysées :**
- Couverture GPS (coordonnées géographiques)
- Couverture salaire (données salariales parsées)
- Distribution des codes ROME
- Distribution géographique (départements)
- Compétences techniques détectées

**Utilisation :**
```bash
# Tester le mapping sur l'échantillon par défaut
python tests/test_enriched_mapping.py

# Tester sur un fichier spécifique
python tests/test_enriched_mapping.py data/raw/francetravail/offers_kw_data_analyst.jsonl
```

**Résultats attendus :**
- ✅ GPS : >95% de couverture
- ✅ Salaire : >80% de couverture
- ✅ Compétences : Détection des technologies (Python, SQL, etc.)
- ✅ Codes ROME : Cohérence avec le type d'offres

---

## Ajouter de nouveaux tests

### Tests unitaires
Pour tester des fonctions individuelles (parsers, extracteurs, etc.) :

```python
# tests/test_parsers.py
def test_parse_salary():
    from pipelines.ingest.sources.francetravail.mapping import _parse_salary
    result = _parse_salary({"libelle": "Mensuel de 3000.0 Euros sur 12.0 mois"})
    assert result["salary_min"] == 3000.0
    assert result["salary_unit"] == "monthly"
```

### Tests d'intégration
Pour tester le pipeline complet sur des données réelles :

```python
# tests/test_integration_francetravail.py
def test_full_pipeline():
    # Collecte → Normalisation → Validation
    pass
```

---

## Framework de tests

Pour l'instant, les tests sont des scripts standalone. Pour une approche plus structurée, considérez :

- **pytest** : Framework de test recommandé pour Python
- **unittest** : Framework intégré à Python
- **coverage** : Mesure de la couverture du code

### Installation (future)
```bash
pip install pytest pytest-cov
```

### Exécution (future)
```bash
# Tous les tests
pytest tests/

# Avec couverture
pytest --cov=pipelines tests/

# Test spécifique
pytest tests/test_enriched_mapping.py
```

---

## Bonnes pratiques

1. **Nommage** : Préfixez les fichiers de test avec `test_`
2. **Isolation** : Chaque test doit être indépendant
3. **Documentation** : Expliquez ce que teste chaque fonction
4. **Données** : Utilisez des fixtures ou des échantillons de test
5. **Assertions** : Vérifiez les résultats attendus explicitement
