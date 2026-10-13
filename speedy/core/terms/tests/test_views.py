"""
Test cases for the terms of service view of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.tests.test_views import NonCanonicalPathRedirectsPermanentlyTestCaseMixin


        class TermsOfServiceViewOnlyEnglishTestCase(NonCanonicalPathRedirectsPermanentlyTestCaseMixin, SiteTestCase):
            """
            Test the terms of service page view (English only, since the terms of service page doesn't depend on the language).

            Methods:
                test_visitor_can_access_terms_of_service_page(self): Verify a visitor can access the terms of service page.
            """

            def set_up(self):
                """
                Sets up the terms of service page URL.
                """
                super().set_up()
                self.page_url = '/terms/'

            def test_visitor_can_access_terms_of_service_page(self):
                """
                Asserts a visitor can access the terms of service page and that it uses the expected template.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='terms/terms_of_service.html')


