from .base_site import *
from speedy.core.settings.production_utils import activate_production

activate_production(settings=globals())

# Sender addresses of notification emails and server error emails on the Speedy Match production site.
DEFAULT_FROM_EMAIL = 'notifications@speedymatch.com'
SERVER_EMAIL = 'webmaster+production-server@speedymatch.com'


