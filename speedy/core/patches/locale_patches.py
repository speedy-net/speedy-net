from django.conf import settings as django_settings
from django.utils import formats


def patch():
    formats.FORMAT_SETTINGS = formats.FORMAT_SETTINGS.union(django_settings.FORMAT_SETTINGS)


