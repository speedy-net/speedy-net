from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase


    class AboutViewOnlyEnglishTestCase(SiteTestCase):
        """
        Test the about page view (English only, since the about page doesn't depend on the language).

        Methods:
            test_visitor_can_access_about_page(self): Verify a visitor can access the about page.
            test_non_canonical_path_redirects_permanently_to_canonical_path(self): Verify a non-canonical path (with a query string) redirects permanently to the canonical path.
        """

        def set_up(self):
            """
            Sets up the about page URL.
            """
            super().set_up()
            self.page_url = '/about/'

        def test_visitor_can_access_about_page(self):
            """
            Asserts a visitor can access the about page and that it uses the expected template.
            """
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertTemplateUsed(response=r, template_name='about/about.html')

        def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
            """
            Asserts a non-canonical path (with a query string) redirects permanently (301) to the canonical path.
            """
            r = self.client.get(path=self.page_url + '?utm_source=test')
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


