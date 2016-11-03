from speedy.core.test import TestCase
from .models import SiteProfile


class SiteProfileTestCase(TestCase):
    def test_get_active_languages(self):
        p = SiteProfile(active_languages='en, he, de')
        self.assertListEqual(p.get_active_languages(), ['en', 'he', 'de'])
        p = SiteProfile(active_languages='')
        self.assertListEqual(p.get_active_languages(), [])

    def test_set_active_languages(self):
        p = SiteProfile()
        p.set_active_languages(['en', 'he'])
        self.assertSetEqual(set(p.get_active_languages()), {'en' , 'he'})
