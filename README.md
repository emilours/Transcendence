nano ~/.zshrc
export PATH="$PATH:/mnt/nfs/homes/eminatch/.local/bin"
(O pui X) -> scripts installés dans ce répertoire (comme django-admin après l'installation de Django) sont accessibles depuis n'importe quel terminal

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
    │   ├── pong/
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   └── urls.py
    │   ├── second_game/
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   └── urls.py
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
    │   ├── webpack.config.js
    |── NGINX/
    │   ├── Dockerfile
    │   └── nginx.conf
    └── .env
    └── docker-compose.yml