"""
Base test case mixins for the views of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import TestCaseMixin


    class StaticBaseViewTestCaseMixin(TestCaseMixin):
        """
        A mixin for test cases of views which redirect non-canonical paths to the canonical path.

        Test cases using this mixin must set `self.page_url` to the canonical path of the page (in `set_up`).

        Methods:
            test_non_canonical_path_redirects_permanently_to_canonical_path(self): Tests that requesting the page with an extra query string redirects permanently (301) to the canonical page URL.
        """

        def test_non_canonical_path_redirects_permanently_to_canonical_path(self):
            """
            Tests that requesting the page with an extra query string redirects permanently (301) to the canonical page URL.
            """
            r = self.client.get(path=self.page_url + '?utm_source=test')
            self.assertRedirects(response=r, expected_url=self.page_url, status_code=301, target_status_code=200)


