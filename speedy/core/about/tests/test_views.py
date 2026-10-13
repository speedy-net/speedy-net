"""
Test cases for the about page view of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.tests.test_views import StaticBaseViewTestCaseMixin


    class AboutViewOnlyEnglishTestCase(StaticBaseViewTestCaseMixin, SiteTestCase):
        """
        Test the about page view (English only, since the about page doesn't depend on the language).

        Methods:
            test_visitor_can_access_about_page(self): Verify a visitor can access the about page.
        """

        def get_page_url(self):
            """Returns the URL of the "about my match" settings edit page."""
            return '/about/'

        def get_template_name(self):
            """Returns the template name of the "about my match" settings edit page."""
            return 'about/about.html'

        def test_visitor_can_access_about_page(self):
            """
            Asserts a visitor can access the about page and that it uses the expected template.
            """
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertTemplateUsed(response=r, template_name=self.template_name)


