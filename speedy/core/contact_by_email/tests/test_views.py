"""
Test cases for the Contact Us view of the contact by email app of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (not (django_settings.LOGIN_ENABLED)):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_without_login
        from speedy.core.base.tests.test_views import StaticBaseViewTestCaseMixin


        @only_on_sites_without_login
        class ContactUsViewOnlyEnglishTestCase(StaticBaseViewTestCaseMixin, SiteTestCase):
            """
            Tests the static contact-us page, for sites without login (English only).

            Methods:
                get_page_url(self): Returns the canonical URL path of the page.
                get_template_name(self): Returns the name of the template expected to render the page.
            """

            def get_page_url(self):
                """
                :return: The canonical URL path of the page.
                """
                return '/contact/'

            def get_template_name(self):
                """
                :return: The name of the template expected to render the page.
                """
                return 'contact_by_email/contact_us.html'


