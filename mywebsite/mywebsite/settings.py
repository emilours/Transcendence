"""
Django settings for mywebsite project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-=tr6v@=3o78u=rnby-i3&$&b%(wlbr6lm$_7kw3!usjj&bbn9%'
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'


# ALLOWED_HOSTS = ["127.0.0.1"]
# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split()
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'rest_framework',
	'rest_framework.authtoken',
    'frontend',
    'authentification',
    'invaders',
    'pong',
]

ASGI_APPLICATION = 'mywebsite.asgi.application'

# in production we would use redis for in-memory database
# CHANNEL_LAYERS={
# 	'default':{
# 		'BACKEND':'channels.layers.InMemoryChannelLayer'
# 	}
# }

# For production (using redis)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("redis", 6379)]
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mywebsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		# 'DIRS': [BASE_DIR / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mywebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        'NAME': os.environ.get('SQL_DATABASE', 'default_db_name'),
        'USER': os.environ.get('SQL_USER', 'default_user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'default_password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django_password_validators.password_character_requirements.password_validation.PasswordCharacterValidator',
        'OPTIONS': {
            'min_length_digit': 1,
            'min_length_alpha': 1,
            'min_length_special': 1,
            'min_length_lower': 1,
            'min_length_upper': 1,
            'special_characters': "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~",
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# Directory where collectstatic will place the files
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # Redirect after login
# LOGIN_REDIRECT_URL = 'home'
# LOGOUT_REDIRECT_URL = 'home'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',  # Nginx is serving the app here
    'http://127.0.0.1:8080',  # Ensure this is included if you're using localhost
    'http://paul-f4ar5s4:8080',# Add other domains as needed
]

# Custom user model
AUTH_USER_MODEL = 'frontend.CustomUser'

# Configuration de l'API 42
FORTYTWO_AUTHORIZATION_BASE_URL = 'https://api.intra.42.fr/oauth/authorize'
FORTYTWO_TOKEN_URL = 'https://api.intra.42.fr/v2/oauth/token'
FORTYTWO_USER_URL = 'https://api.intra.42.fr/v2/me'
API_42_AUTH_URL = os.environ.get('API_42_AUTH_URL')

# API 42 AUTHENTIFICATION
FORTYTWO_CLIENT_ID = os.getenv('CLIENT_ID')
FORTYTWO_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
FORTYTWO_REDIRECT_URI = os.getenv('API_42_REDIRECT_URI')

# Configuration de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
