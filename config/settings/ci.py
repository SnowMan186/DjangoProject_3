from .base import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'test_db'),
        'USER': os.environ.get('POSTGRES_USER', 'test_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'test_password'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'courses']