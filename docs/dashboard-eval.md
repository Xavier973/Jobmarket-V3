# Dashboard - Evaluation

## Contexte
- **Objectif** : Portfolio visible en ligne pour recruteurs
- **Hebergement** : VPS dédié
- **Mise à jour** : Quotidienne (pipeline automatisé)
- **Public cible** : Recruteurs tech (Data Engineer, Analytics Engineer)

## Options comparées

### 1. Dash (Plotly) — **RECOMMANDÉ pour profil Data**
**Pros :**
- Production-ready, stack data standard
- Montre maîtrise Python avancée (callbacks, composants interactifs)
- Déploiement simple VPS (un seul process Python + gunicorn)
- Performances correctes pour données quotidiennes
- Personnalisable avec Bootstrap/CSS custom
- Communauté active et documentation solide

**Cons :**
- Moins sexy visuellement que React (mais largement suffisant)
- Courbe d'apprentissage moyenne pour callbacks complexes

**Temps de dev estimé** : 1-2 semaines
**Déploiement VPS** : gunicorn + nginx reverse proxy

---

### 2. React/Next.js + FastAPI — **RECOMMANDÉ pour profil Fullstack**
**Pros :**
- Stack moderne qui impressionne (montre polyvalence)
- API réutilisable (autres projets portfolio, mobile, etc.)
- Interface professionnelle et très personnalisable
- Bon pour SEO (Next.js SSR)
- Séparation claire front/back (bonnes pratiques)

**Cons :**
- Temps de dev 2-3x supérieur à Dash
- Maintenance deux stacks (Node.js + Python)
- Plus complexe à déployer (deux services)

**Temps de dev estimé** : 3-4 semaines
**Déploiement VPS** : PM2 (Next.js) + gunicorn (FastAPI) + nginx

---

### 3. Streamlit — **NON RECOMMANDÉ**
**Cons critiques pour portfolio :**
- Look "prototype" peu professionnel
- Peu personnalisable (difficile de se démarquer)
- Performances moyennes (rechargement complet à chaque interaction)
- Ne valorise pas suffisamment vos compétences

---

### 4. Metabase / Superset — **NON RECOMMANDÉ**
**Cons critiques pour portfolio :**
- Solution clé en main = ne montre pas de compétences dev
- Moins impressionnant pour recruteurs tech
- Customisation limitée

---

## Critères de décision

| Critère | Dash | React + FastAPI | Streamlit | Metabase |
|---------|------|-----------------|-----------|----------|
| Temps dev | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Impact portfolio | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Personnalisation | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| Déploiement VPS | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Maintenance | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Perf data quotidienne | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Décision finale : **Dash (Plotly)**

**Justification :**
1. **Aligné avec profil Data** : valorise compétences Python/data
2. **Ratio impact/temps optimal** : professionnel en 1-2 semaines
3. **Déploiement VPS simple** : architecture monolithique Python
4. **Adapté au use case** : dashboard analytique avec filtres et cartes
5. **Extensible** : possibilité d'ajouter authentification (dash-auth) si besoin

**Architecture technique retenue :**
```
JobMarket V3 Dashboard (Dash)
├── app.py                 # Point d'entrée Dash
├── components/            # Composants réutilisables
│   ├── filters.py         # Filtres interactifs
│   ├── charts.py          # Graphiques Plotly
│   └── maps.py            # Carte géographique
├── callbacks/             # Logique interactive
│   └── update_charts.py
├── assets/                # CSS/JS custom
│   └── custom.css
└── data/                  # Interface avec Elasticsearch
    └── queries.py
```

**Stack déploiement VPS :**
- **Python 3.9+** + virtualenv
- **Gunicorn** (WSGI server)
- **Nginx** (reverse proxy + HTTPS)
- **Systemd** (service auto-restart)
- **Certbot** (SSL Let's Encrypt)

**Planning :**
- Semaine 1 : Structure Dash + composants de base + connexion Elasticsearch
- Semaine 2 : Filtres avancés + cartes + styling + déploiement VPS
