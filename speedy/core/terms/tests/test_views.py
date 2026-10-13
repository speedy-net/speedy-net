"""
Test cases for the terms of service view of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.base.tests.test_views import StaticBaseViewTestCaseMixin


        @only_on_sites_with_login
        class TermsOfServiceViewOnlyEnglishTestCase(StaticBaseViewTestCaseMixin, SiteTestCase):
            """
            Test the terms of service page view (English only, since the terms of service page doesn't depend on the language).
            """

            def get_page_url(self):
                """
                :return: The canonical URL path of the page.
                """
                return '/terms/'

            def get_template_name(self):
                """
                :return: The name of the template expected to render the page.
                """
                return 'terms/terms_of_service.html'


