FROM python:3.11-slim

WORKDIR /app

# Installer curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copier les requirements du projet principal (pour pipelines)
COPY requirements.txt ./requirements_main.txt

# Copier les requirements du backend
COPY backend/requirements.txt ./requirements_backend.txt

# Installer toutes les dépendances
RUN pip install --no-cache-dir -r requirements_main.txt && \
    pip install --no-cache-dir -r requirements_backend.txt

# Copier le module pipelines (pour réutilisation du code)
COPY pipelines /app/pipelines

# Copier le code de l'application backend
COPY backend/app /app/app

# Exposer le port
EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
