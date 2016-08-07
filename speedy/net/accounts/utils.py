import random
import string

from django.apps import apps
from django.conf import settings


def generate_id(id_length):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if i > 0 else digits_without_zero) for i in range(id_length))


def get_site_profile_model():
    return apps.get_model(*settings.AUTH_SITE_PROFILE_MODEL.split('.'))
