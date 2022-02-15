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
        'console': {  # for development
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


def activate_development(settings):
    settings.update({
        'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
        'MIDDLEWARE': ['debug_toolbar.middleware.DebugToolbarMiddleware'] + settings['MIDDLEWARE'],
        'INSTALLED_APPS': settings['INSTALLED_APPS'] + ['debug_toolbar'],
        'LOGGING': LOGGING,
        'USE_HTTPS': False,
        'SESSION_COOKIE_SECURE': False,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'CSRF_COOKIE_SECURE': False,
        'DEBUG': True,
    })


