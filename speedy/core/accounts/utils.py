from django.apps import apps
from django.conf import settings as django_settings


def get_site_profile_model(profile_model=None):
    if (not (profile_model)):
        profile_model = django_settings.AUTH_SITE_PROFILE_MODEL
    return apps.get_model(*profile_model.split('.'))


