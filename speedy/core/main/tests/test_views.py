"""
Test cases for the main page view of Speedy Composer and Speedy Mail Software.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (not (django_settings.LOGIN_ENABLED)):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_without_login
        from speedy.core.base.tests.test_views import StaticBaseViewTestCaseMixin


        @only_on_sites_without_login
        class MainPageViewOnlyEnglishTestCase(StaticBaseViewTestCaseMixin, SiteTestCase):
            """
            Tests speedy.composer.main.views.MainPageView and speedy.mail.main.views.MainPageView.

            These views are registered as the Django apps speedy.composer.main and speedy.mail.main, which have no tests/
            directory of their own, so they are tested here, in the speedy.core.main app, which is installed on every site without login.
            """

            def get_page_url(self):
                """
                :return: The canonical URL path of the page.
                """
                return '/'

            def get_template_name(self):
                """
                :return: The name of the template expected to render the page.
                """
                return 'main/main_page.html'


