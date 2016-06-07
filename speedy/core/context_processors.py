from django.conf import settings as dj_settings


def settings(request):
    return {
        'settings': dj_settings,
    }
