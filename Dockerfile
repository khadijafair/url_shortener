# Image de base légère avec Python
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier uniquement requirements.txt d'abord (optimisation du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Port exposé (documentation, ne fait rien seul)
EXPOSE 8000

# Commande de lancement du conteneur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]