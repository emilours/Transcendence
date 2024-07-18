mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py

Le premier répertoire racine mysite/ est un contenant pour votre projet. Son nom n’a pas d’importance pour Django ; vous pouvez le renommer comme vous voulez.

manage.py : un utilitaire en ligne de commande qui vous permet d’interagir avec ce projet Django de différentes façons.

Le sous-répertoire mysite/ correspond au paquet Python effectif de votre projet. C’est le nom du paquet Python que vous devrez utiliser pour importer ce qu’il contient (par ex. mysite.urls).

mysite/__init__.py : un fichier vide qui indique à Python que ce répertoire doit être considéré comme un paquet. 

mysite/settings.py : réglages et configuration de ce projet Django.

mysite/urls.py : les déclarations des URL de ce projet Django, une sorte de « table des matières » de votre site Django. 

mysite/asgi.py : un point d’entrée pour les serveurs Web compatibles aSGI pour déployer votre projet. Voir Comment déployer avec ASGI pour plus de détails.

mysite/wsgi.py : un point d’entrée pour les serveurs Web compatibles WSGI pour déployer votre projet. Voir Comment déployer avec WSGI pour plus de détails.

******************************************************************************************************************************************************************

Utilisation de Django admin :

Gérer les utilisateurs : Utilisez Django admin pour ajouter et gérer les utilisateurs, attribuer des rôles et des permissions.
Modérer le contenu : La modération des messages, des commentaires et autres contenus générés par les utilisateurs peut être effectuée via l'interface admin.
Visualiser les données : Accédez rapidement aux statistiques et aux données clés de l'application via l'interface admin.

Utilisation de manage.py :

Développement et déploiement : Utilisez manage.py pour appliquer des migrations, exécuter le serveur de développement, collecter des fichiers statiques pour le déploiement, etc.
Automatisation des tâches : Écrivez des scripts de gestion et des tâches récurrentes, comme la sauvegarde de la base de données ou l'importation de données en masse.
Tests : Exécutez des tests unitaires et fonctionnels pour vous assurer que votre application fonctionne correctement.

******************************************************************************************************************************************************************

Les fichiers package.json, yarn.lock et webpack.config.js sont tous les trois des éléments importants dans un projet frontend utilisant des outils comme Webpack et Yarn, notamment lorsque l'on utilise des bibliothèques comme Bootstrap pour la gestion des dépendances et la compilation des assets. 