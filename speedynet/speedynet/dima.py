from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'speedynet',
        'USER': 'initech',
        # No password, use peer authentication
    }
}

FROM_EMAIL = 'dima@initech.co.il'

# Install django extensions locally
INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)
