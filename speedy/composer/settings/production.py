"""
Django settings of the Speedy Composer production environment.
"""
from .base_site import *
from speedy.core.settings.production_utils import activate_production

activate_production(settings=globals())


