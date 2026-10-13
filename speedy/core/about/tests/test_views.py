"""
Test cases for the about page view of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.tests.test_views import StaticBaseViewTestCaseMixin


    class AboutViewOnlyEnglishTestCase(StaticBaseViewTestCaseMixin, SiteTestCase):
        """
        Test the about page view (English only, since the about page doesn't depend on the language).
        """

        def get_page_url(self):
            """
            :return: The canonical URL path of the page.
            """
            return '/about/'

        def get_template_name(self):
            """
            :return: The name of the template expected to render the page.
            """
            return 'about/about.html'


