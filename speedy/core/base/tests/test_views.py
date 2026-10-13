"""
Base test case mixins for the views of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    import random

    from speedy.core.base.test.mixins import TestCaseMixin
    from speedy.core.base.test.models import SiteTestCase


    class StaticBaseViewTestCaseMixin(TestCaseMixin):
        """
        A mixin for test cases of views which redirect non-canonical paths to the canonical path.

        Test cases using this mixin must define `get_page_url` and `get_template_name`. Their results are stored in `self.page_url` and `self.template_name` in `set_up`.

        Methods:
            get_page_url(self): Returns the canonical URL path of the page. Must be defined in classes inherited from this class.
            get_template_name(self): Returns the name of the template expected to render the page. Must be defined in classes inherited from this class.
            set_up(self): Sets `self.page_url` and `self.template_name`.
            test_visitor_can_access_page(self): Asserts a visitor can access the page and that it uses the expected template.
            test_non_canonical_path_redirects_permanently_to_canonical_path(self): Tests that requesting the page with an extra query string redirects permanently (301) to the canonical page URL.
            test_path_starting_with_2_slashes_redirects_permanently_to_canonical_path(self): Tests that requesting the page with a path starting with 2 slashes redirects permanently (301) to the canonical page URL.
            test_path_ending_with_2_slashes_redirects_permanently_to_canonical_path(self): Tests that requesting the page with a path ending with 2 slashes redirects permanently (301) to the canonical page URL.
            test_path_not_ending_with_a_slash_redirects_permanently_to_canonical_path(self): Tests that requesting the page with a path which doesn't end with a slash redirects permanently (301) to the canonical page URL.
        """

        def get_page_url(self):
            """
            :return: The canonical URL path of the page.
            :raises NotImplementedError: Must be defined in classes inherited from this class.
            """
            raise NotImplementedError("get_page_url must be defined in classes inherited from StaticBaseViewTestCaseMixin.")

        def get_template_name(self):
            """
            :return: The name of the template expected to render the page.
            :raises NotImplementedError: Must be defined in classes inherited from this class.
            """
            raise NotImplementedError("get_template_name must be defined in classes inherited from StaticBaseViewTestCaseMixin.")

        def set_up(self):
            """
            Sets `self.page_url` and `self.template_name` from `get_page_url` and `get_template_name`.
            """
            super().set_up()
            self.page_url = self.get_page_url()
            self.template_name = self.get_template_name()

        def test_visitor_can_access_page(self):
            """
            Asserts a visitor can access the page and that it uses the expected template.
            """
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertTemplateUsed(response=r, template_name=self.template_name)

        def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
            """
            Tests that requesting the page with an extra query string redirects permanently (301) to the canonical page URL.
            """
            r = self.client.get(path=self.page_url + '?utm_source=test')
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)

        def test_path_starting_with_2_slashes_redirects_permanently_to_canonical_path(self):
            """
            Tests that requesting the page with a path starting with 2 slashes (for example "//about/") redirects permanently (301) to the canonical page URL.
            """
            # The test client treats a path starting with 2 slashes as a host, so the path is passed in PATH_INFO.
            r = self.client.get(path=self.page_url, PATH_INFO='/' + self.page_url)
            # The target is fetched separately, since assertRedirects would reuse PATH_INFO of this request.
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, fetch_redirect_response=False)
            self.assertEqual(first=self.client.get(path=self.page_url).status_code, second=200)

        def test_path_ending_with_2_slashes_redirects_permanently_to_canonical_path(self):
            """
            Tests that requesting the page with a path ending with 2 slashes (for example "/about//") redirects permanently (301) to the canonical page URL.
            """
            r = self.client.get(path=self.page_url, PATH_INFO=self.page_url + '/')
            # The target is fetched separately, since assertRedirects would reuse PATH_INFO of this request.
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, fetch_redirect_response=False)
            self.assertEqual(first=self.client.get(path=self.page_url).status_code, second=200)

        def test_path_not_ending_with_a_slash_redirects_permanently_to_canonical_path(self):
            """
            Tests that requesting the page with a path which doesn't end with a slash (for example "/about") redirects permanently (301) to the canonical page URL.
            """
            if (self.page_url == '/'):
                self.skipTest(reason="The main page has no path without a slash.")
            self.assertEqual(first=self.page_url[:-1] + '/', second=self.page_url, msg="The canonical page URL must end with a slash.")
            r = self.client.get(path=self.page_url[:-1])
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


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
            # Extra slashes are removed first (by RemoveExtraSlashesMiddleware), and then the "www" page is served.
            r = self.client.get(path='/', PATH_INFO='//')
            self.assertRedirects(response=r, expected_url='/', status_code=301, fetch_redirect_response=False)
            self.assertEqual(first=self.client.get(path='/').status_code, second=200)

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

        def test_domain_without_language_code_redirects_permanently_to_www_page_1(self):
            """
            Asserts the domain of the site without a language code redirects permanently (301) to the "www" page.
            """
            http_host = "1.{domain}".format(domain=self.site.domain)
            client = self.client_class(HTTP_HOST=http_host)
            r = client.get(path='/')
            self.assertEqual(first=r.status_code, second=301)
            self.assertEqual(first=r['Location'], second=self.www_page_url)

        def test_domain_without_language_code_redirects_permanently_to_www_page_2(self):
            """
            Asserts the domain of the site without a language code redirects permanently (301) to the "www" page.
            """
            http_host = "{labels}.{domain}".format(labels=".".join([str(i) for i in range(1, random.randint(2, 6) + 1)]), domain=self.site.domain)
            client = self.client_class(HTTP_HOST=http_host)
            r = client.get(path='/')
            self.assertEqual(first=r.status_code, second=301)
            self.assertEqual(first=r['Location'], second=self.www_page_url)


