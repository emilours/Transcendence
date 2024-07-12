FROM python:3.9

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Ajouter psycopg2-binary
RUN pip install psycopg2-binary

# Copie tous les fichiers du répertoire courant
COPY . .

# pour Gunicorn
EXPOSE 8000

# demarre l'application avec Gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
