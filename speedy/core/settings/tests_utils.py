from .utils import ROOT_DIR

TESTS_MEDIA_ROOT = str(ROOT_DIR / 'tests' / 'media')

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
        #         'verbose': {
# #            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#             'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
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
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'speedy': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


def activate_tests(settings):
    settings.update({
        'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
        'TESTS_MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'MEDIA_ROOT': TESTS_MEDIA_ROOT,
        'LOGGING': LOGGING,
        'TESTS': True,
        'DEBUG': True,
    })


