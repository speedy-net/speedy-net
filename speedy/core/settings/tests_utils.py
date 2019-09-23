from .utils import ROOT_DIR

TESTS_MEDIA_ROOT = str(ROOT_DIR / 'tests' / 'media')


def activate_tests(settings):
    settings.update({
        'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
        'TESTS_MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'TESTS': True,
        'DEBUG': True,
    })
