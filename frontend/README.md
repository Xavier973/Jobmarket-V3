# Frontend Dashboard - JobMarket V3

Dashboard React + Next.js pour visualiser les données du marché de l'emploi.

## Stack

- **Next.js 14** (App Router)
- **React 18**
- **TypeScript**
- **TailwindCSS** (styling)
- **Recharts** (graphiques)
- **Leaflet** (carte)
- **Tanstack Query** (data fetching)
- **Axios** (HTTP client)

## Installation

```bash
cd frontend
npm install
```

## Configuration

Créer un fichier `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Développement

```bash
npm run dev
```

Accès : http://localhost:3000

## Build

```bash
npm run build
npm start
```

## Structure

```
frontend/
├── src/
│   ├── app/                  # Pages Next.js (App Router)
│   │   ├── layout.tsx
│   │   ├── page.tsx          # Landing page
│   │   └── dashboard/
│   │       ├── page.tsx      # Dashboard principal
│   │       ├── offers/       # Liste offres
│   │       ├── analytics/    # Analytics avancées
│   │       └── map/          # Carte interactive
│   ├── components/           # Composants réutilisables
│   │   ├── ui/               # Composants UI génériques
│   │   ├── charts/           # Graphiques
│   │   ├── filters/          # Filtres
│   │   └── map/              # Carte
│   ├── lib/                  # Utilitaires
│   │   ├── api.ts            # Client API
│   │   └── formatters.ts     # Formatage données
│   ├── hooks/                # Custom hooks React
│   ├── types/                # Types TypeScript
│   └── styles/               # Styles globaux
└── public/                   # Assets statiques
```

## Pages

- `/` : Landing page
- `/dashboard` : Vue d'ensemble (KPIs + stats)
- `/dashboard/offers` : Liste des offres (à implémenter)
- `/dashboard/analytics` : Analyses approfondies (à implémenter)
- `/dashboard/map` : Carte géographique (à implémenter)

## Développement

Le frontend communique avec le backend FastAPI via l'API REST.

Assurez-vous que :
1. Elasticsearch est démarré
2. Le backend FastAPI tourne sur le port 8000
3. Les données sont indexées

## TODO

- [ ] Implémenter page liste des offres
- [ ] Implémenter page analytics avancées
- [ ] Implémenter carte interactive Leaflet
- [ ] Ajouter système de filtres
- [ ] Ajouter graphiques interactifs (Recharts)
- [ ] Ajouter mode sombre
- [ ] Optimiser performances (React Query)
- [ ] Tests E2E
