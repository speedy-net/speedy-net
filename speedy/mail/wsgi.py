"""
WSGI config for speedy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

from speedy.core.patches import locale_patches

sys.path.insert(0, str(Path(__file__).absolute().parent.parent.parent))
from speedy.core.settings.utils import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speedy.mail.settings.{}".format(env('ENVIRONMENT')))

locale_patches.patch()

application = get_wsgi_application()


