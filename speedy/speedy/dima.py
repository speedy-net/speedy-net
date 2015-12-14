from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'speedynet',
        'USER': 'initech',
        # No password, use peer authentication
    }
}

FROM_EMAIL = 'dima.orman@initech.co.il'

# Install django extensions locally
INSTALLED_APPS.append('django_extensions')
