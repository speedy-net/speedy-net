"""
Django settings used when running the Speedy Composer tests.
"""
from .base_site import *
from speedy.core.settings.tests_utils import activate_tests

activate_tests(settings=globals())


