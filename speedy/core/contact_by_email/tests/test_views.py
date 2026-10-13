"""
Test cases for the Contact Us view of the contact by email app of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (not (django_settings.LOGIN_ENABLED)):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.tests.test_views import NonCanonicalPathRedirectsPermanentlyTestCaseMixin


        class ContactUsViewOnlyEnglishTestCase(NonCanonicalPathRedirectsPermanentlyTestCaseMixin, SiteTestCase):
            """
            Tests the static contact-us page, for sites without login (English only).

            Methods:
                set_up(self): Sets the contact-us page URL.
                test_visitor_can_access_contact_us_page(self): Asserts a visitor can access the contact-us page and it renders the expected template.
            """

            def set_up(self):
                """
                Sets the contact-us page URL.
                """
                super().set_up()
                self.page_url = '/contact/'

            def test_visitor_can_access_contact_us_page(self):
                """
                Asserts a visitor can access the contact-us page and it renders the expected template.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='contact_by_email/contact_us.html')


