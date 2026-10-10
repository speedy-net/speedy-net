"""
Django settings of the Speedy Match site for the development environment.
"""
from .base_site import *
from speedy.core.settings.development_utils import activate_development

activate_development(settings=globals())


