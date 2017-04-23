from .base_site import *
from speedy.core.settings.staging import activate_staging

activate_staging(settings=globals())

DEFAULT_FROM_EMAIL = 'webmaster@speedymatch.org'

