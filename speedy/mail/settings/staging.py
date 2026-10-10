"""
Django settings of Speedy Mail Software for the staging environment.
"""
from .base_site import *
from speedy.core.settings.staging_utils import activate_staging

activate_staging(settings=globals())


