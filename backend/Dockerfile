# FROM python:3.9

# WORKDIR /backend
# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# # Ajouter psycopg2-binary -> connecteur DB
# RUN pip install psycopg2-binary

# RUN python -m venv venv

# # Copie tous les fichiers du répertoire courant
# COPY . .

# COPY entrypoint.sh /backend/

# RUN chmod +x /backend/entrypoint.sh

# # pour Gunicorn
# EXPOSE 8000

# ENTRYPOINT ["/backend/entrypoint.sh"]

# # demarre l'application avec Gunicorn
# CMD ["gunicorn", "my_website.wsgi:application", "--bind", "0.0.0.0:8000"]

# Utilisez une image Python officielle comme image de base
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /backend

# Copier les fichiers de requirements
COPY ./requirements.txt /backend/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary
RUN pip install python-decouple
RUN python -m venv venv
# Copier le reste du code
COPY . /backend/

# Définir la commande d'entrée pour démarrer le serveur
CMD ["gunicorn", "my_website.wsgi:application", "--bind", "0.0.0.0:8000"]
