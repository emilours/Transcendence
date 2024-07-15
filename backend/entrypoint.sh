#!/bin/bash

if [ -d "venv" ]; then
  source venv/bin/activate
fi

# migrations de la base de données
python manage.py migrate

# Collecte les fichiers statiques
python manage.py collectstatic --noinput

exec "$@"
