from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase


        class TermsOfServiceViewOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.page_url = '/terms/'

            def test_visitor_can_access_terms_of_service_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='terms/terms_of_service.html')

            def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
                r = self.client.get(path=self.page_url + '?utm_source=test')
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


