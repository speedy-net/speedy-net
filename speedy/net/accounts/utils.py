import random
import string

from django.apps import apps
from django.conf import settings


def generate_id():
    chars = string.digits + string.ascii_lowercase
    chars_without_zero = chars[1:]
    return ''.join(random.choice(chars if i > 0 else chars_without_zero) for i in range(15))


def get_site_profile_model():
    return apps.get_model(*settings.AUTH_SITE_PROFILE_MODEL.split('.'))
