from django.apps import apps
from django.conf import settings


def get_site_profile_model():
    return apps.get_model(*settings.AUTH_SITE_PROFILE_MODEL.split('.'))
