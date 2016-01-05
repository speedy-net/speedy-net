from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'speedynet',
        'USER': 'speedynet',
        'PASSWORD': 'speedynet',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

FROM_EMAIL = 'webmaster@speedy.net'
