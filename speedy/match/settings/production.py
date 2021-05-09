from .base_site import *
from speedy.core.settings.production_utils import activate_production

activate_production(settings=globals())

DEFAULT_FROM_EMAIL = 'notifications@speedymatch.com'
SERVER_EMAIL = 'webmaster+production-server@speedymatch.com'


