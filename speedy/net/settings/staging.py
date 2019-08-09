from .base_site import *
from speedy.core.settings.staging_utils import activate_staging

activate_staging(settings=globals())

DEFAULT_FROM_EMAIL = 'webmaster@speedy.net.2.speedy-technologies.com'
SERVER_EMAIL = 'webmaster+staging-server@speedy.net.2.speedy-technologies.com'

