import os
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(repo_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

from config.settings.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'test_db'),
        'USER': os.environ.get('POSTGRES_USER', 'test_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'test_password'),
        'HOST': 'localhost', # Сервис postgres доступен по имени хоста
        'PORT': '5432',
    }
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'courses']