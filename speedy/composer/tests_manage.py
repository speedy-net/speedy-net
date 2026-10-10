#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks on the Speedy Composer site, using the tests environment settings.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parent.parent.parent))

from speedy.core.settings.utils import env

if (__name__ == "__main__"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speedy.composer.settings.{}".format(env('TESTS_ENVIRONMENT')))

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv=sys.argv)


