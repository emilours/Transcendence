TRANSCENDENCE/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── myproject/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── ...
│   ├── manage.py
│   └── ...
│
├── nginx/
│   └── nginx.conf
│
├── docker-compose.yml
├── .env


pour gerer DB : docker exec -it postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

nano ~/.zshrc
export PATH="$PATH:/mnt/nfs/homes/eminatch/.local/bin"
(O pui X) -> scripts installés dans ce répertoire (comme django-admin après l'installation de Django) sont accessibles depuis n'importe quel terminal, 
