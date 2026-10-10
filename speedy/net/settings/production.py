"""
Django settings of the Speedy Net site for the production environment.
"""
from .base_site import *
from speedy.core.settings.production_utils import activate_production

activate_production(settings=globals())

# Sender addresses of notification emails and server error emails on the Speedy Net production site.
DEFAULT_FROM_EMAIL = 'notifications@speedy.net'
SERVER_EMAIL = 'webmaster+production-server@speedy.net'


