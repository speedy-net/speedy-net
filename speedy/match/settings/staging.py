from .base_site import *
from speedy.core.settings.staging_utils import activate_staging

activate_staging(settings=globals())

DEFAULT_FROM_EMAIL = 'webmaster@speedy.match.2.speedy-technologies.com'


