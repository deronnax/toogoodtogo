import os

import dj_database_url

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASES = {
    'default': dj_database_url.config()
}

STATIC_ROOT = BASE_DIR / 'static'

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
