from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (not (django_settings.LOGIN_ENABLED)):
        from speedy.core.base.test.models import SiteTestCase


        class MainPageViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests speedy.composer.main.views.MainPageView and speedy.mail.main.views.MainPageView.

            These views are not registered as Django apps (they have no apps.py and are not listed in
            INSTALLED_APPS), so they have no tests/ directory of their own and are not discovered by the
            default test runner. We test them here instead, since speedy.core.base is installed on every site.
            """
            def set_up(self):
                """
                Sets up the main page URL used by the tests.
                """
                super().set_up()
                self.page_url = '/'

            def test_visitor_can_access_main_page(self):
                """
                Tests that a visitor can access the main page and that it renders the expected template.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
                """
                Tests that requesting the main page with an extra query string redirects permanently (301) to the canonical page URL.
                """
                r = self.client.get(path=self.page_url + '?utm_source=test')
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


