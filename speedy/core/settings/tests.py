"""
Django settings of Speedy Core for running tests.
"""
from .base_site import *
from speedy.core.settings.tests_utils import activate_tests

activate_tests(settings=globals())


