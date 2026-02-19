FROM node:20-alpine

WORKDIR /app

# Installer curl pour le healthcheck
RUN apk add --no-cache curl

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer toutes les dépendances (dev incluses pour le hot reload)
RUN npm ci

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 3000

# Démarrer en mode dev (peut être surchargé par docker-compose)
CMD ["npm", "run", "dev"]
