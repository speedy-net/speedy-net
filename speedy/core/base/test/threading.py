from django.core.management import call_command
from django.test.testcases import LiveServerThread

from speedy.core.base.test import tests_settings


class SiteLiveServerThread(LiveServerThread):
    def run(self):
        call_command('load_data', tests_settings.SITES_FIXTURE, verbosity=0)
        return super().run()
