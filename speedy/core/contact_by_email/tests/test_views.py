from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (not (django_settings.LOGIN_ENABLED)):
        from speedy.core.base.test.models import SiteTestCase


        class ContactUsViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the static contact-us page, for sites without login (English only).

            Methods:
                set_up(self): Sets the contact-us page URL.
                test_visitor_can_access_contact_us_page(self): Asserts a visitor can access the contact-us page and it renders the expected template.
                test_non_canonical_path_redirects_permanently_to_canonical_path(self): Asserts a non-canonical path (with a query string) redirects permanently to the canonical contact-us page URL.
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

            def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
                """
                Asserts a non-canonical path (with an extra query string) redirects permanently (301) to the canonical contact-us page URL.
                """
                r = self.client.get(path=self.page_url + '?utm_source=test')
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


