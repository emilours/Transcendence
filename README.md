nano ~/.zshrc
export PATH="$PATH:/mnt/nfs/homes/eminatch/.local/bin"
(O pui X) -> scripts installés dans ce répertoire (comme django-admin après l'installation de Django) sont accessibles depuis n'importe quel terminal

http://localhost:8000 -> check if true












Transcendence/
├── backend/
│   ├── auth/
│   ├── gameplay/
│   ├── games/
│   ├── manage.py
│   ├── my_website/
│   ├── media/
│   └── static/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── yarn.lock
│   └── webpack.config.js
└── NGINX/
└── docker-compose.yml

Transcendence/
    ├── backend/
    │   ├── auth/
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   ├── user_management/
    │   │   ├── gdpr/
    │   │   ├── two_factor_auth/
    │   │   └── user_stats/
    │   ├── gameplay/
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   ├── remote_players/
    │   │   ├── game_customization/
    │   │   ├── ai_opponent/
    │   │   └── graphics/
    │   ├── games/
    │   │   ├── __init__.py
    │   │   ├── first_game/
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── views.py
    │   │   │   └── urls.py
    │   │   ├── second_game/
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── views.py
    │   │   │   └── urls.py
    │   ├── manage.py
    │   └── my_website/
    │       ├── __init__.py
    │       ├── settings.py
    │       ├── urls.py
    │       └── wsgi.py
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── pages/
    │   │   ├── services/
    │   │   └── index.js
    │   ├── public/
    │   │   ├── index.html
    │   │   └── assets/
    │   ├── package.json
    │   ├── yarn.lock
    │   ├── webpack.config.js (ou autre config de build)
    │   └── .env
    └── docker-compose.yml



MICRO SERVICES:
Transcendence/
    ├── backend/
    │   ├── auth-service/
    │   │   ├── manage.py
    │   │   ├── auth/
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── views.py
    │   │   │   ├── urls.py
    │   │   │   ├── user_management/
    │   │   │   ├── gdpr/
    │   │   │   ├── two_factor_auth/
    │   │   │   └── user_stats/
    │   │   └── requirements.txt
    │   ├── gameplay-service/
    │   │   ├── manage.py
    │   │   ├── gameplay/
    │   │   │   ├── __init__.py
    │   │   │   ├── models.py
    │   │   │   ├── views.py
    │   │   │   ├── urls.py
    │   │   │   ├── remote_players/
    │   │   │   ├── game_customization/
    │   │   │   ├── ai_opponent/
    │   │   │   └── graphics/
    │   │   └── requirements.txt
    │   ├── game-service/
    │   │   ├── manage.py
    │   │   ├── games/
    │   │   │   ├── __init__.py
    │   │   │   ├── first_game/
    │   │   │   │   ├── __init__.py
    │   │   │   │   ├── models.py
    │   │   │   │   ├── views.py
    │   │   │   │   └── urls.py
    │   │   │   ├── second_game/
    │   │   │   │   ├── __init__.py
    │   │   │   │   ├── models.py
    │   │   │   │   ├── views.py
    │   │   │   │   └── urls.py
    │   │   └── requirements.txt
    │   ├── docker-compose.yml
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── pages/
    │   │   ├── services/
    │   │   └── index.js
    │   ├── public/
    │   │   ├── index.html
    │   │   └── assets/
    │   ├── package.json
    │   ├── yarn.lock
    │   ├── webpack.config.js (ou autre config de build)
    │   └── .env
    └── docker-compose.yml

APIs REST pour la communication entre microservices.
Dockerfiles pour chaque microservice + MAJ docker-compose.yml.
Monitoring et Gestion des Logs : Prometheus and Grafana 
Déployer  les microservices et tester leur intégration et leur fonctionnement dans l'ensemble du système.