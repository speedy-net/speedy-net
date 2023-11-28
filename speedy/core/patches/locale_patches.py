from django.conf import settings as django_settings
from django.utils import formats
from django.utils.translation.trans_real import translation


def patch():
    formats.FORMAT_SETTINGS = formats.FORMAT_SETTINGS.union(django_settings.FORMAT_SETTINGS)

    # Change translation('pt')._fallback[='en'] to translation('pt')._fallback[='pt-br'].
    # https://forum.djangoproject.com/t/missing-translations-in-pt-portuguese/23993
    # Note: translation('pt').add_fallback(translation('pt-br')) will set translation('pt')._fallback[='en']._fallback[='pt-br']
    translation('pt')._fallback = translation('pt-br')


