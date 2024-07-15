FROM python:3.9

# Définit le répertoire de travail dans le conteneur
WORKDIR ./backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Ajouter psycopg2-binary -> connecteur DB
RUN pip install psycopg2-binary

# Copie tous les fichiers du répertoire courant
COPY . .

# pour Gunicorn
EXPOSE 8000

# demarre l'application avec Gunicorn
CMD ["gunicorn", "my_website.wsgi:application", "--bind", "0.0.0.0:8000"]
