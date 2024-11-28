"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from os.path import join, dirname
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from split_settings.tools import include

load_dotenv(find_dotenv())

include(
    'components/database.py',
)

include(
    'components/middleware.py',
)

include(
    'components/apps.py',
)
include(
    'components/notification.py',
)

# Custom user model
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
AUTH_API_LOGIN_URL = os.environ.get('AUTH_API_LOGIN_URL')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
LIMIT_OF_REQUESTS_PER_MINUTE = int(os.environ.get('ADMIN_LIMIT_OF_REQUESTS_PER_MINUTE'))

DEBUG = os.environ.get('DEBUG', False) == 'True'

CORS_ALLOW_ALL_ORIGINS = True

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'config.urls'

LOCALE_PATHS = ('movies/locale',)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'