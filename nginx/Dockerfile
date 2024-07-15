FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

# Copie les fichiers statiques collectés par Django dans le conteneur
COPY backend/static /static
COPY backend/media /media

EXPOSE 80
