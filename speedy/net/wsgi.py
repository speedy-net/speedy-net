"""
WSGI config for speedy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, str(Path(__file__).absolute().parent.parent.parent))
from speedy.core.settings.utils import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speedy.net.settings.{}".format(env('ENVIRONMENT')))

application = get_wsgi_application()


