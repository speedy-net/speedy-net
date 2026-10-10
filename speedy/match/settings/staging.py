from .base_site import *
from speedy.core.settings.staging_utils import activate_staging

activate_staging(settings=globals())

# Sender addresses of notification emails and server error emails on the Speedy Match staging site.
DEFAULT_FROM_EMAIL = 'notifications@speedy.match.2.speedy-technologies.com'
SERVER_EMAIL = 'webmaster+staging-server@speedy.match.2.speedy-technologies.com'


