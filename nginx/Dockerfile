FROM nginx:1.25

RUN apt update && apt install -y openssl
RUN mkdir -p /etc/nginx/ssl /var/run/nginx
RUN openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=arincon.42.fr/UID=arincon"

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080