"""
Utilities for the Speedy Core tests environment settings: the tests media root, the logging configuration and the function which updates a settings dict for tests.
"""
from .utils import ROOT_DIR

# Directory where media files are stored while running tests.
TESTS_MEDIA_ROOT = str(ROOT_DIR / 'tests' / 'media')

# Logging configuration for tests: console logging at DEBUG level.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {  # for tests
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'loggers': {
        'django': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
        'speedy': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


def activate_tests(settings):
    """
    Update the given settings dict in place for the test environment (locmem email backend, tests media root, verbose logging, TESTS flag enabled, DEBUG disabled).

    :param settings: The settings dict to update.
    :type settings: dict
    """
    settings.update({
        'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',  # Django sets it to locmem.EmailBackend anyway.
        'TESTS_MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'LOGGING': LOGGING,
        'TESTS': True,
        'DEBUG': False,  # Django sets it to False anyway.
    })


