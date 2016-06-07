from speedy.net.settings.base import *

from .utils import APP_DIR

SITE_NAME = 'Speedy Match'

STATIC_ROOT = str(APP_DIR / 'static_serve')

TEMPLATES[0]['DIRS'].insert(0, str(APP_DIR / 'templates'))

STATICFILES_DIRS.insert(0, str(APP_DIR / 'static'))
