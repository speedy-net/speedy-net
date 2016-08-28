from unittest import TestCase

from django.conf import settings
from django.test.runner import DiscoverRunner

from speedy.net.settings.utils import env


class SiteDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = [label for label in settings.INSTALLED_APPS if label.startswith('speedy.')]
        return super().build_suite(test_labels, extra_tests, **kwargs)

def conditional_test(test_func):
    def wrapper(method):
        def inner(self: TestCase):
            if test_func():
                return method(self)
            else:
                return
        return inner
    return wrapper

exclude_on_site = lambda site_id: conditional_test(lambda: int(settings.SITE_ID) != int(site_id))
exclude_on_speedy_net = exclude_on_site(env('SPEEDY_NET_SITE_ID'))
exclude_on_speedy_match = exclude_on_site(env('SPEEDY_MATCH_SITE_ID'))

# only_on_site = lambda site_id: conditional_test(lambda: int(settings.SITE_ID) == int(site_id))
# only_on_speedy_net = only_on_site(env('SPEEDY_NET_SITE_ID'))
# only_on_speedy_match = only_on_site(env('SPEEDY_MATCH_SITE_ID'))
