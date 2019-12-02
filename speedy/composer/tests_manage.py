#!/usr/bin/env python
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).absolute().parent.parent.parent))

from speedy.core.settings.utils import env
from speedy.core.patches import locale_patches

if (__name__ == "__main__"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speedy.composer.settings.{}".format(env('TESTS_ENVIRONMENT')))

    locale_patches.patch()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


