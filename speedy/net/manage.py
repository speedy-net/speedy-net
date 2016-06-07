#!/usr/bin/env python
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).absolute().parent.parent.parent))

from speedy.net.settings.utils import env

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speedy.net.settings.{}".format(env('ENVIRONMENT')))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
