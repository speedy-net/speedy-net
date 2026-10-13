"""
Test cases for the middleware of Speedy Core which removes extra slashes from URLs.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase

    from speedy.core.base.middleware import RemoveExtraSlashesMiddleware


    class RemoveExtraSlashesMiddlewareOnlyEnglishTestCase(SiteTestCase):
        """
        Tests RemoveExtraSlashesMiddleware, in English.
        """

        def test_normalize_path(self):
            """
            Tests that normalize_path() collapses multiple consecutive slashes anywhere in a path into a single slash, without otherwise changing an already-normalized path.
            """
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/'), second='/zzz/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy///'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='////zzz/yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz//yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='////xxx////yyy////'), second='/xxx/yyy/')

        def test_redirect_to_url_without_extra_slashes(self):
            """
            Tests that requests with extra slashes in the path still return a 200 response, and a request with extra trailing slashes redirects (301) to the canonical path.
            """
            # ~~~~ TODO: fix this test!
            r = self.client.get(path='/about/')
            self.assertEqual(first=r.status_code, second=200)
            r = self.client.get(path='///about/')
            self.assertEqual(first=r.status_code, second=200)  # ~~~~ TODO: should be 301
            # self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)
            r = self.client.get(path='/about///')
            self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)
            r = self.client.get(path='///about///')
            self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)


    class WwwViewOnlyEnglishTestCase(SiteTestCase):
        """
        Test the "www" welcome page of the site, handled by LocaleDomainMiddleware (English only, since the "www" page is always in English).

        Methods:
            set_up(self): Sets up the "www" host and the client requesting it.
            test_visitor_can_access_www_page(self): Verify a visitor can access the "www" welcome page.
            test_non_canonical_path_redirects_permanently_to_www_page(self): Verify a path other than the root path on the "www" host redirects permanently to the "www" page.
            test_query_string_redirects_permanently_to_www_page(self): Verify the "www" page with a query string redirects permanently to the "www" page without it.
            test_domain_without_www_redirects_permanently_to_www_page(self): Verify the domain of the site without "www" redirects permanently to the "www" page.
        """

        def set_up(self):
            """
            Sets up the "www" host and the client requesting it.
            """
            super().set_up()
            self.www_host = 'www.{domain}'.format(domain=self.site.domain)
            self.www_page_url = '//{www_host}/'.format(www_host=self.www_host)
            self.client = self.client_class(HTTP_HOST=self.www_host)

        def test_visitor_can_access_www_page(self):
            """
            Asserts a visitor can access the "www" welcome page and that it uses the expected template.
            """
            r = self.client.get(path='/')
            self.assertEqual(first=r.status_code, second=200)
            self.assertTemplateUsed(response=r, template_name='www/welcome.html')

        def test_non_canonical_path_redirects_permanently_to_www_page(self):
            """
            Asserts a path other than the root path on the "www" host redirects permanently (301) to the "www" page.
            """
            for path in ['/about/', '/login/', '/zzz/']:
                r = self.client.get(path=path)
                self.assertEqual(first=r.status_code, second=301, msg="{} didn't return 301.".format(path))
                self.assertEqual(first=r['Location'], second=self.www_page_url, msg="{} didn't redirect to the www page.".format(path))

        def test_query_string_redirects_permanently_to_www_page(self):
            """
            Asserts the "www" page with a query string redirects permanently (301) to the "www" page without it.
            """
            r = self.client.get(path='/?utm_source=test')
            self.assertEqual(first=r.status_code, second=301)
            self.assertEqual(first=r['Location'], second=self.www_page_url)

        def test_domain_without_www_redirects_permanently_to_www_page(self):
            """
            Asserts the domain of the site without "www" redirects permanently (301) to the "www" page.
            """
            client = self.client_class(HTTP_HOST=self.site.domain)
            r = client.get(path='/')
            self.assertEqual(first=r.status_code, second=301)
            self.assertEqual(first=r['Location'], second=self.www_page_url)


